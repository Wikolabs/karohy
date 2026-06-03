"""Lightweight session-based auth for the Connect flow.
Uses PostgreSQL for storage; sha256 with random salt for password hashing
(good enough for the MVP — swap for argon2 when production-bound)."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
from datetime import datetime, timezone

import asyncpg

from models import UserPublic

logger = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "karohy_session"
SESSION_LIFETIME_DAYS = 30
_PEPPER = os.getenv("AUTH_PEPPER", "karohy-default-pepper-change-in-prod")


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{_PEPPER}:{password}".encode("utf-8")).hexdigest()


def _new_session_token() -> str:
    return secrets.token_urlsafe(32)


class AuthService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def signup(self, username: str, password: str, full_name: str = "", email: str = "") -> UserPublic:
        username = username.strip().lower()
        if not username or not password:
            raise ValueError("Username and password are required")
        salt = secrets.token_hex(8)
        pwd_hash = _hash_password(password, salt)
        stored = f"{salt}${pwd_hash}"
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    """INSERT INTO users (username, email, password_hash, full_name)
                       VALUES ($1, NULLIF($2, ''), $3, $4)
                       RETURNING id::text, username, full_name, COALESCE(email, '') AS email""",
                    username, email.strip().lower(), stored, full_name.strip(),
                )
            except asyncpg.UniqueViolationError:
                raise ValueError("Username already taken")
        return UserPublic(id=row["id"], username=row["username"], full_name=row["full_name"], email=row["email"])

    async def login(self, username: str, password: str) -> tuple[UserPublic, str]:
        username = username.strip().lower()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT id::text AS id, username, full_name, COALESCE(email, '') AS email, password_hash
                   FROM users WHERE username = $1""",
                username,
            )
        if not row:
            raise ValueError("Invalid credentials")
        salt, expected = row["password_hash"].split("$", 1)
        if _hash_password(password, salt) != expected:
            raise ValueError("Invalid credentials")
        token = await self._issue_session(row["id"])
        return (
            UserPublic(id=row["id"], username=row["username"], full_name=row["full_name"], email=row["email"]),
            token,
        )

    async def _issue_session(self, user_id: str) -> str:
        token = _new_session_token()
        async with self.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO sessions (token, user_id, expires_at)
                   VALUES ($1, $2::uuid, NOW() + ($3 || ' days')::interval)""",
                token, user_id, str(SESSION_LIFETIME_DAYS),
            )
        return token

    async def me(self, token: str | None) -> UserPublic | None:
        if not token:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT u.id::text AS id, u.username, u.full_name, COALESCE(u.email, '') AS email
                   FROM sessions s JOIN users u ON u.id = s.user_id
                   WHERE s.token = $1 AND s.expires_at > NOW()""",
                token,
            )
        if not row:
            return None
        return UserPublic(id=row["id"], username=row["username"], full_name=row["full_name"], email=row["email"])

    async def logout(self, token: str | None) -> None:
        if not token:
            return
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM sessions WHERE token = $1", token)

    async def register_connection(self, user_id: str, prestataire_id: str, message: str = "") -> bool:
        """Returns True if a new connection was created, False if it already existed."""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """INSERT INTO connections (user_id, prestataire_id, message)
                   VALUES ($1::uuid, $2, $3)
                   ON CONFLICT (user_id, prestataire_id) DO NOTHING
                   RETURNING id""",
                user_id, prestataire_id, message.strip(),
            )
        return result is not None
