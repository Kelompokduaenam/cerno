from datetime import timedelta
from io import BytesIO

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db, utcnow
from app.ocr.api import router
from app.ocr.application import validate_ocr_review
from app.ocr.cleanup import cleanup_expired
from app.ocr.infrastructure.models import OcrJob
from app.ocr.worker import _process_job
from app.security import hash_token


def _png() -> bytes:
    output = BytesIO()
    Image.new("RGB", (128, 128), "white").save(output, format="PNG")
    return output.getvalue()


def _client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def db_override():
        with Session(engine) as db:
            yield db

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = db_override
    monkeypatch.setattr("app.ocr.api.upload_screenshot", lambda key, body: None)
    monkeypatch.setattr("app.ocr.api.enqueue_job", lambda job_id: None)
    monkeypatch.setattr("app.ocr.api.delete_screenshot", lambda key: None)
    return TestClient(app), engine


def test_upload_poll_and_review_authorization(monkeypatch):
    client, engine = _client(monkeypatch)
    created = client.post("/api/v1/ocr-jobs", files={"screenshot": ("chat.png", _png(), "image/png")})
    assert created.status_code == 202
    body = created.json()
    assert created.headers["cache-control"] == "no-store"
    assert client.get(body["status_url"]).status_code == 404
    assert client.get(body["status_url"], headers={"X-Access-Token": "wrong"}).status_code == 404
    polled = client.get(body["status_url"], headers={"X-Access-Token": body["access_token"]})
    assert polled.status_code == 200
    assert polled.json()["status"] == "queued"

    with Session(engine) as db:
        job = db.get(OcrJob, body["id"])
        assert job.token_hash != body["access_token"]
        job.status = "completed"
        job.extracted_text = "Transfer sekarang"
        db.commit()
        reviewed_job, reviewed = validate_ocr_review(db, body["id"], body["access_token"], "  Ini koreksi pengguna  ")
        assert reviewed_job.id == body["id"]
        assert reviewed == "Ini koreksi pengguna"
        job.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert client.get(body["status_url"], headers={"X-Access-Token": body["access_token"]}).status_code == 404


def test_invalid_image_and_queue_failure(monkeypatch):
    client, engine = _client(monkeypatch)
    bad = client.post("/api/v1/ocr-jobs", files={"screenshot": ("chat.png", b"not an image", "image/png")})
    assert bad.status_code == 422
    monkeypatch.setattr("app.ocr.api.enqueue_job", lambda job_id: (_ for _ in ()).throw(OSError("queue unavailable")))
    unavailable = client.post("/api/v1/ocr-jobs", files={"screenshot": ("chat.png", _png(), "image/png")})
    assert unavailable.status_code == 503
    with Session(engine) as db:
        assert db.query(OcrJob).count() == 1
        assert db.query(OcrJob).one().status == "failed"


def test_worker_extracts_text_and_removes_blob(monkeypatch):
    _, engine = _client(monkeypatch)
    deleted = []
    monkeypatch.setattr("app.ocr.worker.download_screenshot", lambda key: _png())
    monkeypatch.setattr("app.ocr.worker.extract_text", lambda image: "Halo, transfer ke rekening ini")
    monkeypatch.setattr("app.ocr.worker.delete_screenshot", deleted.append)
    with Session(engine) as db:
        job = OcrJob(id="7f14f45f-2af7-42ca-8f11-f9a110de8e11", token_hash=hash_token("secret"), status="queued", object_key="ocr/test.png")
        db.add(job)
        db.commit()
        assert _process_job(db, job.id)
        assert job.status == "completed"
        assert job.extracted_text == "Halo, transfer ke rekening ini"
        assert deleted == ["ocr/test.png"]


def test_cleanup_removes_expired_metadata_and_blob(monkeypatch):
    _, engine = _client(monkeypatch)
    deleted = []
    monkeypatch.setattr("app.ocr.cleanup.delete_screenshot", deleted.append)
    with Session(engine) as db:
        job = OcrJob(id="00ad5fe2-e857-4ef9-8c43-84a95bd333a3", token_hash=hash_token("secret"), object_key="ocr/expired.png", expires_at=utcnow() - timedelta(seconds=1))
        db.add(job)
        db.commit()
        assert cleanup_expired(db) == 1
        assert db.get(OcrJob, job.id) is None
    assert deleted == ["ocr/expired.png"]
