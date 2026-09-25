# Cloud Infrastructure Auditor & Cost Optimizer

A Python CLI tool for auditing cloud infrastructure, identifying cost optimization opportunities, and safely managing cloud resources.

## Project Goals

The tool is designed to:

- Audit cloud infrastructure resources.
- Identify unused or potentially unnecessary resources.
- Analyze infrastructure for cost optimization opportunities.
- Provide clear terminal and exportable reports.
- Support safe cleanup through dry-run and controlled execution.
- Support AWS initially with architecture prepared for Google Cloud integration.

## Project Structure

```text
app/
|-- cli/              # CLI commands and command routing
|-- auth/             # Authentication and session management
|-- audit/            # Infrastructure audit logic
|-- reporting/        # Terminal and file-based reporting
|-- cleanup/          # Resource cleanup operations
|-- core/             # Shared configuration and utilities
`-- providers/
    |-- aws/          # AWS-specific integrations
    `-- gcp/          # Google Cloud integrations

tests/                # Automated tests
docs/                 # Architecture and development documentation
```

## Technology Stack

- Python 3.11+
- Typer
- Rich
- Boto3
- Google Cloud Compute Client
- PyYAML
- Pytest
- Setuptools
- PyInstaller

## Setup

Create a virtual environment:

```text
python -m venv .venv
```

Activate it on Windows PowerShell:

```text
.venv\Scripts\Activate.ps1
```

Install the project with development dependencies:

```text
pip install -e ".[dev]"
```

## CLI Usage

The CLI can be run during development with:

```text
python -m app.cli.main
```

### Show CLI Help

```text
python -m app.cli.main --help
```

### Show Version

```text
python -m app.cli.main version
```

### Audit Resources

Run an audit with the default options:

```text
python -m app.cli.main audit
```

Specify a provider, region, and resource type:

```text
python -m app.cli.main audit --provider aws --region us-east-1 --resource compute
```

Supported providers:

- `aws`
- `gcp`

Supported resource types:

- `all`
- `compute`
- `storage`
- `network`

### Generate Reports

Run the report command with default options:

```text
python -m app.cli.main report
```

Specify the report format, output file, and provider:

```text
python -m app.cli.main report --format json --output audit.json --provider gcp
```

### Clean Up Resources

The cleanup command uses dry-run mode by default:

```text
python -m app.cli.main cleanup
```

Specify a provider and resource:

```text
python -m app.cli.main cleanup --provider gcp --resource compute
```

To explicitly enable execution mode:

```text
python -m app.cli.main cleanup --provider gcp --resource compute --execute
```

Use `--help` with any command to view its available options:

```text
python -m app.cli.main audit --help
python -m app.cli.main report --help
python -m app.cli.main cleanup --help
```

## Testing

Run the test suite with:

```text
pytest
```

Run tests with coverage:

```text
pytest --cov=app
```

## Documentation

Additional documentation is available in:

- `docs/ARCHITECTURE.md` — project architecture and module responsibilities.
- `docs/DEVELOPMENT.md` — development setup and contribution guidelines.

## Development Workflow

Development work is organized using issue-specific branches.

Example:

```text
issue-1-project-architecture
```

Changes should be submitted through pull requests and reviewed before merging into `main`.

## Security

Do not commit cloud credentials, access keys, secret keys, `.env` files, or other sensitive information to the repository.
