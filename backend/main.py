import base64
import logging
import os
from contextlib import asynccontextmanager

from fastapi import Cookie, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.genai.errors import APIError as GeminiAPIError
from groq import APIError as GroqAPIError

from chat_service import ChatService
from config import Settings
from embedding_service import EmbeddingService, UnsupportedImageError
from auth_service import AuthService, SESSION_COOKIE_NAME, SESSION_LIFETIME_DAYS
from criteria_extractor import CriteriaExtractor, sanitize_for_user
from models import (
    ConnectRequest,
    LoginRequest,
    Prestataire,
    SearchRequest,
    SearchResult,
    SignupRequest,
    UserPublic,
)
from seed_data import load_seed_prestataires
from vector_store import PGVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

settings = Settings()
embed_svc = EmbeddingService(settings)
chat_svc = ChatService(settings)
criteria_svc = CriteriaExtractor(settings)
vector_store: PGVectorStore | None = None
auth_svc: AuthService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store, auth_svc
    dsn = os.getenv("POSTGRES_URI", "postgresql://ps:ps_pgvector_2024@db:5432/karohy")
    vector_store = await PGVectorStore.create(dsn)
    auth_svc = AuthService(vector_store.pool)
    try:
        await load_seed_prestataires(vector_store, embed_svc)
    except Exception as e:
        logger.error("Seed loading failed (server starts without seed data): %s", e)
    yield


app = FastAPI(title="PrestaSearch API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _store() -> PGVectorStore:
    if vector_store is None:
        raise HTTPException(503, "Database not ready")
    return vector_store


# --- GET /health ---
@app.get("/health")
async def health():
    count = await _store().count
    return {"status": "ok", "prestataire_count": count}


# --- GET /prestataires ---
@app.get("/prestataires", response_model=list[Prestataire])
async def list_prestataires():
    return await _store().list_all()


# --- GET /prestataires/{id} ---
@app.get("/prestataires/{prestataire_id}", response_model=Prestataire)
async def get_prestataire(prestataire_id: str):
    p = await _store().get(prestataire_id)
    if not p:
        raise HTTPException(404, "Prestataire not found")
    return p


# --- POST /prestataires ---
@app.post("/prestataires", status_code=201)
async def add_prestataire(
    name: str = Form(...),
    specialty: str = Form(...),
    description: str = Form(...),
    services: str = Form(""),
    city: str = Form(""),
    country: str = Form(""),
    hourly_rate: float = Form(0),
    phone: str = Form(""),
    email: str = Form(""),
    rating: float = Form(0),
    image: UploadFile | None = File(None),
):
    image_base64 = ""
    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode()

    svc_list = [s.strip() for s in services.split(",") if s.strip()]
    prestataire = Prestataire(
        name=name, specialty=specialty, description=description,
        services=svc_list, city=city, country=country,
        hourly_rate=hourly_rate, phone=phone, email=email,
        rating=rating, image_base64=image_base64,
    )

    try:
        embedding = embed_svc.embed_prestataire(prestataire)
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    await _store().add(prestataire, embedding)
    return {"prestataire_id": prestataire.id}


# --- PUT /prestataires/{id} ---
@app.put("/prestataires/{prestataire_id}")
async def update_prestataire(
    prestataire_id: str,
    name: str = Form(...),
    specialty: str = Form(...),
    description: str = Form(...),
    services: str = Form(""),
    city: str = Form(""),
    country: str = Form(""),
    hourly_rate: float = Form(0),
    phone: str = Form(""),
    email: str = Form(""),
    rating: float = Form(0),
    image: UploadFile | None = File(None),
    keep_image: str = Form("false"),
):
    all_prestataires = await _store().list_all()
    existing = next((p for p in all_prestataires if p.id == prestataire_id), None)
    if not existing:
        raise HTTPException(404, "Prestataire not found")

    image_base64 = ""
    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode()
    elif keep_image == "true":
        image_base64 = existing.image_base64

    svc_list = [s.strip() for s in services.split(",") if s.strip()]
    prestataire = Prestataire(
        id=prestataire_id, name=name, specialty=specialty, description=description,
        services=svc_list, city=city, country=country,
        hourly_rate=hourly_rate, phone=phone, email=email,
        rating=rating, image_base64=image_base64, created_at=existing.created_at,
    )

    try:
        embedding = embed_svc.embed_prestataire(prestataire)
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    await _store().update(prestataire_id, prestataire, embedding)
    return {"prestataire_id": prestataire_id}


# --- POST /search ---
@app.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    if not request.text and not request.image_base64:
        raise HTTPException(422, "At least one of text or image_base64 is required")

    image_description = None
    if request.image_base64:
        image_bytes = base64.b64decode(request.image_base64)
        try:
            image_description = embed_svc.describe_image(image_bytes)
        except UnsupportedImageError as e:
            raise HTTPException(415, str(e)) from e
        except Exception as e:
            logger.error("Image description failed: %s", e)
            raise HTTPException(502, "Image analysis service temporarily unavailable.") from e

    # Criteria extraction (cheap LLM call) — produces filters + intent text
    criteria = await criteria_svc.extract(request.text or "", image_description)
    embed_text = criteria.intent_text or " ".join(filter(None, [request.text, image_description]))
    try:
        query_embedding = embed_svc.embed_query(text=embed_text, image_description=image_description)
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    # Hybrid retrieval: structured filter narrows the candidate set, vector ranks within
    results = await _store().filtered_search(query_embedding, criteria, top_k=settings.TOP_K_RESULTS)
    # Fallback to pure semantic if filter eliminates everything
    if not results:
        results = await _store().search(query_embedding, top_k=settings.TOP_K_RESULTS)
    return results


# --- POST /chat ---
@app.post("/chat")
async def chat(request: SearchRequest):
    if not request.text and not request.image_base64:
        raise HTTPException(422, "At least one of text or image_base64 is required")

    image_description = None
    if request.image_base64:
        image_bytes = base64.b64decode(request.image_base64)
        try:
            image_description = embed_svc.describe_image(image_bytes)
        except UnsupportedImageError as e:
            raise HTTPException(415, str(e)) from e
        except Exception as e:
            logger.error("Image description failed: %s", e)
            raise HTTPException(502, "Image analysis service temporarily unavailable.") from e

    criteria = await criteria_svc.extract(request.text or "", image_description)
    embed_text = criteria.intent_text or " ".join(filter(None, [request.text, image_description]))
    try:
        query_embedding = embed_svc.embed_query(text=embed_text, image_description=image_description)
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    results = await _store().filtered_search(query_embedding, criteria, top_k=settings.TOP_K_RESULTS)
    if not results:
        results = await _store().search(query_embedding, top_k=settings.TOP_K_RESULTS)
    user_message = " ".join(filter(None, [request.text, image_description]))

    async def event_stream():
        try:
            async for token in chat_svc.generate_response_stream(user_message, results):
                # Strip markdown / stars before sending to the user
                clean = sanitize_for_user(token)
                if clean:
                    yield f"data: {clean}\n\n"
            yield "data: [DONE]\n\n"
        except GroqAPIError as e:
            logger.error("Chat generation failed: %s", e)
            yield "data: [ERROR] Chat service unavailable\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Auth & Connect (Lot 3+) ─────────────────────────────────────────────────
def _auth() -> AuthService:
    if auth_svc is None:
        raise HTTPException(503, "Auth not ready")
    return auth_svc


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=SESSION_LIFETIME_DAYS * 24 * 3600,
        httponly=True,
        samesite="lax",
        path="/",
    )


