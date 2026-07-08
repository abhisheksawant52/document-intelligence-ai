"""Tests for entity and key-value extraction."""

from __future__ import annotations

from document_intelligence.extraction import extract, extract_entities

SAMPLE = """Invoice INV-2024-0042
Date: 2026-07-08
Bill To: Acme Corp
Total: $1,250.00
Contact: billing@acme.example
"""


def test_extracts_date_and_amount() -> None:
    """A date and a monetary amount should be recognized in the sample."""
    entities = extract_entities(SAMPLE)
    types = {e.type for e in entities}
    assert "date" in types
    assert "amount" in types

    dates = [e.value for e in entities if e.type == "date"]
    amounts = [e.value for e in entities if e.type == "amount"]
    assert "2026-07-08" in dates
    assert any("1,250.00" in a for a in amounts)


def test_extracts_key_values() -> None:
    """Labelled key-value pairs should be extracted from the sample."""
    result = extract(SAMPLE)
    keys = {kv.key.lower() for kv in result.key_values}
    assert "total" in keys
    assert "date" in keys
