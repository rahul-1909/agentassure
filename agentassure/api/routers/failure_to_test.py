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
test_cases_router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


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
@router.get("/test-cases", response_model=TestCaseListResponse)
@test_cases_router.get("", response_model=TestCaseListResponse)
def list_test_cases(
    category_l1: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active regression test cases with filtering by category and severity."""
    query = select(RegressionTestCase).where(RegressionTestCase.is_active.is_(True))
    if category_l1:
        query = query.where(RegressionTestCase.category_l1 == category_l1)
    if severity:
        query = query.where(RegressionTestCase.severity == severity)

    all_cases = db.scalars(query).all()
    total = len(all_cases)
    cases = db.scalars(query.offset(offset).limit(limit)).all()
    return TestCaseListResponse(items=cases, total=total)


@router.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
@test_cases_router.get("/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(
    test_case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed regression test case specifications and assertions."""
    test_case = db.get(RegressionTestCase, test_case_id)
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case '{test_case_id}' not found.",
        )
    return test_case


@router.put("/test-cases/{test_case_id}", response_model=TestCaseResponse)
@test_cases_router.put("/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(
    test_case_id: str,
    title: Optional[str] = None,
    expected_assertion: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update regression test case assertions and metadata."""
    test_case = db.get(RegressionTestCase, test_case_id)
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case '{test_case_id}' not found.",
        )
    if title is not None:
        test_case.title = title
    if expected_assertion is not None:
        test_case.expected_assertion = expected_assertion
    db.commit()
    db.refresh(test_case)
    return test_case


@router.delete("/test-cases/{test_case_id}", status_code=status.HTTP_200_OK)
@test_cases_router.delete("/{test_case_id}", status_code=status.HTTP_200_OK)
def delete_test_case(
    test_case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate or soft-delete regression test case."""
    test_case = db.get(RegressionTestCase, test_case_id)
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case '{test_case_id}' not found.",
        )
    test_case.is_active = False
    db.commit()
    return {"success": True, "message": f"Test case '{test_case_id}' deactivated."}


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
