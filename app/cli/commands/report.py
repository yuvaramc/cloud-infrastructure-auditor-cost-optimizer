
import typer

from app.reporting.exporter import export_audit_results
from app.reporting.report_loader import load_audit_results
from app.reporting.rich_reporter import render_audit_report

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
    input_file: str = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to an existing audit results JSON or CSV file.",
    ),
) -> None:
    """Generate a report from previously exported audit results."""

    normalized_format = format.strip().lower()

    if normalized_format not in SUPPORTED_FORMATS:
        raise typer.BadParameter(
            f"Unsupported report format '{format}'. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    try:
        findings = load_audit_results(input_file)
    except ValueError as exc:
        raise typer.BadParameter(
            str(exc),
            param_hint="--input",
        ) from exc

    if normalized_format == "text":
        render_audit_report(findings)
        return

    try:
        export_audit_results(
            findings,
            output,
            normalized_format,
        )
    except (OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Report exported successfully: format={normalized_format}, "
        f"output={output}"
    )
