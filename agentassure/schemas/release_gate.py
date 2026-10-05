"""Pydantic v2 Schemas for Release Gating and Statistical Significance."""

from typing import List, Optional

from pydantic import BaseModel, Field


class GateRunRequest(BaseModel):
    """Payload to trigger an automated release gating evaluation."""

    agent_version: str = Field(..., description="Target release candidate version string")
    commit_hash: Optional[str] = Field(default="head-sha", description="Git commit hash")
    baseline_version: str = Field(
        default="v2.4.0", description="Production baseline to compare against"
    )
    include_simulator: bool = True
    dry_run: bool = False


class CategoryResultSchema(BaseModel):
    """Quality metrics for a single taxonomy category under release gating."""

    category: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    is_critical: bool
    threshold: float
    status: str  # PASSED, BLOCKED


class StatisticalSignificanceSchema(BaseModel):
    """Result of hypothesis testing between candidate and baseline metrics."""

    metric_name: str
    test_type: str  # Chi-square or Two-sample t-test
    statistic: float
    p_value: float
    is_significant: bool
    conclusion: str


class GateRunResponse(BaseModel):
    """Comprehensive release gate decision report."""

    gate_id: str
    status: str  # PASSED or BLOCKED
    agent_version: str
    commit_hash: Optional[str]
    overall_pass_rate: float
    baseline_pass_rate: float
    delta_pass_rate: float
    critical_categories_passed: bool
    blocked_categories: List[str]
    category_breakdown: List[CategoryResultSchema]
    statistical_tests: List[StatisticalSignificanceSchema]
    markdown_summary: str
