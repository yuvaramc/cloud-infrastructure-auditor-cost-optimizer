# Cloud Infrastructure Auditor & Cost Optimizer

A Python CLI project for auditing cloud infrastructure, identifying cost optimization opportunities, exporting reports, and safely previewing eligible cleanup actions.

## Current Status

- AWS EBS storage scanning is implemented.
- AWS compute and network scanners are not yet implemented.
- GCP integration is not yet implemented; selecting GCP does not perform a cloud scan.
- JSON and CSV report export work, but the report command currently exports an empty findings collection.
- Cleanup supports read-only dry-run previews only. Actual cleanup execution is not implemented.
- The Windows executable can be built with PyInstaller.

## Requirements

- Python 3.11 or newer
- AWS credentials for AWS scanning and cleanup previews
- PyInstaller for building the standalone executable

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If PowerShell blocks virtual environment activation, use the Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## AWS Credentials

Configure credentials using your normal AWS authentication method. For example, with the AWS CLI installed:

```powershell
aws configure
```

Alternatively, use an AWS profile or environment-based credentials supported by boto3.

Never commit AWS access keys, secret keys, session tokens, or local `.env` files. Use only credentials with the minimum permissions needed for the operation.

The default AWS region is `us-east-1`. Specify another supported region with `--region`.

## CLI Usage

Run the CLI from the repository root:

```powershell
python -m app.cli.main --help
python -m app.cli.main version
```

The installed console command is also available after installation:

```powershell
cloud-auditor version
cloud-auditor --help
```

### Audit

Audit AWS storage resources:

```powershell
python -m app.cli.main audit --provider aws --region us-east-1 --resource storage
```

The supported resource selections are `all`, `compute`, `storage`, and `network`. Currently, only the EBS storage scanner is implemented. Selecting compute or network reports that those scanners are unavailable.

The audit command accepts `gcp` as a provider selection, but GCP scanning is not implemented yet.

### Reports

Display the current text report:

```powershell
python -m app.cli.main report --format text
```

Export JSON or CSV:

```powershell
python -m app.cli.main report --format json --output report.json
python -m app.cli.main report --format csv --output report.csv
```

Supported formats are `text`, `json`, and `csv`.

**Current limitation:** the report command currently exports an empty findings collection. It does not yet consume findings from a completed audit. A successful export therefore does not confirm that a cloud scan succeeded.

### Safe Cleanup Preview

Preview eligible AWS storage cleanup actions:

```powershell
python -m app.cli.main cleanup --provider aws --region us-east-1 --resource storage --dry-run
```

Cleanup previews are read-only. The `--execute` option is deliberately blocked because cleanup execution has not been implemented. No resources should be deleted by this command.

## Build a Windows Executable

Install the development dependencies, including PyInstaller, and run:

```powershell
python -m PyInstaller --onefile --name cloud-auditor --paths . app\cli\main.py
```

The executable is written to:

```text
dist\cloud-auditor.exe
```

Test the packaged CLI:

```powershell
.\dist\cloud-auditor.exe version
.\dist\cloud-auditor.exe --help
.\dist\cloud-auditor.exe report --format json --output packaged-report.json
```

The executable is platform-specific. Build and test it on the target operating system. Cloud scans still require valid cloud credentials and implemented scanners.

## Run Tests

Run the automated test suite:

```powershell
python -m pytest -q
```

The test suite covers implemented functionality and should be run after code or configuration changes.

## Project Structure

```text
app/
├── audit/
│   ├── aggregation/
│   └── models.py
├── auth/
├── aws/
├── cleanup/
├── cli/
│   └── commands/
├── core/
├── providers/
│   ├── aws/
│   └── gcp/
├── reporting/
└── scanners/
```

## Known Limitations

- Only AWS EBS storage scanning is currently implemented.
- AWS compute and network scanning are pending.
- GCP scanning is pending.
- Report exports are not yet connected to live audit findings.
- Cleanup execution is not implemented; dry-run previews only are supported.
- A successful CLI launch or report export is not proof of a successful live cloud audit.
