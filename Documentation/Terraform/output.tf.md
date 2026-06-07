## 📋⠀Table of Contents

- [🧩⠀output "secret_arn" { ... }](#secret-arn)
- [🧩⠀output "secret_name" { ... }](#secret-name)
- [🧩⠀output "youtube_cookies_secret_arn" { ... }](#yt-secret-arn)
- [🧩⠀output "youtube_cookies_secret_name" { ... }](#yt-secret-name)
- [🧩⠀output "secret_reader_iam_user_name" { ... }](#user-name)
- [🧩⠀output "secret_reader_access_key_id" { ... }](#access-key-id)
- [🧩⠀output "secret_reader_secret_access_key" { ... }](#secret-access-key)

<br><br>

# 📜⠀output.tf

This file defines Terraform outputs. Outputs are values Terraform prints or makes available after `terraform apply`. They are useful when you need to know what Terraform created.

<br>

<a id="secret-arn"></a>

## 🧩⠀output "secret_arn" { ... }

This output exposes the ARN of the created secret.

```terraform
output "secret_arn" {
    description = "Unique ID of the created secret"
    value       = aws_secretsmanager_secret.discord_bot_secret.arn
}
```

- `value`: This returns the ARN (AWS Resource Name) of the secret resource created in `main.tf`.

<br>

<a id="secret-name"></a>

## 🧩⠀output "secret_name" { ... }

This output exposes the secret name.

```terraform
output "secret_name" {
    description = "Name of the created secret"
    value       = aws_secretsmanager_secret.discord_bot_secret.name
}
```

- `value = aws_secretsmanager_secret.discord_bot_secret.name`: This returns the human-readable secret name, such as `discord_music_bot_secrets`.

<br>

<a id="yt-secret-arn"></a>

## 🧩⠀output "youtube_cookies_secret_arn" { ... }

This output exposes the ARN of the YouTube cookies secret.

```terraform
output "youtube_cookies_secret_arn" {
    description = "Unique ID of the created YouTube cookies secret"
    value       = aws_secretsmanager_secret.youtube_cookies_secret.arn
}
```

- `value`: This returns the ARN of the YouTube cookies secret resource created in `main.tf`.

<br>

<a id="yt-secret-name"></a>

## 🧩⠀output "youtube_cookies_secret_name" { ... }

This output exposes the name of the YouTube cookies secret.

```terraform
output "youtube_cookies_secret_name" {
    description = "Name of the created YouTube cookies secret"
    value       = aws_secretsmanager_secret.youtube_cookies_secret.name
}
```

- `value`: This returns the human-readable secret name, such as `discord_music_bot_youtube_cookies`.

<br>

<a id="user-name"></a>

## 🧩⠀output "secret_reader_iam_user_name" { ... }

This output shows the name of the restricted IAM user (bot/cookies read-only), if that user is enabled.

```terraform
output "secret_reader_iam_user_name" {
    description = "IAM user restricted to reading the bot secret"
    value       = var.create_secret_reader_user ? aws_iam_user.secret_reader[0].name : null
}
```

- `value`: This is a conditional expression:
  - if the IAM user is enabled, Terraform returns the username
  - if the IAM user is disabled, Terraform returns `null`

<br>

<a id="access-key-id"></a>

## 🧩⠀output "secret_reader_access_key_id" { ... }

This output shows the access key ID for the restricted IAM user.

```terraform
output "secret_reader_access_key_id" {
    description = "Access key ID for the restricted IAM user"
    value       = var.create_secret_reader_user && var.create_secret_reader_access_key ? aws_iam_access_key.secret_reader[0].id : null
    sensitive   = true
}
```

- `value`: 
    - If the access key exists, Terraform returns the key ID.
    - If not, Terraform returns `null`.
- `sensitive`: This tells Terraform to hide the value from normal console output because it is security-related. Even though the access key ID is less sensitive than the secret access key, hiding it is still a cautious choice.

<br>

<a id="secret-access-key"></a>

## 🧩⠀output "secret_reader_secret_access_key" { ... }

This output shows the secret access key for the restricted IAM user.

```terraform
output "secret_reader_secret_access_key" {
    description = "Secret access key for the restricted IAM user"
    value       = var.create_secret_reader_user && var.create_secret_reader_access_key ? aws_iam_access_key.secret_reader[0].secret : null
    sensitive   = true
}
```

- `value = ... aws_iam_access_key.secret_reader[0].secret : null`
    - If the access key exists, Terraform returns the secret key.
    - If not, Terraform returns `null`.
- `sensitive`: This is very important. The secret access key should not be printed openly in logs or terminals unless you intentionally request it.
