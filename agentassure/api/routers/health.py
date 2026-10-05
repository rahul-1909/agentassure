"""Health check and Telemetry Metrics API Endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from agentassure.config import settings
from agentassure.db.models.conversation import Conversation
from agentassure.db.models.test_case import RegressionTestCase
from agentassure.db.models.ticket import Ticket
from agentassure.db.session import get_db

router = APIRouter(tags=["Health & Telemetry"])


@router.get("/health", summary="System Health Check")
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Verify backend API service status and database connectivity."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


@router.get("/metrics", summary="System Operational Telemetry")
def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve operational counters for monitoring and Grafana dashboards."""
    total_convs = db.scalar(select(func.count(Conversation.id))) or 0
    pending_reviews = (
        db.scalar(
            select(func.count(Conversation.id)).where(Conversation.review_status == "pending")
        )
        or 0
    )
    completed_reviews = (
        db.scalar(
            select(func.count(Conversation.id)).where(Conversation.review_status == "completed")
        )
        or 0
    )
    active_tests = (
        db.scalar(
            select(func.count(RegressionTestCase.id)).where(RegressionTestCase.is_active.is_(True))
        )
        or 0
    )
    open_tickets = db.scalar(select(func.count(Ticket.id)).where(Ticket.status == "open")) or 0

    return {
        "conversations_total": total_convs,
        "reviews_pending": pending_reviews,
        "reviews_completed": completed_reviews,
        "regression_tests_active": active_tests,
        "open_engineering_tickets": open_tickets,
    }
