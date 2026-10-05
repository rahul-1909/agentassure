"""Unit Tests for AgentAssure Click CLI commands."""

import pytest
from click.testing import CliRunner
from agentassure.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "agentassure" in result.output


def test_cli_init_db(runner):
    result = runner.invoke(cli, ["init-db"])
    assert result.exit_code == 0
    assert "[SUCCESS]" in result.output


def test_cli_run_simulation(runner):
    result = runner.invoke(cli, ["run-simulation", "--persona", "confused_elderly", "--turns", "2"])
    assert result.exit_code == 0
    assert "Simulation Complete" in result.output


def test_cli_run_gate(runner):
    result = runner.invoke(cli, ["run-gate", "--version", "v2.5.0-candidate"])
    assert result.exit_code == 0
    assert "RELEASE GATE DECISION" in result.output


def test_cli_generate_report(runner):
    result = runner.invoke(cli, ["generate-report", "--no-html"])
    assert result.exit_code == 0
    assert "Generated report" in result.output
