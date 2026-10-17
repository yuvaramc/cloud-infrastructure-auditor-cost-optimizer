# Cloud Infrastructure Auditor & Cost Optimizer

A Python CLI tool for auditing cloud infrastructure, identifying cost optimization opportunities, generating reports, and safely previewing cleanup actions.

## Project Goals

- Audit cloud infrastructure for potential cost and configuration issues.
- Identify unused or unnecessary cloud resources.
- Analyze infrastructure for cost optimization opportunities.
- Generate terminal reports and exportable JSON/CSV reports.
- Import saved audit results and generate reports without rerunning a scan.
- Support safe cleanup through dry-run previews.
- Support AWS auditing, with Google Cloud integration planned for future development.

## Requirements

- Python 3.11 or later
- AWS credentials configured for AWS auditing
- AWS permissions appropriate for the resources being inspected

## Installation

From the project root, install the package in editable mode:

```powershell
python -m pip install -e .
```

Check the installed CLI version:

```powershell
cloud-auditor version
```

Alternatively, run the CLI through Python:

```powershell
python -m app.cli.main version
```

## Audit Resources

Run an AWS audit using the default region (`us-east-1`):

```powershell
cloud-auditor audit
```

Choose a specific AWS region:

```powershell
cloud-auditor audit --provider aws --region ap-south-1 --resource storage
```

Choose a resource category:

```powershell
cloud-auditor audit --resource all
cloud-auditor audit --resource storage
cloud-auditor audit --resource compute
cloud-auditor audit --resource network
```

**Current implementation scope:** the implemented AWS scanner checks EBS volumes. Compute and network scanners are not yet implemented. Google Cloud auditing is not yet implemented; selecting GCP does not perform a real resource scan.

## Export Audit Results

Export AWS audit findings to JSON:

```powershell
cloud-auditor audit --provider aws --region us-east-1 --resource storage --output audit-results.json --format json
```

Export findings to CSV:

```powershell
cloud-auditor audit --provider aws --region us-east-1 --resource storage --output audit-results.csv --format csv
```

The `--output` option specifies the destination file. The `--format` option accepts `json` or `csv` and defaults to JSON.

The destination directory must already exist, and the configured AWS credentials must permit the scan.

## Generate Reports From Saved Results

Display a text report from a previously exported JSON file:

```powershell
cloud-auditor report --input audit-results.json --format text
```

Generate a JSON report:

```powershell
cloud-auditor report --input audit-results.json --format json --output report.json
```

Generate a CSV report:

```powershell
cloud-auditor report --input audit-results.json --format csv --output report.csv
```

The report command accepts JSON or CSV input and supports `text`, `json`, and `csv` output formats.

To inspect all available options:

```powershell
cloud-auditor audit --help
cloud-auditor report --help
```

## Cleanup Safety

The cleanup functionality supports dry-run previews. These previews describe proposed cleanup actions without executing destructive cloud operations.

Review the proposed actions before considering any future cleanup execution functionality.

## Run Tests

Run the full test suite:

```powershell
python -m pytest -q
```

Check for whitespace errors in Git changes:

```powershell
git diff --check
```

The test suite includes CLI tests, report loading and export tests, and mocked audit-export integration tests.

## Project Structure

```text
app/
|-- cli/              # CLI commands and entry point
|-- audit/            # Infrastructure audit logic
|-- reporting/        # Terminal and file-based reporting
|-- cleanup/          # Cleanup eligibility and preview logic
|-- core/              # Shared configuration and utilities
|-- aws/               # AWS authentication and region management
|-- scanners/          # Cloud resource scanners
`-- providers/
    |-- aws/           # AWS-specific integrations
    `-- gcp/           # Google Cloud integrations
```

## Current Limitations

- AWS resource scanning currently implements EBS volume checks.
- Compute and network scanners are not yet implemented.
- GCP auditing is not yet implemented.
- Cleanup is limited to dry-run previews; destructive cleanup is not performed by the current workflow.
