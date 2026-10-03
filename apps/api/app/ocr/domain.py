"""Rules that do not depend on FastAPI or Azure."""

from datetime import datetime, timezone


MAX_REVIEW_CHARS = 20_000


def is_accessible(expires_at: datetime, now: datetime) -> bool:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > now


def normalize_reviewed_text(value: str) -> str:
    text = value.strip()
    if not text or len(text) > MAX_REVIEW_CHARS:
        raise ValueError("Teks hasil review harus berisi 1 sampai 20000 karakter.")
    return text
