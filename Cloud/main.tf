terraform {
    required_version = ">= 1.5.0"

    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = var.aws_region
}

resource "aws_secretsmanager_secret" "app" {
    name                    = var.secret_name
    description             = "Discord Music Bot Token"
    recovery_window_in_days = 7

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}