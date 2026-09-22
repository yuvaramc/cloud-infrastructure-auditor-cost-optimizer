from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from app.reporting.exporter import export_audit_results


app = typer.Typer(
    help="Cloud Infrastructure Auditor & Cost Optimizer"
)


@app.command()
def export(
    output: Path = typer.Option(
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

    results: list[dict[str, Any]] = []

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