"""OCR engine abstraction.

Provides a pluggable interface for optical character recognition. A
Tesseract-backed engine is referenced for real deployments, while a
deterministic, dependency-free fallback engine is always available so the
pipeline can run in any environment (and in tests).

The fallback engine interprets the uploaded bytes as UTF-8 text and lays the
tokens out on a synthetic grid, producing realistic bounding boxes without
requiring heavy OCR dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .logging_config import get_logger
from .models import BoundingBox, OCRResult, OCRToken

logger = get_logger(__name__)

# Synthetic layout constants used by the fallback engine (in pixels).
_CHAR_WIDTH = 8.0
_TOKEN_HEIGHT = 16.0
_LINE_HEIGHT = 24.0
_MARGIN_X = 10.0
_MARGIN_Y = 10.0
_SPACE_WIDTH = 8.0


class OCREngine(ABC):
    """Abstract base class for OCR engines."""

    name: str = "base"

    @abstractmethod
    def recognize(self, data: bytes, language: str = "eng") -> OCRResult:
        """Recognize text in the given document bytes.

        Args:
            data: Raw bytes of an image or document.
            language: Language hint for recognition.

        Returns:
            An :class:`OCRResult` with the full text and positioned tokens.
        """
        raise NotImplementedError


class FallbackOCREngine(OCREngine):
    """Deterministic OCR engine that decodes bytes as UTF-8 text.

    This engine does not perform image recognition. It is used as a safe
    default when no OCR backend is configured or available, and it makes the
    downstream pipeline fully functional for text-based inputs.
    """

    name = "fallback"

    def recognize(self, data: bytes, language: str = "eng") -> OCRResult:
        """Decode ``data`` as text and lay tokens out on a synthetic grid."""
        text = data.decode("utf-8", errors="replace")
        tokens = self._tokenize(text)
        return OCRResult(text=text, tokens=tokens, engine=self.name, language=language)

    @staticmethod
    def _tokenize(text: str) -> list[OCRToken]:
        """Split text into positioned tokens using deterministic geometry."""
        tokens: list[OCRToken] = []
        for line_index, line in enumerate(text.splitlines()):
            y = _MARGIN_Y + line_index * _LINE_HEIGHT
            x = _MARGIN_X
            for word in line.split():
                width = max(len(word), 1) * _CHAR_WIDTH
                tokens.append(
                    OCRToken(
                        text=word,
                        box=BoundingBox(x=x, y=y, width=width, height=_TOKEN_HEIGHT),
                        confidence=1.0,
                    )
                )
                x += width + _SPACE_WIDTH
        return tokens


class TesseractOCREngine(OCREngine):
    """Tesseract-backed OCR engine.

    Requires the optional ``pytesseract`` and ``pillow`` dependencies along
    with a system Tesseract installation. Falls back gracefully with a clear
    error if those dependencies are unavailable.
    """

    name = "tesseract"

    def recognize(self, data: bytes, language: str = "eng") -> OCRResult:
        """Run Tesseract OCR over the provided image bytes.

        Raises:
            RuntimeError: If the optional OCR dependencies are not installed.
        """
        try:
            import io

            import pytesseract  # type: ignore[import-not-found]
            from PIL import Image  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depends on optional deps
            raise RuntimeError(
                "Tesseract OCR requires 'pytesseract' and 'pillow'. "
                "Install them or set DOCAI_OCR_ENGINE=fallback."
            ) from exc

        image = Image.open(io.BytesIO(data))  # pragma: no cover - needs image input
        data_dict = pytesseract.image_to_data(  # pragma: no cover
            image, lang=language, output_type=pytesseract.Output.DICT
        )
        tokens: list[OCRToken] = []  # pragma: no cover
        for i, word in enumerate(data_dict["text"]):  # pragma: no cover
            if not word.strip():
                continue
            conf = float(data_dict["conf"][i])
            tokens.append(
                OCRToken(
                    text=word,
                    box=BoundingBox(
                        x=float(data_dict["left"][i]),
                        y=float(data_dict["top"][i]),
                        width=float(data_dict["width"][i]),
                        height=float(data_dict["height"][i]),
                    ),
                    confidence=max(conf, 0.0) / 100.0 if conf >= 0 else 0.0,
                )
            )
        full_text = " ".join(t.text for t in tokens)  # pragma: no cover
        return OCRResult(  # pragma: no cover
            text=full_text, tokens=tokens, engine=self.name, language=language
        )


def get_engine(name: str = "fallback") -> OCREngine:
    """Return an OCR engine by name, defaulting to the fallback engine.

    Args:
        name: Engine identifier, e.g. ``"tesseract"`` or ``"fallback"``.

    Returns:
        An :class:`OCREngine` instance.
    """
    engines: dict[str, type[OCREngine]] = {
        "fallback": FallbackOCREngine,
        "tesseract": TesseractOCREngine,
    }
    engine_cls = engines.get(name.lower())
    if engine_cls is None:
        logger.warning("Unknown OCR engine '%s'; using fallback.", name)
        engine_cls = FallbackOCREngine
    return engine_cls()
