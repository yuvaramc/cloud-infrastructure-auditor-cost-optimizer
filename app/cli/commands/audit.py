import typer

app = typer.Typer(help="Audit cloud infrastructure resources.")


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
    typer.echo(
        f"Audit command selected: provider={provider}, "
        f"region={region}, resource={resource}"
    )
