from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.domain import normalize_email
from app.auth.models import LoginSession, User
from app.config import settings
from app.db import utcnow
from app.errors import problem
from app.security import hash_password, hash_token, new_token, verify_password


def create_user(db: Session, email: str, password: str) -> User:
    user = User(email=normalize_email(email), password_hash=hash_password(password), role="user")
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise problem(409, "Email sudah terdaftar", "Gunakan alamat email lain.")
    return user


def start_session(db: Session, email: str, password: str) -> tuple[User, str, str, object]:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if not user or not verify_password(password, user.password_hash):
        raise problem(401, "Kredensial tidak valid", "Email atau kata sandi tidak sesuai.")
    token, csrf = new_token(), new_token()
    expires_at = utcnow() + timedelta(days=settings.session_days)
    db.add(LoginSession(user_id=user.id, token_hash=hash_token(token), csrf_hash=hash_token(csrf), expires_at=expires_at))
    db.commit()
    return user, token, csrf, expires_at
