## 📋⠀Table of Contents

- [🧩⠀aws_region](#aws-region)
- [🧩⠀project_name](#project-name)
- [🧩⠀secret_name](#secret-name)
- [🧩⠀youtube_cookies_secret_name](#yt-secret-name)
- [🧩⠀create_secret_reader_user](#create-user)
- [🧩⠀secret_reader_user_name](#user-name)
- [🧩⠀create_secret_reader_access_key](#create-key)

<br><br>

# 📜⠀variables.tf

This file defines input variables to change values without rewriting the Terraform resources.

<br>

<a id="aws-region"></a>

## 🧩⠀aws_region

This variable defines the AWS region where Terraform will create resources.

```terraform
variable "aws_region" {
    type        = string
    description = "AWS region where the secret will be created"
    default     = "eu-west-1"
}
```

<br>

<a id="project-name"></a>

## 🧩⠀project_name

This variable stores the project name used in AWS tags.

```terraform
variable "project_name" {
    type        = string
    description = "Project tag name"
    default     = "Discord Music Bot"
}
```

<br>

<a id="secret-name"></a>

## 🧩⠀secret_name

This variable sets the name of the Secrets Manager secret.

```terraform
variable "secret_name" {
    type        = string
    description = "Name of the Secrets Manager secret"
    default     = "discord_music_bot_secrets"
}
```

<br>

<a id="yt-secret-name"></a>

## 🧩⠀youtube_cookies_secret_name

This variable sets the name of the Secrets Manager secret used for YouTube cookies.

```terraform
variable "youtube_cookies_secret_name" {
    type        = string
    description = "Name of the Secrets Manager secret that stores YouTube cookies"
    default     = "discord_music_bot_youtube_cookies"
}
```

<br>

<a id="create-user"></a>

## 🧩⠀create_secret_reader_user

This variable controls whether Terraform should create the restricted IAM user. If set to `false`, Terraform will skip the IAM user and anything that depends on it.

```terraform
variable "create_secret_reader_user" {
    type        = bool
    description = "Whether Terraform should create an IAM user limited to reading the bot secret"
    default     = true
}
```

<br>

<a id="user-name"></a>

## 🧩⠀secret_reader_user_name

This variable defines the username for the restricted IAM user that reads both bot and cookies secrets.

```terraform
variable "secret_reader_user_name" {
    type        = string
    description = "Name of the IAM user that can only read the bot secret"
    default     = "discord_music_bot_secret_reader"
}
```

<br>

<a id="create-key"></a>

## 🧩⠀create_secret_reader_access_key

This variable controls whether Terraform should generate an access key for the restricted IAM user. If set to `false`, the IAM user can still be created, but Terraform will not generate programmatic credentials for it.

```terraform
variable "create_secret_reader_access_key" {
    type        = bool
    description = "Whether Terraform should create an access key for the limited IAM user"
    default     = true
}
```
