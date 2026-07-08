locals {
  table_name = "${var.name_prefix}-${var.table_name}"
}

# DynamoDB table storing structured extraction results keyed by document id.
resource "aws_dynamodb_table" "results" {
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "document_id"

  attribute {
    name = "document_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = local.table_name
    Environment = var.environment
  }
}
