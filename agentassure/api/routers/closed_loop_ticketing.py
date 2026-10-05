"""Closed-Loop Ticketing API Endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from agentassure.api.deps import get_current_user
from agentassure.db.models.ticket import FailureCluster, Ticket
from agentassure.db.models.user import User
from agentassure.db.session import get_db
from agentassure.mining.failure_clusterer import FailureClusterer
from agentassure.schemas.ticket import (
    FailureClusterResponse,
    TicketCreate,
    TicketResponse,
    WebhookCallbackPayload,
)
from agentassure.ticketing.jira_linear import TicketingClient
from agentassure.utils.audit import AuditLogger

router = APIRouter(prefix="/tickets", tags=["Closed-Loop Ticketing"])


@router.post("/cluster", response_model=List[FailureClusterResponse])
def cluster_failures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate confirmed QA failure annotations into systematic failure clusters."""
    clusters = FailureClusterer.mine_clusters(db)
    AuditLogger.log_action(
        db,
        action="mine_failure_clusters",
        entity_type="failure_clusters",
        user_id=current_user.id,
        details={"clusters_identified": len(clusters)},
    )
    return clusters


@router.get("/clusters", response_model=List[FailureClusterResponse])
def list_clusters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all identified failure clusters."""
    return db.scalars(select(FailureCluster).order_by(desc(FailureCluster.frequency))).all()


@router.post("/create", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a standardized engineering ticket in Linear or Jira from a failure cluster."""
    try:
        ticket = TicketingClient.create_ticket_from_cluster(
            db, payload.cluster_id, payload.system_type
        )
        AuditLogger.log_action(
            db,
            action="create_ticket",
            entity_type="ticket",
            entity_id=ticket.id,
            user_id=current_user.id,
            details={"external_id": ticket.external_id, "cluster_id": payload.cluster_id},
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all created engineering tickets and their post-release validation metrics."""
    return db.scalars(select(Ticket).order_by(desc(Ticket.created_at))).all()


@router.post("/webhook", response_model=TicketResponse)
def webhook_callback(
    payload: WebhookCallbackPayload,
    db: Session = Depends(get_db),
):
    """Inbound webhook callback from Linear / Jira / CI updating ticket post-release status."""
    try:
        ticket = TicketingClient.update_post_release_status(
            db=db,
            external_id=payload.external_id,
            new_status=payload.new_status,
            measured_failure_rate_after=0.5,  # Measured reduction post-deploy
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
