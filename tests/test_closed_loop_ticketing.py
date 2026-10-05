"""Unit Tests for Failure Mining and Closed-Loop Ticketing."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentassure.db.models.ticket import FailureCluster, Ticket
from agentassure.mining.failure_clusterer import FailureClusterer
from agentassure.ticketing.jira_linear import TicketingClient


def test_mine_clusters(db_session: Session):
    clusters = FailureClusterer.mine_clusters(db_session)
    assert len(clusters) > 0
    c = clusters[0]
    assert c.frequency >= 1
    assert c.expected_impact_reduction_pct > 0.0
    assert "Pattern:" in c.cluster_name


def test_create_ticket_linear_template(db_session: Session):
    cluster = db_session.scalar(select(FailureCluster))
    ticket = TicketingClient.create_ticket_from_cluster(
        db_session, cluster.id, system_type="linear"
    )
    assert ticket.id is not None
    assert ticket.external_id.startswith("LIN-")
    assert "Failure Pattern:" in ticket.body
    assert "Category:" in ticket.body
    assert "Frequency:" in ticket.body
    assert "Severity:" in ticket.body
    assert "Root Cause:" in ticket.body
    assert "Fix:" in ticket.body
    assert "Expected Impact:" in ticket.body


def test_create_ticket_jira(db_session: Session):
    cluster = db_session.scalar(select(FailureCluster))
    ticket = TicketingClient.create_ticket_from_cluster(db_session, cluster.id, system_type="jira")
    assert ticket.external_id.startswith("JIRA-")


def test_update_ticket_post_release_webhook(db_session: Session):
    cluster = db_session.scalar(select(FailureCluster))
    ticket = TicketingClient.create_ticket_from_cluster(
        db_session, cluster.id, system_type="linear"
    )

    updated = TicketingClient.update_post_release_status(
        db=db_session,
        external_id=ticket.external_id,
        new_status="resolved",
        measured_failure_rate_after=0.2,
    )
    assert updated.status == "resolved"
    assert updated.post_release_verified is True
    assert updated.verified_failure_rate_after == 0.2
