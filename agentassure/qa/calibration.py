"""Reviewer Calibration and Inter-Rater Reliability (Cohen's Kappa).

Implements statistical calibration audits, turnaround SLA metrics,
and Cohen's kappa calculations:
kappa = (P_observed - P_expected) / (1 - P_expected)
"""

from typing import List, Dict, Tuple, Any
import numpy as np


class CalibrationEngine:
    """Computes inter-rater agreement and reviewer performance statistics."""

    @classmethod
    def calculate_cohens_kappa(
        cls, rater_a_labels: List[str], rater_b_labels: List[str]
    ) -> float:
        """Calculate Cohen's kappa coefficient between two raters on categorical labels.

        Args:
            rater_a_labels: List of category labels from reviewer A.
            rater_b_labels: List of category labels from reviewer B for matching items.

        Returns:
            Cohen's kappa score in [-1.0, 1.0]. A score > 0.80 signifies strong agreement.
        """
        if not rater_a_labels or not rater_b_labels or len(rater_a_labels) != len(rater_b_labels):
            return 1.0 if rater_a_labels == rater_b_labels else 0.0

        n = len(rater_a_labels)
        categories = sorted(list(set(rater_a_labels) | set(rater_b_labels)))
        if len(categories) <= 1:
            return 1.0

        cat_to_idx = {cat: i for i, cat in enumerate(categories)}
        k = len(categories)

        # Build confusion matrix
        matrix = np.zeros((k, k), dtype=np.int32)
        for a, b in zip(rater_a_labels, rater_b_labels):
            matrix[cat_to_idx[a], cat_to_idx[b]] += 1

        # Observed agreement (Po)
        po = np.trace(matrix) / n

        # Expected chance agreement (Pe)
        sum_rows = np.sum(matrix, axis=1)
        sum_cols = np.sum(matrix, axis=0)
        pe = np.sum((sum_rows * sum_cols)) / (n * n)

        if pe >= 1.0:
            return 1.0

        kappa = (po - pe) / (1.0 - pe)
        return round(float(np.clip(kappa, -1.0, 1.0)), 4)

    @classmethod
    def audit_reviewer_calibration(
        cls, reviewer_labels: List[str], gold_labels: List[str]
    ) -> Dict[str, Any]:
        """Audit a reviewer against gold-standard benchmark annotations.

        Args:
            reviewer_labels: Annotations assigned by the reviewer.
            gold_labels: Canonical annotations confirmed by QA lead.

        Returns:
            Dict containing total items, agreed items, kappa, and pass status.
        """
        total = len(gold_labels)
        if total == 0:
            return {
                "total_items": 0,
                "agreed_items": 0,
                "kappa_score": 1.0,
                "passed": True,
                "status": "passed",
            }

        agreed = sum(1 for r, g in zip(reviewer_labels, gold_labels) if r == g)
        kappa = cls.calculate_cohens_kappa(reviewer_labels, gold_labels)

        # Target threshold: kappa >= 0.80
        passed = kappa >= 0.80
        return {
            "total_items": total,
            "agreed_items": agreed,
            "accuracy": round(agreed / total, 4),
            "kappa_score": kappa,
            "passed": passed,
            "status": "passed" if passed else "needs_training",
        }
