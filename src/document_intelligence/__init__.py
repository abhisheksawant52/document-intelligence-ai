"""Document intelligence AI service.

A FastAPI service that ingests documents (PDF/images), runs OCR, analyzes
layout, extracts entities and key-value pairs, and classifies documents by
type (invoice, contract, resume, and more).
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "classification",
    "config",
    "extraction",
    "layout",
    "models",
    "ocr",
    "pipeline",
]
