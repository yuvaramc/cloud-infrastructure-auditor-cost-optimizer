import csv
import json

import pytest
from typer.testing import CliRunner

from app.cli.main import app


runner = CliRunner()


@pytest.fixture
def input_file(tmp_path):
    path = tmp_path / "audit_results.json"
    findings = [
        {
            "resource_type": "EBS",
            "resource_id": "vol-report-test",
            "region": "us-east-1",
            "severity": "MEDIUM",
            "description": "Unused EBS volume.",
            "account_id": "123456789012",
            "status": "OPEN",
            "estimated_cost": 15.0,
            "estimated_savings": 15.0,
            "metadata": {"volume_type": "gp3"},
        }
    ]
    path.write_text(json.dumps(findings), encoding="utf-8")
    return path


def test_report_text_format_succeeds(input_file):
    result = runner.invoke(
        app,
        ["report", "--input", str(input_file), "--format", "text"],
    )

    assert result.exit_code == 0, result.output
    assert "Cloud Infrastructure Audit Results" in result.output
    assert "EBS" in result.output
    assert "Audit Summary" in result.output
    assert "Total findings: 1" in result.output
    assert "$15.00" in result.output


@pytest.mark.parametrize("export_format", ["json", "csv"])
def test_report_exports_loaded_findings(tmp_path, input_file, export_format):
    output_file = tmp_path / f"report.{export_format}"

    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(input_file),
            "--format",
            export_format,
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0, result.output
    assert output_file.exists()
    assert "Report exported successfully" in result.output

    if export_format == "json":
        exported = json.loads(output_file.read_text(encoding="utf-8"))
        assert exported[0]["resource_id"] == "vol-report-test"
        assert exported[0]["metadata"] == {"volume_type": "gp3"}
    else:
        with output_file.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            exported = list(csv.DictReader(file))

        assert exported[0]["resource_id"] == "vol-report-test"
        assert json.loads(exported[0]["metadata"]) == {
            "volume_type": "gp3"
        }


def test_report_rejects_missing_input_file(tmp_path):
    missing_file = tmp_path / "does-not-exist.json"

    result = runner.invoke(
        app,
        ["report", "--input", str(missing_file)],
    )

    assert result.exit_code != 0
    assert "Unable to read audit results" in result.output


def test_report_rejects_unsupported_format(input_file):
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(input_file),
            "--format",
            "xml",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported report format" in result.output

def test_report_rejects_provider_option(input_file):
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(input_file),
            "--provider",
            "aws",
        ],
    )

    assert result.exit_code != 0
    assert "provider" in result.output.lower()
