"""Run with `python -m app.ocr.worker` from apps/api."""

import logging
import subprocess
import tempfile
import time
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal, utcnow

from .domain import is_accessible
from .infrastructure.models import OcrJob
from .infrastructure.storage import delete_screenshot, download_screenshot, get_queue_client


logger = logging.getLogger(__name__)


def extract_text(image_bytes: bytes) -> str:
    """Tesseract receives a temporary local image; no input is logged."""
    with tempfile.TemporaryDirectory(prefix="cerno-ocr-") as directory:
        image_path = Path(directory) / "image.png"
        image_path.write_bytes(image_bytes)
        result = subprocess.run(
            [settings.tesseract_cmd, str(image_path), "stdout", "-l", settings.tesseract_lang],
            capture_output=True,
            timeout=90,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError("OCR_PROCESS_FAILED")
    return result.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n").strip()[:20_000]


def _process_job(db: Session, job_id: str) -> bool:
    """Return True when queue message can be acknowledged."""
    job = db.get(OcrJob, job_id)
    if job is None:
        return True
    if not is_accessible(job.expires_at, utcnow()):
        delete_screenshot(job.object_key)
        db.delete(job)
        db.commit()
        return True
    if job.status in {"completed", "failed"}:
        return True
    job.status = "processing"
    db.commit()
    try:
        image = download_screenshot(job.object_key)
        extracted = extract_text(image)
    except (FileNotFoundError, subprocess.TimeoutExpired, RuntimeError):
        job.status = "failed"
        job.error_code = "OCR_PROCESS_FAILED"
        db.commit()
        delete_screenshot(job.object_key)
        return True
    except Exception:
        db.rollback()
        # An Azure outage is retried by Queue Storage after visibility timeout.
        logger.warning("OCR storage operation failed for job %s", job_id)
        return False
    job.extracted_text = extracted
    job.status = "completed" if extracted else "failed"
    job.error_code = None if extracted else "OCR_EMPTY_TEXT"
    db.commit()
    delete_screenshot(job.object_key)
    return True


def run_worker_once() -> bool:
    queue = get_queue_client()
    message = next(iter(queue.receive_messages(messages_per_page=1, visibility_timeout=120)), None)
    if message is None:
        return False
    with SessionLocal() as db:
        acknowledge = _process_job(db, message.content)
    if acknowledge:
        queue.delete_message(message.id, message.pop_receipt)
    return True


def run_worker_forever(poll_interval: float = 2.0) -> None:
    while True:
        try:
            processed = run_worker_once()
        except KeyboardInterrupt:
            return
        except Exception:
            logger.exception("OCR worker operation failed")
            processed = False
        if not processed:
            time.sleep(poll_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_worker_forever()
