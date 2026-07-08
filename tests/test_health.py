"""Tests for the health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from document_intelligence.main import create_app


def test_health_returns_200() -> None:
    """The /health endpoint should return 200 with an 'ok' status."""
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
