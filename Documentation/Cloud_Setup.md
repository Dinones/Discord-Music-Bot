## 📋ㅤTable of Contents

- [🪣ㅤCreate the S3 Backend Bucket (One Time Only)](#s3-backend)
- [🗂️ㅤConfigure the Shared Terraform State](#terraform-state)
- [📦ㅤWhat This Terraform Creates](#what-creates)
- [📥ㅤInstall the Required Tools](#install-tools)
  - [🪟ㅤWindows Environment](#windows)
  - [🐧ㅤUbuntu Environment](#ubuntu)
- [🔐ㅤAuthenticate to AWS](#authenticate)
- [🛠️ㅤRun Terraform](#run-terraform)
  - [🚀ㅤInitialize Terraform](#init)
  - [🔎ㅤPreview the Changes](#plan)
  - [🏗️ㅤApply the Infrastructure](#apply)
- [🪪ㅤRetrieve the Limited IAM Credentials](#credentials)
- [🔑ㅤFill the Secret Values in AWS](#fill-secrets)
  - [🔐ㅤFill `discord_music_bot_secrets`](#fill-bot-secret)
  - [🔐ㅤFill `discord_music_bot_youtube_cookies`](#fill-cookies-secret)

<br><br>

# ☁️ㅤCloud Setup

This guide explains how to run the Terraform in the `Cloud/` folder from zero and how to safely apply future changes without duplicating AWS resources or overwriting any existing value/file.

> [!TIP]
> Once the AWS infrastructure is set up, configure billing alerts and a budget hard-block to protect against unexpected charges. See <a href="./AWS_Cost_Protection.md">AWS_Cost_Protection.md</a>.

<br>

<a id="s3-backend"></a>

## 🪣ㅤCreate the S3 Backend Bucket (One Time Only)

Before running the main Terraform, create an empty S3 bucket manually in AWS. This only has to be done once because this bucket will store the shared Terraform state for the project.

Why this is done:

- Terraform uses the state file to remember which AWS resources it already manages.
- If the state is shared in S3, different computers can run the same Terraform safely.
- If every computer uses a different local state file, Terraform can lose track of existing AWS resources and try to create new ones again, duplicating and overwriting them.

The bucket can be empty at the beginning. Terraform will create the state object inside the bucket on the first successful run. The bucket must already exist before Terraform can use it as a remote backend.

How to create it in AWS Console:

1. Open `AWS Console`.
2. Go to `S3`.
3. Click `Create bucket`.
4. Use these recommended settings:

   - `AWS Region`: `Europe (Ireland) eu-west-1`
   - `Bucket type`: `General purpose`
   - `Bucket namespace`: `Account Regional namespace`
   - `Object Ownership`: `ACLs disabled`
   - `Block all public access`: Tick the box
   - `Bucket Versioning`: `Enable`
   - `Tags`: Optional
   - `Default encryption`: `Server-side encryption with Amazon S3 managed keys (SSE-S3)`
   - `Bucket Key`: `Enable`

5. Choose an appropriate bucket name.
6. Click `Create bucket`.

<br>

<a id="terraform-state"></a>

## 🗂️ㅤConfigure the Shared Terraform State

This project now uses the shared S3 backend bucket:

- Bucket: provided during `terraform init`
- State path inside the bucket: `terraform.tfstate`
- Region: `eu-west-1`

This means Terraform will automatically:

- Check whether the remote state already exists in that bucket.
- Use it if it already exists or create it there on the first successful apply if the bucket is still empty.
- Update the same shared state after every future apply.

You do **NOT** need to manually download or upload the `terraform.tfstate` file.

<br>

<a id="what-creates"></a>

## 📦ㅤWhat This Terraform Creates

The Terraform in this project currently creates:

- One AWS Secrets Manager secret for the bot JSON configuration.
- One AWS Secrets Manager secret for the YouTube cookies file.
- One restricted IAM user that can read only those two secrets.
- One access key for that restricted IAM user that will allow the server to authenticate with that IAM user.
- One `extra-commands/` folder in S3 and the corresponding IAM read permissions (only when `extra_commands_bucket` is set in `terraform.tfvars`).

> [!NOTE]
> The Terraform creates the secret containers, but not their values. That means both secret values must be filled manually in AWS. Read section [Fill the Secret Values in AWS](#fill-secrets).

<br>

<a id="install-tools"></a>

## 📥ㅤInstall the Required Tools

Install **Terraform** and **AWS CLI**.

<a id="windows"></a>

### 🪟ㅤWindows Environment

```bash
choco install terraform awscli -y
```

<a id="ubuntu"></a>

### 🐧ㅤUbuntu Environment

```bash
sudo apt-get update
sudo apt-get install -y unzip gpg curl

sudo rm -f /usr/share/keyrings/hashicorp-archive-keyring.gpg
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update
sudo apt-get install -y terraform

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -o awscliv2.zip
sudo ./aws/install --update
```

Check everything was installed correctly by running:

```bash
aws --version
terraform --version
```

You can now safely delete any downloaded folders like `aws/` or `awscliv2.zip`.

<br>

<a id="authenticate"></a>

## 🔐ㅤAuthenticate to AWS

Before running Terraform, authenticate with an AWS identity that has permission to read the S3 bucket mentioned before and create:

- Secrets Manager secrets
- Secrets Manager secret values
- IAM users
- IAM policies
- IAM access keys

Use the following command to authenticate:
```bash
aws configure
```

> [!CAUTION]
> Please, do **NOT** use your root account to run the Terraform. Use an account that follows the AWS least-privilege principles.

<br>

<a id="run-terraform"></a>

## 🛠️ㅤRun Terraform

<a id="init"></a>

### 🚀ㅤInitialize Terraform

Open a terminal in the root folder and run:

```bash
cd Cloud/
terraform init -reconfigure -backend-config="bucket=bucket-name"
```

> [!WARN]
> Please, note that `"bucket=bucket-name"` contains the key `"bucket=..."`.

What this does:

- Downloads the AWS provider.
- Prepares the local Terraform working directory.
- Creates the `.terraform/` working files Terraform needs.
- Connects Terraform to the shared S3 backend.
- Uses the existing remote state automatically if it already exists.
- Prepares the first remote state file if the bucket is empty.

<hr>

<a id="plan"></a>

### 🔎ㅤPreview the Changes

Now, preview the changes by running:

```bash
terraform plan
```

This is one of the most important commands. It shows what Terraform wants to do before it changes AWS. 

If the plan shows something unexpected, stop there and review it before applying.

<hr>

<a id="apply"></a>

### 🏗️ㅤApply the Infrastructure

Run:

```bash
terraform apply
```

Terraform will show the execution plan again and ask for confirmation.

Type:

```text
yes
```

After that, Terraform will create the AWS resources defined in the `Cloud/` folder.

<br>

<a id="credentials"></a>

## 🪪ㅤRetrieve the Limited IAM Credentials

After `terraform apply`, you can retrieve the credentials of the restricted IAM user with:

```bash
terraform output -raw secret_reader_access_key_id
terraform output -raw secret_reader_secret_access_key
```

Then configure that IAM user on the server with:

```bash
aws configure
```

Set:

- AWS Access Key ID
- AWS Secret Access Key
- Default region: `eu-west-1`
- Default output format: `json`

> [!WARNING]  
> If Terraform created the secret access key, it may also be stored in the Terraform state. Keep the state file private and secure.

<br>

<a id="fill-secrets"></a>

## 🔑ㅤFill the Secret Values in AWS
<a id="sec:fill-secret-value"></a>

After the secrets have been created, go to:

`AWS Console` → `Secrets Manager` **→** *Select the secret* → `Edit secret value`

<hr>

<a id="fill-bot-secret"></a>

### 🔐ㅤFill `discord_music_bot_secrets`

Set the JSON content with:

```json
{
    "DISCORD_MUSIC_BOT_TOKEN_PROD" : "",
    "DISCORD_MUSIC_BOT_TOKEN_DEV"  : "",

    "SPOTIFY_CLIENT_ID"            : "",
    "SPOTIFY_CLIENT_SECRET"        : "",

    "BOT_ACTIVITY_NAME"            : "",
    "DISCORD_SERVER_NAME"          : "",
    "DISCORD_TEXT_CHANNEL_PROD"    : "",
    "DISCORD_TEXT_CHANNEL_DEV"     : "",

    "S3_EXTRA_COMMANDS_BUCKET"     : "",   // Name of the S3 bucket — enables Extra_Commands download at startup
    "SPOTIFY_PLAYLISTS"            : []    // Array of {"name": "...", "url": "..."} objects shown as buttons by !playlists
}
```

> [!NOTE]
> Terraform does not manage this secret value, so if the JSON is filled manually and Terraform is run again later, Terraform should not replace it with an empty JSON object.

<hr>

<a id="fill-cookies-secret"></a>

### 🔐ㅤFill `discord_music_bot_youtube_cookies`

1. Extract the session Youtube cookies from your browser as explained in <a href="./Youtube_Cookies.md">Youtube_Cookies.md</a>.
2. Paste the full Netscape cookies content in the AWS secret.

> [!NOTE]
> Keep the cookies content exactly as exported (including header/comments and line breaks). Terraform does not manage this secret value either.
