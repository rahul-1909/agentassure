"""Data Retention and Privacy Purge Utility.

Enforces compliance rules:
- 60-day archive policy: flags old conversations as archived
- 90-day purge policy: irreversibly strips customer IDs, transcripts, and audio paths
"""

from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from agentassure.config import settings
from agentassure.db.models.conversation import Conversation, Turn


class DataRetentionManager:
    """Automates archival and PII purging according to statutory retention schedules."""

    @classmethod
    def apply_policies(cls, db: Session) -> Dict[str, Any]:
        """Execute archival (60d) and purge (90d) operations across conversations.

        Args:
            db: Database session.

        Returns:
            Dictionary with counts of archived and purged records.
        """
        now = datetime.now(timezone.utc)
        archive_threshold = now - timedelta(days=settings.ARCHIVE_RETENTION_DAYS)
        purge_threshold = now - timedelta(days=settings.PURGE_RETENTION_DAYS)

        # 1. Flag conversations older than 60 days as archived
        archive_stmt = (
            select(Conversation)
            .where(Conversation.created_at <= archive_threshold)
            .where(Conversation.is_archived.is_(False))
        )
        archived_records = db.scalars(archive_stmt).all()
        for conv in archived_records:
            conv.is_archived = True

        # 2. Irreversibly purge PII for conversations older than 90 days
        purge_stmt = (
            select(Conversation)
            .where(Conversation.created_at <= purge_threshold)
            .where(Conversation.is_purged.is_(False))
        )
        purged_records = db.scalars(purge_stmt).all()
        for conv in purged_records:
            conv.is_purged = True
            conv.customer_id = "ANONYMIZED_PURGED_ID"
            conv.audio_url = None

            # Anonymize linked turn transcripts
            for t in conv.turns:
                t.transcript = "[PURGED_COMPLIANCE_90D]"
                t.entities = None

        db.commit()

        return {
            "archived_count": len(archived_records),
            "purged_count": len(purged_records),
            "timestamp": now.isoformat(),
        }
