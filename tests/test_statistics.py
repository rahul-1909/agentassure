"""Unit Tests for SignificanceTester (Chi-Square & Two-Sample t-Test)."""

import pytest

from agentassure.evaluation.statistics import SignificanceTester


def test_chi_square_identical_rates():
    res = SignificanceTester.test_pass_rate_significance(
        candidate_passed=95,
        candidate_failed=5,
        baseline_passed=95,
        baseline_failed=5,
    )
    assert res["is_significant"] is False
    assert res["statistic"] == 0.0
    assert res["p_value"] == 1.0


def test_chi_square_significant_improvement():
    # 98% vs 70% in 100 samples
    res = SignificanceTester.test_pass_rate_significance(
        candidate_passed=98,
        candidate_failed=2,
        baseline_passed=70,
        baseline_failed=30,
    )
    assert res["is_significant"] is True
    assert res["p_value"] < 0.01
    assert "improvement" in res["conclusion"]


def test_chi_square_insufficient_sample():
    res = SignificanceTester.test_pass_rate_significance(0, 0, 10, 2)
    assert res["is_significant"] is False
    assert "Insufficient" in res["conclusion"]


def test_two_sample_t_test_significant_difference():
    cand_latencies = [200.0, 210.0, 195.0, 205.0, 202.0, 198.0]
    base_latencies = [450.0, 470.0, 440.0, 460.0, 455.0, 448.0]
    res = SignificanceTester.test_continuous_metric(cand_latencies, base_latencies, "Latency")
    assert res["is_significant"] is True
    assert res["p_value"] < 0.01
    assert "faster" in res["conclusion"]


def test_two_sample_t_test_insufficient_samples():
    res = SignificanceTester.test_continuous_metric([100.0], [200.0])
    assert res["is_significant"] is False
    assert "Insufficient" in res["conclusion"]
