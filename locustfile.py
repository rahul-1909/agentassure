"""Locust Load Testing Suite for AgentAssure.

Simulates:
- 50 concurrent QA reviewers operating on the review workbench
- High-throughput production telemetry ingestion (1000+ conversations/hour)
"""

from locust import HttpUser, task, between
import random
import uuid


class ReviewerUser(HttpUser):
    """Simulates active QA reviewers navigating workbench and submitting annotations."""

    wait_time = between(1, 3)

    def on_start(self):
        """Authenticate user on test startup."""
        res = self.client.post(
            "/api/v1/auth/login",
            json={"username": "reviewer_alice", "password": "password123"},
        )
        if res.status_code == 200:
            token = res.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(3)
    def view_prioritized_queue(self):
        """Fetch prioritized smart sampling review queue."""
        self.client.get(
            "/api/v1/sampling/queue?page=1&page_size=20",
            headers=self.headers,
            name="/api/v1/sampling/queue",
        )

    @task(2)
    def review_conversation_session(self):
        """Fetch conversation details and audio metadata."""
        # Grab queue first to obtain an ID
        res = self.client.get("/api/v1/sampling/queue?page=1&page_size=5", headers=self.headers)
        if res.status_code == 200:
            items = res.json().get("items", [])
            if items:
                conv_id = random.choice(items)["id"]
                self.client.get(
                    f"/api/v1/review/conversation/{conv_id}",
                    headers=self.headers,
                    name="/api/v1/review/conversation/[id]",
                )

    @task(1)
    def check_disagreement_queue(self):
        """Check double-review adjudication cases."""
        self.client.get(
            "/api/v1/review/disagreements",
            headers=self.headers,
            name="/api/v1/review/disagreements",
        )


class ProductionIngestionUser(HttpUser):
    """Simulates production telephony/chat ingestion pushing 1000+ conversations/hour."""

    wait_time = between(0.1, 0.5)

    @task
    def ingest_live_call(self):
        """Ingest production conversation with real-time PII masking and risk calculation."""
        cust_id = f"+91 {random.randint(6000000000, 9999999999)}"
        payload = {
            "customer_id": cust_id,
            "channel": random.choice(["voice", "chat"]),
            "agent_version": "v2.5.0-candidate",
            "duration_seconds": random.uniform(15.0, 180.0),
            "language": random.choice(["en", "hi", "hinglish"]),
            "judge_score": random.uniform(0.3, 0.99),
            "asr_error_rate": random.uniform(0.01, 0.35),
            "loop_count": random.choice([0, 0, 1, 2, 3]),
            "customer_dropped": random.choice([False, False, False, True]),
            "negative_sentiment": random.uniform(0.0, 0.8),
            "sample_stratum": "risk_ranked",
            "turns": [
                {
                    "turn_index": 0,
                    "speaker": "user",
                    "transcript": f"Hello, my PAN is ABCDE{random.randint(1000, 9999)}F and I want loan info.",
                    "audio_start_time": 0.0,
                    "audio_end_time": 3.5,
                },
                {
                    "turn_index": 1,
                    "speaker": "agent",
                    "transcript": "Our loan rate is 10.5% p.a. subject to eligibility. Terms and conditions apply.",
                    "audio_start_time": 3.8,
                    "audio_end_time": 7.2,
                },
            ],
        }
        self.client.post(
            "/api/v1/sampling/ingest",
            json=payload,
            name="/api/v1/sampling/ingest",
        )
