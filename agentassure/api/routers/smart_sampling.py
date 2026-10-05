"""Smart Sampling and Ingestion API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func

from agentassure.db.session import get_db
from agentassure.db.models.conversation import Conversation, Turn
from agentassure.db.models.user import User
from agentassure.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListItem,
    ConversationListResponse,
)
from agentassure.mining.risk_scorer import RiskScorer
from agentassure.mining.stratified_sampler import StratifiedSampler
from agentassure.utils.pii_masker import mask_pii
from agentassure.api.deps import get_current_user

router = APIRouter(prefix="/sampling", tags=["Smart Sampling"])


@router.get("/queue", response_model=ConversationListResponse)
def get_prioritized_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    review_status: Optional[str] = Query("pending"),
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated prioritized review queue ordered by composite risk score descending."""
    query = select(Conversation).where(Conversation.is_archived.is_(False))

    if review_status:
        query = query.where(Conversation.review_status == review_status)
    if language:
        query = query.where(Conversation.language == language)

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Paginate and order by risk_score DESC
    items_query = (
        query.order_by(desc(Conversation.risk_score))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    convs = db.scalars(items_query).all()

    items = []
    for c in convs:
        turn_count = len(c.turns)
        items.append(
            ConversationListItem(
                id=c.id,
                customer_id=c.customer_id,
                channel=c.channel,
                agent_version=c.agent_version,
                language=c.language,
                duration_seconds=c.duration_seconds,
                judge_score=c.judge_score,
                asr_error_rate=c.asr_error_rate,
                loop_count=c.loop_count,
                customer_dropped=c.customer_dropped,
                negative_sentiment=c.negative_sentiment,
                risk_score=c.risk_score,
                sample_stratum=c.sample_stratum,
                review_status=c.review_status,
                turn_count=turn_count,
            )
        )

    return ConversationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/sample", response_model=List[ConversationResponse])
def sample_review_batch(
    target_batch_size: int = Query(50, ge=1, le=200),
    latest_version: str = Query("v2.5.0"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute stratified random sampling: 65% risk-ranked, 20% new agent version, 15% edge cases."""
    selected_convs = StratifiedSampler.sample_batch(
        db, target_batch_size=target_batch_size, latest_version=latest_version
    )
    db.commit()
    return selected_convs


@router.post("/ingest", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def ingest_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest production conversation with real-time PII masking and risk score computation."""
    # 1. Compute multi-factor risk score
    computed_risk = RiskScorer.compute(
        judge_score=payload.judge_score,
        asr_error_rate=payload.asr_error_rate,
        loop_count=payload.loop_count,
        customer_dropped=payload.customer_dropped,
        negative_sentiment=payload.negative_sentiment,
    )

    # 2. Mask Customer ID PII if applicable
    masked_cust_id = mask_pii(payload.customer_id)

    conv = Conversation(
        customer_id=masked_cust_id,
        channel=payload.channel,
        agent_version=payload.agent_version,
        duration_seconds=payload.duration_seconds,
        audio_url=payload.audio_url,
        language=payload.language,
        judge_score=payload.judge_score,
        asr_error_rate=payload.asr_error_rate,
        loop_count=payload.loop_count,
        customer_dropped=payload.customer_dropped,
        negative_sentiment=payload.negative_sentiment,
        risk_score=computed_risk,
        sample_stratum=payload.sample_stratum,
        review_status="pending",
    )
    db.add(conv)
    db.flush()

    # 3. Add turns with PII masking
    for t in payload.turns:
        sanitized_transcript = mask_pii(t.transcript)
        turn = Turn(
            conversation_id=conv.id,
            turn_index=t.turn_index,
            speaker=t.speaker,
            transcript=sanitized_transcript,
            audio_start_time=t.audio_start_time,
            audio_end_time=t.audio_end_time,
            asr_confidence=t.asr_confidence,
            intent=t.intent,
            entities=t.entities,
            sentiment=t.sentiment,
        )
        db.add(turn)

    db.commit()
    db.refresh(conv)
    return conv
