# Cloud Infrastructure Auditor & Cost Optimizer

A Python CLI tool for auditing cloud infrastructure, identifying cost optimization opportunities, generating audit reports, and safely previewing resource cleanup operations.

> **Current status:** AWS auditing and reporting foundations are implemented. Cleanup currently supports **dry-run/preview only**; destructive resource execution is not implemented.

---

## Project Purpose

Cloud environments can accumulate unused, misconfigured, or unnecessary resources that increase infrastructure costs.

The **Cloud Infrastructure Auditor & Cost Optimizer** helps identify these resources through automated audits and provides structured findings that can be viewed in the terminal or exported to JSON and CSV.

The project is designed with a provider-based architecture so that AWS is supported first while the codebase can be extended to other cloud providers such as Google Cloud.

## Key Features

- AWS infrastructure auditing through a CLI.
- Provider-based architecture for AWS and GCP.
- Configurable AWS region selection.
- Resource filtering for compute, storage, network, or all resources.
- Detection of infrastructure optimization opportunities.
- Unattached AWS EBS volume auditing.
- Severity-based audit findings.
- Estimated cost and savings fields in audit findings.
- Terminal reporting.
- JSON and CSV report export.
- Cleanup preview through dry-run mode.
- Automated test suite with pytest.
- Python package installation through the project CLI entry point.
- Optional executable packaging with PyInstaller.

---

## Project Goals

The project aims to:

1. Audit cloud infrastructure resources.
2. Identify unused or potentially unnecessary resources.
3. Highlight infrastructure cost optimization opportunities.
4. Provide clear and structured audit findings.
5. Export audit results for further analysis.
6. Allow users to preview cleanup operations safely.
7. Keep cloud credentials out of application source code.
8. Provide an extensible architecture for multiple cloud providers.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Application development |
| Typer | CLI framework |
| Rich | Terminal output |
| Boto3 | AWS SDK |
| Google Cloud Compute Client | GCP integration |
| PyYAML | Configuration support |
| Pytest | Automated testing |
| pytest-cov | Test coverage |
| Setuptools | Python packaging |
| PyInstaller | Executable packaging |

---

## Project Structure

```text
cloud-infrastructure-auditor-cost-optimizer/
|
|-- app/
|   |-- cli/
|   |   |-- commands/
|   |   |   |-- audit.py
|   |   |   |-- cleanup.py
|   |   |   `-- report.py
|   |   `-- main.py
|   |
|   |-- aws/
|   |   |-- session.py
|   |   `-- region.py
|   |
|   |-- audit/
|   |   `-- models.py
|   |
|   |-- cleanup/
|   |
|   |-- core/
|   |
|   |-- providers/
|   |   |-- aws/
|   |   `-- gcp/
|   |
|   |-- reporting/
|   |   `-- exporter.py
|   |
|   `-- scanners/
|       `-- ebs.py
|
|-- tests/
|-- docs/
|   |-- ARCHITECTURE.md
|   `-- DEVELOPMENT.md
|
|-- pyproject.toml
|-- README.md
`-- .gitignore
```

---

# Installation and Setup

## Prerequisites

Install the following before using the project:

- Python 3.11 or later
- pip
- Git
- AWS CLI (recommended for configuring AWS credentials)

Verify Python:

```text
python --version
```

The project requires Python 3.11 or newer.

---

## Clone the Repository

```text
git clone https://github.com/yuvaramc/cloud-infrastructure-auditor-cost-optimizer.git
cd cloud-infrastructure-auditor-cost-optimizer
```

---

## Create a Virtual Environment

### Windows

```text
python -m venv .venv
```

Activate it in Command Prompt:

```text
.venv\Scripts\activate
```

Activate it in PowerShell:

```text
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```text
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install the Project

For normal installation:

```text
pip install .
```

For development installation with test dependencies:

```text
pip install -e ".[dev]"
```

After installation, the CLI is available as:

```text
cloud-auditor
```

---

# AWS Authentication and Configuration

The application uses **Boto3** for AWS access.

AWS credentials should **never be hard-coded** into the source code or committed to Git.

Recommended authentication methods include:

- AWS CLI configuration.
- Environment variables.
- IAM roles when running in AWS infrastructure.
- Other credential providers supported by Boto3.

## Configure AWS CLI

Install and configure the AWS CLI, then run:

```text
aws configure
```

Provide:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name
Default output format
```

For example, the default region can be:

```text
us-east-1
```

Verify that credentials are available:

```text
aws sts get-caller-identity
```

The application uses AWS identity information to establish and validate the AWS session.

### Security

Never commit:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
.env
```

or other cloud credentials to the repository.

Use IAM policies with only the permissions required by the auditing operations.

---

# AWS Region Selection