@app.post("/auth/signup", response_model=UserPublic)
async def auth_signup(req: SignupRequest, response: Response):
    try:
        user = await _auth().signup(req.username, req.password, req.full_name, req.email)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    _, token = await _auth().login(req.username, req.password)
    _set_session_cookie(response, token)
    return user


@app.post("/auth/login", response_model=UserPublic)
async def auth_login(req: LoginRequest, response: Response):
    try:
        user, token = await _auth().login(req.username, req.password)
    except ValueError as e:
        raise HTTPException(401, str(e)) from e
    _set_session_cookie(response, token)
    return user


@app.get("/auth/me", response_model=UserPublic | None)
async def auth_me(karohy_session: str | None = Cookie(default=None)):
    return await _auth().me(karohy_session)


@app.post("/auth/logout")
async def auth_logout(response: Response, karohy_session: str | None = Cookie(default=None)):
    await _auth().logout(karohy_session)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@app.post("/connect")
async def connect(req: ConnectRequest, karohy_session: str | None = Cookie(default=None)):
    user = await _auth().me(karohy_session)
    if not user:
        raise HTTPException(401, "Login required")
    prestataire = await _store().get(req.prestataire_id)
    if not prestataire:
        raise HTTPException(404, "Prestataire not found")
    created = await _auth().register_connection(user.id, req.prestataire_id, req.message)
    return {"ok": True, "created": created, "prestataire_name": prestataire.name}
