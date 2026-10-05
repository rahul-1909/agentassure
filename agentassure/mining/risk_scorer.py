"""Smart Sampling Risk Scorer.

Computes multi-signal risk scores according to the specification:
risk_score = (low LLM judge score * 0.35) + (high ASR error rate * 0.25)
           + (conversation loops * 0.20) + (customer drop-off * 0.10)
           + (negative sentiment * 0.10)
"""

from typing import Union
from agentassure.config import settings


class RiskScorer:
    """Calculates prioritized sampling risk score for conversational sessions."""

    @classmethod
    def compute(
        cls,
        judge_score: float,
        asr_error_rate: float,
        loop_count: int,
        customer_dropped: Union[bool, int],
        negative_sentiment: float,
    ) -> float:
        """Compute the composite risk score in the interval [0.0, 1.0].

        Args:
            judge_score: LLM judge quality rating from 0.0 (worst) to 1.0 (best).
            asr_error_rate: Word error rate or acoustic error proportion (0.0 to 1.0).
            loop_count: Number of repetitive non-progress turns.
            customer_dropped: Flag indicating abrupt customer abandonment (True/1 or False/0).
            negative_sentiment: Degree of negative acoustic/text sentiment (0.0 to 1.0).

        Returns:
            Normalized risk score between 0.0 and 1.0.
        """
        # Clamp inputs into valid mathematical domains
        clamped_judge = max(0.0, min(1.0, float(judge_score)))
        clamped_asr = max(0.0, min(1.0, float(asr_error_rate)))
        clamped_sentiment = max(0.0, min(1.0, float(negative_sentiment)))
        drop_val = 1.0 if customer_dropped else 0.0

        # Invert judge score so lower score yields higher risk
        low_judge_component = 1.0 - clamped_judge

        # Normalize loop count (3 or more loops is maximum risk 1.0)
        normalized_loop = min(1.0, max(0, loop_count) / 3.0)

        # Weighted linear combination
        score = (
            low_judge_component * settings.SAMPLING_WEIGHT_JUDGE_SCORE
            + clamped_asr * settings.SAMPLING_WEIGHT_ASR_ERROR
            + normalized_loop * settings.SAMPLING_WEIGHT_LOOP_COUNT
            + drop_val * settings.SAMPLING_WEIGHT_CUSTOMER_DROPOFF
            + clamped_sentiment * settings.SAMPLING_WEIGHT_NEGATIVE_SENTIMENT
        )

        return round(float(max(0.0, min(1.0, score))), 4)
