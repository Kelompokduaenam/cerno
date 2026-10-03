"""Run periodically with `python -m app.maintenance`."""

from sqlalchemy import delete, select

from app.analysis.models import Analysis, HistoryItem
from app.auth.models import LoginSession
from app.community.service import cleanup_expired as cleanup_community, delete_feedback_for_analysis
from app.db import SessionLocal, utcnow
from app.ocr.cleanup import cleanup_expired as cleanup_ocr


def run_cleanup() -> dict[str, int]:
    with SessionLocal() as db:
        now = utcnow()
        for item in db.scalars(select(HistoryItem).where(HistoryItem.expires_at <= now)).all():
            if item.analysis_id:
                delete_feedback_for_analysis(db, item.analysis_id, owner_id=item.user_id)
        sessions = db.execute(delete(LoginSession).where(LoginSession.expires_at <= now)).rowcount
        histories = db.execute(delete(HistoryItem).where(HistoryItem.expires_at <= now)).rowcount
        analyses = db.execute(delete(Analysis).where(Analysis.expires_at <= now)).rowcount
        db.commit()
        community = cleanup_community(db)
        ocr = cleanup_ocr(db)
    return {"sessions_removed": sessions, "history_removed": histories, "analyses_removed": analyses, "ocr_jobs_removed": ocr, **community}


if __name__ == "__main__":
    print(run_cleanup())
