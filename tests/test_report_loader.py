import csv
import json

import pytest

from app.reporting.report_loader import load_audit_results


@pytest.fixture
def sample_finding() -> dict:
    return {
        "resource_type": "EBS Volume",
        "resource_id": "vol-123456",
        "region": "us-east-1",
        "severity": "MEDIUM",
        "description": "Volume is unattached.",
        "estimated_cost": 12.5,
        "estimated_savings": 12.5,
        "metadata": {"volume_type": "gp3"},
    }


def test_load_json_findings(tmp_path, sample_finding):
    input_file = tmp_path / "findings.json"
    input_file.write_text(
        json.dumps([sample_finding]),
        encoding="utf-8",
    )

    findings = load_audit_results(input_file)

    assert len(findings) == 1
    assert findings[0]["resource_id"] == "vol-123456"
    assert findings[0]["metadata"] == {"volume_type": "gp3"}


def test_load_csv_findings(tmp_path, sample_finding):
    input_file = tmp_path / "findings.csv"

    with input_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sample_finding.keys())
        writer.writeheader()
        row = sample_finding.copy()
        row["metadata"] = json.dumps(row["metadata"])
        writer.writerow(row)

    findings = load_audit_results(input_file)

    assert len(findings) == 1
    assert findings[0]["resource_id"] == "vol-123456"
    assert findings[0]["metadata"] == {"volume_type": "gp3"}


def test_load_empty_json_list(tmp_path):
    input_file = tmp_path / "empty.json"
    input_file.write_text("[]", encoding="utf-8")

    assert load_audit_results(input_file) == []


def test_reject_unsupported_extension(tmp_path):
    input_file = tmp_path / "findings.xml"
    input_file.write_text("<findings />", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported input file format"):
        load_audit_results(input_file)


def test_reject_invalid_json(tmp_path):
    input_file = tmp_path / "findings.json"
    input_file.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="Unable to read audit results"):
        load_audit_results(input_file)


def test_reject_missing_required_field(tmp_path):
    input_file = tmp_path / "findings.json"
    input_file.write_text(
        json.dumps([{"resource_id": "vol-123456"}]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required fields"):
        load_audit_results(input_file)


def test_reject_negative_savings(tmp_path, sample_finding):
    sample_finding["estimated_savings"] = -1
    input_file = tmp_path / "findings.json"
    input_file.write_text(
        json.dumps([sample_finding]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="negative 'estimated_savings'"):
        load_audit_results(input_file)


def test_reject_non_list_json(tmp_path):
    input_file = tmp_path / "findings.json"
    input_file.write_text(
        json.dumps({"resource_id": "vol-123456"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must contain a list"):
        load_audit_results(input_file)

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("estimated_cost", float("nan")),
        ("estimated_cost", float("inf")),
        ("estimated_cost", float("-inf")),
        ("estimated_savings", float("nan")),
        ("estimated_savings", float("inf")),
        ("estimated_savings", float("-inf")),
    ],
)
def test_reject_non_finite_cost_values(tmp_path, sample_finding, field, value):
    sample_finding[field] = value
    input_file = tmp_path / "findings.json"
    input_file.write_text(
        json.dumps([sample_finding]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=f"invalid '{field}' value"):
        load_audit_results(input_file)