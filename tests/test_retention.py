"""Unit Tests for Data Retention and PII Purge Policies."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentassure.db.models.conversation import Conversation, Turn
from agentassure.utils.retention import DataRetentionManager


def test_retention_policy_archival_and_purge(db_session: Session):
    # Create an old conversation (>95 days old)
    old_time = datetime.now(timezone.utc) - timedelta(days=100)
    conv = Conversation(
        customer_id="9876543210-CUST",
        agent_version="v1.0.0",
        created_at=old_time,
        updated_at=old_time,
        audio_url="https://audio.example.com/recording.wav",
        is_archived=False,
        is_purged=False,
    )
    db_session.add(conv)
    db_session.flush()

    turn = Turn(
        conversation_id=conv.id,
        turn_index=0,
        speaker="user",
        transcript="My secret Aadhaar is 4921 8832 9012.",
        created_at=old_time,
    )
    db_session.add(turn)
    db_session.commit()

    # Apply policies
    res = DataRetentionManager.apply_policies(db_session)
    assert res["archived_count"] >= 1
    assert res["purged_count"] >= 1

    # Verify purge
    db_session.refresh(conv)
    db_session.refresh(turn)
    assert conv.is_archived is True
    assert conv.is_purged is True
    assert conv.customer_id == "ANONYMIZED_PURGED_ID"
    assert conv.audio_url is None
    assert turn.transcript == "[PURGED_COMPLIANCE_90D]"
