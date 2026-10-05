"""Slack Webhook Notifier for Critical CI Gates and Ticket Alerts."""

from typing import Dict, Any, Optional
import httpx
from agentassure.config import settings
from agentassure.utils.logging import get_logger

logger = get_logger("slack")


class SlackNotifier:
    """Sends rich alert cards to Slack channels via incoming webhooks."""

    @classmethod
    def post_alert(cls, message: str, blocks: Optional[list] = None) -> bool:
        """Send message or structured Block Kit payload to configured Slack webhook URL."""
        webhook_url = settings.SLACK_WEBHOOK_URL
        if not webhook_url or "mock" in webhook_url:
            logger.info(f"[Mock Slack Alert]: {message}")
            return True

        payload: Dict[str, Any] = {"text": message}
        if blocks:
            payload["blocks"] = blocks

        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(webhook_url, json=payload)
                return res.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to post to Slack: {e}")
            return False

    @classmethod
    def post_gate_blocked_alert(
        cls, version: str, blocked_categories: list, pass_rate: float
    ) -> bool:
        """Post high-priority release block notice."""
        msg = (
            f"🚨 *AgentAssure CI Release Gate BLOCKED*\n"
            f"*Candidate:* `{version}`\n"
            f"*Overall Pass Rate:* `{pass_rate*100:.1f}%`\n"
            f"*Breached Categories:* `{', '.join(blocked_categories)}`\n"
            f"Merge has been restricted until critical regressions are resolved."
        )
        return cls.post_alert(msg)
