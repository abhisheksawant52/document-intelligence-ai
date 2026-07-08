variable "name_prefix" {
  description = "Prefix applied to resource names (project + environment)."
  type        = string
}

variable "table_name" {
  description = "Base name of the results table."
  type        = string
  default     = "results"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}
