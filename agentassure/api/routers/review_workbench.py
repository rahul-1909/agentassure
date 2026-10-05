"""Review Workbench API Endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentassure.api.deps import get_current_user, require_roles
from agentassure.db.models.annotation import DisagreementReview
from agentassure.db.models.conversation import Conversation
from agentassure.db.models.user import User
from agentassure.db.session import get_db
from agentassure.qa.review_engine import ReviewEngine
from agentassure.schemas.annotation import (
    AdjudicationRequest,
    AnnotationCreate,
    AnnotationResponse,
    DisagreementResponse,
    ReviewerMetricsResponse,
)
from agentassure.schemas.conversation import ConversationResponse
from agentassure.utils.audit import AuditLogger

router = APIRouter(prefix="/review", tags=["Review Workbench"])


@router.post("/session/start/{conversation_id}", response_model=ConversationResponse)
def start_review_session(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start or lock a conversation review session for the authenticated reviewer."""
    try:
        conv = ReviewEngine.start_review_session(db, conversation_id, current_user.id)
        AuditLogger.log_action(
            db,
            action="start_review_session",
            entity_type="conversation",
            entity_id=conversation_id,
            user_id=current_user.id,
        )
        return conv
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full conversation details including synchronized turns and audio metadata."""
    conv = db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found.",
        )
    return conv


@router.post("/annotation", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
def submit_annotation(
    payload: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a QA turn annotation, route double-reviews, and detect rater disagreements."""
    try:
        annotation = ReviewEngine.submit_annotation(db, current_user.id, payload)
        AuditLogger.log_action(
            db,
            action="submit_annotation",
            entity_type="annotation",
            entity_id=annotation.id,
            user_id=current_user.id,
            details={"turn_id": payload.turn_id, "category_l1": payload.failure_category_l1},
        )
        return annotation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/disagreements", response_model=List[DisagreementResponse])
def get_disagreement_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "qa_manager"])),
):
    """Retrieve all pending dual-reviewer disagreement cases requiring adjudication."""
    disagreements = db.scalars(
        select(DisagreementReview).where(DisagreementReview.status == "pending")
    ).all()
    return disagreements


@router.post("/adjudicate", response_model=DisagreementResponse)
def adjudicate_disagreement(
    payload: AdjudicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "qa_manager"])),
):
    """Adjudicate and resolve a dual-reviewer disagreement case."""
    try:
        resolved = ReviewEngine.adjudicate_disagreement(db, current_user.id, payload)
        AuditLogger.log_action(
            db,
            action="adjudicate_disagreement",
            entity_type="disagreement_review",
            entity_id=resolved.id,
            user_id=current_user.id,
            details={"resolved_category_l1": payload.resolved_category_l1},
        )
        return resolved
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/metrics/{reviewer_id}", response_model=ReviewerMetricsResponse)
def get_reviewer_metrics(
    reviewer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch turnaround SLA, failure confirmation count, and inter-rater Cohen's kappa."""
    metrics = ReviewEngine.get_reviewer_metrics(db, reviewer_id)
    return metrics
