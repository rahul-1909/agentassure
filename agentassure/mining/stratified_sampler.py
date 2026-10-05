"""Stratified Sampling Engine.

Partitions candidate conversations into three complementary strata:
- 65% Risk-Ranked (High potential failure rate)
- 20% New Agent Versions (Regression coverage for latest deploys)
- 15% Edge Cases (Code-switching Hinglish, interruptions, extreme loops)
"""

import math
from typing import List

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from agentassure.config import settings
from agentassure.db.models.conversation import Conversation


class StratifiedSampler:
    """Selects stratified review batches for human-in-the-loop QA."""

    @classmethod
    def sample_batch(
        cls, db: Session, target_batch_size: int = 50, latest_version: str = "v2.5.0"
    ) -> List[Conversation]:
        """Perform stratified random selection across risk, new version, and edge strata.

        Args:
            db: Active database session.
            target_batch_size: Total number of conversations to retrieve for review.
            latest_version: Current candidate or latest deployed agent version.

        Returns:
            List of unique Conversation models selected for review.
        """
        if target_batch_size <= 0:
            return []

        risk_count = math.ceil(target_batch_size * settings.STRATA_RISK_PERCENT)
        version_count = math.floor(target_batch_size * settings.STRATA_NEW_VERSION_PERCENT)
        edge_count = target_batch_size - risk_count - version_count

        selected_ids = set()
        result_conversations: List[Conversation] = []

        # 1. Stratum 1: Risk-Ranked (Highest risk score first)
        risk_stmt = (
            select(Conversation)
            .where(Conversation.review_status == "pending")
            .where(Conversation.is_archived.is_(False))
            .order_by(desc(Conversation.risk_score))
            .limit(risk_count * 2)
        )
        risk_candidates = db.scalars(risk_stmt).all()
        for conv in risk_candidates:
            if len(result_conversations) >= risk_count:
                break
            if conv.id not in selected_ids:
                conv.sample_stratum = "risk_ranked"
                selected_ids.add(conv.id)
                result_conversations.append(conv)

        # 2. Stratum 2: New Agent Version
        version_stmt = (
            select(Conversation)
            .where(Conversation.review_status == "pending")
            .where(Conversation.agent_version == latest_version)
            .where(Conversation.is_archived.is_(False))
            .limit(version_count * 2)
        )
        version_candidates = db.scalars(version_stmt).all()
        added_versions = 0
        for conv in version_candidates:
            if added_versions >= version_count:
                break
            if conv.id not in selected_ids:
                conv.sample_stratum = "new_version"
                selected_ids.add(conv.id)
                result_conversations.append(conv)
                added_versions += 1

        # 3. Stratum 3: Edge Cases (Hinglish or high loops or high asr error)
        edge_stmt = (
            select(Conversation)
            .where(Conversation.review_status == "pending")
            .where(Conversation.is_archived.is_(False))
            .where(
                (Conversation.language == "hinglish")
                | (Conversation.loop_count >= 2)
                | (Conversation.asr_error_rate >= 0.25)
            )
            .limit(edge_count * 2)
        )
        edge_candidates = db.scalars(edge_stmt).all()
        added_edges = 0
        for conv in edge_candidates:
            if added_edges >= edge_count:
                break
            if conv.id not in selected_ids:
                conv.sample_stratum = "edge_case"
                selected_ids.add(conv.id)
                result_conversations.append(conv)
                added_edges += 1

        # Fill any deficit up to target_batch_size with remaining pending conversations
        deficit = target_batch_size - len(result_conversations)
        if deficit > 0:
            fill_stmt = (
                select(Conversation)
                .where(Conversation.review_status == "pending")
                .where(Conversation.is_archived.is_(False))
                .limit(deficit * 2)
            )
            for conv in db.scalars(fill_stmt).all():
                if len(result_conversations) >= target_batch_size:
                    break
                if conv.id not in selected_ids:
                    conv.sample_stratum = "random_unbiased"
                    selected_ids.add(conv.id)
                    result_conversations.append(conv)

        return result_conversations
