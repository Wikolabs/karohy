import json
import logging

import asyncpg
import numpy as np
from pgvector.asyncpg import register_vector

from models import CriteriaFilter, Prestataire, SearchResult, ServiceDetail

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 3072

# All optional enrichment columns — applied as ALTER TABLE … IF NOT EXISTS
_PRESTATAIRES_EXTRA_COLUMNS = [
    # Lot 3+
    ("organization", "TEXT DEFAULT ''"),
    ("specialties", "JSONB DEFAULT '[]'"),
    ("bio", "TEXT DEFAULT ''"),
    ("cover_photo_base64", "TEXT DEFAULT ''"),
    ("services_detail", "JSONB DEFAULT '[]'"),
    ("latitude", "DOUBLE PRECISION"),
    ("longitude", "DOUBLE PRECISION"),
    ("address", "TEXT DEFAULT ''"),
    # Lot 4 — filterable structured criteria
    ("category", "TEXT DEFAULT ''"),
    ("languages", "JSONB DEFAULT '[]'"),
    ("years_experience", "INTEGER DEFAULT 0"),
    ("emergency_available", "BOOLEAN DEFAULT FALSE"),
    ("accepts_payment", "JSONB DEFAULT '[]'"),
    ("certifications", "JSONB DEFAULT '[]'"),
    ("service_radius_km", "DOUBLE PRECISION DEFAULT 0"),
    ("min_price", "DOUBLE PRECISION DEFAULT 0"),
    ("max_price", "DOUBLE PRECISION DEFAULT 0"),
    ("currency", "TEXT DEFAULT 'Ar'"),
    ("verified", "BOOLEAN DEFAULT FALSE"),
    ("team_size", "INTEGER DEFAULT 1"),
    ("response_time_hours", "INTEGER DEFAULT 24"),
]


