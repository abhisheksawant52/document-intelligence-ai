# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-08

### Added

- FastAPI service with `/health`, `/ready`, `/process`, `/ocr`, `/extract`,
  and `/classify` endpoints.
- Document processing pipeline: OCR (Tesseract-backed with a deterministic
  fallback engine), geometric layout analysis, entity and key-value
  extraction, and keyword-based document type classification.
- Pydantic data models covering OCR tokens, layout blocks, entities,
  extraction results, classification, and the aggregate `DocumentResult`.
- Multi-stage `Dockerfile` running as a non-root user with a `/health`
  healthcheck.
- Terraform infrastructure under `infra/terraform/` (ECR repository, S3
  documents bucket with versioning, CloudWatch log group, and a DynamoDB
  results-storage module) with dev/prod environment variables.
- Documentation, CI pipeline, pre-commit hooks, and open-source project files.
