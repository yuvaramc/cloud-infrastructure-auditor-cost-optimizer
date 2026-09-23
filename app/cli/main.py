import typer

from app.cli.commands import audit, cleanup, report

VERSION = "0.1.0"

app = typer.Typer(
    name="cloud-auditor",
    help="Audit cloud infrastructure and identify cost optimization opportunities.",
)

app.add_typer(audit.app, name="audit")
app.add_typer(report.app, name="report")
app.add_typer(cleanup.app, name="cleanup")


@app.callback()
def main() -> None:
    """Cloud Infrastructure Auditor & Cost Optimizer CLI."""


@app.command()
def version() -> None:
    """Display the current CLI version."""
    typer.echo(f"cloud-auditor version {VERSION}")


if __name__ == "__main__":
    app()
