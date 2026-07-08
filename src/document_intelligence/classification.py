"""Document type classification.

Implements a lightweight, keyword-based classifier that scores document text
against a set of known document types and returns the best label with a
normalized confidence. Pure standard library; works standalone.
"""

from __future__ import annotations

import re

from .models import Classification

# Keyword signatures per document class. Weighting is uniform per keyword hit.
_CLASS_KEYWORDS: dict[str, list[str]] = {
    "invoice": [
        "invoice",
        "amount due",
        "bill to",
        "subtotal",
        "tax",
        "total",
        "payment",
        "due date",
    ],
    "contract": [
        "agreement",
        "party",
        "parties",
        "hereby",
        "terms and conditions",
        "governing law",
        "signature",
        "effective date",
    ],
    "resume": [
        "experience",
        "education",
        "skills",
        "curriculum vitae",
        "resume",
        "references",
        "objective",
        "employment",
    ],
    "receipt": [
        "receipt",
        "cash",
        "change",
        "cashier",
        "thank you",
        "qty",
        "item",
    ],
    "report": [
        "report",
        "summary",
        "introduction",
        "conclusion",
        "findings",
        "analysis",
    ],
}


def _count_keyword(text: str, keyword: str) -> int:
    """Count non-overlapping, word-boundary occurrences of ``keyword``."""
    pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
    return len(pattern.findall(text))


def classify(text: str) -> Classification:
    """Classify ``text`` into a document type using keyword scoring.

    Args:
        text: Document text.

    Returns:
        A :class:`Classification` with the winning label, its confidence, and
        the full per-class score distribution. When no keywords match, the
        label is ``"unknown"`` with zero confidence.
    """
    raw_scores: dict[str, int] = {}
    for label, keywords in _CLASS_KEYWORDS.items():
        raw_scores[label] = sum(_count_keyword(text, kw) for kw in keywords)

    total = sum(raw_scores.values())
    if total == 0:
        scores = {label: 0.0 for label in _CLASS_KEYWORDS}
        return Classification(label="unknown", confidence=0.0, scores=scores)

    scores = {label: round(count / total, 4) for label, count in raw_scores.items()}
    best_label = max(scores, key=lambda label: scores[label])
    return Classification(
        label=best_label,
        confidence=scores[best_label],
        scores=scores,
    )
