"""Conversation and Turn ORM Models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentassure.db.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from agentassure.db.models.annotation import Annotation


class Conversation(Base, TimestampMixin):
    """Voice or text conversation session with calculated risk telemetry."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), default="voice", nullable=False)  # voice, chat
    agent_version: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(
        String(20), default="en", nullable=False
    )  # en, hi, hinglish

    # Risk Telemetry Signals
    judge_score: Mapped[float] = mapped_column(
        Float, default=1.0, index=True
    )  # 0.0 (bad) to 1.0 (good)
    asr_error_rate: Mapped[float] = mapped_column(Float, default=0.0, index=True)  # 0.0 to 1.0
    loop_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    customer_dropped: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    negative_sentiment: Mapped[float] = mapped_column(Float, default=0.0, index=True)  # 0.0 to 1.0
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    # Sampling and Review State
    sample_stratum: Mapped[str] = mapped_column(String(50), default="risk_ranked", nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True, nullable=False
    )
    # pending, in_review, double_review, completed, disagreement

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_purged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relationships
    turns: Mapped[List["Turn"]] = relationship(
        "Turn",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Turn.turn_index",
    )
    annotations: Mapped[List["Annotation"]] = relationship(
        "Annotation", back_populates="conversation", cascade="all, delete-orphan"
    )


class Turn(Base, TimestampMixin):
    """Individual conversational turn between user and agent."""

    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    speaker: Mapped[str] = mapped_column(String(20), nullable=False)  # user, agent, system
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    audio_start_time: Mapped[float] = mapped_column(Float, default=0.0)  # Seconds in waveform
    audio_end_time: Mapped[float] = mapped_column(Float, default=0.0)  # Seconds in waveform
    asr_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationship
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="turns")
    annotations: Mapped[List["Annotation"]] = relationship("Annotation", back_populates="turn")
