"""Annotation and Disagreement Resolution Models."""

from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentassure.db.base import Base, TimestampMixin, generate_uuid


class Annotation(Base, TimestampMixin):
    """Quality annotation record submitted by a human reviewer for a specific turn."""

    __tablename__ = "annotations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    turn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("turns.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Taxonomy and Severity
    failure_category_l1: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    failure_category_l2: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(10), default="S3", index=True, nullable=False)  # S1, S2, S3, S4

    root_cause_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_confirmed_failure: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    fix_type: Mapped[str] = mapped_column(
        String(50), default="prompt_patch", nullable=False
    )  # prompt_patch, kb_entry, tool_retry, asr_vocab_boost

    review_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="annotations")
    turn: Mapped["Turn"] = relationship("Turn", back_populates="annotations")
    reviewer: Mapped["User"] = relationship("User", back_populates="annotations")


class DisagreementReview(Base, TimestampMixin):
    """Disagreement case between dual reviewers requiring supervisor adjudication."""

    __tablename__ = "disagreement_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    turn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("turns.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reviewer_1_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    reviewer_2_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    annotation_1_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotations.id"), nullable=False)
    annotation_2_id: Mapped[str] = mapped_column(String(36), ForeignKey("annotations.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)  # pending, adjudicated
    adjudicated_by_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    resolved_category_l1: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved_category_l2: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved_severity: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
