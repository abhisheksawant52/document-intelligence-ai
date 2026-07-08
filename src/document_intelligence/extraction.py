"""Entity and key-value extraction.

Uses regular expressions and simple heuristics to extract common entities
(dates, monetary amounts, email addresses, invoice numbers) and labelled
key-value pairs from document text. Pure standard library; works standalone.
"""

from __future__ import annotations

import re

from .models import Entity, ExtractionResult, KeyValue

# Entity patterns. Each maps an entity type to a compiled regular expression.
_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "date": re.compile(
        r"\b("
        r"\d{4}-\d{2}-\d{2}"  # 2026-07-08
        r"|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"  # 07/08/2026
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r")\b",
        re.IGNORECASE,
    ),
    "amount": re.compile(r"(?:USD|EUR|GBP|\$|€|£)\s?\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?\b"),
    "invoice_number": re.compile(
        r"\b(?:invoice|inv)\s*(?:no\.?|number|#)?\s*[:#]?\s*([A-Z0-9][A-Z0-9-]{2,})\b",
        re.IGNORECASE,
    ),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b"),
}

# Key-value labels recognized on a single line, e.g. "Total: $10.00".
_KV_LABEL = re.compile(r"^\s*([A-Za-z][A-Za-z /_-]{1,40}?)\s*[:=]\s*(.+?)\s*$")


def extract_entities(text: str) -> list[Entity]:
    """Extract typed entities from ``text`` using regex patterns.

    Args:
        text: Document text.

    Returns:
        A list of :class:`Entity` objects (deduplicated by type and value).
    """
    seen: set[tuple[str, str]] = set()
    entities: list[Entity] = []
    for entity_type, pattern in _PATTERNS.items():
        for match in pattern.finditer(text):
            # Prefer a capturing group when present, else the whole match.
            value = (match.group(1) if match.groups() else match.group(0)).strip()
            key = (entity_type, value.lower())
            if not value or key in seen:
                continue
            seen.add(key)
            entities.append(Entity(type=entity_type, value=value, confidence=0.9))
    return entities


def extract_key_values(text: str) -> list[KeyValue]:
    """Extract ``label: value`` pairs found on individual lines.

    Args:
        text: Document text.

    Returns:
        A list of :class:`KeyValue` pairs.
    """
    pairs: list[KeyValue] = []
    for line in text.splitlines():
        match = _KV_LABEL.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key and value:
                pairs.append(KeyValue(key=key, value=value, confidence=0.8))
    return pairs


def extract(text: str) -> ExtractionResult:
    """Run entity and key-value extraction over ``text``.

    Args:
        text: Document text.

    Returns:
        An :class:`ExtractionResult` combining entities and key-value pairs.
    """
    return ExtractionResult(
        entities=extract_entities(text),
        key_values=extract_key_values(text),
    )
