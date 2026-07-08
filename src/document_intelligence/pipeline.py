"""Document processing pipeline.

Orchestrates the end-to-end flow: OCR -> layout analysis -> extraction ->
classification, producing a single :class:`DocumentResult`.
"""

from __future__ import annotations

from . import classification, extraction, layout
from .config import Settings, get_settings
from .logging_config import get_logger
from .models import DocumentResult
from .ocr import OCREngine, get_engine

logger = get_logger(__name__)


class DocumentPipeline:
    """Coordinates OCR, layout, extraction, and classification stages."""

    def __init__(self, settings: Settings | None = None, engine: OCREngine | None = None) -> None:
        """Initialize the pipeline.

        Args:
            settings: Optional settings; defaults to :func:`get_settings`.
            engine: Optional OCR engine; defaults to the configured engine.
        """
        self.settings = settings or get_settings()
        self.engine = engine or get_engine(self.settings.ocr_engine)

    def process(self, data: bytes, filename: str = "document") -> DocumentResult:
        """Run the full pipeline over document bytes.

        Args:
            data: Raw bytes of the uploaded document.
            filename: Original filename, recorded in the result.

        Returns:
            A fully populated :class:`DocumentResult`.
        """
        logger.info("Processing document '%s' (%d bytes)", filename, len(data))

        ocr_result = self.engine.recognize(data, language=self.settings.ocr_language)
        layout_blocks = layout.analyze_layout(ocr_result.tokens)
        extraction_result = extraction.extract(ocr_result.text)
        classification_result = classification.classify(ocr_result.text)

        return DocumentResult(
            filename=filename,
            ocr=ocr_result,
            layout=layout_blocks,
            extraction=extraction_result,
            classification=classification_result,
        )
