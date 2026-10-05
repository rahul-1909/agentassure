"""Regression Test Case and Test Run Result ORM Models."""

from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentassure.db.base import Base, TimestampMixin, generate_uuid


class RegressionTestCase(Base, TimestampMixin):
    """Structured regression test case distilled atomically from confirmed QA failures."""

    __tablename__ = "regression_test_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_conversation_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    source_turn_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("turns.id", ondelete="SET NULL"), index=True, nullable=True
    )
    cluster_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("failure_clusters.id", ondelete="SET NULL"), index=True, nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_l1: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category_l2: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(10), default="S2", index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)

    # Conversation Context & Prompts
    conversation_context: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    expected_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    actual_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    fix_suggestion: Mapped[str] = mapped_column(Text, nullable=False)

    # Structured Assertions: list of dicts with {"type": "...", "params": {...}}
    assertion_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Relationships
    test_runs: Mapped[List["TestRunResult"]] = relationship(
        "TestRunResult", back_populates="test_case", cascade="all, delete-orphan"
    )


class TestRunResult(Base, TimestampMixin):
    """Result of evaluating a regression test case against an agent version."""

    __tablename__ = "test_run_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    test_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("regression_test_cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    run_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    commit_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    agent_version: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    test_case: Mapped["RegressionTestCase"] = relationship("RegressionTestCase", back_populates="test_runs")
