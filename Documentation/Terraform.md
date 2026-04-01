# Install Terraform and AWS CLI

Install Terraform and AWS CLI using a PowerShell by running:

```bash
choco install terraform awscli -y
```

# Log in to AWS CLI

Log in to AWS CLI by running:

```bash
aws login
```

The region is `eu-west-1` (Ireland).

# Execute Terraform

Execute Terraform by running:

```bash
cd Cloud
terraform init
terraform plan
terraform apply
```

# What Terraform Creates

Terraform creates:

- The AWS Secrets Manager secret used by the bot
- An IAM user that can only call `secretsmanager:GetSecretValue` on that specific secret
- An access key for that IAM user so the server can authenticate without using your broader admin identity

This IAM user is not a separate AWS account. It is a restricted IAM user inside your AWS account.

# Retrieve the Limited Credentials

After `terraform apply`, get the generated credentials with:

```bash
terraform output -raw secret_reader_access_key_id
terraform output -raw secret_reader_secret_access_key
```

Use them on the server with:

```bash
aws configure
```

Set:

- AWS Access Key ID: value from `secret_reader_access_key_id`
- AWS Secret Access Key: value from `secret_reader_secret_access_key`
- Default region name: `eu-west-1`
- Default output format: `json`

Important: the generated secret access key is sensitive and is also stored in the Terraform state file. Keep the state file private and secure.

# Set Secret Values

Go to `AWS Console` → `Secrets Manager` → _Select the created secret_ → `Edit secret value`. Set the secret value as a JSON object:

```json
{
    "DISCORD_MUSIC_BOT_TOKEN_PROD" : "",
    "DISCORD_MUSIC_BOT_TOKEN_DEV"  : "",
    "BOT_ACTIVITY_NAME"            : "",
    "SPOTIFY_CLIENT_ID"            : "",
    "SPOTIFY_CLIENT_SECRET"        : ""
}
```
