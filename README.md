# Infrastructure as Code (IaC) Security Scanning & Compliance

Automated Infrastructure as Code (IaC) security scanning and AWS Config compliance pipeline for Terraform infrastructure.

This repository demonstrates how to integrate continuous IaC vulnerability scanning (using **Trivy**) with automated AWS compliance monitoring (using **AWS Config**, **EventBridge**, **SNS**, and **AWS Chatbot**).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Automated IaC Security Scanning (CI/CD)](#automated-iac-security-scanning-cicd)
  - [Trivy Scan Workflow](#trivy-scan-workflow)
- [AWS Config Compliance Monitoring](#aws-config-compliance-monitoring)
  - [Resources Created](#resources-created)
  - [Prerequisites](#prerequisites)
  - [Variables](#variables)
- [Usage & Deployment](#usage--deployment)
- [Compliance Verification & Testing](#compliance-verification--testing)
- [Troubleshooting](#troubleshooting)

---

## 🔍 Overview

Maintaining secure infrastructure requires both **pre-deployment scanning** (detecting misconfigurations in Terraform before applying) and **post-deployment monitoring** (continuously checking live AWS resources against compliance rules).

Key features of this repository:
1. **IaC Security Scanning:** Automated GitHub Actions workflow running `trivy` on every push/pull request to detect security risks and policy violations in Terraform code.
2. **AWS Config Monitoring:** Terraform configuration deploying AWS Config recorder, S3 history storage, and the `EKS_SECRETS_ENCRYPTED` managed rule.
3. **Targeted Alerting:** CloudWatch/EventBridge rule filtering for `Config Rules Compliance Change` events to route critical compliance notifications to SNS (Email) and AWS Chatbot (Slack), avoiding noisy delivery log alerts.

---

## 🏗 Architecture

```
                                  +---------------------------------------+
                                  |         GitHub CI/CD Pipeline         |
                                  |                                       |
                                  |         [Push / PR to main]           |
                                  |                  │                    |
                                  |                  ▼                    |
                                  |            ┌───────────┐              |
                                  |            │   Trivy   │              |
                                  |            │  Action   │              |
                                  |            └─────┬─────┘              |
                                  |                  │                    |
                                  |                  ▼                    |
                                  |            HTML Artifacts             |
                                  +---------------------------------------+
                                                     │
                                             terraform apply
                                                     │
                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 AWS Account (eu-west-2)                                  │
│                                                                                          │
│  ┌──────────────────┐    evaluates    ┌──────────────────┐                               │
│  │   EKS Cluster    │ ──────────────► │  AWS Config Rule │                               │
│  │  (my-cluster)    │                 │  eks-secrets-    │                               │
│  └──────────────────┘                 │  encrypted       │                               │
│                                       └────────┬─────────┘                               │
│                                          State Changes Only                              │
│                                                │                                         │
│                                                ▼                                         │
│                                       ┌──────────────────┐                               │
│                                       │   EventBridge    │                               │
│                                       │   Event Rule     │                               │
│                                       └────────┬─────────┘                               │
│                                                │                                         │
│                                                ▼                                         │
│                                       ┌──────────────────┐                               │
│                                       │    SNS Topic     │                               │
│                                       │ (Compliance      │                               │
│                                       │  Alerts Only)    │                               │
│                                       └────────┬─────────┘                               │
│                                                │                                         │
│                                ┌───────────────┴───────────────┐                         │
│                                ▼                               ▼                         │
│                       ┌──────────────────┐            ┌──────────────────┐               │
│                       │  📧 SNS Email    │            │ 💬 AWS Chatbot   │               │
│                       │   Subscription   │            │   (Slack)        │               │
│                       └──────────────────┘            └──────────────────┘               │
│                                                                                          │
│  Config Snapshots & History ──────────────────────────────────► S3 Bucket                │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── trivy-scan.yml       # GitHub Actions workflow for Trivy IaC scanning
├── terraform/
│   ├── main.tf                  # AWS Provider & CloudPosse AWS Config module setup
│   ├── eks.tf                   # Target EKS cluster configuration for compliance testing
│   ├── notifications.tf         # EventBridge, SNS, Email, and AWS Chatbot Slack resources
│   ├── s3-bucket.tf             # AWS Config delivery S3 bucket & public access block
│   ├── variables.tf             # Input variables (alert email, Slack team/channel IDs)
│   └── output.tf                # Stack outputs (ARNs, bucket names, cluster info)
```

---

## 🛡 Automated IaC Security Scanning (CI/CD)

This repository incorporates static code analysis directly into GitHub Actions. On every commit or pull request to `main`, scanning jobs evaluate the Terraform code in `./terraform`.

### Trivy Scan Workflow
- **File:** [`.github/workflows/trivy-scan.yml`](.github/workflows/trivy-scan.yml)
- **Engine:** Aqua Security / Trivy (using `scan2html` plugin)
- **Function:** Scans for misconfigurations and vulnerabilities across Terraform code using custom template support.
- **Artifact:** Generates `trivy-terraform-report.html` and uploads it as a workflow artifact.

---

## ⚙️ AWS Config Compliance Monitoring

### Resources Created

| File | Resource / Data Source | Description |
|---|---|---|
| [`main.tf`](terraform/main.tf) | `module.aws-config` | Config recorder, delivery channel, and `EKS_SECRETS_ENCRYPTED` rule |
| [`eks.tf`](terraform/eks.tf) | `module.eks` | EKS cluster (`my-cluster`) configured for testing compliance evaluation |
| [`s3-bucket.tf`](terraform/s3-bucket.tf) | `aws_s3_bucket.config` | Secure S3 bucket for storing AWS Config history and snapshots |
| [`notifications.tf`](terraform/notifications.tf) | `aws_sns_topic.compliance_alerts` | SNS topic specifically for compliance state transitions |
| [`notifications.tf`](terraform/notifications.tf) | `aws_cloudwatch_event_rule.compliance` | EventBridge rule matching `Config Rules Compliance Change` |
| [`notifications.tf`](terraform/notifications.tf) | `aws_sns_topic_subscription.email` | Email alert subscription for compliance changes |
| [`notifications.tf`](terraform/notifications.tf) | `aws_chatbot_slack_channel_configuration.slack` | AWS Chatbot integration forwarding notifications to Slack |
| [`output.tf`](terraform/output.tf) | — | Stack outputs (Recorder ID, S3 Bucket, SNS Topic ARN, EKS details) |

---

## 📋 Prerequisites & Setup

### Prerequisites
- **Terraform:** `>= 1.3`
- **AWS CLI:** `>= 2.0` configured with appropriate regional credentials (`eu-west-2`).
- **AWS IAM Role:** An existing IAM role (e.g., `LabRole` or administrative role) if using the provided EKS manifest.

### Slack Authorization (Optional for Chatbot Notifications)
AWS Chatbot Slack integration requires a one-time OAuth handshake in the AWS Console before Terraform can deploy `aws_chatbot_slack_channel_configuration`:

1. Open **AWS Chatbot** in the AWS Console.
2. Select **Slack** under *Configured clients* and click **Configure client**.
3. Complete authorization to connect your Slack workspace.
4. Retrieve your **Workspace/Team ID** (`T...`) and target **Channel ID** (`C...` or `G...`).

---

## 🎛 Variables

Define your configuration values in `terraform/terraform.tfvars`:

```hcl
alert_email      = "your-security-team@example.com"
slack_team_id    = "T0123456789"
slack_channel_id = "C0123456789"
```

| Variable | Type | Default | Description |
|---|---|---|---|
| `alert_email` | `string` | `"your-email@example.com"` | Recipient email address for SNS compliance notifications |
| `slack_team_id` | `string` | `"T0000000000"` | Slack Workspace / Team ID for AWS Chatbot integration |
| `slack_channel_id` | `string` | `"C0000000000"` | Slack Channel ID for AWS Chatbot alerts |

---

## 🚀 Usage & Deployment

```bash
# 1. Navigate to the terraform directory
cd terraform

# 2. Initialize Terraform modules & providers
terraform init

# 3. Review planned infrastructure changes
terraform plan

# 4. Apply the configuration
terraform apply
```

---

## 🧪 Compliance Verification & Testing

### 1. Check Compliance via AWS CLI
Trigger an evaluation and query the compliance result of the EKS cluster:

```bash
# Trigger immediate rule evaluation
aws configservice start-config-rules-evaluation \
    --config-rule-names eks-secrets-encrypted \
    --region eu-west-2

# Retrieve compliance status
aws configservice get-compliance-details-by-config-rule \
    --config-rule-name eks-secrets-encrypted \
    --region eu-west-2
```

### 2. Verify EKS Cluster Encryption Configuration
Check if KMS secrets encryption is currently active on the EKS cluster:

```bash
aws eks describe-cluster \
    --name my-cluster \
    --region eu-west-2 \
    --query "cluster.encryptionConfig"
```

### 3. Remediation / Enabling Encryption
To make the cluster `COMPLIANT`, configure the `encryption_config` block in `terraform/eks.tf` with a KMS Key ARN and run `terraform apply`:

```hcl
encryption_config = {
  resources        = ["secrets"]
  provider_key_arn = "arn:aws:kms:eu-west-2:ACCOUNT_ID:key/KEY_ID"
}
```

---

## 🔧 Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| **No notification email received** | SNS subscription remains unconfirmed or no state transition occurred | 1. Check spam folder for confirmation email from `no-reply@sns.amazonaws.com`. <br> 2. Note that EventBridge only fires on **state changes** (e.g., `COMPLIANT` ↔ `NON_COMPLIANT`). |
| **`aws_chatbot_slack_channel_configuration` apply fails** | Slack workspace is not authorized | Complete the AWS Chatbot OAuth authorization in the AWS Console prior to `terraform apply`. |
| **`ConfigurationRecorderAlreadyExistsException`** | AWS Config is already enabled in the region | AWS permits only 1 Config Recorder per region. Import the existing recorder or delete it before running `terraform apply`. |
| **Slack alerts not appearing** | AWS Chatbot bot is absent from channel | In Slack, run `/invite @aws` in the designated channel to ensure the bot has permission to post. |
