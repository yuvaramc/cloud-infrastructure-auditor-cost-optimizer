"""CLI commands for safe cloud resource cleanup."""

import typer

from app.audit.aggregation.aggregator import AggregatedAuditResult
from app.aws.region import DEFAULT_AWS_REGION, validate_aws_region
from app.aws.session import AWSAuthenticationError, get_aws_session
from app.cleanup.formatter import format_cleanup_preview
from app.cleanup.preview import build_cleanup_preview
from app.scanners.ebs import EBSScannerError, scan_ebs_volumes

app = typer.Typer(help="Clean up identified cloud resources.")

SUPPORTED_PROVIDERS = ["aws"]
SUPPORTED_RESOURCES = ["all", "storage"]


@app.callback(invoke_without_command=True)
def cleanup(
    provider: str = typer.Option(
        "aws",
        "--provider",
        "-p",
        help="Cloud provider for cleanup.",
    ),
    region: str = typer.Option(
        DEFAULT_AWS_REGION,
        "--region",
        "-r",
        help="AWS region to scan.",
    ),
    resource: str = typer.Option(
        "all",
        "--resource",
        help="Resource type to clean up.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview cleanup actions without making changes.",
    ),
) -> None:
    """Generate a read-only preview of eligible cleanup actions."""

    normalized_provider = provider.strip().lower()
    normalized_resource = resource.strip().lower()

    if normalized_provider not in SUPPORTED_PROVIDERS:
        raise typer.BadParameter(
            f"Unsupported provider '{provider}'. "
            f"Currently supported: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    if normalized_resource not in SUPPORTED_RESOURCES:
        raise typer.BadParameter(
            f"Unsupported resource '{resource}'. "
            f"Currently supported: {', '.join(SUPPORTED_RESOURCES)}"
        )

    if not dry_run:
        typer.echo(
            "Cleanup execution is not implemented. "
            "Only --dry-run is supported. No changes were made.",
            err=True,
        )
        raise typer.Exit(code=2)

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

    try:
        findings = scan_ebs_volumes(session)

    except EBSScannerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    aggregated_results = AggregatedAuditResult(findings)

    preview = build_cleanup_preview(aggregated_results)

    typer.echo(format_cleanup_preview(preview))
