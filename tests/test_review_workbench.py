"""Unit Tests for Review Workbench and Disagreement Adjudication."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentassure.db.models.annotation import Annotation, DisagreementReview
from agentassure.db.models.conversation import Conversation, Turn
from agentassure.db.models.user import User
from agentassure.qa.review_engine import ReviewEngine
from agentassure.schemas.annotation import AdjudicationRequest, AnnotationCreate


def test_start_review_session(db_session: Session):
    conv = db_session.scalar(select(Conversation).where(Conversation.review_status == "pending"))
    user = db_session.scalar(select(User).where(User.username == "reviewer_alice"))

    started_conv = ReviewEngine.start_review_session(db_session, conv.id, user.id)
    assert started_conv.review_status == "in_review"


def test_submit_annotation_single_reviewer(db_session: Session):
    conv = db_session.scalar(select(Conversation))
    turn = conv.turns[0]
    reviewer = db_session.scalar(select(User).where(User.username == "reviewer_alice"))

    payload = AnnotationCreate(
        conversation_id=conv.id,
        turn_id=turn.id,
        failure_category_l1="Compliance",
        failure_category_l2="Missing Statutory or RBI Disclaimer",
        severity="S1",
        root_cause_notes="Disclaimer missing in opening turn.",
        fix_type="prompt_patch",
        review_duration_seconds=35.0,
        is_confirmed_failure=True,
    )

    annotation = ReviewEngine.submit_annotation(db_session, reviewer.id, payload)
    assert annotation.id is not None
    assert annotation.severity == "S1"
    assert annotation.failure_category_l1 == "Compliance"


def test_double_review_disagreement_detection(db_session: Session):
    conv = db_session.scalar(select(Conversation))
    turn = conv.turns[0]
    reviewer_1 = db_session.scalar(select(User).where(User.username == "reviewer_alice"))
    reviewer_2 = db_session.scalar(select(User).where(User.username == "reviewer_bob"))

    # Reviewer 1 submits
    payload_1 = AnnotationCreate(
        conversation_id=conv.id,
        turn_id=turn.id,
        failure_category_l1="Factual Accuracy",
        failure_category_l2="Unsupported Numerical or Pricing Claim",
        severity="S1",
        root_cause_notes="Hallucinated interest rate.",
        fix_type="prompt_patch",
    )
    ReviewEngine.submit_annotation(db_session, reviewer_1.id, payload_1)

    # Reviewer 2 submits a conflicting category/severity
    payload_2 = AnnotationCreate(
        conversation_id=conv.id,
        turn_id=turn.id,
        failure_category_l1="Compliance",
        failure_category_l2="Missing Statutory or RBI Disclaimer",
        severity="S2",
        root_cause_notes="Compliance disclaimer absent.",
        fix_type="prompt_patch",
    )
    ReviewEngine.submit_annotation(db_session, reviewer_2.id, payload_2)

    # Verify disagreement created and conversation flagged
    disagreement = db_session.scalar(
        select(DisagreementReview).where(DisagreementReview.turn_id == turn.id)
    )
    assert disagreement is not None
    assert disagreement.status == "pending"
    assert conv.review_status == "disagreement"


def test_adjudicate_disagreement(db_session: Session):
    conv = db_session.scalar(select(Conversation))
    turn = conv.turns[0]
    reviewer_1 = db_session.scalar(select(User).where(User.username == "reviewer_alice"))
    reviewer_2 = db_session.scalar(select(User).where(User.username == "reviewer_bob"))
    supervisor = db_session.scalar(select(User).where(User.username == "admin"))

    # Trigger disagreement
    p1 = AnnotationCreate(
        conversation_id=conv.id,
        turn_id=turn.id,
        failure_category_l1="Tone, Sentiment & Empathy",
        failure_category_l2="Dismissive / Rude Demeanor",
        severity="S3",
    )
    p2 = AnnotationCreate(
        conversation_id=conv.id,
        turn_id=turn.id,
        failure_category_l1="Conversational Flow & Loops",
        failure_category_l2="Repetitive Non-Progress Loop",
        severity="S2",
    )
    ReviewEngine.submit_annotation(db_session, reviewer_1.id, p1)
    ReviewEngine.submit_annotation(db_session, reviewer_2.id, p2)

    disagreement = db_session.scalar(
        select(DisagreementReview).where(DisagreementReview.turn_id == turn.id)
    )

    req = AdjudicationRequest(
        disagreement_id=disagreement.id,
        resolved_category_l1="Conversational Flow & Loops",
        resolved_category_l2="Repetitive Non-Progress Loop",
        resolved_severity="S2",
        resolution_notes="Supervisor confirmed loop failure takes precedence over minor tone friction.",
    )

    resolved = ReviewEngine.adjudicate_disagreement(db_session, supervisor.id, req)
    assert resolved.status == "adjudicated"
    assert resolved.resolved_category_l1 == "Conversational Flow & Loops"
    assert conv.review_status == "completed"


def test_reviewer_metrics(db_session: Session):
    reviewer = db_session.scalar(select(User).where(User.username == "reviewer_alice"))
    metrics = ReviewEngine.get_reviewer_metrics(db_session, reviewer.id)
    assert "total_reviews" in metrics
    assert "confirmed_failures" in metrics
    assert "avg_turnaround_seconds" in metrics
    assert "inter_rater_kappa" in metrics
    assert metrics["inter_rater_kappa"] >= 0.0
