# AgentAssure System Architecture

## 1. High-Level Architecture Overview

AgentAssure is a three-tier, cloud-native Human-in-the-Loop QA, regression testing, and closed-loop improvement platform for enterprise conversational AI agents. It bridges the critical divide between customer support QA findings and production release engineering.

```mermaid
flowchart TD
    subgraph ClientLayer["Tier 1: Client Applications"]
        UI["React 19 Frontend<br/>(wavesurfer.js, Keyboard Shortcuts)"]
        CLI["AgentAssure CLI<br/>(Local QA & CI Gates)"]
        GH["GitHub Actions CI<br/>(PR Gate Checks)"]
    end

    subgraph APILayer["Tier 2: Application Core (FastAPI)"]
        GW["FastAPI Gateway<br/>(SlowAPI Limiter, JWT Auth, RBAC)"]
        
        subgraph Subsystems["Core Engine Subsystems"]
            RW["Review Workbench<br/>(Double-Review & Adjudication)"]
            SS["Smart Sampling<br/>(5-Factor Risk Scorer & 65/20/15 Strata)"]
            F2T["Failure-to-Test Pipeline<br/>(Atomic Assertion Synthesis)"]
            SIM["Persona Simulator<br/>(10+ Adversarial Personas & Voice Layer)"]
            RG["Release Gate Evaluator<br/>(Chi-Square & Two-Sample t-Test)"]
            CLT["Closed-Loop Ticketing<br/>(Linear / Jira Dispatch & Post-Deploy Verifier)"]
            GOV["Governance & Reporting<br/>(Versioned YAML Rubrics & Cohen's Kappa)"]
            PII["PII Redaction Engine<br/>(Aadhaar, PAN, Phone, Email, Card)"]
        end
    end

    subgraph StorageLayer["Tier 3: Persistence & Async Workers"]
        PG[("PostgreSQL 16 / SQLite<br/>(Relational State & Audit Trail)")]
        RD[("Redis 7<br/>(Session Cache & Celery Broker)")]
        CEL["Celery Async Worker<br/>(Ticket Dispatch & Heavy Mining)"]
    end

    UI -->|HTTP / JSON REST| GW
    CLI -->|Local Execution & REST| GW
    GH -->|CLI / Webhook API| GW
    
    GW --> Subsystems
    Subsystems --> PII
    Subsystems --> PG
    Subsystems --> RD
    RD --> CEL
    CEL --> PG
```

---

## 2. End-to-End Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer / Bot User
    participant Ingest as Production Telephony / Bot
    participant Scorer as Smart Sampling Scorer
    participant DB as PostgreSQL Database
    actor Reviewer as QA Reviewer
    participant Workbench as Review Workbench
    participant Runner as Failure-to-Test Pipeline
    participant Gate as CI Release Gate
    actor Dev as Engineering Team

    Customer->>Ingest: Multi-turn voice call / chat session
    Ingest->>Scorer: Post telemetry (judge_score, asr_err, loops, drop, sentiment)
    Scorer->>Scorer: Mask PII (Aadhaar, PAN, Phone, Email)
    Scorer->>Scorer: Compute Risk Score = 0.35(1-Judge) + 0.25(ASR) + 0.20(Loops) + 0.10(Drop) + 0.10(Sent)
    Scorer->>DB: Persist prioritized conversation
    
    Reviewer->>Workbench: Pull top risk batch (65% risk, 20% new ver, 15% edge)
    Reviewer->>Workbench: Inspect waveform + transcript (A to approve, D to tag defect)
    Reviewer->>DB: Submit turn annotation with root cause & fix recommendation
    
    DB->>Runner: Confirmed failure triggers atomic test synthesis
    Runner->>DB: Persist RegressionTestCase with structured assertions
    
    Dev->>Gate: Commit prompt / model update on PR
    Gate->>DB: Fetch active regression test cases + run persona simulator
    Gate->>Gate: Execute assertions, calculate category pass rates
    Gate->>Gate: Run Chi-Square (categorical) & t-test (latency) vs. baseline
    
    alt Critical category pass rate < 95%
        Gate-->>Dev: 🔴 MERGE BLOCKED (Fail-fast report with p-values)
    else All gates satisfied
        Gate-->>Dev: 🟢 RELEASE AUTHORIZED
    end
```

---

## 3. Deployment Topology

AgentAssure is containerized via a multi-stage Docker build producing a lean runtime (<300MB). In production, it deploys via Kubernetes or Docker Compose:

1. **`agentassure-api`**: FastAPI ASGI container running Uvicorn workers behind an ingress load balancer.
2. **`agentassure-postgres`**: PostgreSQL 16 cluster with connection pooling (`pool_size=10`, `max_overflow=20`) and read-replica support.
3. **`agentassure-redis`**: In-memory broker for Celery async tasks and rate-limiting counters.
4. **`agentassure-worker`**: Celery worker instance offloading batch cluster mining and ticket creation.
5. **`agentassure-grafana`**: Operational observability dashboard monitoring queue latency, reviewer turnaround SLA, and test pass rate trends.

---

## 4. Failure Scenarios and Resiliency

| Failure Scenario | Mitigation Strategy | Recovery Time Objective (RTO) |
| :--- | :--- | :--- |
| **Database Network Partition** | Connection pool with pre-ping validation (`pool_pre_ping=True`) and exponential backoff retry. | < 5 seconds |
| **Redis Broker Failure** | Automatic fallback to in-memory eager task execution (`CELERY_TASK_ALWAYS_EAGER=True`). | Instantaneous (0s) |
| **API Rate Spikes / Abuse** | SlowAPI IP-based rate limiting (100 req/min default) returning HTTP 429. | Instantaneous (0s) |
| **Dual Reviewer Disagreement** | Automated conflict detection routing to supervisor adjudication queue with majority resolution. | Handled in SLA |
| **Regulatory PII Exposure** | Deterministic pre-storage regex redaction for Aadhaar, PAN, phone numbers, and payment cards. | Zero-leakage guarantee |
