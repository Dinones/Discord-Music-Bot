output "secret_arn" {
    description = "Unique ID of the created secret"
    value       = aws_secretsmanager_secret.app.arn
}

output "secret_name" {
    description = "Name of the created secret"
    value       = aws_secretsmanager_secret.app.name
}