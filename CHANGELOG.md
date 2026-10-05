# Changelog

All notable changes to the AgentAssure platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-05

### Added
- **Core Architecture**:
  - FastAPI REST API backend with SQLAlchemy 2.0 ORM and Pydantic v2 schemas.
  - Multi-stage Docker containerization (<300MB) with Celery and Redis workers.
  - SlowAPI IP-based rate limiting and JWT RBAC authorization (`admin`, `qa_manager`, `reviewer`, `viewer`).
- **Review Workbench**:
  - React 19 interface with wavesurfer.js audio waveform visualization.
  - Synchronized turn-by-turn transcript highlighting and click-to-seek.
  - Keyboard shortcuts: `Tab` for turn navigation, `A` for compliant approval, `D` for defect tagging, and `Enter` for confirmation.
  - Dual-review disagreement detection and supervisor adjudication queue.
  - Reviewer turnaround stopwatch timer and SLA metric tracking.
- **Smart Sampling Engine**:
  - 5-factor risk scoring formula: `0.35(1-Judge) + 0.25(ASR) + 0.20(Loops) + 0.10(Drop) + 0.10(Sentiment)`.
  - Stratified random sampling maintaining 65% risk-ranked, 20% new agent versions, and 15% edge cases.
- **Failure-to-Test Pipeline**:
  - Atomic conversion of confirmed failures into executable regression test cases.
  - Structured assertion engine supporting `must_contain`, `must_not_contain`, `regex_match`, `compliance_check`, `no_hallucination`, and `latency_under`.
- **Persona Simulator**:
  - 10+ synthetic customer personalities (price-sensitive haggler, confused elderly, hostile debtor, Hinglish student, rapid interrupter, etc.).
  - Pluggable voice simulation with acoustic ASR jitter and phonetic homophone corruption.
  - Automated edge-case defect surfacing and one-click regression test generation.
- **CI/CD Release Gating**:
  - Automated GitHub Actions release gating workflow.
  - Fail-fast threshold enforcement on critical categories (>95% pass rate for Compliance and Factual Accuracy).
  - Hypothesis testing via Chi-Square (categorical pass rate) and Welch's two-sample t-test (turn latency).
  - Automated GitHub PR markdown comment generation.
- **Closed-Loop Ticketing**:
  - Automated mining and aggregation of QA failures into named clusters.
  - Standardized Linear and Jira issue creation.
  - Inbound webhook receiver to verify post-release defect drop.
- **Quality Reporting & Governance**:
  - Versioned YAML rubrics (`v1.0`, `v1.1`) with dynamic rollback capability.
  - Reviewer calibration audits with Cohen's kappa reliability calculations (&kappa; > 0.80 target).
  - Standalone client-ready HTML dashboard generation.
- **Data Privacy & Security**:
  - End-to-end PII masking for Indian Aadhaar, PAN, phone numbers, emails, and payment cards.
  - 60-day archive and 90-day PII purge data retention policies.
  - Immutable database audit trail for sensitive actions.
- **Testing & Quality Assurance**:
  - 70 unit and integration tests passing with 87% code coverage.
  - Locust load testing suite simulating 50 concurrent reviewers and 1,000 conversations/hour.
