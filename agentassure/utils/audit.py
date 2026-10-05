"""Audit Logging Utility for Security and Regulatory Compliance."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from agentassure.db.models.user import AuditLog


class AuditLogger:
    """Records immutable audit trail entries in the database."""

    @classmethod
    def log_action(
        cls,
        db: Session,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create and commit an audit log entry.

        Args:
            db: Database session.
            action: Action verb (e.g., 'submit_annotation', 'trigger_release_gate').
            entity_type: Name of affected entity.
            entity_id: Optional ID of affected entity.
            user_id: User who initiated the action.
            ip_address: Client IP address.
            details: Contextual metadata dictionary.

        Returns:
            The created AuditLog instance.
        """
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            ip_address=ip_address,
            details=details or {},
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
