import typer

from app.cli.commands import audit, cleanup, report
from app.reporting.exporter import export_audit_results

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


@app.command()
def export(
    output: str = typer.Option(
        ...,
        "--output",
        "-o",
        help="Output file path.",
    ),
    export_format: str = typer.Option(
        ...,
        "--export-format",
        "-f",
        help="Export format: json or csv.",
    ),
) -> None:
    """Export audit results to JSON or CSV."""

    results: list[dict] = []

    try:
        output_path = export_audit_results(
            results=results,
            output_path=output,
            export_format=export_format,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Audit results exported to {output_path}"
    )


if __name__ == "__main__":
    app()