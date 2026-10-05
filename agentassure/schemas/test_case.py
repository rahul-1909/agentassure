"""Pydantic v2 Schemas for Regression Test Cases and Assertions."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AssertionRuleSchema(BaseModel):
    """Specification for an executable assertion on agent output."""

    assertion_type: str = Field(
        ...,
        description="Assertion operator: must_contain, must_not_contain, regex_match, compliance_check, latency_under",
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration parameters (e.g. keywords, pattern, forbidden_terms, max_ms)",
    )
    description: Optional[str] = None


class TestCaseCreate(BaseModel):
    """Payload to create or convert a failure into a regression test case."""

    source_conversation_id: Optional[str] = None
    source_turn_id: Optional[str] = None
    cluster_id: Optional[str] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    category_l1: str
    category_l2: str
    severity: str = "S2"
    language: str = "en"
    conversation_context: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Historical dialogue turns preceding the evaluation turn",
    )
    expected_behavior: str = Field(..., description="Target compliant response or assertion rule")
    actual_behavior: str = Field(..., description="Observed agent failure")
    fix_suggestion: str = Field(..., description="Prompt patch, KB entry, tool retry, or ASR boost")
    assertion_rules: List[AssertionRuleSchema] = Field(default_factory=list)


class TestCaseResponse(TestCaseCreate):
    """Regression test case response schema."""

    id: str
    is_active: bool

    model_config = {"from_attributes": True}


class TestCaseListResponse(BaseModel):
    """Paginated list of regression test cases."""

    items: List[TestCaseResponse]
    total: int


class TestRunResultSchema(BaseModel):
    """Evaluation result of a test case against an agent response."""

    id: str
    test_case_id: str
    run_id: str
    commit_hash: Optional[str] = None
    agent_version: str
    passed: bool
    response_text: str
    latency_ms: float
    failure_reason: Optional[str] = None

    model_config = {"from_attributes": True}
