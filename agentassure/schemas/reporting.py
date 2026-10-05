"""Pydantic v2 Schemas for Quality Reporting, Rubrics, and Governance."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class RubricVersionSchema(BaseModel):
    """Rubric version configuration schema."""

    id: str
    version_tag: str
    description: str
    content_yaml: str
    is_active: bool

    model_config = {"from_attributes": True}


class CalibrationResponse(BaseModel):
    """Reviewer calibration and Cohen's kappa score schema."""

    id: str
    session_name: str
    reviewer_id: str
    gold_standard_count: int
    agreed_count: int
    kappa_score: float
    status: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class QualityReportResponse(BaseModel):
    """Comprehensive weekly/monthly executive quality scorecard."""

    report_date: str
    total_conversations: int
    reviewed_conversations: int
    conversation_coverage_pct: float
    review_sla_compliance_pct: float
    inter_rater_kappa_overall: float
    active_rubric_version: str
    failure_distribution_by_category: Dict[str, int]
    top_failure_patterns: List[Dict[str, Any]]
    before_after_fix_impact: List[Dict[str, Any]]
    reviewer_calibrations: List[CalibrationResponse]
