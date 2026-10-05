"""Unit Tests for PII Masking and Data Privacy Engine."""

import pytest

from agentassure.utils.pii_masker import PIIMasker, mask_pii


def test_mask_aadhaar_formatted():
    raw = "My Aadhaar number is 4921 8832 9012, please verify."
    masked = mask_pii(raw)
    assert "4921" not in masked
    assert "[MASKED_AADHAAR]" in masked


def test_mask_aadhaar_continuous():
    raw = "Customer quoted 492188329012 on voice line."
    masked = mask_pii(raw)
    assert "[MASKED_AADHAAR]" in masked
    assert "492188329012" not in masked


def test_mask_pan_card():
    raw = "Here is my PAN: ABCDE1234F for KYC update."
    masked = mask_pii(raw)
    assert "[MASKED_PAN]" in masked
    assert "ABCDE1234F" not in masked


def test_mask_email():
    raw = "Send statement to rahul.teja@example.co.in thanks."
    masked = mask_pii(raw)
    assert "[MASKED_EMAIL]" in masked
    assert "rahul.teja@example.co.in" not in masked


def test_mask_phone_numbers():
    cases = [
        "Call me back on +91 9876543210 please.",
        "My mobile number is 09876543210.",
        "Contact 9876543210 for delivery.",
    ]
    for raw in cases:
        masked = mask_pii(raw)
        assert "[MASKED_PHONE]" in masked
        assert "9876543210" not in masked


def test_mask_payment_card():
    raw = "Debit card ending in 4111 2222 3333 4444 debited."
    masked = mask_pii(raw)
    assert "[MASKED_CARD]" in masked
    assert "4111" not in masked


def test_detect_pii_multiple():
    text = "User with PAN ABCDE1234F and email test@agentassure.internal called from +91 9876543210"
    detected = PIIMasker.detect(text)
    assert "PAN" in detected
    assert "EMAIL" in detected
    assert "PHONE" in detected
    assert PIIMasker.has_pii(text) is True


def test_empty_and_clean_text():
    assert mask_pii("") == ""
    assert mask_pii(None) == ""
    assert PIIMasker.has_pii("Hello, what is your personal loan interest rate?") is False
    assert PIIMasker.detect("Clean inquiry without PII") == {}
