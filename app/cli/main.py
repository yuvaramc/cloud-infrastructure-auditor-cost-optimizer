import typer

app = typer.Typer(
    name="cloud-auditor",
    help="Audit cloud infrastructure and identify cost optimization opportunities.",
)


@app.callback()
def main() -> None:
    """Cloud Infrastructure Auditor & Cost Optimizer CLI."""


if __name__ == "__main__":
    app()