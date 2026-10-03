from pathlib import Path

import pytest

from app.reporting.exporter import (
    export_audit_results,
    export_csv,
    export_json,
)


SAMPLE_RESULTS = [
    {
        "resource_type": "EC2",
        "resource_id": "i-1234567890",
        "region": "us-east-1",
        "severity": "HIGH",
        "description": "Unused EC2 instance",
        "estimated_cost": 25.50,
        "estimated_savings": 25.50,
    },
    {
        "resource_type": "EBS",
        "resource_id": "vol-1234567890",
        "region": "us-east-1",
        "severity": "MEDIUM",
        "description": "Unused EBS volume",
        "estimated_cost": 10.00,
        "estimated_savings": 10.00,
    },
]


def test_export_json(tmp_path: Path):
    output_file = tmp_path / "audit_results.json"

    result = export_json(SAMPLE_RESULTS, output_file)

    assert result == output_file
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert '"resource_type": "EC2"' in content
    assert '"resource_id": "i-1234567890"' in content
    assert '"estimated_cost": 25.5' in content
    assert '"estimated_savings": 25.5' in content


def test_export_csv(tmp_path: Path):
    output_file = tmp_path / "audit_results.csv"

    result = export_csv(SAMPLE_RESULTS, output_file)

    assert result == output_file
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert "resource_type" in content
    assert "resource_id" in content
    assert "region" in content
    assert "severity" in content
    assert "estimated_cost" in content
    assert "estimated_savings" in content

    assert "EC2" in content
    assert "i-1234567890" in content
    assert "25.5" in content


def test_export_json_empty_results(tmp_path: Path):
    output_file = tmp_path / "empty.json"

    export_audit_results([], output_file, "json")

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8").strip() == "[]"


def test_export_csv_empty_results(tmp_path: Path):
    output_file = tmp_path / "empty.csv"

    export_audit_results([], output_file, "csv")

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == ""


def test_export_audit_results_json(tmp_path: Path):
    output_file = tmp_path / "results.json"

    result = export_audit_results(
        SAMPLE_RESULTS,
        output_file,
        "json",
    )

    assert result == output_file
    assert output_file.exists()


def test_export_audit_results_csv(tmp_path: Path):
    output_file = tmp_path / "results.csv"

    result = export_audit_results(
        SAMPLE_RESULTS,
        output_file,
        "csv",
    )

    assert result == output_file
    assert output_file.exists()


def test_unsupported_export_format(tmp_path: Path):
    output_file = tmp_path / "results.xml"

    with pytest.raises(ValueError, match="Unsupported export format"):
        export_audit_results(
            SAMPLE_RESULTS,
            output_file,
            "xml",
        )