import typer

from app.aws.region import DEFAULT_AWS_REGION, validate_aws_region

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

    normalized_provider = provider.lower()
    normalized_resource = resource.lower()

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
        except ValueError as exc:
            raise typer.BadParameter(
                str(exc),
                param_hint="--region",
            ) from exc

    typer.echo(
        f"Audit command selected: provider={normalized_provider}, "
        f"region={selected_region}, resource={normalized_resource}"
    )