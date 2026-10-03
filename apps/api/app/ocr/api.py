"""Public screenshot upload and protected OCR polling endpoints."""

from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Header, Request, Response, UploadFile
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.errors import problem
from app.security import hash_token, new_token

from .application import get_authorized_job
from .infrastructure.models import OcrJob
from .infrastructure.storage import delete_screenshot, enqueue_job, upload_screenshot


router = APIRouter(prefix="/api/v1/ocr-jobs", tags=["OCR"])


class OcrAccepted(BaseModel):
    id: str
    status: str = "queued"
    access_token: str = Field(description="Simpan sementara di sisi klien dan kirim sebagai X-Access-Token saat polling.")
    status_url: str


class OcrStatus(BaseModel):
    id: str
    status: str
    extracted_text: str | None = None
    error_code: str | None = None
    expires_at: str


def _safe_png(payload: bytes) -> bytes:
    """Decode and re-encode to strip metadata and reject disguised/bomb files."""
    try:
        with Image.open(BytesIO(payload)) as image:
            if image.format not in {"PNG", "JPEG"}:
                raise ValueError("Format screenshot harus PNG atau JPEG.")
            width, height = image.size
            if not (64 <= width <= 10_000 and 64 <= height <= 10_000) or width * height > 30_000_000:
                raise ValueError("Dimensi screenshot tidak didukung.")
            image.load()
            clean = image.convert("RGB")
            output = BytesIO()
            clean.save(output, format="PNG", optimize=True)
            result = output.getvalue()
            if len(result) > settings.max_upload_bytes:
                raise ValueError("Screenshot setelah diproses melebihi batas ukuran.")
            return result
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("File bukan screenshot PNG atau JPEG yang valid.") from exc


@router.post("", response_model=OcrAccepted, status_code=202)
async def create_ocr_job(request: Request, response: Response, screenshot: UploadFile = File(...), db: Session = Depends(get_db)) -> OcrAccepted:
    response.headers["Cache-Control"] = "no-store"
    if screenshot.content_type not in {"image/png", "image/jpeg"}:
        raise problem(415, "Tipe file tidak didukung", "Gunakan screenshot PNG atau JPEG.")
    payload = await screenshot.read(settings.max_upload_bytes + 1)
    if len(payload) > settings.max_upload_bytes:
        raise problem(413, "Screenshot terlalu besar", f"Ukuran maksimum {settings.max_upload_bytes} byte.")
    try:
        clean_png = _safe_png(payload)
    except ValueError as exc:
        raise problem(422, "Screenshot tidak valid", str(exc)) from exc

    token = new_token()
    job_id = str(uuid4())
    object_key = f"ocr/{job_id}.png"
    job = OcrJob(id=job_id, token_hash=hash_token(token), status="queued", object_key=object_key)
    try:
        db.add(job)
        db.commit()
        upload_screenshot(object_key, clean_png)
        enqueue_job(job_id)
    except Exception as exc:
        db.rollback()
        # Keep metadata until cleanup so a failed Blob deletion remains discoverable.
        try:
            persisted = db.get(OcrJob, job_id)
            if persisted:
                persisted.status = "failed"
                persisted.error_code = "QUEUE_OR_STORAGE_UNAVAILABLE"
                db.commit()
        except Exception:
            db.rollback()
        try:
            delete_screenshot(object_key)
        except Exception:
            pass
        raise problem(503, "Layanan OCR belum tersedia", "Screenshot belum dapat diterima. Coba lagi nanti.") from exc
    response.headers["Location"] = str(request.url_for("get_ocr_job", job_id=job_id))
    return OcrAccepted(id=job_id, access_token=token, status_url=f"/api/v1/ocr-jobs/{job_id}")


@router.get("/{job_id}", response_model=OcrStatus)
def get_ocr_job(job_id: str, response: Response, x_access_token: str | None = Header(default=None, alias="X-Access-Token"), db: Session = Depends(get_db)) -> OcrStatus:
    response.headers["Cache-Control"] = "no-store"
    job = get_authorized_job(db, job_id, x_access_token)
    return OcrStatus(id=job.id, status=job.status, extracted_text=job.extracted_text if job.status == "completed" else None, error_code=job.error_code, expires_at=job.expires_at.isoformat())
