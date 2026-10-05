"""Failure Cluster and Closed-Loop Ticket ORM Models."""

from typing import List, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentassure.db.base import Base, TimestampMixin, generate_uuid


class FailureCluster(Base, TimestampMixin):
    """Aggregated group of recurring failure patterns identified by mining."""

    __tablename__ = "failure_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    cluster_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    category_l1: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category_l2: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(10), default="S2", nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    fix_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    expected_impact_reduction_pct: Mapped[float] = mapped_column(Float, default=15.0)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relationships
    tickets: Mapped[List["Ticket"]] = relationship(
        "Ticket", back_populates="cluster", cascade="all, delete-orphan"
    )


class Ticket(Base, TimestampMixin):
    """External issue tracking ticket (Linear or Jira) linked to failure clusters."""

    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    cluster_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("failure_clusters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    system_type: Mapped[str] = mapped_column(
        String(20), default="linear", nullable=False
    )  # linear, jira
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", index=True, nullable=False)
    post_release_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    verified_failure_rate_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    verified_failure_rate_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationship
    cluster: Mapped["FailureCluster"] = relationship("FailureCluster", back_populates="tickets")
