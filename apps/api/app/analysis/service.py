from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analysis.models import Analysis
from app.auth.models import User
from app.db import as_utc, utcnow
from app.errors import problem
from app.security import verify_token
from app.url.domain import URL_PATTERN, normalize_url
from app.url.application import inspect_url
from app.analysis.domain import redact, text_evidence, risk_level, recommendations

VERSION = "baseline-rules-v1"


def assess(text: str, explicit_url: str | None, db: Session) -> dict:
    urls = [explicit_url] if explicit_url else URL_PATTERN.findall(text)
    score, evidence = text_evidence(text)
    url_results = []
    for raw in urls[:5]:
        url_check = inspect_url(raw)
        host = url_check["host"]
        flags = url_check["lexical_flags"]
        if flags:
            score += min(10 * len(flags), 20)
            evidence.append({"code": "struktur_url", "title": "Struktur URL perlu diperiksa", "description": f"Domain {host} memiliki ciri yang perlu diverifikasi.", "weight": min(10 * len(flags), 20)})
        from app.community.service import community_signal
        community = community_signal(db, raw, "url")
        if community.get("accepted_count", 0):
            score += min(community["accepted_count"] * 3, 15)
        url_results.append({**url_check, "community": community})
    score = min(score, 100)
    level = risk_level(score)
    return {"risk_score": score, "risk_level": level, "evidence": evidence, "checks": {"text_rules": "completed", "url_reputation": "not_checked" if urls else "not_applicable"}, "url_results": url_results, "limitations": ["Skor berasal dari aturan awal, belum dari model AI terlatih."] + (["Reputasi URL belum diperiksa oleh provider eksternal."] if urls else []), "recommendations": recommendations(level, bool(urls)), "version": VERSION}


def authorize_analysis(db: Session, analysis_id: str, token: str | None, user: User | None) -> Analysis:
    analysis = db.get(Analysis, analysis_id)
    if analysis is None or as_utc(analysis.expires_at) <= utcnow():
        raise problem(404, "Hasil tidak ditemukan", "Hasil tidak ada atau masa aksesnya sudah habis.")
    if user and analysis.owner_id == user.id:
        return analysis
    if not token or not verify_token(token, analysis.token_hash):
        raise problem(403, "Akses ditolak", "Token akses hasil tidak sah.")
    return analysis


def analysis_metrics(db: Session) -> dict:
    rows = db.execute(select(Analysis.risk_level, func.count(Analysis.id)).group_by(Analysis.risk_level)).all()
    distribution = {"low": 0, "medium": 0, "high": 0}
    for level, count in rows:
        distribution[level] = count
    return {"analysis_count": sum(distribution.values()), "risk_distribution": distribution}
