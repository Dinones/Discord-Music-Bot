# ☁️ㅤCloud Setup

This guide explains how to run the Terraform in the `Cloud/` folder from zero and how to safely apply future changes without duplicating AWS resources or overwriting any existing value/file.

<br>

## 📦ㅤWhat This Terraform Creates

The Terraform in this project currently creates:

- One AWS Secrets Manager secret.
- One restricted IAM user that can read only that secret.
- One access key for that restricted IAM user that will allow the server to authenticate with that IAM user.

> [!NOTE]
> The Terraform creates the secret itself, but not the JSON content inside the secret. That means the secret value must be filled manually in AWS.

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

Before running Terraform, authenticate with an AWS identity that has permission to create:

- Secrets Manager secrets
- IAM users
- IAM policies
- IAM access keys

> [!CAUTION]
> Please, do **NOT** use your root account to run the Terraform. Use an account that follows the AWS least-privilege principles.

<br>

## 🛠️ㅤRun Terraform

### Initialize Terraform

Open a terminal in the `Cloud/` and run:

```bash
terraform init
```

What this does:

- Downloads the AWS provider.
- Prepares the local Terraform working directory.
- Creates the `.terraform/` working files Terraform needs.

### Preview the Changes

Now, preview the changes by running:

```bash
terraform plan
```

This is one of the most important commands. It shows what Terraform wants to do before it changes AWS. 

If the plan shows something unexpected, stop there and review it before applying.

### Apply the Infrastructure

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
> If Terraform created the secret access key, it is also stored in Terraform state. Keep the state file private and secure.

<br>

## 🔑ㅤFill the Secret Value in AWS

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

<br>

## 10. What Happens If You Run Terraform Again Later

This is the part that usually worries people when they are new to Terraform.

If you keep using the same Terraform state and the same AWS account:

- Terraform will not duplicate resources it already manages
- Terraform will compare the code with the existing state
- Terraform will only create, update, or destroy what has actually changed

So if you already created:

- the secret
- the restricted IAM user
- the access key

and then run `terraform plan` or `terraform apply` again without changing the code, Terraform should show no changes.

## 11. Example: You Add a New AWS Resource Later

Imagine that in the future you add a new Terraform block, such as:

- another IAM user
- another output
- another AWS resource

The normal workflow is:

```bash
cd Cloud
terraform plan
terraform apply
```

Terraform will:

- keep the existing managed resources
- create only the new resource
- update only the resources whose configuration changed

It should not duplicate the original secret or IAM user just because you ran `apply` again.

## 12. Why the Secret Value Is Not Being Overwritten

In the current Terraform code, there is an `aws_secretsmanager_secret` resource, but there is no `aws_secretsmanager_secret_version` resource.

That means Terraform is managing:

- the existence of the secret
- its metadata, such as name and tags

but not:

- the JSON content stored inside the secret

Because of that, manually editing the secret value in AWS Console is safe with the current Terraform setup.

## 13. When Duplicates or Conflicts Can Happen

Terraform is safe when the state is correct, but conflicts can happen in these situations:

### A. The resource already exists in AWS, but Terraform has never tracked it

Example:

- you manually created the secret in AWS first
- then you run this Terraform for the first time

Terraform may try to create the same resource name and fail, because it does not automatically adopt existing resources.

In that case, you usually need to import the existing resource into Terraform state instead of creating it again.

### B. You lose the Terraform state

If the state file is lost, deleted, or replaced with another empty state:

- Terraform may think nothing exists
- it may try to create resources again
- AWS may reject that because names already exist

So keeping Terraform state safe is extremely important.

### C. You intentionally change resource names

If you rename resources such as:

- the secret name
- the IAM user name

Terraform may interpret that as:

- create a new resource
- replace the old one

This depends on the specific resource and change.

That is why you should always check `terraform plan` before `terraform apply`.

## 14. Safe Workflow for Future Changes

Whenever you change the Terraform code, use this workflow:

```bash
cd Cloud
terraform plan
terraform apply
```

Safe habits:

- Always run `terraform plan` first
- Read the plan carefully before applying
- Keep the Terraform state file safe
- Do not manually delete managed resources in AWS unless you also update Terraform
- If a resource already exists outside Terraform, import it instead of trying to recreate it

## 15. Practical Answer to Your Main Concern

If you:

1. run Terraform now
2. let it create the secret and IAM user
3. manually fill the secret value in AWS
4. later change Terraform to add another resource
5. run `terraform plan` and `terraform apply` again

then with the current setup:

- Terraform should not duplicate the existing secret
- Terraform should not duplicate the existing IAM user
- Terraform should not replace the secret value with a blank JSON file

That is true as long as:

- you are using the same Terraform state
- you did not change the secret resource into one that manages the secret content directly
- the plan does not show a replacement you were not expecting

## 16. Recommended Habit

Before every real apply, look closely at:

```bash
terraform plan
```

If the plan says:

- `No changes`, Terraform will do nothing
- `1 to add`, it will create something new
- `1 to change`, it will update something existing
- `1 to destroy`, pause and review carefully before continuing
