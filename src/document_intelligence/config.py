"""Application configuration using pydantic-settings.

Settings are read from environment variables prefixed with ``DOCAI_`` and from
an optional ``.env`` file. Use :func:`get_settings` to obtain a cached instance.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the document intelligence service."""

    model_config = SettingsConfigDict(
        env_prefix="DOCAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "document-intelligence-ai"
    environment: str = "development"
    log_level: str = "INFO"

    ocr_engine: str = "tesseract"
    ocr_language: str = "eng"
    max_file_size_mb: int = 25

    classifier_model: str = "heuristic"
    storage_backend: str = "local"
    confidence_threshold: float = 0.5


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
