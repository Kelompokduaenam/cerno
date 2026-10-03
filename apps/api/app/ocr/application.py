"""OCR use cases and the small boundary used by the analysis module."""

from sqlalchemy.orm import Session

from app.db import utcnow
from app.errors import problem
from app.security import verify_token

from .domain import is_accessible, normalize_reviewed_text
from .infrastructure.models import OcrJob


def get_authorized_job(db: Session, job_id: str, access_token: str | None) -> OcrJob:
    job = db.get(OcrJob, job_id)
    if not job or not is_accessible(job.expires_at, utcnow()):
        raise problem(404, "Pekerjaan OCR tidak ditemukan", "Pekerjaan tidak ada atau telah kedaluwarsa.")
    if not access_token or not verify_token(access_token, job.token_hash):
        raise problem(404, "Pekerjaan OCR tidak ditemukan", "Pekerjaan tidak ada atau token tidak sah.")
    return job


def validate_ocr_review(db: Session, job_id: str, access_token: str, reviewed_text: str) -> tuple[OcrJob, str]:
    """Authorize an OCR source and the user's corrected text before analysis."""
    job = get_authorized_job(db, job_id, access_token)
    if job.status != "completed":
        raise problem(409, "OCR belum selesai", "Tunggu hasil OCR atau kirim teks tanpa pekerjaan OCR.")
    if job.analysis_id is not None:
        raise problem(409, "Pekerjaan OCR sudah dipakai", "Buat pekerjaan OCR baru untuk analisis berikutnya.")
    try:
        text = normalize_reviewed_text(reviewed_text)
    except ValueError as exc:
        raise problem(422, "Teks review tidak valid", str(exc)) from exc
    return job, text


def mark_analysis_used(db: Session, job: OcrJob, analysis_id: str) -> None:
    """Caller commits this change in the same transaction as its analysis result."""
    if job.analysis_id is not None:
        raise problem(409, "Pekerjaan OCR sudah dipakai", "Pekerjaan ini telah dikaitkan dengan analisis.")
    job.analysis_id = analysis_id
    db.add(job)
