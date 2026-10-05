# AgentAssure

Intelligent QA automation that converts production failures into CI-gated regression tests for voice and chat AI agents.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://github.com/rahul-1909/agentassure)
[![CI Status](https://img.shields.io/github/actions/workflow/status/rahul-1909/agentassure/ci.yml?branch=main&style=flat-square&logo=github-actions)](https://github.com/rahul-1909/agentassure/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Coverage](https://img.shields.io/badge/Coverage-87%25-brightgreen?style=flat-square)](https://github.com/rahul-1909/agentassure)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](./LICENSE)

---

## The Problem

Every prompt edit, knowledge-base update, or model swap can silently break conversational AI agents. Teams ship changes without measuring whether compliance, objection handling, or financial accuracy regressed. QA findings sit in spreadsheets instead of reaching engineers.

## The Solution

AgentAssure connects QA feedback to CI/CD pipelines by:
- Converting human-verified failures into executable regression tests
- Gating releases on statistical quality thresholds (95% accuracy, compliance, safety)
- Auto-creating engineering tickets with root causes and impact estimates
- Tracking whether fixes actually reduce recurring failure patterns

---

## Key Features

| Feature | Benefit |
| :--- | :--- |
| **Review Workbench** | Audio + transcript sync with keyboard shortcuts; 50% faster annotation |
| **Smart Sampling** | Risk-scored prioritization; reviewers focus on high-impact conversations |
| **Failure-to-Test** | Automate regression test generation from confirmed QA failures |
| **Persona Simulator** | 10+ adversarial personas (haggler, confused, hostile, Hinglish) stress-test agents |
| **Release Gating** | Block deployments if compliance or accuracy drops below 95% |
| **Closed-Loop Ticketing** | Auto-create tickets; track whether fixes reduce failure rates |
| **Governance & Privacy** | Versioned rubrics, reviewer calibration (kappa > 0.80), 90-day PII purge |

---

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, Redis, SQLAlchemy 2.0, Pydantic v2, Celery
- **Frontend:** React 19, TypeScript/JavaScript, Tailwind CSS, wavesurfer.js (audio sync)
- **Testing:** pytest (72 tests, 87% coverage), Locust load tests
- **DevOps:** Docker, Docker Compose, GitHub Actions, Vercel

---

## Architecture

```
[Production Conversations]
         |
[PII Masking Engine]
         |
[Smart Risk Prioritization] ---> [Review Workbench] ---> [QA Annotation]
         |                                                     |
[Audio Waveform Sync]                                [Failure Confirmation]
                                                               |
                                                 [Atomic Test Case Synthesis]
                                                               |
                                                 [Regression Test Suite]
         |                                                     |
[Persona Simulator] -----------------------------------> [Release Gate]
         |                                                     |
[10+ Synthetic Personas]                             [Statistical Tests]
                                                               |
                                                 +-------------+-------------+
                                                 |                           |
                                                 v                           v
                                            [Deploy]                  [Create Tickets]
```

---

## Quick Start

### Docker Compose
```bash
docker compose up --build
# API & UI: http://localhost:8000
# Swagger: http://localhost:8000/docs
# Grafana: http://localhost:3001
```

### Local Development

1. **Clone and install dependencies:**
   ```bash
   git clone https://github.com/rahul-1909/agentassure.git
   cd agentassure
   pip install -r requirements.txt
   ```

2. **Initialize database & enterprise seed data:**
   ```bash
   python -m agentassure.cli.main init-db
   ```

3. **Build frontend assets:**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Launch development server:**
   ```bash
   uvicorn agentassure.api.app:app --reload --port 8000
   ```
   Open your browser at `http://localhost:8000`.

---

## API Endpoints

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/health` | GET | System health and database connectivity |
| `/api/v1/review/session/start/{id}` | POST | Begin or lock conversation review session |
| `/api/v1/review/annotation` | POST | Submit turn annotation and check rater agreement |
| `/api/v1/sampling/queue` | GET | Stratified risk-prioritized conversation queue |
| `/api/v1/test-cases` | GET | List active regression test cases with assertions |
| `/api/v1/audio/{conversation_id}` | GET | Serve or synthesize WAV audio for waveform playback |
| `/api/v1/simulator/run` | POST | Execute multi-turn adversarial persona dialogue |
| `/api/v1/release-gate/evaluate` | POST | Run full regression suite & statistical gate check |
| `/api/v1/tickets` | GET | List auto-created Linear/Jira failure tickets |
| `/api/v1/reports/summary` | GET | Reviewer SLA compliance and inter-rater kappa metrics |

---

## Testing & Quality Coverage

AgentAssure maintains strict automated testing standards with an enforced 85% coverage gate:

```bash
# Execute pytest suite with coverage verification
pytest --cov=agentassure --cov-fail-under=85 tests/

# Execute static analysis & style checks
python -m black --check agentassure tests
python -m isort --check-only agentassure tests
python -m flake8 agentassure tests --max-line-length=120 --ignore=E203,W503,F401,F841,E501,E226
```

**Test Results:** 72 unit/integration tests passing (87% coverage, runtime <15s).

---

## Documentation

- [Architecture & Deployment Topology](./docs/architecture.md)
- [Conversational AI Failure Taxonomy (7+3 Categories)](./docs/taxonomy.md)
- [Developer Setup & CLI Handbook](./DEVELOPMENT.md)
- [Database Schema & Data Dictionary](./docs/data_dictionary.md)

---

## Contributing

We welcome contributions to AgentAssure. Please review [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution workflows and coding standards.

---

## License

This project is licensed under the terms of the [MIT License](./LICENSE).
