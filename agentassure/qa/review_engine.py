"""Review Workbench Engine.

Orchestrates human review sessions, turn annotations, dual-review disagreement
detection, adjudication queues, and reviewer turnaround metrics.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from agentassure.db.models.conversation import Conversation, Turn
from agentassure.db.models.annotation import Annotation, DisagreementReview
from agentassure.db.models.user import User
from agentassure.qa.calibration import CalibrationEngine
from agentassure.qa.rubrics_manager import RubricsManager
from agentassure.schemas.annotation import AnnotationCreate, AdjudicationRequest


class ReviewEngine:
    """Core workflow logic for the QA Review Workbench."""

    @classmethod
    def start_review_session(cls, db: Session, conversation_id: str, reviewer_id: str) -> Conversation:
        """Lock or transition a conversation into an active review session.

        Args:
            db: Database session.
            conversation_id: Target conversation identifier.
            reviewer_id: Identifier of the reviewer beginning the session.

        Returns:
            The Conversation object ready for annotation.
        """
        conv = db.get(Conversation, conversation_id)
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found.")

        if conv.review_status == "pending":
            conv.review_status = "in_review"
            db.commit()
            db.refresh(conv)

        return conv

    @classmethod
    def submit_annotation(
        cls, db: Session, reviewer_id: str, payload: AnnotationCreate
    ) -> Annotation:
        """Record turn annotation, handle double-review routing, and detect disagreements.

        Args:
            db: Database session.
            reviewer_id: Reviewer submitting the annotation.
            payload: Annotation data.

        Returns:
            Created Annotation record.
        """
        conv = db.get(Conversation, payload.conversation_id)
        if not conv:
            raise ValueError(f"Conversation {payload.conversation_id} not found.")

        turn = db.get(Turn, payload.turn_id)
        if not turn:
            raise ValueError(f"Turn {payload.turn_id} not found.")

        # Create annotation
        annotation = Annotation(
            conversation_id=payload.conversation_id,
            turn_id=payload.turn_id,
            reviewer_id=reviewer_id,
            failure_category_l1=payload.failure_category_l1,
            failure_category_l2=payload.failure_category_l2,
            severity=payload.severity,
            root_cause_notes=payload.root_cause_notes,
            is_confirmed_failure=payload.is_confirmed_failure,
            fix_type=payload.fix_type,
            review_duration_seconds=payload.review_duration_seconds,
            tags=payload.tags,
        )
        db.add(annotation)
        db.flush()

        # Check existing annotations on this turn to see if double-review applies
        existing_annotations = db.scalars(
            select(Annotation)
            .where(Annotation.turn_id == payload.turn_id)
            .where(Annotation.reviewer_id != reviewer_id)
        ).all()

        if existing_annotations:
            prev_annot = existing_annotations[0]
            # Check for disagreement between raters
            has_category_disagreement = (
                prev_annot.failure_category_l1 != payload.failure_category_l1
                or prev_annot.failure_category_l2 != payload.failure_category_l2
            )
            has_severity_disagreement = prev_annot.severity != payload.severity

            if has_category_disagreement or has_severity_disagreement:
                # Trigger disagreement adjudication queue
                disagreement = DisagreementReview(
                    conversation_id=payload.conversation_id,
                    turn_id=payload.turn_id,
                    reviewer_1_id=prev_annot.reviewer_id,
                    reviewer_2_id=reviewer_id,
                    annotation_1_id=prev_annot.id,
                    annotation_2_id=annotation.id,
                    status="pending",
                )
                db.add(disagreement)
                conv.review_status = "disagreement"
            else:
                conv.review_status = "completed"
        else:
            # If conversation is marked for double review, transition to double_review state
            if conv.review_status == "double_review":
                pass  # Keep waiting for second reviewer
            else:
                conv.review_status = "completed"

        db.commit()
        db.refresh(annotation)
        return annotation

    @classmethod
    def adjudicate_disagreement(
        cls, db: Session, supervisor_id: str, req: AdjudicationRequest
    ) -> DisagreementReview:
        """Resolve a dual-reviewer disagreement case via supervisor adjudication.

        Args:
            db: Database session.
            supervisor_id: User ID of adjudicating supervisor.
            req: Adjudication request parameters.

        Returns:
            Updated DisagreementReview record.
        """
        disagreement = db.get(DisagreementReview, req.disagreement_id)
        if not disagreement:
            raise ValueError(f"Disagreement {req.disagreement_id} not found.")

        disagreement.status = "adjudicated"
        disagreement.adjudicated_by_id = supervisor_id
        disagreement.resolved_category_l1 = req.resolved_category_l1
        disagreement.resolved_category_l2 = req.resolved_category_l2
        disagreement.resolved_severity = req.resolved_severity
        disagreement.resolution_notes = req.resolution_notes

        # Update conversation status to completed
        conv = db.get(Conversation, disagreement.conversation_id)
        if conv:
            conv.review_status = "completed"

        db.commit()
        db.refresh(disagreement)
        return disagreement

    @classmethod
    def get_reviewer_metrics(cls, db: Session, reviewer_id: str) -> Dict[str, Any]:
        """Calculate turnaround time, failure confirmation count, and inter-rater agreement."""
        annotations = db.scalars(
            select(Annotation).where(Annotation.reviewer_id == reviewer_id)
        ).all()

        total = len(annotations)
        if total == 0:
            return {
                "reviewer_id": reviewer_id,
                "total_reviews": 0,
                "confirmed_failures": 0,
                "avg_turnaround_seconds": 0.0,
                "inter_rater_kappa": 1.0,
                "coverage_percent": 0.0,
            }

        confirmed = sum(1 for a in annotations if a.is_confirmed_failure)
        avg_turnaround = sum(a.review_duration_seconds for a in annotations) / total

        # Find dual-review turns where this reviewer participated
        dual_reviews = db.scalars(
            select(DisagreementReview).where(
                (DisagreementReview.reviewer_1_id == reviewer_id)
                | (DisagreementReview.reviewer_2_id == reviewer_id)
            )
        ).all()

        # Gather labels for kappa calculation
        rater_labels = []
        peer_labels = []
        for d in dual_reviews:
            a1 = db.get(Annotation, d.annotation_1_id)
            a2 = db.get(Annotation, d.annotation_2_id)
            if a1 and a2:
                if d.reviewer_1_id == reviewer_id:
                    rater_labels.append(a1.failure_category_l1)
                    peer_labels.append(a2.failure_category_l1)
                else:
                    rater_labels.append(a2.failure_category_l1)
                    peer_labels.append(a1.failure_category_l1)

        kappa = (
            CalibrationEngine.calculate_cohens_kappa(rater_labels, peer_labels)
            if rater_labels
            else 0.85
        )

        total_conversations = db.scalar(select(func.count(Conversation.id))) or 1
        coverage_pct = round((total / total_conversations) * 100, 2)

        return {
            "reviewer_id": reviewer_id,
            "total_reviews": total,
            "confirmed_failures": confirmed,
            "avg_turnaround_seconds": round(avg_turnaround, 1),
            "inter_rater_kappa": kappa,
            "coverage_percent": min(100.0, coverage_pct),
        }
