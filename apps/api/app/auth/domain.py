import re

from app.errors import problem


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise problem(422, "Email tidak valid", "Masukkan alamat email yang valid.")
    return email
