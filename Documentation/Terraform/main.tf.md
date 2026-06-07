## 📋⠀Table of Contents

- [🧩⠀terraform { ... }](#terraform-block)
- [🧩⠀provider "aws" { ... }](#provider)
- [🧩⠀resource "aws_secretsmanager_secret" "discord_bot_secret" { ... }](#secret)
- [🧩⠀resource "aws_secretsmanager_secret" "youtube_cookies_secret" { ... }](#yt-secret)
- [🧩⠀data "aws_iam_policy_document" "secret_reader" { ... }](#policy-doc)
- [🧩⠀resource "aws_iam_user" "secret_reader" { ... }](#iam-user)
- [🧩⠀resource "aws_iam_user_policy" "secret_reader" { ... }](#user-policy)
- [🧩⠀resource "aws_iam_access_key" "secret_reader" { ... }](#access-key)

<br><br>

# 📜⠀main.tf

This file contains the main infrastructure definition. It tells Terraform which provider to use and which AWS resources should exist.

<br>

<a id="terraform-block"></a>

## 🧩⠀terraform { ... }

This block configures Terraform itself. This tells Terraform that this project uses the AWS provider.

```terraform
terraform {
    required_version = ">= 1.5.0"

    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}
```

<br>

<a id="provider"></a>

## 🧩⠀provider "aws" { ... }

This block tells Terraform how to connect to AWS. Terraform will create resources in the AWS region stored in the variable `aws_region`.

```terraform
provider "aws" {
    region = var.aws_region
}
```

<br>

<a id="secret"></a>

## 🧩⠀resource "aws_secretsmanager_secret" "discord_bot_secret" { ... }

This block creates the AWS Secrets Manager secret itself. This creates the secret container and metadata, not the JSON value inside the secret.

```terraform
resource "aws_secretsmanager_secret" "discord_bot_secret" {
    name                    = var.secret_name
    description             = "Discord Music Bot Token"
    recovery_window_in_days = 7

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}
```

- `name`: This gives the secret its name stored the variable `secret_name`.
- `description`: This is just a human-readable description shown in AWS.
- `recovery_window_in_days`: If the secret is deleted, AWS keeps it recoverable for 7 days before permanent deletion. This is a safety feature in case the secret is deleted by mistake.
- `tags`: These tags help identify the resource in AWS:
    - `Project = var.project_name` marks which project owns the resource
    - `Managed = "Terraform"` marks that Terraform is responsible for it

<br>

<a id="yt-secret"></a>

## 🧩⠀resource "aws_secretsmanager_secret" "youtube_cookies_secret" { ... }

This block creates a second AWS Secrets Manager secret used to store the YouTube cookies file.

```terraform
resource "aws_secretsmanager_secret" "youtube_cookies_secret" {
    name                    = var.youtube_cookies_secret_name
    description             = "Discord Music Bot YouTube Cookies"
    recovery_window_in_days = 7

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}
```

- `name`: This gives the YouTube cookies secret its name from `youtube_cookies_secret_name`.
- `description`: Human-readable description shown in AWS.
- `recovery_window_in_days`: Recovery window before permanent deletion.
- `tags`: Same ownership/management tags as the other resources.

<br>

<a id="policy-doc"></a>

## 🧩⠀data "aws_iam_policy_document" "secret_reader" { ... }

This is a data block, not a real AWS resource. Its job is to build a JSON IAM policy document that can later be attached to an IAM user.

```terraform
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
```

- `statement`: An IAM policy is made of one or more statements.
    - `sid = "ReadOnlyBotSecrets"`: Statement ID to help identify this policy rule.
    - `effect = "Allow"`: This means the policy allows the action listed below.
    - `actions`: AWS actions that the IAM user is allowed to perform.
        - `"secretsmanager:GetSecretValue"`: It allows the user to read the content of a secret from AWS Secrets Manager.
    - `resources`: Resources the IAM user is able to perform the specified actions to.
        - `aws_secretsmanager_secret.discord_bot_secret.arn`: Permission to read the bot JSON secret containing the tokens.
        - `aws_secretsmanager_secret.youtube_cookies_secret.arn`: Permission to read the YouTube cookies secret.

This is the most important least-privilege part of the design:

- The user can read only these two secrets.
- The user cannot read other secrets.
- The user cannot manage other AWS resources.

<br>

<a id="iam-user"></a>

## 🧩⠀resource "aws_iam_user" "secret_reader" { ... }

This block creates a restricted IAM user for the server.

```terraform
resource "aws_iam_user" "secret_reader" {
    count = var.create_secret_reader_user ? 1 : 0

    name = var.secret_reader_user_name

    tags = {
        Project = var.project_name
        Managed = "Terraform"
    }
}
```

- `count = var.create_secret_reader_user ? 1 : 0`: This is conditional creation.
    - If `create_secret_reader_user` is `true`, Terraform creates one user.
    - If `create_secret_reader_user` is `false`, Terraform creates no user.
    - This gives flexibility if want to disable that user without deleting the rest of the Terraform code.
- `name`: This sets the IAM username using the variable `secret_reader_user_name`.
- `tags`: These tags serve the same purpose as on the secret: identifying ownership and Terraform management.

<br>

<a id="user-policy"></a>

## 🧩⠀resource "aws_iam_user_policy" "secret_reader" { ... }

This block attaches the policy document to the IAM user as an inline policy.

```terraform
resource "aws_iam_user_policy" "secret_reader" {
    count = var.create_secret_reader_user ? 1 : 0

    name   = "${var.secret_reader_user_name}-read-secret"
    user   = aws_iam_user.secret_reader[0].name
    policy = data.aws_iam_policy_document.secret_reader.json
}
```

- `count = var.create_secret_reader_user ? 1 : 0`: This follows the same condition as the user resource, so the policy is only created when the user exists.
- `name`: This gives the policy a readable name based on the username.
- `user`: This attaches the policy to the IAM user created above. The `[0]` is used because the user resource uses `count`, so Terraform treats it like a list with either:
    - One item at index `0`.
    - No items at all.
- `policy`: This uses the policy document built earlier in the `data "aws_iam_policy_document"` block.

<a id="access-key"></a>

## 🧩⠀resource "aws_iam_access_key" "secret_reader" { ... }

This block creates an AWS access key for the restricted IAM user. This is what allows the server to authenticate with that IAM user.

```terraform
resource "aws_iam_access_key" "secret_reader" {
    count = var.create_secret_reader_user && var.create_secret_reader_access_key ? 1 : 0

    user = aws_iam_user.secret_reader[0].name
}
```

- `count = var.create_secret_reader_user && var.create_secret_reader_access_key ? 1 : 0`: This resource is created only when both conditions are true:
    - The IAM user should exist.
    - An access key should be created.
- `user`: This says the access key belongs to the restricted IAM user.
