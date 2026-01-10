terraform {
  required_version = ">= 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # Match your installed provider version
    }
  }
}

provider "aws" {
  region = var.aws_region
}