"""Structured Assertion Engine for Conversational AI Testing.

Executes deterministic and semantic assertions:
- must_contain (required substrings or tokens)
- must_not_contain (forbidden terms, hallucinations, competitor mentions)
- regex_match (syntactic structural verification, statutory disclaimers)
- compliance_check (RBI regulations, mandatory disclosures)
- latency_under (latency SLA thresholds)
"""

import re
from typing import Any, Dict, Tuple


class AssertionEngine:
    """Executes structured assertions against agent outputs."""

    @classmethod
    def evaluate_rule(
        cls,
        rule_type: str,
        parameters: Dict[str, Any],
        agent_response: str,
        latency_ms: float = 0.0,
    ) -> Tuple[bool, str]:
        """Evaluate a single assertion rule against an agent response.

        Args:
            rule_type: Type of assertion rule.
            parameters: Parameter dictionary for the rule.
            agent_response: String response from the agent.
            latency_ms: Turn latency in milliseconds.

        Returns:
            Tuple of (passed: bool, message: str).
        """
        response_lower = agent_response.lower()

        if rule_type == "must_contain":
            targets = parameters.get("targets", [])
            for target in targets:
                if target.lower() not in response_lower:
                    return False, f"Missing required term: '{target}'"
            return True, "All required terms present."

        elif rule_type == "must_not_contain":
            forbidden = parameters.get("forbidden", [])
            for word in forbidden:
                if word.lower() in response_lower:
                    return False, f"Forbidden term detected in response: '{word}'"
            return True, "No forbidden terms found."

        elif rule_type == "regex_match":
            pattern = parameters.get("pattern", "")
            if not re.search(pattern, agent_response, re.IGNORECASE):
                return False, f"Response does not match required regex pattern: {pattern}"
            return True, "Regex pattern matched successfully."

        elif rule_type == "compliance_check":
            disclaimer = parameters.get("required_disclaimer", "")
            if disclaimer and disclaimer.lower() not in response_lower:
                return False, f"Mandatory compliance disclaimer missing: '{disclaimer}'"
            forbidden_advice = parameters.get("forbidden_advice", [])
            for advice in forbidden_advice:
                if advice.lower() in response_lower:
                    return False, f"Unauthorized advice detected: '{advice}'"
            return True, "Compliance requirements verified."

        elif rule_type == "latency_under":
            max_ms = parameters.get("max_ms", 3000.0)
            if latency_ms > max_ms:
                return (
                    False,
                    f"Latency {latency_ms:.1f}ms exceeded maximum allowable {max_ms:.1f}ms.",
                )
            return True, f"Latency {latency_ms:.1f}ms is within SLA ({max_ms:.1f}ms)."

        elif rule_type == "no_hallucination":
            forbidden_facts = parameters.get("unsupported_facts", [])
            for fact in forbidden_facts:
                if fact.lower() in response_lower:
                    return False, f"Hallucinated / unsupported fact detected: '{fact}'"
            return True, "No hallucinated facts found."

        # Default fallback: passes if rule unknown or neutral
        return True, f"Unknown rule '{rule_type}' evaluated as neutral pass."
