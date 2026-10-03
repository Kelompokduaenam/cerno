from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.analysis.models import Analysis
from app.analysis.service import assess, authorize_analysis, normalize_url, redact
from app.auth.dependencies import optional_user
from app.auth.models import User
from app.db import get_db, utcnow
from app.errors import problem
from app.rate_limit import limit
from app.security import hash_token, new_token

router = APIRouter(prefix="/api/v1/analyses", tags=["Analisis"])


class AnalysisInput(BaseModel):
    input_type: Literal["text", "url", "screenshot"]
    text: str | None = Field(default=None, max_length=10000)
    url: str | None = Field(default=None, max_length=2048)
    ocr_job_id: str | None = None
    ocr_access_token: str | None = None

    @model_validator(mode="after")
    def validate_shape(self):
        if self.input_type == "text" and not (self.text and self.text.strip()):
            raise ValueError("text wajib diisi")
        if self.input_type == "url" and not (self.url and self.url.strip()):
            raise ValueError("url wajib diisi")
        if self.input_type == "screenshot" and not (self.text and self.text.strip() and self.ocr_job_id and self.ocr_access_token):
            raise ValueError("text hasil review, ocr_job_id, dan ocr_access_token wajib diisi")
        return self


class EvidenceOutput(BaseModel):
    code: str
    title: str
    description: str
    weight: int


class UrlOutput(BaseModel):
    host: str
    lexical_flags: list[str]
    reputation: dict
    community: dict


class AnalysisRead(BaseModel):
    id: str
    created_at: datetime
    expires_at: datetime
    input_type: Literal["text", "url", "screenshot"]
    redacted_input: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal["low", "medium", "high"]
    evidence: list[EvidenceOutput]
    checks: dict[str, str]
    url_results: list[UrlOutput]
    limitations: list[str]
    recommendations: list[str]
    version: str


class AnalysisCreated(AnalysisRead):
    access_token: str = Field(description="Kirim pada X-Access-Token; jangan letakkan di path atau query API.")


@router.post("", status_code=201, response_model=AnalysisCreated)
def create_analysis(payload: AnalysisInput, request: Request, db: Session = Depends(get_db)) -> dict:
    limit(request, "analyses", 30, 3600)
    job = None
    text = payload.text or ""
    if payload.input_type == "url":
        normalize_url(payload.url or "")
    if payload.input_type == "screenshot":
        from app.ocr.application import validate_ocr_review
        job, text = validate_ocr_review(db, payload.ocr_job_id, payload.ocr_access_token, text)
    result = assess(text, payload.url if payload.input_type == "url" else None, db)
    token = new_token()
    analysis = Analysis(
        owner_id=None,
        token_hash=hash_token(token),
        input_type=payload.input_type,
        redacted_input=redact(payload.url if payload.input_type == "url" else text),
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        result=result,
        version=result["version"],
        expires_at=utcnow() + timedelta(hours=24),
    )
    db.add(analysis)
    db.flush()
    if job is not None:
        from app.ocr.application import mark_analysis_used
        mark_analysis_used(db, job, analysis.id)
    db.commit()
    return {"id": analysis.id, "access_token": token, "created_at": analysis.created_at, "expires_at": analysis.expires_at, "input_type": analysis.input_type, "redacted_input": analysis.redacted_input, **result}


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: str, x_access_token: str | None = Header(default=None), db: Session = Depends(get_db), user: User | None = Depends(optional_user)) -> dict:
    analysis = authorize_analysis(db, analysis_id, x_access_token, user)
    return {"id": analysis.id, "created_at": analysis.created_at, "expires_at": analysis.expires_at, "input_type": analysis.input_type, "redacted_input": analysis.redacted_input, **analysis.result}
