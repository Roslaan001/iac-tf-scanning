# Infrastructure as Code (IaC) Security & Compliance Scanning

Automated Infrastructure as Code (IaC) security and compliance scanning pipelines using **Trivy** and **Checkov** with GitHub Actions for Terraform.

This repository demonstrates how to integrate continuous IaC vulnerability, misconfiguration, and compliance scanning into your CI/CD workflows before provisioning resources in the cloud.

---

## 📑 Article Series

* **Part 1:** [IaC Security Scanning with Trivy](#part-1-iac-security-scanning-with-trivy) — Misconfiguration detection, CVE scanning, and HTML report generation.
* **Part 2:** [Policy & Compliance Scanning with Checkov](#part-2-policy--compliance-scanning-with-checkov) — CIS benchmarks, policy-as-code validation, and interactive HTML compliance reports.

---

## Table of Contents

- [Overview & Architecture](#overview--architecture)
- [Tool Comparison: Trivy vs. Checkov](#tool-comparison-trivy-vs-checkov)
- [Repository Structure](#repository-structure)
- [Part 1: IaC Security Scanning with Trivy](#part-1-iac-security-scanning-with-trivy)
  - [Trivy Workflow](#trivy-scan-workflow)
  - [Running Trivy Locally](#running-trivy-locally)
  - [Trivy Scan Reports & Findings (Screenshots)](#trivy-scan-reports--findings)
- [Part 2: Policy & Compliance Scanning with Checkov](#part-2-policy--compliance-scanning-with-checkov)
  - [Checkov Workflow](#checkov-scan-workflow)
  - [Running Checkov Locally](#running-checkov-locally)
  - [Checkov Scan Reports & Findings (Screenshots)](#checkov-scan-reports--findings)
- [Workflow Artifacts](#workflow-artifacts)

---

## Overview & Architecture

Maintaining secure cloud infrastructure requires **pre-deployment scanning** to catch misconfigurations, hardcoded credentials, and compliance violations in Terraform code before resources are ever provisioned.

```text
+-------------------------------------------------------------------+
|                     GitHub CI/CD Pipeline                         |
|                                                                   |
|                     [Push / PR to main]                           |
|                              │                                    |
|               ┌──────────────┴──────────────┐                     |
|               ▼                             ▼                     |
|     ┌──────────────────┐          ┌──────────────────┐            |
|     │   Trivy Scan     │          │   Checkov Scan   │            |
|     │ (GitHub Action)  │          │ (GitHub Action)  │            |
|     └─────────┬────────┘          └─────────┬────────┘            |
|               │                             │                     |
|               ▼                             ▼                     |
|    ┌──────────────────────┐      ┌──────────────────────┐         |
|    │ trivy-terraform-     │      │ checkov-terraform-   │         |
|    │ report (HTML)        │      │ report (HTML)        │         |
|    └──────────────────────┘      └──────────────────────┘         |
+-------------------------------------------------------------------+
```

---

## Tool Comparison: Trivy vs. Checkov

| Capability / Feature | Trivy (Aqua Security) | Checkov (Bridgecrew / Prisma) |
| :--- | :--- | :--- |
| **Primary Strength** | Misconfiguration detection, fast CVE lookup, secret scanning | Deep policy-as-code (CIS, NIST, HIPAA, PCI-DSS) |
| **Visual Reports** | Interactive HTML dashboard via `scan2html` | Interactive HTML dashboard via `generate_checkov_html.py` |
| **Graph-based Analysis** | Basic dependency checks | Advanced resource dependency & connection graph |
| **Best Used For** | Fast developer feedback & visual HTML audit reports | Rigorous compliance validation & governance gates |

---

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       ├── trivy-scan.yml       # GitHub Actions workflow for Trivy IaC scanning (Part 1)
│       └── checkov-scan.yml     # GitHub Actions workflow for Checkov compliance scanning (Part 2)
├── scripts/
│   └── generate_checkov_html.py # Converts Checkov JSON output into an interactive HTML dashboard
└── terraform/
    ├── main.tf                  # AWS Provider & CloudPosse AWS Config module setup
    ├── eks.tf                   # EKS cluster configuration
    ├── notifications.tf         # EventBridge, SNS, and AWS Chatbot resources
    ├── s3-bucket.tf             # AWS Config delivery S3 bucket setup
    ├── variables.tf             # Terraform input variables
    └── output.tf                # Terraform outputs
```

---

## Part 1: IaC Security Scanning with Trivy

### Trivy Scan Workflow
- **Workflow File:** [`.github/workflows/trivy-scan.yml`](.github/workflows/trivy-scan.yml)
- **Scanner:** Aqua Security / Trivy
- **Plugin:** `scan2html`
- **Trigger:** `push` or `pull_request` on `main` branch
- **Action:** Scans Terraform files for misconfigurations, generates an HTML summary report, and uploads it as a workflow artifact.

### Running Trivy Locally

```bash
# 1. Install Trivy (Linux)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# 2. Install scan2html plugin
trivy plugin install scan2html

# 3. Run IaC scan against the terraform directory
trivy scan2html config ./terraform --scan2html-flags --output trivy-terraform-report.html
```

### Trivy Scan Reports & Findings

#### Misconfigurations Summary
![Scan Summary Overview](Screenshot%20From%202026-08-12%2019-32-27.png)

#### Rule Descriptions & Severity Mapping
![Severity Details](Screenshot%20From%202026-08-12%2019-32-32.png)

#### Security Group & Unencrypted SNS Topic Findings
![Security Group & SNS Findings](Screenshot%20From%202026-08-12%2019-32-44.png)

#### RDS Encryption & Unrestricted Ingress Checks
![RDS Encryption & Ingress Findings](Screenshot%20From%202026-08-12%2019-32-55.png)

#### S3 Bucket Public Access Block Checks
![S3 Public Access Block Findings](Screenshot%20From%202026-08-12%2019-33-07.png)

#### S3 Restrict Public Buckets & Customer Managed Key Encryption Checks
![S3 Encryption & Policy Restrictions](Screenshot%20From%202026-08-12%2019-33-26.png)

#### EKS Cluster Secrets Encryption & RDS Backup Retention / Hardcoded Credentials
![EKS Secrets & Hardcoded Secrets Findings](Screenshot%20From%202026-08-12%2019-33-38.png)

---

## Part 2: Policy & Compliance Scanning with Checkov

### Checkov Scan Workflow
- **Workflow File:** [`.github/workflows/checkov-scan.yml`](.github/workflows/checkov-scan.yml)
- **Scanner:** Bridgecrew / Checkov
- **Framework:** Terraform
- **Trigger:** `push` or `pull_request` on `main` branch
- **Action:** Runs policy checks (including CIS benchmarks), converts output into an interactive HTML report via [`generate_checkov_html.py`](scripts/generate_checkov_html.py), and publishes the HTML artifact.

### Running Checkov Locally

```bash
# 1. Install Checkov
pip install checkov

# 2. Run scan and export JSON report
checkov -d ./terraform --framework terraform --output json --soft-fail > checkov-report.json

# 3. Generate interactive HTML report
python3 scripts/generate_checkov_html.py checkov-report.json checkov-terraform-report.html

# 4. Open in browser
xdg-open checkov-terraform-report.html
```

### Checkov Scan Reports & Findings

#### Checkov Overview & Summary Dashboard
![Checkov Summary Overview](Screenshot%20From%202026-08-18%2012-33-41.png)

#### IAM Privilege Escalation, Exfiltration & Wildcard Action Policy Violations
![IAM Policy Violations](Screenshot%20From%202026-08-18%2012-33-54.png)

#### RDS Deletion Protection, Performance Insights & Multi-AZ Compliance Checks
![RDS Compliance Checks](Screenshot%20From%202026-08-18%2012-34-03.png)

#### Passed IAM Policy Documents & Version Tag Validations
![Passed IAM Documents Checks](Screenshot%20From%202026-08-18%2012-34-14.png)

#### Passed IAM Least Privilege & Secure Assume Role Policies
![Passed Least Privilege Policies](Screenshot%20From%202026-08-18%2012-34-23.png)

---

## Workflow Artifacts

When a workflow run completes:
1. Navigate to the **Actions** tab in your GitHub repository.
2. Select any completed run of **Trivy IaC Security Scan** or **Checkov IaC Security & Compliance Scan**.
3. Under the **Artifacts** section at the bottom, download:
   * `trivy-terraform-report` (`trivy-terraform-report.html`)
   * `checkov-terraform-report` (`checkov-terraform-report.html`)
4. Open the `.html` file in any browser to inspect the visual dashboard.
