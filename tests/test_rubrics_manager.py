"""Unit Tests for RubricsManager and Versioned Rubrics."""

import pytest
from pathlib import Path
from sqlalchemy.orm import Session
from agentassure.qa.rubrics_manager import RubricsManager
from agentassure.config import settings


def test_rubrics_manager_load_active_version():
    rubric = RubricsManager.get_rubric("v1.0")
    assert rubric["version"] == "v1.0"
    assert "categories" in rubric
    assert len(rubric["categories"]) >= 10


def test_rubrics_manager_switch_and_rollback():
    # Switch to v1.1
    RubricsManager.set_active_version("v1.1")
    assert RubricsManager.get_active_version() == "v1.1"

    # Rollback to v1.0
    RubricsManager.set_active_version("v1.0")
    assert RubricsManager.get_active_version() == "v1.0"


def test_rubrics_manager_validate_categories():
    assert RubricsManager.validate_category(
        "Factual Accuracy", "Hallucinated Policy / Product Terms"
    ) is True
    assert RubricsManager.validate_category(
        "Compliance", "Missing Statutory or RBI Disclaimer"
    ) is True
    assert RubricsManager.validate_category("NonExistentCategory", "Foo") is False


def test_rubrics_manager_sync_to_db(db_session: Session):
    RubricsManager.sync_to_db(db_session)
    from sqlalchemy import select
    from agentassure.db.models.rubric import RubricVersion
    records = db_session.scalars(select(RubricVersion)).all()
    assert len(records) >= 2
