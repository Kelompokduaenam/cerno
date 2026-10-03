from datetime import timedelta

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.models import HistoryItem
from app.analysis.service import authorize_analysis
from app.auth.dependencies import current_user, require_csrf
from app.auth.models import User
from app.db import as_utc, get_db, utcnow
from app.errors import problem

router = APIRouter(prefix="/api/v1/history", tags=["Riwayat"])


class SaveHistoryInput(BaseModel):
    analysis_id: str
    access_token: str


def visible_item(db: Session, item_id: str, user: User) -> HistoryItem:
    item = db.get(HistoryItem, item_id)
    if item is None or item.user_id != user.id or as_utc(item.expires_at) <= utcnow():
        raise problem(404, "Riwayat tidak ditemukan", "Catatan tidak ada atau telah kedaluwarsa.")
    return item


@router.post("", status_code=201, dependencies=[Depends(require_csrf)])
def save_history(payload: SaveHistoryInput, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    analysis = authorize_analysis(db, payload.analysis_id, payload.access_token, user)
    previous = db.scalar(select(HistoryItem).where(HistoryItem.user_id == user.id, HistoryItem.analysis_id == analysis.id, HistoryItem.expires_at > utcnow()))
    if previous:
        raise problem(409, "Sudah disimpan", "Hasil ini sudah ada di riwayat akun.")
    item = HistoryItem(user_id=user.id, analysis_id=analysis.id, snapshot={"input_type": analysis.input_type, "redacted_input": analysis.redacted_input, "result": analysis.result, "analyzed_at": analysis.created_at.isoformat()}, expires_at=utcnow() + timedelta(days=30))
    db.add(item)
    db.commit()
    return {"id": item.id, "created_at": item.created_at, "expires_at": item.expires_at, "snapshot": item.snapshot}


@router.get("")
def list_history(db: Session = Depends(get_db), user: User = Depends(current_user), limit: int = 20, offset: int = 0) -> dict:
    if not 1 <= limit <= 100 or offset < 0:
        raise problem(422, "Pagination tidak valid", "Gunakan limit 1–100 dan offset non-negatif.")
    items = db.scalars(select(HistoryItem).where(HistoryItem.user_id == user.id, HistoryItem.expires_at > utcnow()).order_by(HistoryItem.created_at.desc()).limit(limit).offset(offset)).all()
    return {"items": [{"id": x.id, "created_at": x.created_at, "expires_at": x.expires_at, "input_type": x.snapshot["input_type"], "risk_score": x.snapshot["result"]["risk_score"], "risk_level": x.snapshot["result"]["risk_level"]} for x in items], "limit": limit, "offset": offset}


@router.get("/{item_id}")
def get_history(item_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    item = visible_item(db, item_id, user)
    return {"id": item.id, "created_at": item.created_at, "expires_at": item.expires_at, "snapshot": item.snapshot}


@router.delete("/{item_id}", status_code=204, dependencies=[Depends(require_csrf)])
def delete_history(item_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)) -> None:
    item = visible_item(db, item_id, user)
    if item.analysis_id:
        from app.community.service import delete_feedback_for_analysis
        delete_feedback_for_analysis(db, item.analysis_id, owner_id=user.id)
    db.delete(item)
    db.commit()
