"""Pydantic v2 Schemas for Personas and Simulation Runs."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PersonaBase(BaseModel):
    """Synthetic customer persona attributes."""

    persona_key: str
    name: str
    description: str
    personality_traits: List[str] = Field(default_factory=list)
    language: str = "en"
    tone: str = "neutral"
    sample_goals: List[str] = Field(default_factory=list)


class PersonaCreate(PersonaBase):
    """Payload to register a new persona profile."""
    pass


class PersonaResponse(PersonaBase):
    """Persona profile response schema."""

    id: str
    is_active: bool

    model_config = {"from_attributes": True}


class SimulationRunRequest(BaseModel):
    """Request to initiate a multi-turn synthetic dialogue simulation."""

    persona_key: str
    agent_version: str = "v2.5.0-candidate"
    max_turns: int = Field(default=6, ge=1, le=20)
    customer_goal: Optional[str] = None
    voice_mode: bool = False


class SimulationRunResponse(BaseModel):
    """Output of a simulation run including surfaced edge case failures."""

    id: str
    persona_id: str
    persona_key: Optional[str] = None
    agent_version: str
    total_turns: int
    successful_goal: bool
    surfaced_failure: bool
    failure_category: Optional[str] = None
    transcript_log: List[Dict[str, Any]]
    latency_avg_ms: float

    model_config = {"from_attributes": True}
