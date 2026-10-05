"""AgentAssure Command Line Interface (CLI).

Local engineering tools for:
- Converting failures to regression test cases
- Running adversarial synthetic persona simulations
- Evaluating CI/CD release gates with statistical testing
- Triggering stratified sampling
- Exporting client-ready quality dashboards
"""

import sys
import click
from pathlib import Path

from agentassure.db.session import init_db as db_init, SessionLocal
from agentassure.db.seed_data import seed_database
from agentassure.evaluation.regression_runner import RegressionRunner
from agentassure.evaluation.gate_evaluator import GateEvaluator
from agentassure.mining.stratified_sampler import StratifiedSampler
from agentassure.simulation.simulator_engine import SimulatorEngine
from agentassure.reporting.metrics_aggregator import MetricsAggregator
from agentassure.reporting.html_generator import HTMLReportGenerator
from agentassure.schemas.release_gate import GateRunRequest
from agentassure.schemas.persona import SimulationRunRequest


@click.group()
@click.version_option(version="1.0.0", prog_name="agentassure")
def cli():
    """AgentAssure CLI: Human-in-the-Loop QA & Regression Testing Platform."""
    pass


@cli.command("init-db")
@click.option("--seed/--no-seed", default=True, help="Seed database with sample data and rubrics.")
def init_database(seed: bool):
    """Initialize database tables and initial configurations."""
    click.echo("Initializing AgentAssure database tables...")
    db_init()
    if seed:
        click.echo("Seeding mock conversations, personas, and rubrics...")
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    click.secho("[SUCCESS] Database successfully initialized!", fg="green")


@cli.command("convert-failure")
@click.option("--annotation-id", required=True, help="Confirmed QA failure annotation ID.")
@click.option("--title", default=None, help="Custom title for the regression test case.")
def convert_failure(annotation_id: str, title: str):
    """Atomically convert a confirmed failure annotation into a regression test case."""
    db = SessionLocal()
    try:
        test_case = RegressionRunner.convert_failure_to_test(db, annotation_id, title)
        click.secho(f"[SUCCESS] Created Regression Test Case: {test_case.id}", fg="green")
        click.echo(f"Title: {test_case.title}")
        click.echo(f"Category: {test_case.category_l1} -> {test_case.category_l2}")
        click.echo(f"Severity: {test_case.severity}")
    except Exception as e:
        click.secho(f"[ERROR] Converting failure: {e}", fg="red")
        sys.exit(1)
    finally:
        db.close()


@cli.command("run-simulation")
@click.option("--persona", "persona_key", default="price_sensitive_haggler", help="Persona profile key.")
@click.option("--version", "agent_version", default="v2.5.0-candidate", help="Target agent version.")
@click.option("--turns", default=4, help="Maximum dialogue turns.")
@click.option("--voice", is_flag=True, default=False, help="Enable acoustic ASR jitter simulation.")
def run_simulation(persona_key: str, agent_version: str, turns: int, voice: bool):
    """Run multi-turn synthetic customer dialogue simulation against candidate agent."""
    db = SessionLocal()
    try:
        req = SimulationRunRequest(
            persona_key=persona_key,
            agent_version=agent_version,
            max_turns=turns,
            voice_mode=voice,
        )
        sim_run = SimulatorEngine.run_simulation(db, req)
        status_color = "red" if sim_run.surfaced_failure else "green"
        click.secho(f"\nSimulation Complete (Run ID: {sim_run.id})", fg="cyan", bold=True)
        click.echo(f"Persona: {persona_key} | Agent Version: {agent_version}")
        click.echo(f"Total Turns: {sim_run.total_turns} | Avg Latency: {sim_run.latency_avg_ms:.1f}ms")
        click.secho(
            f"Surfaced Failure: {sim_run.surfaced_failure} (Category: {sim_run.failure_category or 'None'})",
            fg=status_color,
            bold=True,
        )

        click.echo("\n--- Dialogue Transcript ---")
        for turn in sim_run.transcript_log:
            speaker = turn["speaker"].upper()
            text = turn["text"]
            click.echo(f"[{speaker}]: {text}")
    except Exception as e:
        click.secho(f"[ERROR] Simulation failed: {e}", fg="red")
        sys.exit(1)
    finally:
        db.close()


@cli.command("run-gate")
@click.option("--version", "agent_version", default="v2.5.0-candidate", help="Candidate release version.")
@click.option("--baseline", default="v2.4.0", help="Production baseline version.")
@click.option("--commit", "commit_hash", default="local-head", help="Commit hash.")
def run_release_gate(agent_version: str, baseline: str, commit_hash: str):
    """Evaluate full regression suite, conduct statistical significance tests, and gate release."""
    db = SessionLocal()
    try:
        req = GateRunRequest(
            agent_version=agent_version,
            baseline_version=baseline,
            commit_hash=commit_hash,
        )
        report = GateEvaluator.evaluate_gate(db, req)

        gate_color = "green" if report.status == "PASSED" else "red"
        click.secho(f"\n==========================================", fg=gate_color)
        click.secho(f"RELEASE GATE DECISION: {report.status}", fg=gate_color, bold=True)
        click.secho(f"==========================================", fg=gate_color)
        click.echo(f"Candidate: {report.agent_version} | Baseline: {report.baseline_pass_rate*100:.1f}%")
        click.echo(f"Overall Pass Rate: {report.overall_pass_rate*100:.1f}% (Delta: {report.delta_pass_rate*100:+.1f}%)")

        if report.blocked_categories:
            click.secho(f"[ALERT] BLOCKED CATEGORIES: {', '.join(report.blocked_categories)}", fg="red", bold=True)
        else:
            click.secho("[SUCCESS] All critical category thresholds (>95%) satisfied!", fg="green")

        click.echo("\n--- Category Breakdown ---")
        for c in report.category_breakdown:
            c_color = "green" if c.status == "PASSED" else "red"
            crit_badge = "[CRITICAL]" if c.is_critical else "[STANDARD]"
            click.secho(
                f"{c.category:<30} {crit_badge:<11} {c.passed_tests}/{c.total_tests} ({c.pass_rate*100:.1f}%) -> {c.status}",
                fg=c_color,
            )

        click.echo("\n--- Statistical Significance ---")
        for s in report.statistical_tests:
            click.echo(f"* {s.metric_name} ({s.test_type}): {s.conclusion}")

        if report.status == "BLOCKED":
            sys.exit(1)
    except Exception as e:
        click.secho(f"[ERROR] Gate execution error: {e}", fg="red")
        sys.exit(1)
    finally:
        db.close()


@cli.command("generate-report")
@click.option("--html/--no-html", default=True, help="Render HTML dashboard file.")
@click.option("--output", default="quality_report.html", help="Output file path.")
def generate_report(html: bool, output: str):
    """Generate executive quality report and SLA compliance dashboard."""
    db = SessionLocal()
    try:
        report = MetricsAggregator.generate_report(db)
        click.echo(f"Generated report for {report.report_date}")
        click.echo(f"Reviewed: {report.reviewed_conversations}/{report.total_conversations} ({report.conversation_coverage_pct}%)")
        click.echo(f"SLA Compliance: {report.review_sla_compliance_pct}% | Inter-Rater Kappa: {report.inter_rater_kappa_overall:.2f}")

        if html:
            html_text = HTMLReportGenerator.render(report)
            out_path = Path(output)
            out_path.write_text(html_text, encoding="utf-8")
            click.secho(f"[SUCCESS] HTML Dashboard written to: {out_path.resolve()}", fg="green")
    finally:
        db.close()


def main():
    """CLI entrypoint function."""
    cli()


if __name__ == "__main__":
    main()
