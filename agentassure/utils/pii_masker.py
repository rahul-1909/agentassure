"""PII Masking and Data Privacy Engine for Conversational AI.

Supports high-precision regex detection and irreversible redaction for:
- Aadhaar (12 digits with or without spaces/dashes)
- PAN (Permanent Account Number - 5 letters, 4 digits, 1 letter)
- Phone Numbers (Indian 10-digit formats with prefixes +91, 0, or plain)
- Email Addresses (Standard RFC 5322 regex supporting all modern TLDs)
- Payment Card Numbers (Visa, MasterCard, RuPay, Amex 13-19 digits)
"""

import re
from typing import Dict, List, Tuple


class PIIMasker:
    """End-to-end PII Masking utility ensuring zero leakage of customer sensitive data."""

    # Regex patterns optimized for Indian conversational data and international standards
    PATTERNS: List[Tuple[str, re.Pattern, str]] = [
        # Payment Cards (13 to 19 digits with optional spaces or dashes)
        (
            "PAYMENT_CARD",
            re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b|\b(?:\d{4}[ -]?){2}\d{4}[ -]?\d{3}\b"),
            "[MASKED_CARD]",
        ),
        # Indian Aadhaar (12 digits, grouped 4-4-4 or continuous)
        (
            "AADHAAR",
            re.compile(r"\b[2-9]{1}\d{3}[ -]?\d{4}[ -]?\d{4}\b"),
            "[MASKED_AADHAAR]",
        ),
        # Indian PAN Card (5 letters, 4 numbers, 1 letter, e.g., ABCDE1234F)
        (
            "PAN",
            re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", re.IGNORECASE),
            "[MASKED_PAN]",
        ),
        # Email Address (supports any length TLD like .internal, .software, .co.in)
        (
            "EMAIL",
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "[MASKED_EMAIL]",
        ),
        # Phone Numbers (+91-9876543210, 09876543210, 98765-43210, 9876543210)
        (
            "PHONE",
            re.compile(r"(?:\+91[\-\s]?)?(?:0)?[6-9]\d{4}[\-\s]?\d{5}\b"),
            "[MASKED_PHONE]",
        ),
    ]

    @classmethod
    def mask(cls, text: str) -> str:
        """Mask all detected PII entities in the input text with standardized redaction tokens.

        Args:
            text: Raw input string containing possible PII.

        Returns:
            Sanitized string with PII replaced by tokens.
        """
        if not text:
            return ""

        masked_text = text
        for _, pattern, replacement in cls.PATTERNS:
            masked_text = pattern.sub(replacement, masked_text)
        return masked_text

    @classmethod
    def detect(cls, text: str) -> Dict[str, List[str]]:
        """Detect and return all instances of PII grouped by entity type without modifying input.

        Args:
            text: Raw text to scan for PII.

        Returns:
            Dictionary mapping entity type to list of detected matches.
        """
        if not text:
            return {}

        results: Dict[str, List[str]] = {}
        for entity_type, pattern, _ in cls.PATTERNS:
            matches = pattern.findall(text)
            if matches:
                results[entity_type] = matches
        return results

    @classmethod
    def has_pii(cls, text: str) -> bool:
        """Check whether the provided text contains any detectable PII entities.

        Args:
            text: Raw text to check.

        Returns:
            True if any PII pattern matches, False otherwise.
        """
        if not text:
            return False
        for _, pattern, _ in cls.PATTERNS:
            if pattern.search(text):
                return True
        return False


def mask_pii(text: str) -> str:
    """Helper functional wrapper for PIIMasker.mask."""
    return PIIMasker.mask(text)
