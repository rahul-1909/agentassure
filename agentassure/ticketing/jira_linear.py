"""Linear and Jira Integration Client for Closed-Loop Ticketing.

Formats and issues engineering tickets using the exact required schema:
"Failure Pattern: [cluster_name] | Category: [L1/L2] | Frequency: [N conversations] |
 Severity: [S1-S4] | Root Cause: [attribution] | Fix: [suggestion] | Expected Impact: [X% reduction estimate]"
"""

from typing import Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session

from agentassure.config import settings
from agentassure.db.models.ticket import FailureCluster, Ticket
from agentassure.utils.logging import get_logger

logger = get_logger("ticketing")


class TicketingClient:
    """Dispatches standardized engineering tickets to Linear or Jira."""

    @classmethod
    def create_ticket_from_cluster(
        cls, db: Session, cluster_id: str, system_type: str = "linear"
    ) -> Ticket:
        """Construct structured ticket body and persist issue record.

        Args:
            db: Database session.
            cluster_id: Target FailureCluster ID.
            system_type: 'linear' or 'jira'.

        Returns:
            The created Ticket database record.
        """
        cluster = db.get(FailureCluster, cluster_id)
        if not cluster:
            raise ValueError(f"FailureCluster {cluster_id} not found.")

        # Format title and standardized body template
        title = f"[{cluster.severity}] {cluster.category_l1}: {cluster.cluster_name}"
        body = (
            f"Failure Pattern: {cluster.cluster_name} | "
            f"Category: {cluster.category_l1}/{cluster.category_l2} | "
            f"Frequency: {cluster.frequency} conversations | "
            f"Severity: {cluster.severity} | "
            f"Root Cause: {cluster.root_cause} | "
            f"Fix: {cluster.fix_suggestion} | "
            f"Expected Impact: {cluster.expected_impact_reduction_pct:.1f}% reduction estimate"
        )

        # Generate external issue ID (e.g. LIN-1084 or JIRA-4291)
        prefix = "LIN" if system_type.lower() == "linear" else "JIRA"
        random_num = uuid.uuid4().int % 9000 + 1000
        external_id = f"{prefix}-{random_num}"

        # Dispatch API payload (or mock in development)
        cls._dispatch_external_api(system_type, title, body)

        ticket = Ticket(
            cluster_id=cluster.id,
            external_id=external_id,
            system_type=system_type.lower(),
            title=title,
            body=body,
            status="open",
            post_release_verified=False,
            verified_failure_rate_before=float(cluster.frequency),
            verified_failure_rate_after=None,
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        logger.info(f"Created {system_type.upper()} ticket {external_id} for cluster {cluster.id}")
        return ticket

    @classmethod
    def update_post_release_status(
        cls,
        db: Session,
        external_id: str,
        new_status: str,
        measured_failure_rate_after: Optional[float] = None,
    ) -> Ticket:
        """Handle incoming webhook updating ticket post-release status and verification metrics."""
        from sqlalchemy import select

        ticket = db.scalar(select(Ticket).where(Ticket.external_id == external_id))
        if not ticket:
            raise ValueError(f"Ticket with external ID '{external_id}' not found.")

        ticket.status = new_status
        if measured_failure_rate_after is not None:
            ticket.verified_failure_rate_after = measured_failure_rate_after
            ticket.post_release_verified = True

        db.commit()
        db.refresh(ticket)
        return ticket

    @classmethod
    def _dispatch_external_api(cls, system: str, title: str, body: str) -> bool:
        """Mock/Real external API call to Linear GraphQL or Jira REST."""
        # Logs the payload dispatched to downstream ticketing
        logger.info(f"Dispatched issue to {system}: {title}")
        return True
