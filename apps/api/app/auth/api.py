from fastapi import APIRouter, Cookie, Depends, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import active_session, current_user, require_csrf
from app.auth.models import User
from app.auth.application import create_user, start_session
from app.config import settings
from app.db import get_db
from app.errors import problem
from app.rate_limit import limit

router = APIRouter(prefix="/api/v1/auth", tags=["Akun"])


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=256)


def public_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "role": user.role}


@router.post("/register", status_code=201)
def register(payload: Credentials, request: Request, db: Session = Depends(get_db)) -> dict:
    limit(request, "register", 5, 3600)
    if settings.production:
        raise problem(503, "Pendaftaran ditutup", "Verifikasi email belum tersedia untuk pendaftaran publik.")
    user = create_user(db, payload.email, payload.password)
    return public_user(user)


@router.post("/login")
def login(payload: Credentials, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    limit(request, "login", 10, 900)
    user, token, csrf, expires_at = start_session(db, payload.email, payload.password)
    response.set_cookie("cerno_session", token, max_age=settings.session_days * 86400, secure=settings.production, httponly=True, samesite="lax", path="/")
    return {"user": public_user(user), "csrf_token": csrf, "expires_at": expires_at}


@router.post("/logout", dependencies=[Depends(require_csrf)])
def logout(response: Response, cerno_session: str | None = Cookie(default=None), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    session = active_session(db, cerno_session)
    if session and session.user_id == user.id:
        db.delete(session)
        db.commit()
    response.delete_cookie("cerno_session", path="/")
    return {"ok": True}


@router.get("/me")
def me(user: User = Depends(current_user)) -> dict:
    return public_user(user)
