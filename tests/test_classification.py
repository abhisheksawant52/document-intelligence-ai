"""Tests for document classification."""

from __future__ import annotations

from document_intelligence.classification import classify

INVOICE_TEXT = """INVOICE
Invoice Number: INV-2024-0042
Bill To: Acme Corp
Subtotal: $1,000.00
Tax: $250.00
Total: $1,250.00
Amount Due: $1,250.00
Payment due date: 2026-08-01
"""


def test_classifies_invoice() -> None:
    """Invoice-like text should be classified as an invoice with confidence."""
    result = classify(INVOICE_TEXT)
    assert result.label == "invoice"
    assert result.confidence > 0.0
    assert result.scores["invoice"] >= result.scores["resume"]


def test_unknown_when_no_keywords() -> None:
    """Text with no signature keywords should be classified as unknown."""
    result = classify("qwerty zxcvb")
    assert result.label == "unknown"
    assert result.confidence == 0.0
