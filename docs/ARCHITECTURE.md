# Project Architecture

## 1. Overview

Cloud Infrastructure Auditor & Cost Optimizer is a Python-based CLI tool for auditing cloud infrastructure, identifying cost optimization opportunities, generating reports, and safely managing eligible cloud resources.

The project is organized into separate layers so that CLI interaction, authentication, auditing, reporting, cleanup, and cloud-provider integrations remain loosely coupled.

## 2. Project Structure

````text
app/
|-- cli/
|-- auth/
|-- audit/
|-- reporting/
|-- cleanup/
|-- core/
`-- providers/
    |-- aws/
    `-- gcp/

tests/
docs/

## 3. Module Responsibilities

### app/cli/

Contains CLI commands and command routing.

### app/auth/

Handles cloud authentication, sessions, profiles, and role-based access.

### app/audit/

Contains infrastructure audit logic and resource scanners.

### app/reporting/

Handles terminal reporting and structured report generation.

### app/cleanup/

Handles safe resource cleanup and dry-run operations.

### app/core/

Contains shared configuration, models, utilities, exceptions, retry handling, and common functionality.

### app/providers/

Contains cloud-provider-specific implementations.

- `aws/` - AWS-specific integrations.
- `gcp/` - Google Cloud integrations and future support.

## 4. Application Flow

```text
User
  |
  v
CLI Layer
  |
  v
Authentication / Configuration
  |
  v
Provider Integration
  |
  v
Audit Engine
  |
  +------> Reporting
  |
  +------> Cleanup
````

## 5. Provider Design

Cloud-provider-specific code is isolated inside the provider layer.

AWS functionality will be implemented first, while the structure allows Google Cloud support to be added without restructuring the main application.

## 6. Configuration

Project metadata and dependencies are defined in `pyproject.toml`.

Runtime configuration should remain separate from package metadata.

Credentials and other sensitive information must never be hard-coded or committed to the repository.

## 7. Testing

Tests are maintained under the `tests/` directory.

Testing will cover CLI behavior, authentication, audit scanners, provider integrations, reporting, exports, and cleanup safety.

Cloud-service operations should be mocked or simulated where appropriate.

## 8. Parallel Development

The layered structure allows team members to work independently on CLI, authentication, provider integrations, audit scanners, reporting, cleanup, and testing.

Keeping responsibilities separated should reduce integration conflicts during parallel development.

## 9. Design Principles

1. Separate responsibilities by application layer.
2. Keep cloud-provider-specific code isolated.
3. Never hard-code credentials.
4. Keep audit operations separate from destructive cleanup.
5. Keep reporting independent from audit discovery.
6. Prefer reusable application services over CLI-specific business logic.
7. Keep the architecture extensible for additional cloud providers.
