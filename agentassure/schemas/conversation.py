"""Pydantic v2 Schemas for Conversations and Turns."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TurnBase(BaseModel):
    """Base schema for conversational turn."""

    turn_index: int
    speaker: str = Field(..., description="user, agent, or system")
    transcript: str
    audio_start_time: float = 0.0
    audio_end_time: float = 0.0
    asr_confidence: float = 1.0
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    sentiment: Optional[str] = None


class TurnCreate(TurnBase):
    """Payload to create a new conversational turn."""
    pass


class TurnResponse(TurnBase):
    """Turn response schema with ID and timestamps."""

    id: str
    conversation_id: str

    model_config = {"from_attributes": True}


class ConversationBase(BaseModel):
    """Base conversation attributes."""

    customer_id: str
    channel: str = "voice"
    agent_version: str
    duration_seconds: float = 0.0
    audio_url: Optional[str] = None
    language: str = "en"
    judge_score: float = 1.0
    asr_error_rate: float = 0.0
    loop_count: int = 0
    customer_dropped: bool = False
    negative_sentiment: float = 0.0
    sample_stratum: str = "risk_ranked"


class ConversationCreate(ConversationBase):
    """Payload to ingest a new conversation with turns."""

    turns: List[TurnCreate] = Field(default_factory=list)


class ConversationResponse(ConversationBase):
    """Full conversation detail schema with turns and calculated risk score."""

    id: str
    risk_score: float
    review_status: str
    is_archived: bool
    is_purged: bool
    turns: List[TurnResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    """Summary item for paginated conversation list / prioritized review queue."""

    id: str
    customer_id: str
    channel: str
    agent_version: str
    language: str
    duration_seconds: float
    judge_score: float
    asr_error_rate: float
    loop_count: int
    customer_dropped: bool
    negative_sentiment: float
    risk_score: float
    sample_stratum: str
    review_status: str
    turn_count: int

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Paginated response of conversations."""

    items: List[ConversationListItem]
    total: int
    page: int
    page_size: int
