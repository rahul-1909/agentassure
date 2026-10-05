"""End-to-End Integration Tests for FastAPI REST Endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_api_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data


def test_api_metrics(client: TestClient):
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "conversations_total" in data
    assert "regression_tests_active" in data


def test_api_auth_login_and_me(client: TestClient):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "admin"


def test_api_sampling_queue(client: TestClient, auth_headers):
    res = client.get("/api/v1/sampling/queue", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data


def test_api_sampling_sample_batch(client: TestClient, auth_headers):
    res = client.post("/api/v1/sampling/sample?target_batch_size=2", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_api_sampling_ingest_with_pii_masking(client: TestClient, auth_headers):
    payload = {
        "customer_id": "+91 9876543210",
        "channel": "voice",
        "agent_version": "v2.5.0-rc1",
        "duration_seconds": 12.0,
        "language": "en",
        "judge_score": 0.5,
        "asr_error_rate": 0.1,
        "loop_count": 1,
        "customer_dropped": False,
        "negative_sentiment": 0.2,
        "turns": [
            {
                "turn_index": 0,
                "speaker": "user",
                "transcript": "My PAN is ABCDE1234F and phone is 9876543210",
                "audio_start_time": 0.0,
                "audio_end_time": 4.0,
            }
        ],
    }
    res = client.post("/api/v1/sampling/ingest", json=payload, headers=auth_headers)
    assert res.status_code == 201
    conv = res.json()
    assert conv["customer_id"] == "[MASKED_PHONE]"
    assert "[MASKED_PAN]" in conv["turns"][0]["transcript"]


def test_api_review_workflow_and_annotation(client: TestClient, auth_headers):
    # Fetch queue
    queue_res = client.get("/api/v1/sampling/queue", headers=auth_headers)
    items = queue_res.json()["items"]
    assert len(items) > 0
    conv_id = items[0]["id"]

    # Start session
    start_res = client.post(f"/api/v1/review/session/start/{conv_id}", headers=auth_headers)
    assert start_res.status_code == 200

    # Get conversation details
    detail_res = client.get(f"/api/v1/review/conversation/{conv_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    conv_detail = detail_res.json()
    assert len(conv_detail["turns"]) > 0
    turn_id = conv_detail["turns"][0]["id"]

    # Submit annotation
    annot_payload = {
        "conversation_id": conv_id,
        "turn_id": turn_id,
        "failure_category_l1": "Compliance",
        "failure_category_l2": "Missing Statutory or RBI Disclaimer",
        "severity": "S1",
        "root_cause_notes": "Disclaimer missing on interest rate quote.",
        "fix_type": "prompt_patch",
        "review_duration_seconds": 22.0,
        "is_confirmed_failure": True,
    }
    annot_res = client.post("/api/v1/review/annotation", json=annot_payload, headers=auth_headers)
    assert annot_res.status_code == 201
    annotation = annot_res.json()
    assert annotation["id"] is not None

    # Convert failure to test
    convert_res = client.post(f"/api/v1/failures/convert/{annotation['id']}", headers=auth_headers)
    assert convert_res.status_code == 201
    test_case = convert_res.json()
    assert test_case["category_l1"] == "Compliance"


def test_api_persona_simulator(client: TestClient, auth_headers):
    # List personas
    list_res = client.get("/api/v1/simulator/personas", headers=auth_headers)
    assert list_res.status_code == 200
    personas = list_res.json()
    assert len(personas) >= 10

    # Run simulation
    sim_res = client.post(
        "/api/v1/simulator/run",
        json={"persona_key": "confused_elderly", "agent_version": "v2.5.0-rc1", "max_turns": 2},
        headers=auth_headers,
    )
    assert sim_res.status_code == 201
    sim_data = sim_res.json()
    assert sim_data["total_turns"] > 0


def test_api_release_gate_evaluate(client: TestClient, auth_headers):
    gate_res = client.post(
        "/api/v1/release-gate/evaluate",
        json={"agent_version": "v2.5.0-rc1", "baseline_version": "v2.4.0"},
        headers=auth_headers,
    )
    assert gate_res.status_code == 200
    report = gate_res.json()
    assert report["status"] in ["PASSED", "BLOCKED"]
    assert "category_breakdown" in report


def test_api_closed_loop_ticketing(client: TestClient, auth_headers):
    # Cluster failures
    cluster_res = client.post("/api/v1/tickets/cluster", headers=auth_headers)
    assert cluster_res.status_code == 200
    clusters = cluster_res.json()
    assert len(clusters) > 0
    target_cluster = clusters[0]

    # Create Ticket
    ticket_res = client.post(
        "/api/v1/tickets/create",
        json={"cluster_id": target_cluster["id"], "system_type": "linear"},
        headers=auth_headers,
    )
    assert ticket_res.status_code == 201
    ticket = ticket_res.json()
    assert ticket["external_id"].startswith("LIN-")

    # Inbound Webhook
    webhook_res = client.post(
        "/api/v1/tickets/webhook",
        json={"external_id": ticket["external_id"], "new_status": "resolved"},
    )
    assert webhook_res.status_code == 200
    assert webhook_res.json()["status"] == "resolved"


def test_api_quality_reports_and_rubrics(client: TestClient, auth_headers):
    # Summary
    sum_res = client.get("/api/v1/reports/summary", headers=auth_headers)
    assert sum_res.status_code == 200
    assert "review_sla_compliance_pct" in sum_res.json()

    # HTML
    html_res = client.get("/api/v1/reports/html", headers=auth_headers)
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers["content-type"]

    # Rubrics
    rub_res = client.get("/api/v1/reports/rubrics", headers=auth_headers)
    assert rub_res.status_code == 200
    assert len(rub_res.json()) >= 1

    # Audit Logs
    audit_res = client.get("/api/v1/reports/audit-logs", headers=auth_headers)
    assert audit_res.status_code == 200
    assert isinstance(audit_res.json(), list)
