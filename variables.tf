variable "aws_region" {
  description = "The AWS region to deploy HawkGrid monitoring"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "HawkGrid"
}