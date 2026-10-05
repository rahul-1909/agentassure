"""Pydantic v2 Schemas for Closed-Loop Ticketing and Webhooks."""

from typing import Optional
from pydantic import BaseModel, Field


class FailureClusterResponse(BaseModel):
    """Aggregated failure cluster ready for engineering handoff."""

    id: str
    cluster_name: str
    category_l1: str
    category_l2: str
    severity: str
    root_cause: str
    frequency: int
    fix_suggestion: str
    expected_impact_reduction_pct: float
    is_resolved: bool

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    """Request to generate an engineering issue ticket from a failure cluster."""

    cluster_id: str
    system_type: str = Field(default="linear", description="Target system: linear or jira")


class TicketResponse(BaseModel):
    """External issue tracking ticket metadata."""

    id: str
    cluster_id: str
    external_id: str
    system_type: str
    title: str
    body: str
    status: str
    post_release_verified: bool
    verified_failure_rate_before: Optional[float] = None
    verified_failure_rate_after: Optional[float] = None

    model_config = {"from_attributes": True}


class WebhookCallbackPayload(BaseModel):
    """Inbound webhook payload from Linear / Jira / CI."""

    ticket_id: Optional[str] = None
    external_id: str
    new_status: str
    release_version: Optional[str] = None
