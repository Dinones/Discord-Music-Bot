## 📋⠀Table of Contents

- [🧩⠀terraform { backend "s3" { ... } }](#backend-block)
- [🔎⠀What Happens in Practice](#practice)

<br><br>

# 📜⠀backend.tf

This file configures where Terraform stores its state. Terraform state is the file that remembers which AWS resources Terraform already manages. Without a shared state file, different computers can lose track of the same infrastructure and try to recreate it.

<br>

<a id="backend-block"></a>

## 🧩⠀terraform { backend "s3" { ... } }

This block tells Terraform to use Amazon S3 as the remote backend for its state. That means Terraform will use the shared state in S3 instead of relying only on a local `terraform.tfstate` file.

```terraform
terraform {
    backend "s3" {
        key          = "discord-music-bot/terraform.tfstate"
        region       = "eu-west-1"
        use_lockfile = true
        encrypt      = true
    }
}
```

- `bucket`: This is the S3 bucket where Terraform stores the shared state. It is intentionally omitted from the file for security reasons in a public repository. The bucket name will be specified in the `terraform init` command.
- `key`: This is the object path inside the S3 bucket.
- `region`: This tells Terraform which AWS region contains the S3 bucket.
- `use_lockfile`: This enables state locking for the S3 backend. State locking helps prevent two Terraform operations from modifying the same state at the same time.
- `encrypt`: This tells Terraform to request server-side encryption for the state object stored in S3.

<br>

<a id="practice"></a>

## 🔎⠀What Happens in Practice

When you run:

```bash
terraform init -backend-config="bucket=bucket-name"
```

Terraform will:

1. Connect to the S3 bucket.
2. Check whether the state object already exists.
3. Use it if it exists.
4. Prepare to create it on the first successful apply if it does not exist yet.

<hr>

When you run:

```bash
terraform apply
```

Terraform will:

1. Read the current remote state.
2. Compare it with the Terraform code.
3. Apply the AWS changes.
4. Write the updated state back to S3.
