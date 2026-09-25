import typer

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
        "us-east-1",
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

    if provider.lower() not in SUPPORTED_PROVIDERS:
        raise typer.BadParameter(
            f"Unsupported provider '{provider}'. "
            f"Choose from: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    if resource.lower() not in SUPPORTED_RESOURCES:
        raise typer.BadParameter(
            f"Unsupported resource '{resource}'. "
            f"Choose from: {', '.join(SUPPORTED_RESOURCES)}"
        )

    typer.echo(
        f"Audit command selected: provider={provider.lower()}, "
        f"region={region}, resource={resource.lower()}"
    )