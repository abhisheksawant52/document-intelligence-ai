"""Pydantic data models for the document intelligence pipeline.

These models describe the structured data that flows through the processing
pipeline: OCR tokens, layout blocks, extracted entities and key-value pairs,
classification results, and the aggregate :class:`DocumentResult`.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Axis-aligned bounding box in pixel coordinates.

    The origin ``(0, 0)`` is the top-left corner of the page.
    """

    x: float = Field(..., description="Left edge of the box in pixels.")
    y: float = Field(..., description="Top edge of the box in pixels.")
    width: float = Field(..., ge=0, description="Width of the box in pixels.")
    height: float = Field(..., ge=0, description="Height of the box in pixels.")

    @property
    def right(self) -> float:
        """Return the x-coordinate of the right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> float:
        """Return the y-coordinate of the bottom edge."""
        return self.y + self.height

    @property
    def center_y(self) -> float:
        """Return the vertical center of the box."""
        return self.y + self.height / 2


class OCRToken(BaseModel):
    """A single recognized text token with its position and confidence."""

    text: str = Field(..., description="Recognized token text.")
    box: BoundingBox = Field(..., description="Location of the token on the page.")
    confidence: float = Field(
        1.0, ge=0.0, le=1.0, description="OCR confidence score in the range [0, 1]."
    )


class OCRResult(BaseModel):
    """Result of running OCR over a document page or image."""

    text: str = Field("", description="Full recognized text of the document.")
    tokens: list[OCRToken] = Field(
        default_factory=list, description="Individual tokens with positions."
    )
    engine: str = Field("fallback", description="Name of the OCR engine used.")
    language: str = Field("eng", description="Language hint used for recognition.")


class LayoutBlock(BaseModel):
    """A grouped region of the page such as a line, paragraph, or table cell."""

    block_type: str = Field("line", description="Type of block, e.g. 'line' or 'table'.")
    text: str = Field("", description="Concatenated text of the block.")
    box: BoundingBox = Field(..., description="Bounding box enclosing the block.")
    tokens: list[OCRToken] = Field(
        default_factory=list, description="Tokens that compose this block."
    )


class Entity(BaseModel):
    """A typed entity extracted from document text."""

    type: str = Field(..., description="Entity type, e.g. 'date', 'amount', 'email'.")
    value: str = Field(..., description="Raw text value of the entity.")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence.")


class KeyValue(BaseModel):
    """A key-value pair extracted from the document."""

    key: str = Field(..., description="Field name or label.")
    value: str = Field(..., description="Field value.")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence.")


class ExtractionResult(BaseModel):
    """Aggregate result of entity and key-value extraction."""

    entities: list[Entity] = Field(default_factory=list, description="Extracted entities.")
    key_values: list[KeyValue] = Field(
        default_factory=list, description="Extracted key-value pairs."
    )


class Classification(BaseModel):
    """Document type classification result."""

    label: str = Field(..., description="Predicted document type, e.g. 'invoice'.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of the prediction.")
    scores: dict[str, float] = Field(
        default_factory=dict, description="Per-class scores considered during classification."
    )


class DocumentResult(BaseModel):
    """Full pipeline result for a single processed document."""

    filename: str = Field(..., description="Original filename of the document.")
    ocr: OCRResult = Field(..., description="OCR output.")
    layout: list[LayoutBlock] = Field(
        default_factory=list, description="Layout blocks derived from OCR tokens."
    )
    extraction: ExtractionResult = Field(..., description="Extracted entities and key-values.")
    classification: Classification = Field(..., description="Document type classification.")


class HealthStatus(BaseModel):
    """Health/readiness response payload."""

    status: str = Field(..., description="Overall status, e.g. 'ok'.")
    service: str = Field(..., description="Service name.")
    version: str = Field(..., description="Running service version.")
