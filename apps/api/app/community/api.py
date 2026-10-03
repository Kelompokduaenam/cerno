"""HTTP contracts for anonymous community input and Admin review."""

from typing import Literal

from fastapi import APIRouter, Depends, Header, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import active_session, optional_user, require_admin, require_csrf
from app.auth.models import User
from app.db import get_db, utcnow
from app.errors import problem
from app.rate_limit import limit
from app.security import verify_token
from app.community.models import Feedback, ModerationDecision, Report
from app.community.service import add_feedback, decide_report, is_expired, submit_report


router = APIRouter(prefix="/api/v1", tags=["community"])


class ReportInput(BaseModel):
    target_type: Literal["url", "text"]
    target: str = Field(min_length=10, max_length=5000)
    reason: str = Field(min_length=10, max_length=2000)
    consent: bool


class ReportReceipt(BaseModel):
    id: str
    status: str
    reporter_token: str
    duplicate: bool
    message: str


@router.post("/reports", status_code=202, response_model=ReportReceipt)
def post_report(
    payload: ReportInput,
    request: Request,
    x_reporter_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    limit(request, "reports", 5, 3600)
    if not payload.consent:
        raise problem(422, "Persetujuan diperlukan", "Setujui penggunaan versi teredaksi untuk moderasi.")
    if x_reporter_token and len(x_reporter_token) > 128:
        raise problem(422, "Token tidak valid", "Token pelapor terlalu panjang.")
    report, token, duplicate = submit_report(db, payload.target_type, payload.target, payload.reason, x_reporter_token)
    return ReportReceipt(
        id=report.id,
        status="received",
        reporter_token=token,
        duplicate=duplicate,
        message="Laporan diterima untuk moderasi; belum menjadi sinyal komunitas.",
    )


class FeedbackInput(BaseModel):
    helpful: bool
    verdict: Literal["correct", "too_high", "too_low", "unsure"]
    comment: str | None = Field(default=None, max_length=2000)


@router.post("/analyses/{analysis_id}/feedback", status_code=201)
def post_feedback(
    analysis_id: str,
    payload: FeedbackInput,
    request: Request,
    x_access_token: str | None = Header(default=None),
    x_csrf_token: str | None = Header(default=None),
    user: User | None = Depends(optional_user),
    db: Session = Depends(get_db),
):
    limit(request, "feedback", 10, 3600)
    if user is not None:
        session = active_session(db, request.cookies.get("cerno_session"))
        if session is None or not x_csrf_token or not verify_token(x_csrf_token, session.csrf_hash):
            raise problem(403, "CSRF tidak valid", "Muat ulang sesi dan kirim token CSRF yang sah.")
    from app.analysis.service import authorize_analysis

    analysis = authorize_analysis(db, analysis_id, x_access_token, user)
    feedback = add_feedback(db, analysis, user, payload.helpful, payload.verdict, payload.comment)
    return {"id": feedback.id, "status": "received", "expires_at": feedback.expires_at}


def report_summary(report: Report) -> dict:
    return {
        "id": report.id,
        "target_type": report.target_type,
        "target": report.target_redacted,
        "reason": report.reason_redacted,
        "status": report.status,
        "created_at": report.created_at,
        "decided_at": report.decided_at,
        "expires_at": report.expires_at,
    }


@router.get("/admin/summary")
def admin_summary(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    del admin
    now = utcnow()
    report_counts = dict(db.execute(
        select(Report.status, func.count(Report.id))
        .where(Report.expires_at > now)
        .group_by(Report.status)
    ).all())
    feedback_count = db.scalar(select(func.count(Feedback.id)).where(Feedback.expires_at > now)) or 0
    from app.analysis.service import analysis_metrics

    return {
        "generated_at": now,
        "analyses": analysis_metrics(db),
        "reports": {
            "pending": report_counts.get("pending", 0),
            "accepted": report_counts.get("accepted", 0),
            "rejected": report_counts.get("rejected", 0),
            "duplicate": report_counts.get("duplicate", 0),
        },
        "feedback_count": feedback_count,
        "service_status": {"api": "operational", "ocr_worker": "not_measured", "url_reputation": "not_configured"},
    }


@router.get("/admin/reports")
def list_reports(
    status: Literal["pending", "accepted", "rejected", "duplicate"] | None = None,
    target_type: Literal["url", "text"] | None = None,
    limit_items: int = Query(default=20, ge=1, le=100, alias="limit"),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del admin
    criteria = [Report.expires_at > utcnow()]
    if status:
        criteria.append(Report.status == status)
    if target_type:
        criteria.append(Report.target_type == target_type)
    total = db.scalar(select(func.count(Report.id)).where(*criteria)) or 0
    items = db.scalars(
        select(Report).where(*criteria).order_by(Report.created_at.desc()).offset(offset).limit(limit_items)
    ).all()
    return {"items": [report_summary(item) for item in items], "total": total, "limit": limit_items, "offset": offset}


@router.get("/admin/reports/{report_id}")
def get_report(report_id: str, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    del admin
    report = db.get(Report, report_id)
    if report is None or is_expired(report.expires_at):
        raise problem(404, "Laporan tidak ditemukan", "Laporan telah dihapus atau kedaluwarsa.")
    decisions = db.scalars(
        select(ModerationDecision)
        .where(ModerationDecision.report_id == report.id)
        .order_by(ModerationDecision.created_at)
    ).all()
    return {
        **report_summary(report),
        "decisions": [
            {"decision": item.decision, "reason": item.reason_redacted, "created_at": item.created_at, "admin_id": item.admin_id}
            for item in decisions
        ],
    }


class DecisionInput(BaseModel):
    decision: Literal["accepted", "rejected", "duplicate"]
    reason: str = Field(min_length=5, max_length=2000)


@router.post("/admin/reports/{report_id}/decisions")
def post_decision(
    report_id: str,
    payload: DecisionInput,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf),
):
    report = decide_report(db, report_id, admin.id, payload.decision, payload.reason)
    return report_summary(report)


@router.get("/admin/feedback")
def list_feedback(
    verdict: Literal["correct", "too_high", "too_low", "unsure"] | None = None,
    limit_items: int = Query(default=20, ge=1, le=100, alias="limit"),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    del admin
    criteria = [Feedback.expires_at > utcnow()]
    if verdict:
        criteria.append(Feedback.verdict == verdict)
    total = db.scalar(select(func.count(Feedback.id)).where(*criteria)) or 0
    items = db.scalars(select(Feedback).where(*criteria).order_by(Feedback.created_at.desc()).offset(offset).limit(limit_items)).all()
    return {
        "items": [
            {
                "id": item.id,
                "analysis_id": item.analysis_id,
                "score": item.score,
                "risk_level": item.risk_level,
                "version": item.version,
                "helpful": item.helpful,
                "verdict": item.verdict,
                "comment": item.comment_redacted,
                "created_at": item.created_at,
                "expires_at": item.expires_at,
            }
            for item in items
        ],
        "total": total,
        "limit": limit_items,
        "offset": offset,
    }


@router.get("/admin/models")
def list_models(admin: User = Depends(require_admin)):
    del admin
    return {"items": [{
        "name": "CERNO baseline aturan",
        "version": "baseline-rules-v1",
        "kind": "rules_baseline",
        "evaluation_status": "not_evaluated",
        "evaluation_metrics": None,
    }]}
