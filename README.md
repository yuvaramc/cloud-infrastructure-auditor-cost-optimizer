# Cloud Infrastructure Auditor & Cost Optimizer

A Python CLI tool for auditing cloud infrastructure, identifying cost optimization opportunities, generating reports, and safely previewing cleanup actions.

## Project Goals

- Audit cloud infrastructure for potential cost and configuration issues.
- Identify unused or unnecessary cloud resources.
- Analyze infrastructure for cost optimization opportunities.
- Provide clear terminal and exportable reports.
- Support safe cleanup through dry-run previews.
- Support AWS initially, with architecture prepared for future Google Cloud integration.

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
