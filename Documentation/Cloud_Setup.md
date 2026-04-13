# ☁️ㅤCloud Setup

This guide explains how to run the Terraform in the `Cloud/` folder from zero and how to safely apply future changes without duplicating AWS resources or overwriting any existing value/file.

<br>

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

## 🗂️ㅤConfigure the Shared Terraform State

This project now uses the shared S3 backend bucket:

- Bucket: provided during `terraform init`
- State path inside the bucket: `discord-music-bot/terraform.tfstate`
- Region: `eu-west-1`

This means Terraform will automatically:

- Check whether the remote state already exists in that bucket.
- Use it if it already exists or create it there on the first successful apply if the bucket is still empty.
- Update the same shared state after every future apply.

You do **NOT** need to manually download or upload the `terraform.tfstate` file.

<br>

## 📦ㅤWhat This Terraform Creates

The Terraform in this project currently creates:

- One AWS Secrets Manager secret.
- One restricted IAM user that can read only that secret.
- One access key for that restricted IAM user that will allow the server to authenticate with that IAM user.

> [!NOTE]
> The Terraform creates the secret itself, but not the JSON content inside the secret. That means the secret value must be filled manually in AWS. Read section [Fill the Secret Value in AWS](#sec:fill-secret-value).

<br>

## 📥ㅤInstall the Required Tools

Install **Terraform** and **AWS CLI**.

### Windows environment

```bash
choco install terraform awscli -y
```

### Ubuntu environment

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

## 🔐ㅤAuthenticate to AWS

Before running Terraform, authenticate with an AWS identity that has permission to read the S3 bucket mentioned before and create:

- Secrets Manager secrets
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

## 🛠️ㅤRun Terraform

### 🚀ㅤInitialize Terraform

Open a terminal in the `Cloud/` and run:

```bash
cd Cloud/
terraform init -migrate-state -backend-config="bucket=bucket-name"
```

> [!CAUTION]
> Please, note that `"bucket=bucket-name"` contains the key `"bucket=..."`.

What this does:

- Downloads the AWS provider.
- Prepares the local Terraform working directory.
- Creates the `.terraform/` working files Terraform needs.
- Connects Terraform to the shared S3 backend.
- Uses the existing remote state automatically if it already exists.
- Prepares the first remote state file if the bucket is empty.

<hr>

### 🔎ㅤPreview the Changes

Now, preview the changes by running:

```bash
terraform plan
```

This is one of the most important commands. It shows what Terraform wants to do before it changes AWS. 

If the plan shows something unexpected, stop there and review it before applying.

<hr>

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

## 🔑ㅤFill the Secret Value in AWS
<a id="sec:fill-secret-value"></a>

After the secret has been created, go to:

`AWS Console` → `Secrets Manager` **→** *Select the secret* → `Edit secret value`

Set the JSON content with:

```json
{
    "DISCORD_MUSIC_BOT_TOKEN_PROD" : "",
    "DISCORD_MUSIC_BOT_TOKEN_DEV"  : "",
    "BOT_ACTIVITY_NAME"            : "",
    "SPOTIFY_CLIENT_ID"            : "",
    "SPOTIFY_CLIENT_SECRET"        : ""
}
```

> [!NOTE]
> The current Terraform does not manage this JSON value, so if the file is filled manually and Terraform is run again later, Terraform should not replace it with an empty JSON object.