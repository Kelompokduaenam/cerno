from fastapi import Cookie, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db, utcnow
from app.errors import problem
from app.security import hash_token, verify_token
from app.auth.models import LoginSession, User


def active_session(db: Session, token: str | None) -> LoginSession | None:
    if not token:
        return None
    return db.scalar(select(LoginSession).where(LoginSession.token_hash == hash_token(token), LoginSession.expires_at > utcnow()))


def optional_user(cerno_session: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> User | None:
    session = active_session(db, cerno_session)
    return db.get(User, session.user_id) if session else None


def current_user(user: User | None = Depends(optional_user)) -> User:
    if user is None:
        raise problem(401, "Perlu masuk", "Masuk untuk mengakses data akun.")
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise problem(403, "Akses ditolak", "Fungsi ini hanya untuk Admin.")
    return user


def require_csrf(
    cerno_session: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> None:
    session = active_session(db, cerno_session)
    if session is None or not x_csrf_token or not verify_token(x_csrf_token, session.csrf_hash):
        raise problem(403, "CSRF tidak valid", "Muat ulang sesi dan kirim token CSRF yang sah.")
