"""Asynchronous Celery Worker Tasks.

Offloads long-running failure-to-test conversions, ticket dispatches,
and periodic report generation.
"""

from agentassure.db.session import SessionLocal
from agentassure.evaluation.regression_runner import RegressionRunner
from agentassure.reporting.metrics_aggregator import MetricsAggregator
from agentassure.tasks.celery_app import celery_app
from agentassure.ticketing.jira_linear import TicketingClient
from agentassure.utils.logging import get_logger

logger = get_logger("celery_tasks")


@celery_app.task(name="agentassure.tasks.convert_failure_to_test")
def async_convert_failure_to_test(annotation_id: str) -> str:
    """Async task to convert a confirmed QA failure into a regression test case."""
    logger.info(f"Async converting failure annotation: {annotation_id}")
    db = SessionLocal()
    try:
        test_case = RegressionRunner.convert_failure_to_test(db, annotation_id)
        return test_case.id
    finally:
        db.close()


@celery_app.task(name="agentassure.tasks.create_cluster_ticket")
def async_create_cluster_ticket(cluster_id: str, system_type: str = "linear") -> str:
    """Async task to format and dispatch engineering issue ticket."""
    logger.info(f"Async creating {system_type} ticket for cluster: {cluster_id}")
    db = SessionLocal()
    try:
        ticket = TicketingClient.create_ticket_from_cluster(db, cluster_id, system_type)
        return ticket.external_id
    finally:
        db.close()


@celery_app.task(name="agentassure.tasks.generate_weekly_report")
def async_generate_weekly_report() -> dict:
    """Async periodic task to aggregate and log weekly scorecard metrics."""
    logger.info("Async generating weekly quality report...")
    db = SessionLocal()
    try:
        report = MetricsAggregator.generate_report(db)
        return report.model_dump()
    finally:
        db.close()
