"""Layout analysis.

Groups positioned OCR tokens into higher-level layout blocks (lines) using
pure geometric heuristics. This module has no external dependencies and works
standalone given a list of :class:`OCRToken` objects.
"""

from __future__ import annotations

from .models import BoundingBox, LayoutBlock, OCRToken


def _merge_boxes(boxes: list[BoundingBox]) -> BoundingBox:
    """Return the smallest bounding box enclosing all ``boxes``."""
    left = min(b.x for b in boxes)
    top = min(b.y for b in boxes)
    right = max(b.right for b in boxes)
    bottom = max(b.bottom for b in boxes)
    return BoundingBox(x=left, y=top, width=right - left, height=bottom - top)


def group_lines(tokens: list[OCRToken], y_tolerance: float = 10.0) -> list[LayoutBlock]:
    """Group tokens into text lines by vertical proximity.

    Tokens whose vertical centers fall within ``y_tolerance`` pixels of a line's
    running center are placed on the same line. Within a line, tokens are
    ordered left-to-right.

    Args:
        tokens: Positioned OCR tokens.
        y_tolerance: Maximum vertical distance (pixels) for same-line grouping.

    Returns:
        A list of ``line`` layout blocks ordered top-to-bottom.
    """
    if not tokens:
        return []

    ordered = sorted(tokens, key=lambda t: (t.box.center_y, t.box.x))
    lines: list[list[OCRToken]] = []
    centers: list[float] = []

    for token in ordered:
        placed = False
        for index, center in enumerate(centers):
            if abs(token.box.center_y - center) <= y_tolerance:
                lines[index].append(token)
                # Update the running center as a simple average.
                count = len(lines[index])
                centers[index] = (center * (count - 1) + token.box.center_y) / count
                placed = True
                break
        if not placed:
            lines.append([token])
            centers.append(token.box.center_y)

    blocks: list[LayoutBlock] = []
    for line_tokens in lines:
        line_tokens.sort(key=lambda t: t.box.x)
        text = " ".join(t.text for t in line_tokens)
        block = LayoutBlock(
            block_type="line",
            text=text,
            box=_merge_boxes([t.box for t in line_tokens]),
            tokens=line_tokens,
        )
        blocks.append(block)

    blocks.sort(key=lambda b: b.box.y)
    return blocks


def analyze_layout(tokens: list[OCRToken], y_tolerance: float = 10.0) -> list[LayoutBlock]:
    """Analyze document layout from OCR tokens.

    Currently groups tokens into lines. Serves as the extension point for more
    advanced block/table detection.

    Args:
        tokens: Positioned OCR tokens.
        y_tolerance: Vertical tolerance passed to :func:`group_lines`.

    Returns:
        A list of layout blocks.
    """
    return group_lines(tokens, y_tolerance=y_tolerance)
