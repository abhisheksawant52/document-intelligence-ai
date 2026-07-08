"""Tests for layout analysis."""

from __future__ import annotations

from document_intelligence.layout import group_lines
from document_intelligence.models import BoundingBox, OCRToken


def _token(text: str, x: float, y: float) -> OCRToken:
    """Build a simple OCR token at the given position."""
    return OCRToken(text=text, box=BoundingBox(x=x, y=y, width=8 * len(text), height=16))


def test_groups_tokens_into_lines() -> None:
    """Tokens sharing a vertical band should be grouped into one line."""
    tokens = [
        _token("Hello", x=10, y=10),
        _token("world", x=60, y=12),
        _token("Second", x=10, y=40),
        _token("line", x=80, y=41),
    ]
    lines = group_lines(tokens, y_tolerance=10)

    assert len(lines) == 2
    assert lines[0].text == "Hello world"
    assert lines[1].text == "Second line"


def test_tokens_ordered_left_to_right() -> None:
    """Within a line, tokens should be ordered by x-coordinate."""
    tokens = [
        _token("beta", x=100, y=10),
        _token("alpha", x=10, y=11),
    ]
    lines = group_lines(tokens)
    assert lines[0].text == "alpha beta"
