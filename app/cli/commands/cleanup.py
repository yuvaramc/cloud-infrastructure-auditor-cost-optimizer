import typer

app = typer.Typer(help="Clean up identified cloud resources.")


@app.callback(invoke_without_command=True)
def cleanup() -> None:
    """Run cloud resource cleanup operations."""
    typer.echo("Cleanup command selected.")
