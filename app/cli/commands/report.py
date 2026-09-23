import typer

app = typer.Typer(help="Generate infrastructure audit reports.")


@app.callback(invoke_without_command=True)
def report() -> None:
    """Generate an infrastructure audit report."""
    typer.echo("Report command selected.")
