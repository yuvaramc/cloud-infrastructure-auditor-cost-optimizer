"""CLI commands for infrastructure auditing."""

import typer

from app.audit.aggregation.aggregator import AggregatedAuditResult
from app.aws.region import DEFAULT_AWS_REGION, validate_aws_region
from app.aws.session import AWSAuthenticationError, get_aws_session
from app.reporting.rich_reporter import render_audit_report
from app.scanners.ebs import EBSScannerError, scan_ebs_volumes

app = typer.Typer(help="Audit cloud infrastructure resources.")

SUPPORTED_PROVIDERS = ["aws", "gcp"]
SUPPORTED_RESOURCES = ["all", "compute", "storage", "network"]


@app.callback(invoke_without_command=True)
def audit(
    provider: str = typer.Option(
        "aws",
        "--provider",
        "-p",
        help="Cloud provider to audit.",
    ),
    region: str = typer.Option(
        DEFAULT_AWS_REGION,
        "--region",
        "-r",
        help="Cloud region to audit.",
    ),
    resource: str = typer.Option(
        "all",
        "--resource",
        help="Resource type to audit.",
    ),
) -> None:
    """Run infrastructure audit checks."""

    normalized_provider = provider.strip().lower()
    normalized_resource = resource.strip().lower()

    if normalized_provider not in SUPPORTED_PROVIDERS:
        raise typer.BadParameter(
            f"Unsupported provider '{provider}'. "
            f"Choose from: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    if normalized_resource not in SUPPORTED_RESOURCES:
        raise typer.BadParameter(
            f"Unsupported resource '{resource}'. "
            f"Choose from: {', '.join(SUPPORTED_RESOURCES)}"
        )

    selected_region = region.strip().lower()

    if normalized_provider == "aws":
        try:
            selected_region = validate_aws_region(region)
            session = get_aws_session(region=selected_region)

        except ValueError as exc:
            raise typer.BadParameter(
                str(exc),
                param_hint="--region",
            ) from exc

        except AWSAuthenticationError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

        scanner_results = []

        if normalized_resource in {"all", "storage"}:
            try:
                scanner_results.append(
                    scan_ebs_volumes(session)
                )
            except EBSScannerError as exc:
                typer.echo(
                    f"EBS scanner failed: {exc}",
                    err=True,
                )
                raise typer.Exit(code=1) from exc

        if normalized_resource in {"compute", "network"}:
            typer.echo(
                f"No {normalized_resource} scanners are currently implemented."
            )

        aggregated_result = AggregatedAuditResult(
            findings=(
                finding
                for scanner_findings in scanner_results
                for finding in scanner_findings
            )
        )

        findings = [
            finding.to_dict()
            for finding in aggregated_result.findings
        ]

        typer.echo(
            f"Audit completed: provider={normalized_provider}, "
            f"region={selected_region}, "
            f"resource={normalized_resource}"
        )

        render_audit_report(findings)
        return

    typer.echo(
        f"Audit command selected: provider={normalized_provider}, "
        f"region={selected_region}, resource={normalized_resource}"
    )
