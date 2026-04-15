output "secret_arn" {
    description = "Unique ID of the created secret"
    value       = aws_secretsmanager_secret.discord_bot_secret.arn
}

output "secret_name" {
    description = "Name of the created secret"
    value       = aws_secretsmanager_secret.discord_bot_secret.name
}

output "youtube_cookies_secret_arn" {
    description = "Unique ID of the created YouTube cookies secret"
    value       = aws_secretsmanager_secret.youtube_cookies_secret.arn
}

output "youtube_cookies_secret_name" {
    description = "Name of the created YouTube cookies secret"
    value       = aws_secretsmanager_secret.youtube_cookies_secret.name
}

output "secret_reader_iam_user_name" {
    description = "IAM user restricted to reading the bot secret"
    value       = var.create_secret_reader_user ? aws_iam_user.secret_reader[0].name : null
}

output "secret_reader_access_key_id" {
    description = "Access key ID for the restricted IAM user"
    value       = var.create_secret_reader_user && var.create_secret_reader_access_key ? aws_iam_access_key.secret_reader[0].id : null
    sensitive   = true
}

output "secret_reader_secret_access_key" {
    description = "Secret access key for the restricted IAM user"
    value       = var.create_secret_reader_user && var.create_secret_reader_access_key ? aws_iam_access_key.secret_reader[0].secret : null
    sensitive   = true
}