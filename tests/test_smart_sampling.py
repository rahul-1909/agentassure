"""Unit Tests for Smart Sampling Risk Scorer and Stratified Sampler."""

import pytest
from sqlalchemy.orm import Session
from agentassure.mining.risk_scorer import RiskScorer
from agentassure.mining.stratified_sampler import StratifiedSampler
from agentassure.db.models.conversation import Conversation


def test_risk_scorer_ideal_session():
    # Perfect score, 0 ASR error, 0 loops, no drop, neutral sentiment
    risk = RiskScorer.compute(
        judge_score=1.0,
        asr_error_rate=0.0,
        loop_count=0,
        customer_dropped=False,
        negative_sentiment=0.0,
    )
    assert risk == 0.0


def test_risk_scorer_maximum_failure():
    # Worst case: judge 0.0, 100% ASR error, 3+ loops, customer dropped, 1.0 negative sentiment
    risk = RiskScorer.compute(
        judge_score=0.0,
        asr_error_rate=1.0,
        loop_count=5,
        customer_dropped=True,
        negative_sentiment=1.0,
    )
    assert risk == 1.0


def test_risk_scorer_formula_weights():
    # Test specific weight contributions:
    # low judge score weight is 0.35
    risk_judge = RiskScorer.compute(0.0, 0.0, 0, False, 0.0)
    assert pytest.approx(risk_judge, 0.01) == 0.35

    # ASR error weight is 0.25
    risk_asr = RiskScorer.compute(1.0, 1.0, 0, False, 0.0)
    assert pytest.approx(risk_asr, 0.01) == 0.25

    # Loop count weight is 0.20 (at 3 loops)
    risk_loop = RiskScorer.compute(1.0, 0.0, 3, False, 0.0)
    assert pytest.approx(risk_loop, 0.01) == 0.20

    # Drop-off weight is 0.10
    risk_drop = RiskScorer.compute(1.0, 0.0, 0, True, 0.0)
    assert pytest.approx(risk_drop, 0.01) == 0.10

    # Negative sentiment weight is 0.10
    risk_sent = RiskScorer.compute(1.0, 0.0, 0, False, 1.0)
    assert pytest.approx(risk_sent, 0.01) == 0.10


def test_risk_scorer_boundary_clamping():
    # Negative inputs or extreme numbers should clamp safely without crashing
    risk_low = RiskScorer.compute(-5.0, -1.0, -2, False, -0.5)
    assert risk_low >= 0.0
    risk_high = RiskScorer.compute(10.0, 5.0, 100, True, 10.0)
    assert risk_high <= 1.0


def test_stratified_sampler_partitioning(db_session: Session):
    batch = StratifiedSampler.sample_batch(db_session, target_batch_size=3, latest_version="v2.5.0-rc1")
    assert len(batch) > 0
    strata = [c.sample_stratum for c in batch]
    # Check that sample strata labels are assigned
    assert any(s in ["risk_ranked", "new_version", "edge_case", "random_unbiased"] for s in strata)


def test_stratified_sampler_empty_size(db_session: Session):
    batch = StratifiedSampler.sample_batch(db_session, target_batch_size=0)
    assert batch == []
