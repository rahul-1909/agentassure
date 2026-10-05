"""Unit Tests for Quality Reporting and Executive Dashboard Generation."""

import pytest
from sqlalchemy.orm import Session

from agentassure.reporting.html_generator import HTMLReportGenerator
from agentassure.reporting.metrics_aggregator import MetricsAggregator


def test_metrics_aggregator(db_session: Session):
    report = MetricsAggregator.generate_report(db_session)
    assert report.total_conversations > 0
    assert report.reviewed_conversations >= 0
    assert report.conversation_coverage_pct >= 0.0
    assert report.review_sla_compliance_pct >= 0.0
    assert report.inter_rater_kappa_overall >= 0.0
    assert len(report.failure_distribution_by_category) > 0


def test_html_report_generator(db_session: Session):
    report = MetricsAggregator.generate_report(db_session)
    html = HTMLReportGenerator.render(report)
    assert "<!DOCTYPE html>" in html
    assert "AgentAssure QA & Closed-Loop Quality Report" in html
    assert f"{report.active_rubric_version}" in html
    assert "Closed-Loop Fix Impact" in html
