locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Container registry for the service image.
resource "aws_ecr_repository" "service" {
  name                 = local.name_prefix
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Bucket for uploaded documents (PDFs/images) awaiting processing.
resource "aws_s3_bucket" "documents" {
  bucket = "${var.documents_bucket}-${var.environment}"
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = var.enable_bucket_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Application logs.
resource "aws_cloudwatch_log_group" "service" {
  name              = "/aws/${local.name_prefix}"
  retention_in_days = var.log_retention_days
}

# Storage sub-module: results table for extracted document data.
module "storage" {
  source = "./modules/storage"

  name_prefix = local.name_prefix
  table_name  = var.results_table_name
  environment = var.environment
}
