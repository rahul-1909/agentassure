"""Rubric Versioning and Calibration Models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentassure.db.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from agentassure.db.models.user import User


class RubricVersion(Base, TimestampMixin):
    """Versioned QA evaluation rubric stored as YAML configuration."""

    __tablename__ = "rubric_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_tag: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    content_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )


class ReviewerCalibration(Base, TimestampMixin):
    """Inter-rater reliability calibration audit record for a QA reviewer."""

    __tablename__ = "reviewer_calibrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_name: Mapped[str] = mapped_column(String(100), nullable=False)
    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    gold_standard_count: Mapped[int] = mapped_column(Integer, default=0)
    agreed_count: Mapped[int] = mapped_column(Integer, default=0)
    kappa_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(
        String(30), default="passed", index=True
    )  # passed (kappa > 0.80), needs_training
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    reviewer: Mapped["User"] = relationship("User")
