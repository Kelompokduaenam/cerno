"""Pure report normalization and privacy rules."""

import hashlib
import ipaddress
import re
from urllib.parse import urlsplit

from app.errors import problem


_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE = re.compile(r"(?<!\w)(?:\+?62|0)[\s.-]?(?:\d[\s.-]?){8,13}(?!\w)")
_SECRETS = re.compile(r"\b(?:otp|pin|cvv|password|kata\s+sandi)\s*[:=]?\s*\d{4,8}\b", re.IGNORECASE)
_LINK = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)


def normalize_url(value: str) -> str:
    candidate = value.strip()
    parsed = urlsplit(candidate)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise problem(422, "URL tidak valid", "Gunakan URL HTTP atau HTTPS yang lengkap.")
    try:
        host = parsed.hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise problem(422, "URL tidak valid", "Nama domain tidak valid.") from exc
    if len(host) > 253 or "." not in host:
        raise problem(422, "URL tidak valid", "Nama domain publik diperlukan.")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise problem(422, "URL tidak valid", "Alamat IP tidak dapat dilaporkan sebagai domain.")
    if parsed.username or parsed.password:
        raise problem(422, "URL tidak valid", "URL dengan kredensial tidak diterima.")
    return host


def redact(value: str, limit: int = 1000) -> str:
    value = _LINK.sub(lambda match: f"[URL:{normalize_url(match.group(0))}]" if _safe_url(match.group(0)) else "[URL]", value)
    value = _EMAIL.sub("[EMAIL]", value)
    value = _PHONE.sub("[PHONE]", value)
    value = _SECRETS.sub("[SENSITIVE_CREDENTIAL]", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def _safe_url(value: str) -> bool:
    try:
        normalize_url(value)
        return True
    except Exception:
        return False


def target_identity(target_type: str, target: str) -> tuple[str, str]:
    if target_type == "url":
        display = normalize_url(target)
        identity = f"url:{display}"
    elif target_type == "text":
        display = redact(target, 500)
        if len(display) < 10:
            raise problem(422, "Teks terlalu singkat", "Masukkan paling sedikit 10 karakter.")
        identity = f"text:{display.casefold()}"
    else:
        raise problem(422, "Jenis target tidak valid", "Jenis target harus url atau text.")
    return hashlib.sha256(identity.encode("utf-8")).hexdigest(), display
