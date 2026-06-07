## 📋ㅤTable of Contents

- [📊ㅤAWS Budgets Action](#budgets)
  - [1️⃣ Create the "Panic Deny" IAM Policy](#panic-policy)
  - [2️⃣ Create the Budget Actions IAM Role](#budgets-role)
  - [3️⃣ Create the Budget](#create-budget)
- [🔔ㅤCloudWatch Billing Alarm](#cloudwatch)
  - [1️⃣ Enable Billing Alerts](#billing-alerts)
  - [2️⃣ Create the Alarm](#create-alarm)
- [🤖ㅤAWS Cost Anomaly Detection](#anomaly)

<br><br>

# 🛡️ㅤAWS Cost Protection

Three-layer setup to detect and block unexpected AWS charges. Set all three up for full coverage.

| Layer | Delay | Action |
|---|---|---|
| Cost Anomaly Detection | ~1-2 hours | Email alert |
| CloudWatch Billing Alarm | ~6 hours | Email alert |
| AWS Budgets Action | ~24 hours | Hard IAM block on user |

<br>

<a id="budgets"></a>

## 📊ㅤAWS Budgets Action

Attaches a deny IAM policy to your admin user when actual charges exceed the budget threshold.

<a id="panic-policy"></a>

### 1️⃣ Create the "Panic Deny" IAM Policy

1. Go to `AWS Console` → `IAM` → `Policies` → `Create policy`.
2. Choose `JSON` and paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "StringNotEquals": {
                    "aws:RequestedRegion": []
                }
            }
        }
    ]
}
```

> [!NOTE]
> Customize the deny scope as needed. At minimum, keep `iam:DetachUserPolicy` allowed on the policy itself so you can recover without using root.

3. Name it `BudgetPanicDeny`.

<hr>

<a id="budgets-role"></a>

### 2️⃣ Create the Budget Actions IAM Role

1. Go to `IAM` → `Roles` → `Create role`.
2. Choose `Custom trust policy` and paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "budgets.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:budgets::<YOUR_ACCOUNT_ID>:budget/*"
                },
                "StringEquals": {
                    "aws:SourceAccount": "<YOUR_ACCOUNT_ID>"
                }
            }
        }
    ]
}
```

3. Click `Next` without selecting a managed policy.
4. Name the role `AWSBudgetsActionsRole` and create it.
5. Open the role → `Permissions` → `Add permissions` → `Create inline policy` → `JSON`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:AttachGroupPolicy",
                "iam:AttachRolePolicy",
                "iam:AttachUserPolicy",
                "iam:DetachGroupPolicy",
                "iam:DetachRolePolicy",
                "iam:DetachUserPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

6. Name it `AllowBudgetsToApplyIAMPolicies` and save.

<hr>

<a id="create-budget"></a>

### 3️⃣ Create the Budget

1. Go to `AWS Console` → `AWS Budgets` → `Create budget`.
2. Choose `Customize` → `Cost budget`.
3. Set a monthly amount (e.g. `$5.00`).
4. Under `Alerts`, add a threshold (e.g. `$0.01` actual cost) and add your email.
5. Click `Add action` on the alert:
   - **Action type**: `Apply IAM policy`
   - **IAM role**: `AWSBudgetsActionsRole`
   - **Policy**: `BudgetPanicDeny`
   - **Apply to**: Select your admin user (e.g. `Dinones`) and the `Administrator` group.
6. Save the budget.

> [!NOTE]
> The root account always bypasses IAM policies. If the deny fires and locks you out, log in as root to detach it.

<br>

<a id="cloudwatch"></a>

## 🔔ㅤCloudWatch Billing Alarm

Sends an email when estimated charges cross a fixed threshold. Checks every ~6 hours.

<a id="billing-alerts"></a>

### 1️⃣ Enable Billing Alerts

1. Go to `Billing and Cost Management` → `Billing Preferences`.
2. Enable `Receive CloudWatch Billing Alerts` and save.

<a id="create-alarm"></a>

### 2️⃣ Create the Alarm

> [!IMPORTANT]
> CloudWatch billing metrics only exist in **us-east-1 (N. Virginia)**. Switch to that region before continuing.

1. Go to `CloudWatch` → `Alarms` → `Create alarm`.
2. Click `Select metric` → `Billing` → `Total Estimated Charge` → `EstimatedCharges`.
3. Set:
   - **Statistic**: `Maximum`
   - **Period**: `6 hours`
   - **Threshold**: greater than `$1.00` (or your preferred amount)
4. Under `Notification`, create a new SNS topic and add your email.
5. Confirm the subscription email AWS sends you.

> [!NOTE]
> The billing namespace only appears after enabling billing alerts in step 1.

<br>

<a id="anomaly"></a>

## 🤖ㅤAWS Cost Anomaly Detection

ML-based detection that alerts within 1-2 hours of unusual spending patterns. Free service.

1. Go to `AWS Cost Management` → `Cost Anomaly Detection`.
2. Click `Create monitor`:
   - **Monitor type**: `AWS services`
   - Name it and create.
3. Click `Create subscription`:
   - **Threshold**: individual anomaly above `$0.50`
   - **Notification**: add your email.
4. Done — no further configuration needed.
