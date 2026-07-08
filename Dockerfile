# syntax=docker/dockerfile:1

# ---- Builder stage -------------------------------------------------------
FROM python:3.14-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build tooling and create a self-contained virtual environment.
COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install .

# ---- Runtime stage -------------------------------------------------------
FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Create an unprivileged user to run the service.
RUN groupadd --system appuser && \
    useradd --system --gid appuser --create-home appuser

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "document_intelligence.main:app", "--host", "0.0.0.0", "--port", "8000"]
