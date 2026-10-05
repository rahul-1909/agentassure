"""Unit Tests for CI/CD Release Gating and Threshold Enforcement."""

import pytest
from sqlalchemy.orm import Session

from agentassure.evaluation.gate_evaluator import GateEvaluator
from agentassure.schemas.release_gate import GateRunRequest


def test_gate_evaluator_passed(db_session: Session):
    req = GateRunRequest(
        agent_version="v2.5.0-candidate",
        commit_hash="c0ffee1",
        baseline_version="v2.4.0",
    )
    report = GateEvaluator.evaluate_gate(db_session, req)
    assert report.gate_id is not None
    assert report.status in ["PASSED", "BLOCKED"]
    assert report.overall_pass_rate >= 0.0
    assert len(report.category_breakdown) > 0
    assert len(report.statistical_tests) == 2
    assert "AgentAssure Release Gate" in report.markdown_summary


def test_gate_evaluator_fail_fast_on_critical_failure(db_session: Session):
    req = GateRunRequest(
        agent_version="v2.5.0-failing-candidate",
        commit_hash="bad1234",
    )

    # Invoker that deliberately causes compliance failure
    def failing_invoker(context):
        return "Guaranteed 100% profit with 0% interest loan!", 250.0

    report = GateEvaluator.evaluate_gate(db_session, req, candidate_invoker=failing_invoker)
    assert report.status == "BLOCKED"
    assert report.critical_categories_passed is False
    assert len(report.blocked_categories) > 0
    assert "MERGE BLOCKED" in report.markdown_summary
