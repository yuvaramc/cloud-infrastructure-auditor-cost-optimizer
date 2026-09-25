import typer

from app.reporting.exporter import export_audit_results

app = typer.Typer(help="Generate infrastructure audit reports.")

SUPPORTED_FORMATS = ["text", "json", "csv"]


@app.callback(invoke_without_command=True)
def report(
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Report output format: text, json, or csv.",
    ),
    output: str = typer.Option(
        "report.txt",
        "--output",
        "-o",
        help="Output file for the generated report.",
    ),
    provider: str = typer.Option(
        "aws",
        "--provider",
        "-p",
        help="Cloud provider used for the report.",
    ),
) -> None:
    """Generate an infrastructure audit report."""

    normalized_format = format.lower().strip()

    if normalized_format not in SUPPORTED_FORMATS:
        raise typer.BadParameter(
            f"Unsupported report format '{format}'. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    if normalized_format == "text":
        typer.echo(
            f"Report command selected: format={normalized_format}, "
            f"output={output}, provider={provider}"
        )
        return

    # The current audit command does not yet provide a findings
    # collection, so export an empty, valid report structure.
    findings = []

    try:
        export_audit_results(
            findings,
            output,
            normalized_format,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Report exported successfully: format={normalized_format}, "
        f"output={output}, provider={provider}"
    )