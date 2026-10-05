"""Release Gating and CI/CD Pipeline API Endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agentassure.api.deps import get_current_user
from agentassure.db.models.user import User
from agentassure.db.session import get_db
from agentassure.evaluation.gate_evaluator import GateEvaluator
from agentassure.schemas.release_gate import GateRunRequest, GateRunResponse
from agentassure.ticketing.slack_notifier import SlackNotifier
from agentassure.utils.audit import AuditLogger

router = APIRouter(prefix="/release-gate", tags=["Release Gating"])


@router.post("/evaluate", response_model=GateRunResponse)
def evaluate_release_gate(
    payload: GateRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run regression test cases, execute statistical hypothesis testing, and gate deployment."""
    report = GateEvaluator.evaluate_gate(db, payload)

    # If gate blocked, dispatch Slack alert
    if report.status == "BLOCKED":
        SlackNotifier.post_gate_blocked_alert(
            version=report.agent_version,
            blocked_categories=report.blocked_categories,
            pass_rate=report.overall_pass_rate,
        )

    AuditLogger.log_action(
        db,
        action="evaluate_release_gate",
        entity_type="release_gate",
        entity_id=report.gate_id,
        user_id=current_user.id,
        details={
            "agent_version": report.agent_version,
            "status": report.status,
            "blocked_categories": report.blocked_categories,
        },
    )

    return report
