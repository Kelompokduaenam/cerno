from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db, utcnow
from app.main import app
from app.auth.models import LoginSession, User
from app.analysis.models import Analysis
from app.security import hash_token
from app.community.domain import redact
from app.community.models import AuditLog, Report
from app.community.service import cleanup_expired, community_signal, decide_report, submit_report


def test_report_moderation_deduplication_and_signal():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        report, token, duplicate = submit_report(
            db,
            "url",
            "https://bank-validasi.example/login?otp=123456",
            "Meminta OTP 123456 ke email korban@example.com",
            None,
        )
        assert not duplicate
        assert report.target_redacted == "bank-validasi.example"
        assert "korban@example.com" not in report.reason_redacted
        assert "123456" not in report.reason_redacted
        assert token not in report.reporter_hash
        assert community_signal(db, "https://bank-validasi.example/other")["accepted_count"] == 0

        again, _, duplicate = submit_report(
            db,
            "url",
            "https://bank-validasi.example/new-path",
            "Meminta OTP 123456 ke email korban@example.com",
            token,
        )
        assert duplicate
        assert again.id == report.id

        decided = decide_report(db, report.id, "admin-id", "accepted", "Bukti pola meminta OTP")
        assert decided.status == "accepted"
        assert db.query(AuditLog).count() == 1
        assert community_signal(db, "https://bank-validasi.example/path")["accepted_count"] == 1
        assert community_signal(db, "https://other.example/")["accepted_count"] == 0

        decided.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
        assert community_signal(db, "https://bank-validasi.example/")["accepted_count"] == 0
        assert cleanup_expired(db)["reports_removed"] == 1


def test_redaction_does_not_store_url_paths_or_contact_details():
    value = redact("https://example.org/private?token=secret hubungi a@b.com atau 081234567890 OTP:123456")
    assert "/private" not in value
    assert "a@b.com" not in value
    assert "081234567890" not in value
    assert "123456" not in value


def test_community_routes_authorization_and_feedback():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def db_override():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = db_override
    try:
        with Session(engine) as db:
            admin = User(email="admin@example.test", password_hash="x", role="admin")
            user = User(email="user@example.test", password_hash="x", role="user")
            analysis = Analysis(
                token_hash=hash_token("analysis-access"), input_type="text", redacted_input="pesan teredaksi",
                risk_score=30, risk_level="medium", result={}, version="baseline-rules-v1",
                expires_at=utcnow() + timedelta(hours=1),
            )
            db.add_all([admin, user, analysis])
            db.flush()
            db.add_all([
                LoginSession(user_id=admin.id, token_hash=hash_token("admin-session"), csrf_hash=hash_token("admin-csrf"), expires_at=utcnow() + timedelta(hours=1)),
                LoginSession(user_id=user.id, token_hash=hash_token("user-session"), csrf_hash=hash_token("user-csrf"), expires_at=utcnow() + timedelta(hours=1)),
            ])
            db.commit()
            analysis_id = analysis.id

        client = TestClient(app)
        receipt = client.post("/api/v1/reports", json={
            "target_type": "url", "target": "https://bank-validasi.example/private?token=secret",
            "reason": "Meminta OTP 123456 dari korban@example.com", "consent": True,
        })
        assert receipt.status_code == 202
        report_id = receipt.json()["id"]
        assert client.get("/api/v1/admin/reports").status_code == 401
        client.cookies.set("cerno_session", "user-session")
        assert client.get("/api/v1/admin/reports").status_code == 403
        client.cookies.set("cerno_session", "admin-session")
        listing = client.get("/api/v1/admin/reports")
        assert listing.status_code == 200
        assert listing.json()["total"] == 1
        assert "secret" not in str(listing.json())
        assert client.post(f"/api/v1/admin/reports/{report_id}/decisions", json={"decision": "accepted", "reason": "Pola meminta OTP"}).status_code == 403
        decided = client.post(
            f"/api/v1/admin/reports/{report_id}/decisions",
            headers={"X-CSRF-Token": "admin-csrf"},
            json={"decision": "accepted", "reason": "Pola meminta OTP"},
        )
        assert decided.status_code == 200
        client.cookies.clear()
        feedback = client.post(
            f"/api/v1/analyses/{analysis_id}/feedback",
            headers={"X-Access-Token": "analysis-access"},
            json={"helpful": True, "verdict": "correct", "comment": "Hubungi saya di korban@example.com"},
        )
        assert feedback.status_code == 201
        client.cookies.set("cerno_session", "admin-session")
        reviewed = client.get("/api/v1/admin/feedback")
        assert reviewed.status_code == 200
        assert reviewed.json()["total"] == 1
        assert "korban@example.com" not in str(reviewed.json())
    finally:
        app.dependency_overrides.clear()
