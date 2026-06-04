from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


ServiceOption = Literal["home_visit", "video_call", "in_office"]


class ServiceDetail(BaseModel):
    name: str = Field(max_length=120)
    price: float = Field(ge=0, default=0)
    currency: str = Field(max_length=8, default="Ar")
    duration_min: int = Field(ge=0, default=0)
    options: list[ServiceOption] = []


class Prestataire(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(max_length=120)
    specialty: str = Field(max_length=120)
    description: str = Field(max_length=1000)
    services: list[str] = []
    city: str = Field(max_length=120, default="")
    country: str = Field(max_length=120, default="")
    hourly_rate: float = Field(ge=0, default=0)
    phone: str = Field(max_length=40, default="")
    email: str = Field(max_length=200, default="")
    rating: float = Field(ge=0, le=5, default=0)
    image_base64: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Enriched fields (Lot 3+)
    organization: str = Field(max_length=200, default="")
    specialties: list[str] = []
    bio: str = Field(max_length=2400, default="")
    cover_photo_base64: str = ""
    services_detail: list[ServiceDetail] = []
    latitude: float | None = None
    longitude: float | None = None
    address: str = Field(max_length=300, default="")

    # Filterable criteria (Lot 4) · driven by SQL filter before vector search
    category: str = Field(max_length=60, default="")
    languages: list[str] = []
    years_experience: int = Field(ge=0, default=0)
    emergency_available: bool = False
    accepts_payment: list[str] = []
    certifications: list[str] = []
    service_radius_km: float = Field(ge=0, default=0)
    min_price: float = Field(ge=0, default=0)
    max_price: float = Field(ge=0, default=0)
    currency: str = Field(max_length=8, default="Ar")
    verified: bool = False
    team_size: int = Field(ge=1, default=1)
    response_time_hours: int = Field(ge=0, default=24)


class SearchResult(BaseModel):
    prestataire: Prestataire
    similarity_score: float = Field(ge=0.0, le=1.0)


class SearchRequest(BaseModel):
    text: str | None = None
    image_base64: str | None = None


# Structured filter extracted from the user query by the criteria LLM. All optional.
class CriteriaFilter(BaseModel):
    category: str | None = None
    city: str | None = None
    max_price: float | None = None
    min_price: float | None = None
    currency: str | None = None
    options: list[str] = []        # home_visit / video_call / in_office
    accepts_payment: list[str] = []
    languages: list[str] = []
    min_rating: float | None = None
    min_years_experience: int | None = None
    emergency: bool | None = None
    verified: bool | None = None
    intent_text: str = ""          # rewritten natural-language for embedding


# ── Auth ────────────────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    password: str = Field(min_length=6, max_length=200)
    full_name: str = Field(max_length=200, default="")
    email: str = Field(max_length=200, default="")


class LoginRequest(BaseModel):
    username: str = Field(max_length=60)
    password: str = Field(max_length=200)


class UserPublic(BaseModel):
    id: str
    username: str
    full_name: str = ""
    email: str = ""


class ConnectRequest(BaseModel):
    prestataire_id: str
    message: str = Field(max_length=600, default="")
