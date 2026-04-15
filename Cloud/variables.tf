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

variable "youtube_cookies_secret_name" {
    type        = string
    description = "Name of the Secrets Manager secret that stores YouTube cookies"
    default     = "discord_music_bot_youtube_cookies"
}

variable "create_secret_reader_user" {
    type        = bool
    description = "Whether Terraform should create an IAM user limited to reading the bot secret"
    default     = true
}

variable "secret_reader_user_name" {
    type        = string
    description = "Name of the IAM user that can only read the bot secret"
    default     = "discord_music_bot_secret_reader"
}

variable "create_secret_reader_access_key" {
    type        = bool
    description = "Whether Terraform should create an access key for the limited IAM user"
    default     = true
}
