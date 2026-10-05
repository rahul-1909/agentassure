"""Failure-to-Test Pipeline API Endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agentassure.api.deps import get_current_user
from agentassure.db.models.test_case import RegressionTestCase
from agentassure.db.models.user import User
from agentassure.db.session import get_db
from agentassure.evaluation.regression_runner import RegressionRunner
from agentassure.schemas.test_case import (
    TestCaseCreate,
    TestCaseListResponse,
    TestCaseResponse,
    TestRunResultSchema,
)
from agentassure.utils.audit import AuditLogger

router = APIRouter(prefix="/failures", tags=["Failure-to-Test Pipeline"])


@router.post(
    "/convert/{annotation_id}", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED
)
def convert_failure_to_test(
    annotation_id: str,
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atomically convert a confirmed QA failure annotation into an active regression test case."""
    try:
        test_case = RegressionRunner.convert_failure_to_test(db, annotation_id, title)
        AuditLogger.log_action(
            db,
            action="convert_failure_to_test",
            entity_type="regression_test_case",
            entity_id=test_case.id,
            user_id=current_user.id,
            details={"category_l1": test_case.category_l1, "source_annotation": annotation_id},
        )
        return test_case
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/tests", response_model=TestCaseListResponse)
def list_test_cases(
    category_l1: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active regression test cases with filtering by category and severity."""
    query = select(RegressionTestCase).where(RegressionTestCase.is_active.is_(True))
    if category_l1:
        query = query.where(RegressionTestCase.category_l1 == category_l1)
    if severity:
        query = query.where(RegressionTestCase.severity == severity)

    cases = db.scalars(query).all()
    return TestCaseListResponse(items=cases, total=len(cases))


@router.post("/tests/run", response_model=List[TestRunResultSchema])
def run_regression_suite(
    agent_version: str = Query("v2.5.0-candidate"),
    commit_hash: Optional[str] = Query("head-sha"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run all active regression test cases against specified candidate agent version."""
    results = RegressionRunner.run_suite(db, agent_version=agent_version, commit_hash=commit_hash)
    AuditLogger.log_action(
        db,
        action="run_regression_suite",
        entity_type="regression_suite",
        user_id=current_user.id,
        details={"agent_version": agent_version, "total_tests": len(results)},
    )
    return results
