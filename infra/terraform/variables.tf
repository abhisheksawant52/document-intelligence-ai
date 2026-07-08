variable "region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for tagging and resource naming."
  type        = string
  default     = "document-intelligence-ai"
}

variable "container_image" {
  description = "Container image reference for the service (repository:tag)."
  type        = string
  default     = "document-intelligence-ai:latest"
}

variable "documents_bucket" {
  description = "Name of the S3 bucket used to store uploaded documents."
  type        = string
  default     = "document-intelligence-ai-documents"
}

variable "results_table_name" {
  description = "Name of the storage resource used to persist extraction results."
  type        = string
  default     = "document-intelligence-ai-results"
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs."
  type        = number
  default     = 30
}

variable "enable_bucket_versioning" {
  description = "Whether to enable versioning on the documents bucket."
  type        = bool
  default     = true
}
