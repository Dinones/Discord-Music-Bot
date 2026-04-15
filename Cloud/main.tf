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

resource "aws_secretsmanager_secret" "discord_bot_secret" {
    name                    = var.secret_name
    description             = "Discord Music Bot Token"
    recovery_window_in_days = 7

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}

resource "aws_secretsmanager_secret" "youtube_cookies_secret" {
    name                    = var.youtube_cookies_secret_name
    description             = "Discord Music Bot YouTube Cookies"
    recovery_window_in_days = 7

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}

data "aws_iam_policy_document" "secret_reader" {
    statement {
        sid    = "ReadOnlyBotSecrets"
        effect = "Allow"

        actions = [
            "secretsmanager:GetSecretValue"
        ]

        resources = [
            aws_secretsmanager_secret.discord_bot_secret.arn,
            aws_secretsmanager_secret.youtube_cookies_secret.arn
        ]
    }
}

resource "aws_iam_user" "secret_reader" {
    count = var.create_secret_reader_user ? 1 : 0

    name = var.secret_reader_user_name

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}

resource "aws_iam_user_policy" "secret_reader" {
    count = var.create_secret_reader_user ? 1 : 0

    name   = "${var.secret_reader_user_name}-read-secret"
    user   = aws_iam_user.secret_reader[0].name
    policy = data.aws_iam_policy_document.secret_reader.json
}

resource "aws_iam_access_key" "secret_reader" {
    count = var.create_secret_reader_user && var.create_secret_reader_access_key ? 1 : 0

    user = aws_iam_user.secret_reader[0].name
}