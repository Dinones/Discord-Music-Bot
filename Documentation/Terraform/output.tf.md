# `Cloud/output.tf`

This file defines Terraform outputs.

Outputs are values Terraform prints or makes available after `terraform apply`.  
They are useful when you need to know what Terraform created.

## `output "secret_arn" { ... }`

This output exposes the ARN of the created secret.

### `description = "Unique ID of the created secret"`

This is the text Terraform shows to explain the output.

### `value = aws_secretsmanager_secret.app.arn`

This returns the ARN of the secret resource created in `main.tf`.

An ARN is the full AWS identifier for a resource.

## `output "secret_name" { ... }`

This output exposes the secret name.

### `value = aws_secretsmanager_secret.app.name`

This returns the human-readable secret name, such as `discord_music_bot_secrets`.

## `output "secret_reader_iam_user_name" { ... }`

This output shows the name of the restricted IAM user, if that user is enabled.

### `value = var.create_secret_reader_user ? aws_iam_user.secret_reader[0].name : null`

This is a conditional expression:

- if the IAM user is enabled, Terraform returns the username
- if the IAM user is disabled, Terraform returns `null`

`null` means "there is no value here".

## `output "secret_reader_access_key_id" { ... }`

This output shows the access key ID for the restricted IAM user.

### `value = ... aws_iam_access_key.secret_reader[0].id : null`

If the access key exists, Terraform returns the key ID.  
If not, Terraform returns `null`.

### `sensitive = true`

This tells Terraform to hide the value from normal console output because it is security-related.

Even though the access key ID is less sensitive than the secret access key, hiding it is still a cautious choice.

## `output "secret_reader_secret_access_key" { ... }`

This output shows the secret access key for the restricted IAM user.

### `value = ... aws_iam_access_key.secret_reader[0].secret : null`

If the access key exists, Terraform returns the secret key.  
If not, Terraform returns `null`.

### `sensitive = true`

This is very important.

The secret access key should not be printed openly in logs or terminals unless you intentionally request it.

That is why the documentation uses:

```bash
terraform output -raw secret_reader_secret_access_key
```

## Why Outputs Matter

Outputs make it easier to use Terraform-created resources afterward.

In this project, the outputs help you:

- identify the secret
- see the IAM username
- retrieve the server credentials after deployment

without needing to search manually through the AWS Console.
