terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.65"
    }
  }

  # Remote state backend (uncomment and configure for team use).
  # backend "s3" {
  #   bucket         = "my-terraform-state-bucket"
  #   key            = "document-intelligence-ai/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}
