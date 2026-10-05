"""Pydantic v2 Schemas for Annotations and Adjudication."""

from typing import List, Optional

from pydantic import BaseModel, Field


class AnnotationCreate(BaseModel):
    """Schema for submitting an annotation on a turn."""

    conversation_id: str
    turn_id: str
    failure_category_l1: str = Field(..., description="L1 failure category")
    failure_category_l2: str = Field(..., description="L2 specific failure subtype")
    severity: str = Field(default="S3", description="Severity level: S1, S2, S3, S4")
    root_cause_notes: Optional[str] = None
    is_confirmed_failure: bool = True
    fix_type: str = Field(
        default="prompt_patch",
        description="Suggested fix: prompt_patch, kb_entry, tool_retry, asr_vocab_boost",
    )
    review_duration_seconds: float = 0.0
    tags: List[str] = Field(default_factory=list)


class AnnotationResponse(AnnotationCreate):
    """Returned annotation record with system identifiers."""

    id: str
    reviewer_id: str

    model_config = {"from_attributes": True}


class AdjudicationRequest(BaseModel):
    """Supervisor decision payload resolving a dual-review disagreement."""

    disagreement_id: str
    resolved_category_l1: str
    resolved_category_l2: str
    resolved_severity: str
    resolution_notes: str


class DisagreementResponse(BaseModel):
    """Schema representing an adjudication queue item."""

    id: str
    conversation_id: str
    turn_id: str
    reviewer_1_id: str
    reviewer_2_id: str
    annotation_1_id: str
    annotation_2_id: str
    status: str
    adjudicated_by_id: Optional[str] = None
    resolved_category_l1: Optional[str] = None
    resolved_category_l2: Optional[str] = None
    resolved_severity: Optional[str] = None
    resolution_notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ReviewerMetricsResponse(BaseModel):
    """Metrics tracking reviewer efficiency, accuracy, and inter-rater reliability."""

    reviewer_id: str
    total_reviews: int
    confirmed_failures: int
    avg_turnaround_seconds: float
    inter_rater_kappa: float
    coverage_percent: float
