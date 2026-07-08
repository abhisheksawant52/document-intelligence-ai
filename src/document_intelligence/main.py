"""FastAPI application exposing the document intelligence pipeline.

Endpoints:
    * ``GET  /health``   — liveness probe.
    * ``GET  /ready``    — readiness probe.
    * ``POST /process``  — upload a document and run the full pipeline.
    * ``POST /ocr``      — run OCR only.
    * ``POST /extract``  — run OCR + extraction.
    * ``POST /classify`` — run OCR + classification.
"""

from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile

from . import __version__
from .classification import classify
from .config import Settings, get_settings
from .extraction import extract
from .logging_config import configure_logging, get_logger
from .models import (
    Classification,
    DocumentResult,
    ExtractionResult,
    HealthStatus,
    OCRResult,
)
from .ocr import get_engine
from .pipeline import DocumentPipeline

logger = get_logger(__name__)


async def _read_upload(file: UploadFile, settings: Settings) -> bytes:
    """Read an uploaded file, enforcing the configured size limit.

    Args:
        file: The uploaded file.
        settings: Active settings (for ``max_file_size_mb``).

    Returns:
        The raw file bytes.

    Raises:
        HTTPException: If the upload is empty or exceeds the size limit.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_file_size_mb} MB.",
        )
    return data


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A configured :class:`FastAPI` instance.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Document intelligence service: OCR, layout, extraction, classification.",
    )

    @app.get("/health", response_model=HealthStatus, tags=["system"])
    def health() -> HealthStatus:
        """Return service liveness status."""
        return HealthStatus(status="ok", service=settings.app_name, version=__version__)

    @app.get("/ready", response_model=HealthStatus, tags=["system"])
    def ready() -> HealthStatus:
        """Return service readiness status."""
        return HealthStatus(status="ready", service=settings.app_name, version=__version__)

    @app.post("/process", response_model=DocumentResult, tags=["pipeline"])
    async def process(file: UploadFile = File(...)) -> DocumentResult:
        """Run the full pipeline over an uploaded document."""
        data = await _read_upload(file, settings)
        pipeline = DocumentPipeline(settings=settings)
        return pipeline.process(data, filename=file.filename or "document")

    @app.post("/ocr", response_model=OCRResult, tags=["pipeline"])
    async def ocr(file: UploadFile = File(...)) -> OCRResult:
        """Run OCR only over an uploaded document."""
        data = await _read_upload(file, settings)
        engine = get_engine(settings.ocr_engine)
        return engine.recognize(data, language=settings.ocr_language)

    @app.post("/extract", response_model=ExtractionResult, tags=["pipeline"])
    async def extract_endpoint(file: UploadFile = File(...)) -> ExtractionResult:
        """Run OCR followed by entity/key-value extraction."""
        data = await _read_upload(file, settings)
        engine = get_engine(settings.ocr_engine)
        ocr_result = engine.recognize(data, language=settings.ocr_language)
        return extract(ocr_result.text)

    @app.post("/classify", response_model=Classification, tags=["pipeline"])
    async def classify_endpoint(file: UploadFile = File(...)) -> Classification:
        """Run OCR followed by document type classification."""
        data = await _read_upload(file, settings)
        engine = get_engine(settings.ocr_engine)
        ocr_result = engine.recognize(data, language=settings.ocr_language)
        return classify(ocr_result.text)

    logger.info("Initialized %s v%s", settings.app_name, __version__)
    return app


app = create_app()
