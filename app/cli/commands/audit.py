import typer

app = typer.Typer(help="Audit cloud infrastructure resources.")


@app.callback(invoke_without_command=True)
def audit() -> None:
    """Run infrastructure audit checks."""
    typer.echo("Audit command selected.")
