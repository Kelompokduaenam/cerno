"""Run with DATABASE_URL pointing to a disposable PostgreSQL database named *_test."""

import os
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import User
from app.analysis.models import Analysis, HistoryItem
from app.db import SessionLocal, utcnow
from app.main import app
from app.ocr.infrastructure.models import OcrJob
from app.security import hash_password, hash_token


@pytest.mark.skipif(not os.getenv("CERNO_TEST_DATABASE_URL"), reason="PostgreSQL test database not configured")
def test_product_routes_against_postgres():
    assert "_test" in os.environ["CERNO_TEST_DATABASE_URL"]
    suffix = uuid4().hex[:10]
    client = TestClient(app)
    user_email = f"user-{suffix}@example.test"
    admin_email = f"admin-{suffix}@example.test"
    with SessionLocal() as db:
        db.add(User(email=admin_email, password_hash=hash_password("AdminPassword123!"), role="admin"))
        db.commit()

    assert client.get("/healthz").status_code == 200
    assert client.post("/api/v1/auth/register", json={"email": user_email, "password": "UserPassword123!"}).status_code == 201
    user_login = client.post("/api/v1/auth/login", json={"email": user_email, "password": "UserPassword123!"})
    assert user_login.status_code == 200
    csrf = user_login.json()["csrf_token"]
    assert client.get("/api/v1/auth/me").json()["role"] == "user"
    assert client.get("/api/v1/admin/summary").status_code == 403

    target = f"https://validasi-{suffix}.example/login"
    text_result = client.post("/api/v1/analyses", json={"input_type": "text", "text": f"Bank: segera berikan OTP dan transfer lewat {target}"})
    assert text_result.status_code == 201, text_result.text
    result = text_result.json()
    assert result["risk_score"] >= 70 and result["version"] == "baseline-rules-v1"
    assert result["checks"]["url_reputation"] == "not_checked"
    assert client.get(f"/api/v1/analyses/{result['id']}").status_code == 403
    assert client.get(f"/api/v1/analyses/{result['id']}", headers={"X-Access-Token": result["access_token"]}).status_code == 200
    assert client.post("/api/v1/history", json={"analysis_id": result["id"], "access_token": result["access_token"]}).status_code == 403
    saved = client.post("/api/v1/history", json={"analysis_id": result["id"], "access_token": result["access_token"]}, headers={"X-CSRF-Token": csrf})
    assert saved.status_code == 201, saved.text
    history_id = saved.json()["id"]
    assert "[URL_REDACTED]" in saved.json()["snapshot"]["redacted_input"]
    assert len(client.get("/api/v1/history").json()["items"]) >= 1
    assert client.get(f"/api/v1/history/{history_id}").status_code == 200

    url_result = client.post("/api/v1/analyses", json={"input_type": "url", "url": target})
    assert url_result.status_code == 201
    assert url_result.json()["url_results"][0]["host"] == f"validasi-{suffix}.example"
    job_token = f"ocr-{suffix}"
    with SessionLocal() as db:
        job = OcrJob(token_hash=hash_token(job_token), status="completed", object_key=f"ocr/{suffix}.png", extracted_text="teks OCR belum tepat")
        db.add(job)
        db.commit()
        job_id = job.id
    screenshot_result = client.post("/api/v1/analyses", json={"input_type": "screenshot", "text": "Bank meminta OTP segera", "ocr_job_id": job_id, "ocr_access_token": job_token})
    assert screenshot_result.status_code == 201, screenshot_result.text
    assert screenshot_result.json()["risk_score"] >= 65
    assert client.post("/api/v1/analyses", json={"input_type": "screenshot", "text": "Koreksi kedua", "ocr_job_id": job_id, "ocr_access_token": job_token}).status_code == 409
    feedback = client.post(f"/api/v1/analyses/{result['id']}/feedback", json={"helpful": True, "verdict": "correct", "comment": "cukup jelas"}, headers={"X-Access-Token": result["access_token"], "X-CSRF-Token": csrf})
    assert feedback.status_code == 201, feedback.text
    report = client.post("/api/v1/reports", json={"target_type": "url", "target": target, "reason": "Meminta OTP dan mengaku bank", "consent": True})
    assert report.status_code == 202, report.text
    receipt = report.json()
    duplicate = client.post("/api/v1/reports", json={"target_type": "url", "target": target, "reason": "Meminta OTP dan mengaku bank", "consent": True}, headers={"X-Reporter-Token": receipt["reporter_token"]})
    assert duplicate.json()["duplicate"] is True
    assert client.get("/api/v1/admin/reports").status_code == 403
    assert client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 200

    admin_login = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "AdminPassword123!"})
    admin_csrf = admin_login.json()["csrf_token"]
    summary = client.get("/api/v1/admin/summary")
    assert summary.status_code == 200 and summary.json()["analyses"]["analysis_count"] >= 2
    assert client.get("/api/v1/admin/reports").status_code == 200
    assert client.get(f"/api/v1/admin/reports/{receipt['id']}").status_code == 200
    assert client.post(f"/api/v1/admin/reports/{receipt['id']}/decisions", json={"decision": "accepted", "reason": "Indikator sudah diverifikasi"}).status_code == 403
    decision = client.post(f"/api/v1/admin/reports/{receipt['id']}/decisions", json={"decision": "accepted", "reason": "Indikator sudah diverifikasi"}, headers={"X-CSRF-Token": admin_csrf})
    assert decision.status_code == 200, decision.text
    assert client.get("/api/v1/admin/feedback").status_code == 200
    assert client.get("/api/v1/admin/models").json()["items"][0]["version"] == "baseline-rules-v1"
    followup = client.post("/api/v1/analyses", json={"input_type": "url", "url": target})
    assert followup.json()["url_results"][0]["community"]["accepted_count"] >= 1
    assert client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": admin_csrf}).status_code == 200

    second_email = f"second-{suffix}@example.test"
    client.post("/api/v1/auth/register", json={"email": second_email, "password": "SecondPassword123!"})
    client.post("/api/v1/auth/login", json={"email": second_email, "password": "SecondPassword123!"})
    assert client.get(f"/api/v1/history/{history_id}").status_code == 404
    assert client.delete(f"/api/v1/history/{history_id}").status_code == 403

    with SessionLocal() as db:
        analysis = db.get(Analysis, result["id"])
        history = db.get(HistoryItem, history_id)
        analysis.expires_at = utcnow() - timedelta(seconds=1)
        history.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert client.get(f"/api/v1/analyses/{result['id']}", headers={"X-Access-Token": result["access_token"]}).status_code == 404
    assert client.get(f"/api/v1/history/{history_id}").status_code == 404