The default AWS region is:

```text
us-east-1
```

A different region can be selected using:

```text
--region
```

or:

```text
-r
```

Example:

```text
cloud-auditor audit --provider aws --region ap-south-1 --resource compute
```

The region is normalized and validated before an AWS session is created.

Currently supported AWS regions include:

```text
us-east-1
us-east-2
us-west-1
us-west-2
ap-south-1
ap-southeast-1
ap-southeast-2
ap-northeast-1
eu-west-1
eu-west-2
eu-central-1
```

An unsupported AWS region results in a validation error and prevents creation of the AWS session.

Example:

```text
cloud-auditor audit --provider aws --region invalid-region
```

GCP region names are provider-specific and are not validated against the AWS region list.

---

# CLI Usage

## Show Help

```text
cloud-auditor --help
```

## Show Version

```text
cloud-auditor version
```

The current CLI version is:

```text
0.1.0
```

---

# Audit Command

The audit command scans cloud resources and generates audit findings.

Basic command:

```text
cloud-auditor audit
```

Specify AWS explicitly:

```text
cloud-auditor audit --provider aws
```

Specify a region:

```text
cloud-auditor audit --provider aws --region ap-south-1
```

Specify a resource type:

```text
cloud-auditor audit --provider aws --resource storage
```

Combine provider, region, and resource:

```text
cloud-auditor audit --provider aws --region us-east-1 --resource compute
```

## Audit Options

| Option | Short form | Description |
|---|---|---|
| `--provider` | `-p` | Cloud provider: `aws` or `gcp` |
| `--region` | `-r` | Cloud region |
| `--resource` | | Resource category |

Supported providers:

```text
aws
gcp
```

Supported resource categories:

```text
all
compute
storage
network
```

---

# Audit Scanners

The audit layer identifies resources that may represent waste, unused infrastructure, or optimization opportunities.

## AWS EBS Scanner

The current AWS implementation includes an EBS scanner.

It identifies **unattached EBS volumes**.

An unattached EBS volume can continue generating storage costs even when it is not connected to an EC2 instance.

The scanner records information such as:

- Resource type
- Volume ID
- Region
- Volume size
- Volume type
- Volume state
- Creation time
- AWS account ID
- Finding severity

Unattached EBS volumes are currently classified as:

```text
MEDIUM
```

Additional scanners can be added through the provider/scanner architecture.

---

# Audit Finding Model

Audit findings contain structured information including:

```text
resource_type
resource_id
region
severity
description
account_id
status
estimated_cost
estimated_savings
metadata
```

Example conceptual finding:

```text
Resource Type: EBS Volume
Resource ID: vol-xxxxxxxx
Region: ap-south-1
Severity: MEDIUM
Status: unattached
Estimated Cost: optional
Estimated Savings: optional
```

Cost fields are optional and are not guaranteed to represent live AWS billing information.

---

# Reporting and Export

The report command supports multiple output formats.

## Text Report

```text
cloud-auditor report
```

## JSON Report

```text
cloud-auditor report --format json --output audit.json
```

## CSV Report

```text
cloud-auditor report --format csv --output audit.csv
```

Specify the provider:

```text
cloud-auditor report --format json --output audit.json --provider aws
```

Supported formats:

```text
text
json
csv
```

CSV exports include fields such as:

```text
resource_type
resource_id
region
severity
description
account_id
status
estimated_cost
estimated_savings
metadata
```

### Reporting Limitation

The reporting/export layer is implemented, but report generation currently depends on findings being supplied by the audit workflow.

Therefore, an export may contain no findings when no scanner results have been populated for the selected workflow.

The project does not claim to provide live billing or complete cloud inventory reporting unless the corresponding scanner functionality is implemented.

---

# Cleanup and Dry-Run

The cleanup command is designed to provide a safe way to preview resource cleanup operations.

Basic command:

```text
cloud-auditor cleanup
```

Specify a provider and resource:

```text
cloud-auditor cleanup --provider aws --resource storage
```

The cleanup command supports:

```text
--dry-run
--execute
```

## Dry-Run Mode

Dry-run mode is intended to preview what would be affected without modifying cloud resources.

Example:

```text
cloud-auditor cleanup --provider aws --resource storage --dry-run
```

### Important Current Limitation

**Actual cleanup execution is not currently implemented.**

The `--execute` option is exposed by the CLI, but destructive resource deletion/modification is intentionally not performed by the current implementation.

Therefore:

```text
cloud-auditor cleanup --execute
```

does **not** delete cloud resources.

This is an important safety limitation of the current release.

---

# Cost Estimation

The audit finding model supports:

```text
estimated_cost
estimated_savings
```

These fields are intended to represent the potential cost impact of identified resources.

## Current Assumptions and Limitations

