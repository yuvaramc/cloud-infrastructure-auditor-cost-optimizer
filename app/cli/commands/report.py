import typer

app = typer.Typer(help="Generate infrastructure audit reports.")


@app.callback(invoke_without_command=True)
def report(
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Report output format.",
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
    typer.echo(
        f"Report command selected: format={format}, "
        f"output={output}, provider={provider}"
    )
