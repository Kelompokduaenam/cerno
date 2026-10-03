"""Remove expired OCR metadata and any leftover screenshots."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal, utcnow

from .infrastructure.models import OcrJob
from .infrastructure.storage import delete_screenshot


def cleanup_expired(db: Session) -> int:
    jobs = db.scalars(select(OcrJob).where(OcrJob.expires_at <= utcnow())).all()
    deleted = 0
    for job in jobs:
        # Delete Blob first so a storage outage cannot silently breach retention.
        delete_screenshot(job.object_key)
        db.delete(job)
        deleted += 1
    db.commit()
    return deleted


if __name__ == "__main__":
    with SessionLocal() as session:
        print(f"Deleted {cleanup_expired(session)} expired OCR jobs")
