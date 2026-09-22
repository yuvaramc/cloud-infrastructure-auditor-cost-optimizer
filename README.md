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

## CLI Entry Point

The project provides the following CLI command:

```text
cloud-auditor
```

CLI commands will be implemented incrementally as the project develops.

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
