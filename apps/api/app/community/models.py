"""Infrastructure-owned persistence for the community module."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, utcnow


def identifier() -> str:
    return str(uuid4())


class Report(Base):
    __tablename__ = "community_reports"
    __table_args__ = (
        Index("ix_community_reports_target_status", "target_key", "status", "expires_at"),
        Index("ix_community_reports_dedupe", "target_key", "reporter_hash", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    target_type: Mapped[str] = mapped_column(String(8), nullable=False)
    target_key: Mapped[str] = mapped_column(String(64), nullable=False)
    target_redacted: Mapped[str] = mapped_column(Text, nullable=False)
    reason_redacted: Mapped[str] = mapped_column(Text, nullable=False)
    reporter_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="pending")
    duplicate_of_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ModerationDecision(Base):
    __tablename__ = "community_moderation_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("community_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_id: Mapped[str] = mapped_column(String(36), nullable=False)
    decision: Mapped[str] = mapped_column(String(12), nullable=False)
    reason_redacted: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Feedback(Base):
    __tablename__ = "community_feedback"
    __table_args__ = (Index("ix_community_feedback_analysis", "analysis_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    analysis_id: Mapped[str] = mapped_column(String(36), nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(24), nullable=False)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    helpful: Mapped[bool] = mapped_column(nullable=False)
    verdict: Mapped[str] = mapped_column(String(24), nullable=False)
    comment_redacted: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AuditLog(Base):
    __tablename__ = "community_admin_audit"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    admin_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reason_redacted: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
