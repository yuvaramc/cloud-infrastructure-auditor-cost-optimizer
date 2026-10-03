from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def render_audit_report(
    findings: list[dict[str, Any]],
    console: Console | None = None,
) -> None:
    """Render audit findings as a Rich terminal report."""

    console = console or Console()

    if not findings:
        console.print(
            Panel(
                "No audit findings were found.",
                title="Cloud Infrastructure Audit",
                border_style="yellow",
            )
        )
        console.print("Total findings: 0")
        console.print("Potential savings: $0.00")
        return

    table = Table(
        title="Cloud Infrastructure Audit Results",
        show_lines=True,
    )

    table.add_column(
        "Resource Type",
        style="cyan",
        no_wrap=True,
    )
    table.add_column(
        "Resource ID",
        style="white",
        no_wrap=True,
        overflow="fold",
    )
    table.add_column(
        "Region",
        style="green",
        no_wrap=True,
    )
    table.add_column(
        "Severity",
        style="yellow",
        no_wrap=True,
    )
    table.add_column(
        "Description",
        style="white",
    )
    table.add_column(
        "Estimated Cost",
        justify="right",
        no_wrap=True,
    )
    table.add_column(
        "Potential Savings",
        justify="right",
        no_wrap=True,
    )

    total_savings = 0.0

    for finding in findings:
        estimated_cost = finding.get("estimated_cost")
        estimated_savings = finding.get("estimated_savings")

        if estimated_savings is not None:
            try:
                total_savings += float(estimated_savings)
            except (TypeError, ValueError):
                pass

        table.add_row(
            str(finding.get("resource_type", "N/A")),
            str(finding.get("resource_id", "N/A")),
            str(finding.get("region", "N/A")),
            str(
                finding.get(
                    "severity",
                    finding.get("status", "N/A"),
                )
            ),
            str(finding.get("description", "N/A")),
            _format_money(estimated_cost),
            _format_money(estimated_savings),
        )

    console.print(table)

    console.print(
        Panel(
            f"Total findings: {len(findings)}\n"
            f"Potential savings: ${total_savings:,.2f}",
            title="Audit Summary",
            border_style="green",
        )
    )


def _format_money(value: Any) -> str:
    """Format a cost or savings value for terminal display."""

    if value is None or value == "":
        return "N/A"

    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)