The current implementation does not query the AWS Pricing API for live, account-specific pricing.

Therefore:

- Estimates should not be treated as AWS billing statements.
- Actual prices can vary by region.
- Pricing can vary by storage class, usage, discounts, commitments, and account agreements.
- EBS findings currently identify potentially unnecessary storage resources, but do not provide a guaranteed live billing calculation.
- Future versions can integrate AWS Pricing APIs or billing data for more accurate estimates.

The primary purpose of the current implementation is **resource identification and optimization analysis**, not exact invoice calculation.

---

# Testing

The project uses `pytest`.

Run all tests:

```text
pytest
```

Run tests quietly:

```text
pytest -q
```

Run with coverage:

```text
pytest --cov=app
```

The test suite covers CLI behavior, project structure, exporters, and application functionality implemented in the repository.

Before submitting changes, run:

```text
pytest -q
```

---

# Packaging

The project is packaged as a Python CLI application.

## Install as a Package

```text
pip install .
```

## Development Installation

```text
pip install -e ".[dev]"
```

## Build Python Distribution

If the required build tooling is installed:

```text
python -m build
```

Generated distribution files are placed in:

```text
dist/
```

---

# Creating a Standalone Executable

PyInstaller can be used to package the CLI as an executable.

Example:

```text
pyinstaller --onefile --name cloud-auditor app/cli/main.py
```

The generated executable is placed under:

```text
dist/
```

The exact packaging behavior can depend on the project's imports and installed dependencies.

---

# Common Usage Examples

## 1. Audit AWS Storage

```text
cloud-auditor audit --provider aws --region ap-south-1 --resource storage
```

## 2. Audit AWS Compute

```text
cloud-auditor audit --provider aws --region us-east-1 --resource compute
```

## 3. Audit All Supported Resources

```text
cloud-auditor audit --provider aws --region us-east-1 --resource all
```

## 4. Export Findings to JSON

```text
cloud-auditor report --format json --output audit.json --provider aws
```

## 5. Export Findings to CSV

```text
cloud-auditor report --format csv --output audit.csv --provider aws
```

## 6. Preview Cleanup

```text
cloud-auditor cleanup --provider aws --resource storage --dry-run
```

## 7. View Command Options

```text
cloud-auditor audit --help
cloud-auditor report --help
cloud-auditor cleanup --help
```

---

# Troubleshooting

## AWS Credentials Not Found

Verify that AWS credentials are configured:

```text
aws sts get-caller-identity
```

If this command fails, configure credentials using:

```text
aws configure
```

## Invalid AWS Region

Check that the selected region is supported by the application.

Example:

```text
cloud-auditor audit --provider aws --region ap-south-1
```

## CLI Command Not Found

If `cloud-auditor` is not recognized, activate the virtual environment and install the project:

```text
.venv\Scripts\activate
pip install -e .
```

Then verify:

```text
cloud-auditor --help
```

## Tests Failing

Run:

```text
pytest -q
```

For more detailed output:

```text
pytest -v
```

---

# Development Workflow

Development work is organized using issue-specific Git branches.

Example:

```text
issue-20-readme-documentation
```

Typical workflow:

```text
git checkout main
git pull origin main
git checkout -b issue-<number>-<description>
```

After making changes:

```text
pytest -q
git status
git add .
git commit -m "docs: complete README"
git push -u origin issue-<number>-<description>
```

Changes should be submitted through a pull request and reviewed before merging into `main`.

---

# Security

Never commit cloud credentials or secrets.

Do not commit:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
.env
```

Use environment variables, AWS CLI configuration, IAM roles, or other secure credential providers.

Follow the principle of least privilege when creating IAM permissions for the auditing application.

---

# Additional Documentation

Additional project documentation is available in:

- `docs/ARCHITECTURE.md` — project architecture and module responsibilities.
- `docs/DEVELOPMENT.md` — development setup and contribution guidelines.

---

# Current Implementation Status

| Feature | Status |
|---|---|
| AWS provider support | Implemented |
| GCP provider architecture | Available for integration |
| AWS region selection | Implemented |
| Resource filtering | Implemented |
| AWS EBS audit scanner | Implemented |
| Audit finding model | Implemented |
| Terminal reporting | Implemented |
| JSON export | Implemented |
| CSV export | Implemented |
| Cleanup dry-run | Implemented |
| Actual cleanup execution | Not implemented |
| Live AWS Pricing API integration | Not implemented |
| Full cloud resource coverage | In progress |

---

# License

This project is developed as part of the Zaaliam internship/project work.

Refer to the repository for the applicable project licensing and contribution requirements.

---

## Repository

GitHub:

https://github.com/yuvaramc/cloud-infrastructure-auditor-cost-optimizer