class PGVectorStore:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @classmethod
    async def create(cls, dsn: str) -> "PGVectorStore":
        # Ensure vector extension exists before pool registers the type codec
        boot = await asyncpg.connect(dsn=dsn)
        try:
            await boot.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        finally:
            await boot.close()
        pool = await asyncpg.create_pool(dsn=dsn, min_size=2, max_size=10, init=register_vector)
        store = cls(pool)
        await store._init_schema()
        return store

    async def _init_schema(self) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

            # Base prestataires table — uses CREATE IF NOT EXISTS so existing schema kept
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS prestataires (
                    id          TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    specialty   TEXT NOT NULL,
                    description TEXT NOT NULL,
                    services    JSONB DEFAULT '[]',
                    city        TEXT DEFAULT '',
                    country     TEXT DEFAULT '',
                    hourly_rate FLOAT DEFAULT 0,
                    phone       TEXT DEFAULT '',
                    email       TEXT DEFAULT '',
                    rating      FLOAT DEFAULT 0,
                    image_base64 TEXT DEFAULT '',
                    created_at  TEXT,
                    embedding   VECTOR({EMBEDDING_DIM})
                );
            """)

            # Apply enrichment columns idempotently
            for col_name, col_type in _PRESTATAIRES_EXTRA_COLUMNS:
                await conn.execute(
                    f"ALTER TABLE prestataires ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                )

            # Users + sessions for the Connect flow
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username      TEXT UNIQUE NOT NULL,
                    email         TEXT,
                    password_hash TEXT NOT NULL,
                    full_name     TEXT DEFAULT '',
                    created_at    TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    token      TEXT PRIMARY KEY,
                    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
                    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
                    prestataire_id  TEXT REFERENCES prestataires(id) ON DELETE CASCADE,
                    message         TEXT DEFAULT '',
                    created_at      TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(user_id, prestataire_id)
                );
            """)
        logger.info("PGVectorStore schema ready (with enrichment + auth tables).")

    @property
    async def count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM prestataires")

    async def add(self, prestataire: Prestataire, embedding: np.ndarray) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO prestataires
                   (id,name,specialty,description,services,city,country,hourly_rate,phone,email,rating,image_base64,created_at,embedding,
                    organization,specialties,bio,cover_photo_base64,services_detail,latitude,longitude,address,
                    category,languages,years_experience,emergency_available,accepts_payment,certifications,
                    service_radius_km,min_price,max_price,currency,verified,team_size,response_time_hours)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,
                           $23,$24,$25,$26,$27,$28,$29,$30,$31,$32,$33,$34,$35)
                   ON CONFLICT (id) DO NOTHING""",
                prestataire.id, prestataire.name, prestataire.specialty, prestataire.description,
                json.dumps(prestataire.services), prestataire.city, prestataire.country,
                prestataire.hourly_rate, prestataire.phone, prestataire.email,
                prestataire.rating, prestataire.image_base64, prestataire.created_at,
                embedding.tolist(),
                prestataire.organization,
                json.dumps(prestataire.specialties),
                prestataire.bio,
                prestataire.cover_photo_base64,
                json.dumps([sd.model_dump() for sd in prestataire.services_detail]),
                prestataire.latitude, prestataire.longitude,
                prestataire.address,
                prestataire.category,
                json.dumps(prestataire.languages),
                prestataire.years_experience,
                prestataire.emergency_available,
                json.dumps(prestataire.accepts_payment),
                json.dumps(prestataire.certifications),
                prestataire.service_radius_km,
                prestataire.min_price,
                prestataire.max_price,
                prestataire.currency,
                prestataire.verified,
                prestataire.team_size,
                prestataire.response_time_hours,
            )

    async def update(self, prestataire_id: str, prestataire: Prestataire, embedding: np.ndarray) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """UPDATE prestataires SET name=$2,specialty=$3,description=$4,services=$5,
                   city=$6,country=$7,hourly_rate=$8,phone=$9,email=$10,rating=$11,
                   image_base64=$12,embedding=$13,
                   organization=$14,specialties=$15,bio=$16,cover_photo_base64=$17,services_detail=$18,
                   latitude=$19,longitude=$20,address=$21
                   WHERE id=$1""",
                prestataire_id, prestataire.name, prestataire.specialty, prestataire.description,
                json.dumps(prestataire.services), prestataire.city, prestataire.country,
                prestataire.hourly_rate, prestataire.phone, prestataire.email,
                prestataire.rating, prestataire.image_base64, embedding.tolist(),
                prestataire.organization,
                json.dumps(prestataire.specialties),
                prestataire.bio,
                prestataire.cover_photo_base64,
                json.dumps([sd.model_dump() for sd in prestataire.services_detail]),
                prestataire.latitude, prestataire.longitude,
                prestataire.address,
            )
            return result != "UPDATE 0"

    _LIST_COLS = (
        "id,name,specialty,description,services,city,country,hourly_rate,phone,email,rating,"
        "image_base64,created_at,organization,specialties,bio,cover_photo_base64,"
        "services_detail,latitude,longitude,address,"
        "category,languages,years_experience,emergency_available,accepts_payment,"
        "certifications,service_radius_km,min_price,max_price,currency,verified,"
        "team_size,response_time_hours"
    )

    async def list_all(self) -> list[Prestataire]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT {self._LIST_COLS} FROM prestataires ORDER BY created_at DESC"
            )
        return [_row_to_prestataire(r) for r in rows]

    async def get(self, prestataire_id: str) -> Prestataire | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT {self._LIST_COLS} FROM prestataires WHERE id=$1",
                prestataire_id,
            )
        return _row_to_prestataire(row) if row else None

    async def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""SELECT {self._LIST_COLS},
                           1 - (embedding <=> $1::vector) AS score
                    FROM prestataires
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2""",
                query_embedding.tolist(), top_k,
            )
        return [
            SearchResult(prestataire=_row_to_prestataire(r), similarity_score=max(0.0, min(1.0, float(r["score"]))))
            for r in rows
        ]

    async def filtered_search(
        self,
        query_embedding: np.ndarray,
        criteria: CriteriaFilter,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Hybrid retrieval: structured WHERE pre-filter, then cosine ANN within survivors."""
        where, params = _build_where_clause(criteria)
        params.append(query_embedding.tolist())  # $N+1 for embedding
        params.append(top_k)                       # $N+2 for limit
        embed_param = f"${len(params) - 1}"
        limit_param = f"${len(params)}"
        sql = f"""
            SELECT {self._LIST_COLS},
                   1 - (embedding <=> {embed_param}::vector) AS score
            FROM prestataires
            {where}
            ORDER BY embedding <=> {embed_param}::vector
            LIMIT {limit_param}
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        return [
            SearchResult(prestataire=_row_to_prestataire(r), similarity_score=max(0.0, min(1.0, float(r["score"]))))
            for r in rows
        ]


def _build_where_clause(c: CriteriaFilter) -> tuple[str, list]:
    """Translate the structured filter into a safe parameterised WHERE clause."""
    clauses: list[str] = []
    params: list = []

    def add(clause: str, *values) -> None:
        # Replace {} placeholders with positional $N markers
        n = len(params)
        rendered = clause
        for v in values:
            n += 1
            rendered = rendered.replace("{}", f"${n}", 1)
            params.append(v)
        clauses.append(rendered)

    if c.category:
        add("LOWER(category) = LOWER({})", c.category)
    if c.city:
        add("city ILIKE {}", f"%{c.city}%")
    if c.currency:
        add("(currency = {} OR currency = '')", c.currency)
    if c.max_price is not None and c.max_price > 0:
        # match if any pricing field fits the budget
        add(
            "(min_price <= {0} OR (hourly_rate > 0 AND hourly_rate <= {0}))",
            c.max_price,
        )
    if c.min_price is not None and c.min_price > 0:
        add("(max_price = 0 OR max_price >= {})", c.min_price)
    if c.min_rating is not None:
        add("rating >= {}", c.min_rating)
    if c.min_years_experience is not None:
        add("years_experience >= {}", c.min_years_experience)
    if c.emergency is True:
        add("emergency_available = TRUE")
    if c.verified is True:
        add("verified = TRUE")
    for opt in c.options:
        # check that opt appears in any service_detail.options jsonb array
        add(
            "EXISTS (SELECT 1 FROM jsonb_array_elements(services_detail) sd "
            "WHERE sd->'options' ? {})",
            opt,
        )
    for pay in c.accepts_payment:
        add("accepts_payment ? {}", pay)
    for lang in c.languages:
        add("languages ? {}", lang)

    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where_sql, params


def _maybe_json_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return []
    return value


def _safe_get(row, key, default=None):
    try:
        return row[key]
    except (KeyError, IndexError):
        return default


def _row_to_prestataire(row) -> Prestataire:
    services = _maybe_json_list(_safe_get(row, "services", []))
    specialties = _maybe_json_list(_safe_get(row, "specialties", []))
    services_detail_raw = _maybe_json_list(_safe_get(row, "services_detail", []))
    services_detail = [ServiceDetail(**sd) if isinstance(sd, dict) else sd for sd in services_detail_raw]
    return Prestataire(
        id=row["id"], name=row["name"], specialty=row["specialty"],
        description=row["description"], services=services,
        city=row["city"] or "", country=row["country"] or "",
        hourly_rate=row["hourly_rate"] or 0, phone=row["phone"] or "",
        email=row["email"] or "", rating=row["rating"] or 0,
        image_base64=row["image_base64"] or "", created_at=row["created_at"] or "",
        organization=_safe_get(row, "organization", "") or "",
        specialties=specialties,
        bio=_safe_get(row, "bio", "") or "",
        cover_photo_base64=_safe_get(row, "cover_photo_base64", "") or "",
        services_detail=services_detail,
        latitude=_safe_get(row, "latitude"),
        longitude=_safe_get(row, "longitude"),
        address=_safe_get(row, "address", "") or "",
        # Lot 4 criteria
        category=_safe_get(row, "category", "") or "",
        languages=_maybe_json_list(_safe_get(row, "languages", [])),
        years_experience=_safe_get(row, "years_experience", 0) or 0,
        emergency_available=bool(_safe_get(row, "emergency_available", False)),
        accepts_payment=_maybe_json_list(_safe_get(row, "accepts_payment", [])),
        certifications=_maybe_json_list(_safe_get(row, "certifications", [])),
        service_radius_km=float(_safe_get(row, "service_radius_km", 0) or 0),
        min_price=float(_safe_get(row, "min_price", 0) or 0),
        max_price=float(_safe_get(row, "max_price", 0) or 0),
        currency=_safe_get(row, "currency", "Ar") or "Ar",
        verified=bool(_safe_get(row, "verified", False)),
        team_size=int(_safe_get(row, "team_size", 1) or 1),
        response_time_hours=int(_safe_get(row, "response_time_hours", 24) or 24),
    )
