import typer

app = typer.Typer(
    name="cloud-auditor",
    help="Audit cloud infrastructure and identify cost optimization opportunities.",
)

VERSION = "0.1.0"


@app.command()
def version() -> None:
    """Display the current CLI version."""
    typer.echo(f"cloud-auditor version {VERSION}")


@app.callback()
def main() -> None:
    """Cloud Infrastructure Auditor & Cost Optimizer CLI."""


if __name__ == "__main__":
    app()