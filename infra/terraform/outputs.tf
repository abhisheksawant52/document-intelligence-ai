output "ecr_repository_url" {
  description = "URL of the ECR repository for the service image."
  value       = aws_ecr_repository.service.repository_url
}

output "documents_bucket_name" {
  description = "Name of the S3 bucket storing uploaded documents."
  value       = aws_s3_bucket.documents.bucket
}

output "documents_bucket_arn" {
  description = "ARN of the documents S3 bucket."
  value       = aws_s3_bucket.documents.arn
}

output "log_group_name" {
  description = "CloudWatch log group name for the service."
  value       = aws_cloudwatch_log_group.service.name
}

output "results_table_name" {
  description = "Name of the DynamoDB results table."
  value       = module.storage.table_name
}

output "results_table_arn" {
  description = "ARN of the DynamoDB results table."
  value       = module.storage.table_arn
}
