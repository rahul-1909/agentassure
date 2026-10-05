"""Quality Reporting, Rubrics, and Governance API Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from agentassure.db.session import get_db
from agentassure.db.models.rubric import RubricVersion
from agentassure.db.models.user import AuditLog, User
from agentassure.schemas.reporting import QualityReportResponse, RubricVersionSchema
from agentassure.reporting.metrics_aggregator import MetricsAggregator
from agentassure.reporting.html_generator import HTMLReportGenerator
from agentassure.qa.rubrics_manager import RubricsManager
from agentassure.api.deps import get_current_user, require_roles
from agentassure.utils.audit import AuditLogger

router = APIRouter(prefix="/reports", tags=["Quality Reporting & Governance"])


@router.get("/summary", response_model=QualityReportResponse)
def get_quality_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full system scorecard including SLA compliance, coverage, and kappa agreement."""
    return MetricsAggregator.generate_report(db)


@router.get("/html", response_class=HTMLResponse)
def get_html_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Render client-ready executive HTML dashboard."""
    report = MetricsAggregator.generate_report(db)
    html_content = HTMLReportGenerator.render(report)
    return HTMLResponse(content=html_content)


@router.get("/rubrics", response_model=List[RubricVersionSchema])
def list_rubric_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all loaded YAML rubric versions and their active status."""
    RubricsManager.sync_to_db(db)
    rubrics = db.scalars(select(RubricVersion).order_by(desc(RubricVersion.version_tag))).all()
    return rubrics


@router.post("/rubrics/activate/{version_tag}", response_model=RubricVersionSchema)
def activate_rubric_version(
    version_tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "qa_manager"])),
):
    """Activate or rollback to a specific versioned rubric."""
    try:
        RubricsManager.set_active_version(version_tag)
        RubricsManager.sync_to_db(db)

        rubric = db.scalar(select(RubricVersion).where(RubricVersion.version_tag == version_tag))
        AuditLogger.log_action(
            db,
            action="activate_rubric_version",
            entity_type="rubric_version",
            entity_id=version_tag,
            user_id=current_user.id,
        )
        return rubric
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "qa_manager"])),
):
    """Retrieve immutable security and access audit logs."""
    logs = db.scalars(
        select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    ).all()
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
