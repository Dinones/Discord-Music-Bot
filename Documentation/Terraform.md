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

# Execute Terraform

Execute Terraform by running:

```bash
cd Cloud
terraform init
terraform plan
terraform apply
```

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