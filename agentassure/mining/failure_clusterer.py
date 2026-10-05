"""Failure Clustering and Mining Engine.

Aggregates individual turn-level QA failure annotations into systematic,
actionable engineering failure patterns and clusters.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from agentassure.db.models.annotation import Annotation
from agentassure.db.models.ticket import FailureCluster


class FailureClusterer:
    """Discovers and clusters recurring failure modes from annotations."""

    @classmethod
    def mine_clusters(cls, db: Session) -> List[FailureCluster]:
        """Aggregate unclustered confirmed failures into FailureCluster records.

        Args:
            db: Database session.

        Returns:
            List of created or updated FailureCluster instances.
        """
        # Query confirmed failures grouped by category L1, L2 and fix_type
        group_stmt = (
            select(
                Annotation.failure_category_l1,
                Annotation.failure_category_l2,
                Annotation.severity,
                Annotation.fix_type,
                func.count(Annotation.id).label("freq"),
            )
            .where(Annotation.is_confirmed_failure.is_(True))
            .group_by(
                Annotation.failure_category_l1,
                Annotation.failure_category_l2,
                Annotation.severity,
                Annotation.fix_type,
            )
        )

        grouped_records = db.execute(group_stmt).all()
        clusters_updated = []

        for row in grouped_records:
            cat_l1, cat_l2, severity, fix_type, freq = row

            cluster_name = f"Pattern: {cat_l1} -> {cat_l2} ({fix_type})"

            # Check if cluster already exists
            existing = db.scalar(
                select(FailureCluster).where(FailureCluster.cluster_name == cluster_name)
            )

            # Estimate impact reduction based on frequency and severity
            impact_weight = {"S1": 25.0, "S2": 15.0, "S3": 8.0, "S4": 3.0}.get(severity, 10.0)
            impact_pct = round(min(50.0, freq * 1.5 + impact_weight), 1)

            root_cause = (
                f"Repeated breakdown in {cat_l1} affecting {cat_l2}. "
                f"Identified across {freq} verified customer turns. Primary remediation: {fix_type}."
            )

            fix_suggestion = cls._generate_fix_suggestion(cat_l1, cat_l2, fix_type)

            if existing:
                existing.frequency = freq
                existing.severity = severity
                existing.expected_impact_reduction_pct = impact_pct
                existing.fix_suggestion = fix_suggestion
                clusters_updated.append(existing)
            else:
                new_cluster = FailureCluster(
                    cluster_name=cluster_name,
                    category_l1=cat_l1,
                    category_l2=cat_l2,
                    severity=severity,
                    root_cause=root_cause,
                    frequency=freq,
                    fix_suggestion=fix_suggestion,
                    expected_impact_reduction_pct=impact_pct,
                    is_resolved=False,
                )
                db.add(new_cluster)
                clusters_updated.append(new_cluster)

        db.commit()
        return clusters_updated

    @staticmethod
    def _generate_fix_suggestion(cat_l1: str, cat_l2: str, fix_type: str) -> str:
        """Synthesize actionable engineering guidance based on taxonomy and fix type."""
        if fix_type == "prompt_patch":
            return f"Update system prompt system_instructions.md: Add explicit negative constraint and fallback instructions for '{cat_l2}'."
        elif fix_type == "kb_entry":
            return f"Ingest verified canonical reference document into vector DB / Knowledge Base chunk index for query domain '{cat_l2}'."
        elif fix_type == "tool_retry":
            return f"Implement exponential backoff retry and schema validation on downstream function calling tool handling '{cat_l2}'."
        elif fix_type == "asr_vocab_boost":
            return f"Add domain keywords and transliterated vernacular phrases to ASR custom language model / vocabulary boost list."
        return f"Refactor dialogue state manager policy for {cat_l1}."
