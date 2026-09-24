import typer

app = typer.Typer(help="Clean up identified cloud resources.")


@app.callback(invoke_without_command=True)
def cleanup(
    provider: str = typer.Option(
        "aws",
        "--provider",
        "-p",
        help="Cloud provider for cleanup.",
    ),
    resource: str = typer.Option(
        "all",
        "--resource",
        help="Resource type to clean up.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview cleanup actions without making changes.",
    ),
) -> None:
    """Run cloud resource cleanup operations."""
    mode = "dry-run" if dry_run else "execute"

    typer.echo(
        f"Cleanup command selected: provider={provider}, "
        f"resource={resource}, mode={mode}"
    )
