import json
import logging

import asyncpg
import numpy as np
from pgvector.asyncpg import register_vector

from models import Prestataire, SearchResult, ServiceDetail

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 3072

# All optional enrichment columns added in Lot 3+ — applied as ALTER TABLE … IF NOT EXISTS
_PRESTATAIRES_EXTRA_COLUMNS = [
    ("organization", "TEXT DEFAULT ''"),
    ("specialties", "JSONB DEFAULT '[]'"),
    ("bio", "TEXT DEFAULT ''"),
    ("cover_photo_base64", "TEXT DEFAULT ''"),
    ("services_detail", "JSONB DEFAULT '[]'"),
    ("latitude", "DOUBLE PRECISION"),
    ("longitude", "DOUBLE PRECISION"),
    ("address", "TEXT DEFAULT ''"),
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
                    organization,specialties,bio,cover_photo_base64,services_detail,latitude,longitude,address)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22)
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
        "services_detail,latitude,longitude,address"
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


def _maybe_json_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return []
    return value


def _row_to_prestataire(row) -> Prestataire:
    services = _maybe_json_list(row["services"])
    specialties = _maybe_json_list(row["specialties"]) if "specialties" in row else []
    services_detail_raw = _maybe_json_list(row["services_detail"]) if "services_detail" in row else []
    services_detail = [ServiceDetail(**sd) if isinstance(sd, dict) else sd for sd in services_detail_raw]
    return Prestataire(
        id=row["id"], name=row["name"], specialty=row["specialty"],
        description=row["description"], services=services,
        city=row["city"] or "", country=row["country"] or "",
        hourly_rate=row["hourly_rate"] or 0, phone=row["phone"] or "",
        email=row["email"] or "", rating=row["rating"] or 0,
        image_base64=row["image_base64"] or "", created_at=row["created_at"] or "",
        organization=(row["organization"] if "organization" in row else "") or "",
        specialties=specialties,
        bio=(row["bio"] if "bio" in row else "") or "",
        cover_photo_base64=(row["cover_photo_base64"] if "cover_photo_base64" in row else "") or "",
        services_detail=services_detail,
        latitude=row["latitude"] if "latitude" in row else None,
        longitude=row["longitude"] if "longitude" in row else None,
        address=(row["address"] if "address" in row else "") or "",
    )
