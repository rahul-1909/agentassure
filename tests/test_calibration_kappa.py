"""Unit Tests for CalibrationEngine and Cohen's Kappa Reliability."""

import pytest

from agentassure.qa.calibration import CalibrationEngine


def test_cohens_kappa_perfect_agreement():
    rater_a = ["Compliance", "Factual Accuracy", "Safety", "Flow"]
    rater_b = ["Compliance", "Factual Accuracy", "Safety", "Flow"]
    kappa = CalibrationEngine.calculate_cohens_kappa(rater_a, rater_b)
    assert kappa == 1.0


def test_cohens_kappa_partial_agreement():
    rater_a = ["Compliance", "Compliance", "Factual Accuracy", "Flow", "Safety"]
    rater_b = ["Compliance", "Factual Accuracy", "Factual Accuracy", "Flow", "Safety"]
    kappa = CalibrationEngine.calculate_cohens_kappa(rater_a, rater_b)
    assert 0.5 <= kappa < 1.0


def test_cohens_kappa_empty_and_mismatched():
    assert CalibrationEngine.calculate_cohens_kappa([], []) == 1.0
    assert CalibrationEngine.calculate_cohens_kappa(["A"], ["B", "C"]) == 0.0


def test_reviewer_calibration_audit_pass():
    gold = ["Compliance", "Factual Accuracy", "Safety", "Flow", "Compliance"]
    reviewer = ["Compliance", "Factual Accuracy", "Safety", "Flow", "Compliance"]
    audit = CalibrationEngine.audit_reviewer_calibration(reviewer, gold)
    assert audit["passed"] is True
    assert audit["status"] == "passed"
    assert audit["accuracy"] == 1.0
    assert audit["kappa_score"] == 1.0


def test_reviewer_calibration_audit_fail():
    gold = ["Compliance", "Factual Accuracy", "Safety", "Flow", "Compliance"]
    reviewer = ["Flow", "Safety", "Tone", "Tone", "Tone"]
    audit = CalibrationEngine.audit_reviewer_calibration(reviewer, gold)
    assert audit["passed"] is False
    assert audit["status"] == "needs_training"
    assert audit["kappa_score"] < 0.80
