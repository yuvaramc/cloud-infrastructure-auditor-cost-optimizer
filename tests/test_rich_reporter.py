from io import StringIO

from rich.console import Console

from app.reporting.rich_reporter import render_audit_report


def test_render_audit_report_with_findings():
    output = StringIO()
    console = Console(
        file=output,
        force_terminal=False,
        width=200,
    )

    findings = [
        {
            "resource_type": "EC2",
            "resource_id": "i-123456789",
            "region": "us-east-1",
            "severity": "HIGH",
            "description": "Unused EC2 instance",
            "estimated_cost": 25.50,
            "estimated_savings": 25.50,
        }
    ]

    render_audit_report(findings, console)

    result = output.getvalue()

    assert "Cloud Infrastructure Audit Results" in result
    assert "EC2" in result
    assert "i-123456789" in result
    assert "us-east-1" in result
    assert "HIGH" in result
    assert "Unused EC2 instance" in result
    assert "$25.50" in result
    assert "Total findings: 1" in result
    assert "Potential savings: $25.50" in result


def test_render_audit_report_empty():
    output = StringIO()
    console = Console(
        file=output,
        force_terminal=False,
        width=200,
    )

    render_audit_report([], console)

    result = output.getvalue()

    assert "No audit findings were found." in result
    assert "Total findings: 0" in result
    assert "Potential savings: $0.00" in result