"""Synthetic Customer Persona and Simulation ORM Models."""

from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentassure.db.base import Base, TimestampMixin, generate_uuid


class PersonaProfile(Base, TimestampMixin):
    """Synthetic customer persona profile designed to stress-test conversational agents."""

    __tablename__ = "persona_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    persona_key: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    personality_traits: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    language: Mapped[str] = mapped_column(
        String(20), default="en", nullable=False
    )  # en, hi, hinglish
    tone: Mapped[str] = mapped_column(String(50), default="neutral", nullable=False)
    sample_goals: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Relationships
    simulations: Mapped[List["SimulationRun"]] = relationship(
        "SimulationRun", back_populates="persona", cascade="all, delete-orphan"
    )


class SimulationRun(Base, TimestampMixin):
    """Execution log of a synthetic persona multi-turn dialogue against an agent version."""

    __tablename__ = "simulation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    persona_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("persona_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    agent_version: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    successful_goal: Mapped[bool] = mapped_column(Boolean, default=False)
    surfaced_failure: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    failure_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transcript_log: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    latency_avg_ms: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationship
    persona: Mapped["PersonaProfile"] = relationship("PersonaProfile", back_populates="simulations")
