# Development Guide

## Python Version

The project requires Python 3.11 or newer.

## Project Setup

Create and activate a virtual environment before installing project dependencies.

```text
python -m venv .venv
```

On Windows PowerShell:

```text
.venv\Scripts\Activate.ps1
```

Install the project with development dependencies:

```text
pip install -e ".[dev]"
```

## Running Tests

Run the complete test suite with:

```text
pytest
```

Run tests with coverage:

```text
pytest --cov=app
```

## Development Structure

Application code belongs under `app/`.

Tests belong under `tests/`.

Architecture and developer documentation belong under `docs/`.

## Development Guidelines

- Keep cloud-provider-specific code inside the appropriate provider package.
- Do not commit credentials, access keys, or other secrets.
- Keep CLI commands focused on input handling and orchestration.
- Keep business logic outside the CLI layer.
- Add tests for new application behavior.
- Use clear and descriptive commit messages.
- Keep pull requests focused on a single issue.
- Run the test suite before submitting a pull request.

## Branching

Development work should be performed on issue-specific branches.

Example:

```text
issue-1-project-architecture
```

Changes should be reviewed through pull requests before being merged into `main`.
