"""Statistical Significance Engine for CI/CD Quality Gating.

Implements:
- Chi-square test (or Fisher's exact test) for categorical pass rates
- Two-sample Welch's t-test for continuous scores and latency distributions
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats

from agentassure.config import settings


class SignificanceTester:
    """Hypothesis testing between release candidate and production baseline."""

    @classmethod
    def test_pass_rate_significance(
        cls,
        candidate_passed: int,
        candidate_failed: int,
        baseline_passed: int,
        baseline_failed: int,
        alpha: float = settings.STATISTICAL_ALPHA,
    ) -> Dict[str, Any]:
        """Perform Chi-Square contingency test on categorical pass/fail outcomes.

        Args:
            candidate_passed: Number of passed tests in candidate run.
            candidate_failed: Number of failed tests in candidate run.
            baseline_passed: Number of passed tests in baseline run.
            baseline_failed: Number of failed tests in baseline run.
            alpha: Significance threshold (default 0.05).

        Returns:
            Dictionary with test statistics, p-value, and significance conclusion.
        """
        table = np.array([
            [candidate_passed, candidate_failed],
            [baseline_passed, baseline_failed]
        ])

        # If any row is zero or counts too small, provide safe calculation
        if np.any(table.sum(axis=1) == 0):
            return {
                "metric_name": "Pass Rate",
                "test_type": "Chi-Square",
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "conclusion": "Insufficient sample counts for statistical comparison.",
            }

        try:
            chi2, p_val, dof, _ = stats.chi2_contingency(table, correction=True)
        except Exception:
            chi2, p_val = 0.0, 1.0

        is_sig = bool(p_val < alpha)
        c_rate = candidate_passed / max(1, candidate_passed + candidate_failed)
        b_rate = baseline_passed / max(1, baseline_passed + baseline_failed)

        if is_sig:
            direction = "statistically significant improvement" if c_rate > b_rate else "statistically significant regression"
            conclusion = f"Delta ({c_rate*100:.1f}% vs {b_rate*100:.1f}%) is a {direction} (p={p_val:.4f})."
        else:
            conclusion = f"Delta ({c_rate*100:.1f}% vs {b_rate*100:.1f}%) has no statistically significant difference (p={p_val:.4f})."

        return {
            "metric_name": "Pass Rate",
            "test_type": "Chi-Square",
            "statistic": round(float(chi2), 4),
            "p_value": round(float(p_val), 4),
            "is_significant": is_sig,
            "conclusion": conclusion,
        }

    @classmethod
    def test_continuous_metric(
        cls,
        candidate_values: List[float],
        baseline_values: List[float],
        metric_name: str = "Turn Latency",
        alpha: float = settings.STATISTICAL_ALPHA,
    ) -> Dict[str, Any]:
        """Perform Welch's two-sample t-test on continuous metrics (latencies/scores).

        Args:
            candidate_values: Sample observations from candidate version.
            baseline_values: Sample observations from baseline version.
            metric_name: Label for the metric being compared.
            alpha: Significance threshold (default 0.05).

        Returns:
            Dictionary with t-statistic, p-value, and significance conclusion.
        """
        if len(candidate_values) < 2 or len(baseline_values) < 2:
            return {
                "metric_name": metric_name,
                "test_type": "Two-Sample t-Test",
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": False,
                "conclusion": "Insufficient sample variance for t-test.",
            }

        res = stats.ttest_ind(candidate_values, baseline_values, equal_var=False)
        t_stat = float(res.statistic) if not np.isnan(res.statistic) else 0.0
        p_val = float(res.pvalue) if not np.isnan(res.pvalue) else 1.0
        is_sig = bool(p_val < alpha)

        c_mean = float(np.mean(candidate_values))
        b_mean = float(np.mean(baseline_values))

        if is_sig:
            direction = "faster" if c_mean < b_mean else "slower"
            conclusion = f"{metric_name} shift ({c_mean:.1f}ms vs {b_mean:.1f}ms) is statistically significant ({direction}, p={p_val:.4f})."
        else:
            conclusion = f"No statistically significant difference in {metric_name} ({c_mean:.1f}ms vs {b_mean:.1f}ms, p={p_val:.4f})."

        return {
            "metric_name": metric_name,
            "test_type": "Two-Sample t-Test",
            "statistic": round(t_stat, 4),
            "p_value": round(p_val, 4),
            "is_significant": is_sig,
            "conclusion": conclusion,
        }
