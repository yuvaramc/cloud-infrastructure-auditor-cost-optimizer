# Cloud Infrastructure Auditor & Cost Optimizer

A Python CLI tool for auditing cloud infrastructure, identifying cost optimization opportunities, generating reports, and safely previewing cleanup actions.

## Project Goals

* Audit cloud infrastructure for potential cost and configuration issues.
* Identify unused or unnecessary cloud resources.
* Analyze infrastructure for cost optimization opportunities.
* Provide clear terminal and exportable reports.
* Support safe cleanup through dry-run previews.
* Support AWS initially, with architecture prepared for future Google Cloud integration.

## Project Structure

```text
app/
|-- cli/              # CLI commands and entry point
|-- audit/            # Infrastructure audit logic
|-- reporting/        # Terminal and file-based reporting
|-- cleanup/          # Cleanup eligibility and preview logic
|-- core/             # Shared configuration and utilities
|-- aws/              # AWS authentication and region management
|-- scanners/         # Cloud resource scanners
`-- providers/
    |-- aws/          # AWS-specific integrations
    `-- gcp/          # Google Cloud integrations
```

## Requirements

* Python 3.11 or later
* AWS credentials for live AWS auditing
* Windows, Linux, or macOS

## Installation

Clone the repository and move into the project directory:

```text
git clone https://github.com/yuvaramc/cloud-infrastructure-auditor-cost-optimizer.git
cd cloud-infrastructure-auditor-cost-optimizer
```

Create and activate a virtual environment:

### Windows PowerShell

```text
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```text
python3 -m venv .venv
source .venv/bin/activate
```

Install the project with development dependencies:

```text
python -m pip install -e ".[dev]"
```

## CLI Usage

The CLI entry point is:

```text
cloud-auditor
```

You can also run the application through Python:

```text
python -m app.cli.main
```

### Version

```text
cloud-auditor version
```

Expected output:

```text
cloud-auditor version 0.1.0
```

### Audit

Run an AWS audit:

```text
cloud-auditor audit --provider aws --region us-east-1 --resource all
```

Audit storage resources:

```text
cloud-auditor audit --provider aws --region us-east-1 --resource storage
```

Supported resource selections are:

* `all`
* `compute`
* `storage`
* `network`

Currently implemented AWS auditing includes unattached EBS volume detection. Compute and network scanner implementations are planned for future development.

### AWS Region

The CLI validates supported AWS regions.

Example:

```text
cloud-auditor audit --provider aws --region ap-south-1 --resource storage
```

The default AWS region is:

```text
us-east-1
```

### Cloud Providers

Currently recognized providers:

* `aws`
* `gcp`

AWS auditing is currently implemented. GCP support is prepared in the project architecture but live GCP auditing is not yet implemented.

## Reports

Audit results can be displayed in the terminal using the Rich-based reporter.

Generate a report using:

```text
cloud-auditor report
```

The reporting functionality supports structured audit data and export formats such as JSON and CSV where applicable.

Example report formats:

```text
cloud-auditor report --format json
```

```text
cloud-auditor report --format csv
```

Invalid report formats are rejected by the CLI.

## Clean Up Resources

The cleanup command currently supports **AWS storage resources** and uses dry-run mode by default.

It generates a read-only preview and does not modify cloud resources.

Run the cleanup preview:

```text
cloud-auditor cleanup
```

Specify an AWS region and storage resource:

```text
cloud-auditor cleanup --provider aws --region us-east-1 --resource storage
```

Cleanup execution is **not implemented yet**.

Passing `--execute` is rejected and makes no changes to cloud resources.

This safety behavior prevents accidental deletion while cleanup execution is still under development.

## AWS Credentials

Live AWS auditing requires valid AWS credentials.

The project uses Boto3 for AWS communication.

Configure credentials using your normal AWS credential configuration before running live audits.

For example, credentials may be provided through the AWS credentials/configuration files or environment variables.

Never commit AWS access keys, secret keys, session tokens, or other cloud credentials to the repository.

If credentials are unavailable, the CLI reports an authentication error instead of proceeding with a live AWS scan.

## Testing

Run the complete test suite:

```text
python -m pytest -q
```

The current automated test suite covers:

* CLI command routing
* AWS authentication handling
* AWS region validation
* AWS session management
* EBS scanning
* Audit aggregation
* Reporting
* CSV and JSON export
* Cleanup dry-run behavior
* Cleanup validation
* Retry and error handling
* CLI integration paths
* EBS scanner failure handling

The current test suite passes with:

```text
127 passed
```

Two Typer/Click deprecation warnings may appear from installed third-party dependencies. They do not currently cause test failures.

## Package Build

The project can be built as a Python package using:

```text
python -m build
```

This produces:

```text
dist/
|-- cloud_infrastructure_auditor_cost_optimizer-0.1.0-py3-none-any.whl
`-- cloud_infrastructure_auditor_cost_optimizer-0.1.0.tar.gz
```

The generated wheel can be installed into a clean virtual environment:

```text
python -m pip install dist/cloud_infrastructure_auditor_cost_optimizer-0.1.0-py3-none-any.whl
```

Then verify the installed CLI:

```text
cloud-auditor version
```

Expected:

```text
cloud-auditor version 0.1.0
```

## Development

Create a feature branch for each issue:

```text
git switch -c issue-<number>-<short-description>
```

Run tests before committing:

```text
python -m pytest -q
```

Check the working tree:

```text
git status
```

Use meaningful commit messages describing the actual change.

## Documentation

Additional project documentation is available in:

* `docs/ARCHITECTURE.md`
* `docs/DEVELOPMENT.md`

## Security

Cloud credentials must never be committed to Git.

Do not commit:

* AWS access keys
* AWS secret keys
* AWS session tokens
* GCP service-account private keys
* `.env` files containing credentials
* Other cloud authentication secrets

The cleanup functionality defaults to dry-run mode to prevent unintended resource modifications.

## Current Implementation Status

### Implemented

* Python CLI application
* Typer command routing
* AWS authentication and session management
* AWS region validation
* AWS EBS storage scanning
* Audit finding models
* Audit result aggregation
* Rich terminal reporting
* JSON and CSV reporting
* Cleanup dry-run preview
* Retry and error handling
* CLI integration tests
* Python package building
* Wheel and source distribution generation

### Planned / In Progress

* Additional AWS compute scanners
* AWS network scanners
* GCP resource auditing
* Actual cleanup execution with explicit safety controls
* Expanded end-to-end cloud-provider UAT

## License

This project is currently developed as an academic/team project.
