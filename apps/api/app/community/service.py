"""Application workflows for reports, feedback and moderation."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select, text, update
from sqlalchemy.orm import Session

from app.db import utcnow
from app.errors import problem
from app.security import hash_token, new_token
from app.community.domain import redact, target_identity
from app.community.models import AuditLog, Feedback, ModerationDecision, Report


def is_expired(value: datetime) -> bool:
    return value.replace(tzinfo=timezone.utc) <= utcnow() if value.tzinfo is None else value <= utcnow()


def submit_report(db: Session, target_type: str, target: str, reason: str, reporter_token: str | None) -> tuple[Report, str, bool]:
    now = utcnow()
    target_key, display = target_identity(target_type, target)
    redacted_reason = redact(reason, 1000)
    if len(redacted_reason) < 10:
        raise problem(422, "Alasan terlalu singkat", "Jelaskan alasan laporan dalam sedikitnya 10 karakter.")
    token = reporter_token or new_token()
    reporter_hash = hash_token(token)
    # A repeated token for the same target has no extra influence within seven days.
    # Matching content without a token is also deduplicated to limit anonymous replay.
    if db.bind and db.bind.dialect.name == "postgresql":
        lock_value = int.from_bytes(bytes.fromhex(target_key[:16]), "big", signed=True)
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_value})
    recent = db.scalars(
        select(Report).where(
            Report.target_key == target_key,
            Report.created_at > now - timedelta(days=7),
        )
    ).all()
    duplicate = next(
        (item for item in recent if item.reporter_hash == reporter_hash or (
            item.target_redacted == display and item.reason_redacted == redacted_reason
        )),
        None,
    )
    if duplicate is not None:
        return duplicate, token, True
    report = Report(
        target_type=target_type,
        target_key=target_key,
        target_redacted=display,
        reason_redacted=redacted_reason,
        reporter_hash=reporter_hash,
        status="pending",
        expires_at=now + timedelta(days=30),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report, token, False


def community_signal(db: Session, target: str, target_type: str = "url") -> dict:
    """Read-only boundary called by Analysis; never returns report content."""
    try:
        target_key, _ = target_identity(target_type, target)
    except Exception:
        return {"status": "not_checked", "accepted_count": 0, "score_contribution": 0}
    count = db.scalar(
        select(func.count(Report.id)).where(
            Report.target_key == target_key,
            Report.status == "accepted",
            Report.expires_at > utcnow(),
        )
    ) or 0
    return {"status": "checked", "accepted_count": count, "score_contribution": min(15, count * 3)}


def add_feedback(db: Session, analysis, user, helpful: bool, verdict: str, comment: str | None) -> Feedback:
    item = Feedback(
        analysis_id=analysis.id,
        owner_id=user.id if user else None,
        score=analysis.risk_score,
        risk_level=analysis.risk_level,
        version=analysis.version,
        helpful=helpful,
        verdict=verdict,
        comment_redacted=redact(comment, 1000) if comment else None,
        expires_at=utcnow() + timedelta(days=30),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def decide_report(db: Session, report_id: str, admin_id: str, decision: str, reason: str) -> Report:
    report = db.get(Report, report_id, with_for_update=True)
    if report is None or is_expired(report.expires_at):
        raise problem(404, "Laporan tidak ditemukan", "Laporan telah dihapus atau kedaluwarsa.")
    if report.status != "pending":
        raise problem(409, "Sudah diputuskan", "Laporan ini sudah memiliki keputusan moderasi.")
    if decision not in {"accepted", "rejected", "duplicate"}:
        raise problem(422, "Keputusan tidak valid", "Gunakan accepted, rejected, atau duplicate.")
    redacted_reason = redact(reason, 1000)
    if len(redacted_reason) < 5:
        raise problem(422, "Alasan diperlukan", "Alasan keputusan minimal lima karakter.")
    now = utcnow()
    report.status = decision
    report.decided_at = now
    report.expires_at = now + timedelta(days=90 if decision == "accepted" else 30)
    db.add(ModerationDecision(
        report_id=report.id,
        admin_id=admin_id,
        decision=decision,
        reason_redacted=redacted_reason,
    ))
    db.add(AuditLog(
        admin_id=admin_id,
        action=f"report.{decision}",
        target_id=report.id,
        reason_redacted=redacted_reason,
        expires_at=now + timedelta(days=90),
    ))
    db.commit()
    db.refresh(report)
    return report


def delete_feedback_for_analysis(db: Session, analysis_id: str, owner_id: str | None = None) -> None:
    criteria = [Feedback.analysis_id == analysis_id]
    if owner_id is not None:
        criteria.append(Feedback.owner_id == owner_id)
    db.execute(delete(Feedback).where(*criteria))


def cleanup_expired(db: Session) -> dict[str, int]:
    """Called by the shared cleanup command; API queries enforce expiry independently."""
    now = utcnow()
    reporter = db.execute(update(Report).where(Report.created_at <= now - timedelta(days=7), Report.reporter_hash.is_not(None)).values(reporter_hash=None)).rowcount
    reports = db.execute(delete(Report).where(Report.expires_at <= now)).rowcount
    feedback = db.execute(delete(Feedback).where(Feedback.expires_at <= now)).rowcount
    audit = db.execute(delete(AuditLog).where(AuditLog.expires_at <= now)).rowcount
    db.commit()
    return {"reporter_hashes_removed": reporter, "reports_removed": reports, "feedback_removed": feedback, "audit_removed": audit}
