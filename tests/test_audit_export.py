import importlib

import pytest
from typer.testing import CliRunner

from app.audit.models import AuditFinding, FindingSeverity
from app.cli.main import app
from app.reporting.report_loader import load_audit_results


runner = CliRunner()
audit_module = importlib.import_module("app.cli.commands.audit")


@pytest.mark.parametrize("export_format", ["json", "csv"])
def test_audit_export_can_be_loaded_and_reported(
    tmp_path,
    monkeypatch,
    export_format,
) -> None:
    finding = AuditFinding(
        resource_type="EBS Volume",
        resource_id="vol-123456",
        region="us-east-1",
        severity=FindingSeverity.MEDIUM,
        description=(
            "EBS volume vol-123456 is not attached "
            "to any EC2 instance."
        ),
        estimated_savings=12.50,
    )

    mock_session = object()

    monkeypatch.setattr(
        audit_module,
        "get_aws_session",
        lambda region: mock_session,
    )
    monkeypatch.setattr(
        audit_module,
        "scan_ebs_volumes",
        lambda session: [finding],
    )

    output_path = tmp_path / f"audit-findings.{export_format}"

    audit_result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "aws",
            "--region",
            "us-east-1",
            "--resource",
            "storage",
            "--output",
            str(output_path),
            "--format",
            export_format,
        ],
    )

    assert audit_result.exit_code == 0, audit_result.output
    assert output_path.exists()
    assert "Audit findings exported" in audit_result.output

    loaded_findings = load_audit_results(output_path)

    assert len(loaded_findings) == 1
    assert loaded_findings[0]["resource_id"] == "vol-123456"
    assert loaded_findings[0]["resource_type"] == "EBS Volume"
    assert loaded_findings[0]["region"] == "us-east-1"

    report_result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(output_path),
            "--format",
            "text",
        ],
    )

    assert report_result.exit_code == 0, report_result.output
    assert "Total findings: 1" in report_result.output
