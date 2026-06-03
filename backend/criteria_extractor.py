"""Extract a structured CriteriaFilter from a free-text query via a small LLM call.
The extractor uses the same Groq client as the chat service so no extra deps."""
from __future__ import annotations

import json
import logging
import re

from groq import Groq

from config import Settings
from models import CriteriaFilter

logger = logging.getLogger(__name__)


_VALID_OPTIONS = {"home_visit", "video_call", "in_office"}
_VALID_PAYMENTS = {"cash", "mvola", "orange_money", "airtel_money", "card", "bank_transfer"}
_VALID_LANGUAGES = {"mg", "fr", "en"}


# Known city/quartier aliases for Madagascar — normalise free-form queries
_CITY_ALIASES = {
    "tana": "Antananarivo",
    "tnr": "Antananarivo",
    "antananarivo": "Antananarivo",
    "ankorondrano": "Antananarivo",
    "analakely": "Antananarivo",
    "ivandry": "Antananarivo",
    "antaninarenina": "Antananarivo",
    "antanimena": "Antananarivo",
    "67ha": "Antananarivo",
    "itaosy": "Antananarivo",
    "tanjombato": "Antananarivo",
    "ambatobe": "Antananarivo",
    "antsahabe": "Antananarivo",
    "tamatave": "Toamasina",
    "toamasina": "Toamasina",
    "tulear": "Toliara",
    "toliara": "Toliara",
    "majunga": "Mahajanga",
    "mahajanga": "Mahajanga",
    "diego": "Antsiranana",
    "antsiranana": "Antsiranana",
    "fianar": "Fianarantsoa",
    "fianarantsoa": "Fianarantsoa",
}


_SYSTEM = (
    "You are a request parser for a service-provider search engine. "
    "Read the user query in French, Malagasy or English and produce a STRICT JSON object "
    "matching this TypeScript schema (no extra fields):\n"
    "{\n"
    '  "category": string|null,            // single canonical category lowercase: plumbing|electrical|beauty|construction|mechanic|tech|tourism|agriculture|healthcare|food|tailoring|photo|tutoring|cleaning|moving|gardening|event|null\n'
    '  "city": string|null,                // normalised city name if mentioned\n'
    '  "max_price": number|null,           // numeric max budget if user mentions one\n'
    '  "min_price": number|null,\n'
    '  "currency": "Ar"|"€"|"$"|null,      // detected currency (Ar default if MGA)\n'
    '  "options": ("home_visit"|"video_call"|"in_office")[],\n'
    '  "accepts_payment": ("cash"|"mvola"|"orange_money"|"airtel_money"|"card"|"bank_transfer")[],\n'
    '  "languages": ("mg"|"fr"|"en")[],\n'
    '  "min_rating": number|null,          // 0..5\n'
    '  "min_years_experience": number|null,\n'
    '  "emergency": boolean|null,\n'
    '  "verified": boolean|null,\n'
    '  "intent_text": string                // rephrase user need in natural language for semantic search\n'
    "}\n"
    "Output ONLY the JSON, nothing else."
)


def _parse_json(content: str) -> dict:
    # Some models wrap in ```json blocks — strip them
    s = content.strip()
    if s.startswith("```"):
        s = s.strip("`")
        first_newline = s.find("\n")
        if first_newline > -1:
            s = s[first_newline + 1:]
        if s.endswith("```"):
            s = s[:-3]
    # Find first { and last } to be permissive
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(s[start:end + 1])
    except json.JSONDecodeError as e:
        logger.warning("Criteria JSON parse failed: %s | content=%s", e, s[start:end + 1][:200])
        return {}


def _normalise_city(raw: str | None) -> str | None:
    if not raw:
        return None
    raw_lc = raw.lower().strip()
    return _CITY_ALIASES.get(raw_lc, raw)


class CriteriaExtractor:
    def __init__(self, settings: Settings):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def extract(self, query: str, image_description: str | None = None) -> CriteriaFilter:
        if not query and not image_description:
            return CriteriaFilter()
        merged = " ".join(filter(None, [query, image_description]))
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": merged},
                ],
                temperature=0.1,
                max_tokens=400,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
            data = _parse_json(content)
        except Exception as e:  # noqa: BLE001
            logger.warning("Criteria extraction failed: %s — falling back to vector-only", e)
            data = {}

        # Whitelist + normalise
        options = [o for o in data.get("options") or [] if o in _VALID_OPTIONS]
        payments = [p for p in data.get("accepts_payment") or [] if p in _VALID_PAYMENTS]
        languages = [l for l in data.get("languages") or [] if l in _VALID_LANGUAGES]

        category = (data.get("category") or "").strip().lower() or None

        return CriteriaFilter(
            category=category,
            city=_normalise_city(data.get("city")),
            max_price=_maybe_float(data.get("max_price")),
            min_price=_maybe_float(data.get("min_price")),
            currency=data.get("currency") if data.get("currency") in {"Ar", "€", "$"} else None,
            options=options,
            accepts_payment=payments,
            languages=languages,
            min_rating=_maybe_float(data.get("min_rating")),
            min_years_experience=_maybe_int(data.get("min_years_experience")),
            emergency=_maybe_bool(data.get("emergency")),
            verified=_maybe_bool(data.get("verified")),
            intent_text=(data.get("intent_text") or merged).strip(),
        )


def _maybe_float(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _maybe_int(v) -> int | None:
    f = _maybe_float(v)
    return int(f) if f is not None else None


def _maybe_bool(v) -> bool | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.lower().strip()
        if s in {"true", "yes", "oui", "eny"}:
            return True
        if s in {"false", "no", "non", "tsia"}:
            return False
    return None


# Sanitize content sent BACK to the user (strip stars / markdown)
def sanitize_for_user(text: str) -> str:
    if not text:
        return text
    s = text
    # Bold/italic markdown
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    # Headings
    s = re.sub(r"^\s*#{1,6}\s+", "", s, flags=re.MULTILINE)
    # Bullet stars and rating star spam
    s = re.sub(r"[★⭐]+", "", s)
    # Leading bullet markers `*` / `-` → "•"
    s = re.sub(r"^\s*[\*\-•]\s+", "• ", s, flags=re.MULTILINE)
    # Collapse 3+ newlines
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()
