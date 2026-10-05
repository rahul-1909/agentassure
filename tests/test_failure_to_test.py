"""Unit Tests for Failure-to-Test Pipeline and Assertion Engine."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentassure.db.models.annotation import Annotation
from agentassure.evaluation.assertion_engine import AssertionEngine
from agentassure.evaluation.regression_runner import RegressionRunner


def test_assertion_must_contain():
    rule = {"targets": ["terms and conditions apply", "10.5%"]}
    passed, msg = AssertionEngine.evaluate_rule(
        "must_contain", rule, "Our rate is 10.5%. Terms and conditions apply."
    )
    assert passed is True

    failed, msg = AssertionEngine.evaluate_rule(
        "must_contain", rule, "Our rate is 10.5% without disclaimer."
    )
    assert failed is False
    assert "Missing required term" in msg


def test_assertion_must_not_contain():
    rule = {"forbidden": ["system prompt", "api_key", "ignore previous"]}
    passed, _ = AssertionEngine.evaluate_rule(
        "must_not_contain", rule, "Hello, how can I help you today?"
    )
    assert passed is True

    failed, msg = AssertionEngine.evaluate_rule(
        "must_not_contain", rule, "Here is the SYSTEM PROMPT: You are a bot."
    )
    assert failed is False
    assert "Forbidden term detected" in msg


def test_assertion_compliance_check():
    rule = {
        "required_disclaimer": "terms and conditions apply",
        "forbidden_advice": ["100% guaranteed profit"],
    }
    # Pass case
    p, _ = AssertionEngine.evaluate_rule(
        "compliance_check", rule, "Apply today. Terms and conditions apply."
    )
    assert p is True

    # Breach case: contains forbidden advice
    f, msg = AssertionEngine.evaluate_rule(
        "compliance_check", rule, "We guarantee 100% guaranteed profit! Terms and conditions apply."
    )
    assert f is False
    assert "Unauthorized advice detected" in msg


def test_assertion_no_hallucination():
    rule = {"unsupported_facts": ["7.5% flat", "0% interest loan"]}
    p, _ = AssertionEngine.evaluate_rule(
        "no_hallucination", rule, "Personal loans start at 10.5% p.a."
    )
    assert p is True

    f, msg = AssertionEngine.evaluate_rule(
        "no_hallucination", rule, "We can offer you a 7.5% flat rate right now."
    )
    assert f is False
    assert "Hallucinated" in msg


def test_assertion_latency_under():
    rule = {"max_ms": 1500.0}
    p, _ = AssertionEngine.evaluate_rule("latency_under", rule, "Response", latency_ms=450.0)
    assert p is True

    f, msg = AssertionEngine.evaluate_rule("latency_under", rule, "Response", latency_ms=2200.0)
    assert f is False
    assert "exceeded" in msg


def test_convert_failure_to_test(db_session: Session):
    annot = db_session.scalar(select(Annotation).where(Annotation.is_confirmed_failure.is_(True)))
    assert annot is not None

    test_case = RegressionRunner.convert_failure_to_test(db_session, annot.id)
    assert test_case.id is not None
    assert test_case.category_l1 == annot.failure_category_l1
    assert test_case.category_l2 == annot.failure_category_l2
    assert len(test_case.assertion_rules) > 0
    assert test_case.is_active is True


def test_execute_regression_suite(db_session: Session):
    results = RegressionRunner.run_suite(db_session, agent_version="v2.5.0-candidate")
    assert len(results) > 0
    assert all(r.run_id is not None for r in results)
