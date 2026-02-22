variable "aws_region" {
    type        = string
    description = "AWS region where the secret will be created"
    default     = "eu-west-1"
}

variable "project_name" {
    type        = string
    description = "Project tag name"
    default     = "Discord Music Bot"
}

variable "secret_name" {
    type        = string
    description = "Name of the Secrets Manager secret"
    default     = "discord_music_bot_secrets"
}