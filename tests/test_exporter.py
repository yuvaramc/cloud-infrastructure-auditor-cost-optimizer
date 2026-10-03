import csv
import json

import pytest

from app.audit.models import (
    AuditFinding,
    FindingSeverity,
    FindingStatus,
)
from app.reporting.exporter import (
    export_audit_results,
    export_csv,
    export_json,
)


@pytest.fixture
def sample_findings() -> list[AuditFinding]:
    return [
        AuditFinding(
            resource_type="EC2",
            resource_id="i-123456",
            region="us-east-1",
            severity=FindingSeverity.HIGH,
            description="Underutilized EC2 instance.",
            account_id="123456789012",
            status=FindingStatus.OPEN,
            estimated_cost=120.50,
            estimated_savings=45.25,
            metadata={"instance_type": "t3.medium"},
        ),
        AuditFinding(
            resource_type="EBS",
            resource_id="vol-789012",
            region="us-east-1",
            severity=FindingSeverity.MEDIUM,
            description="Unused EBS volume.",
            account_id="123456789012",
            status=FindingStatus.OPEN,
            estimated_cost=80.00,
            estimated_savings=80.00,
            metadata={"volume_type": "gp3"},
        ),
    ]


def test_export_json(tmp_path, sample_findings):
    output_file = tmp_path / "audit_results.json"

    export_json(sample_findings, output_file)

    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert len(data) == 2
    assert data[0]["resource_id"] == "i-123456"
    assert data[0]["severity"] == "HIGH"
    assert data[0]["estimated_cost"] == 120.50
    assert data[0]["estimated_savings"] == 45.25


def test_export_csv(tmp_path, sample_findings):
    output_file = tmp_path / "audit_results.csv"

    export_csv(sample_findings, output_file)

    assert output_file.exists()

    with output_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["resource_id"] == "i-123456"
    assert rows[0]["resource_type"] == "EC2"
    assert rows[0]["severity"] == "HIGH"
    assert rows[0]["estimated_cost"] == "120.5"
    assert rows[0]["estimated_savings"] == "45.25"


def test_empty_json_export(tmp_path):
    output_file = tmp_path / "empty.json"

    export_json([], output_file)

    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data == []


def test_empty_csv_export(tmp_path):
    output_file = tmp_path / "empty.csv"

    export_csv([], output_file)

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert "resource_type" in content
    assert "estimated_cost" in content
    assert "estimated_savings" in content


def test_unsupported_format(tmp_path, sample_findings):
    output_file = tmp_path / "audit_results.xml"

    with pytest.raises(ValueError, match="Unsupported export format"):
        export_audit_results(
            sample_findings,
            output_file,
            "xml",
        )


def test_export_audit_results_json(tmp_path, sample_findings):
    output_file = tmp_path / "results.json"

    export_audit_results(
        sample_findings,
        output_file,
        "json",
    )

    assert output_file.exists()


def test_export_audit_results_csv(tmp_path, sample_findings):
    output_file = tmp_path / "results.csv"

    export_audit_results(
        sample_findings,
        output_file,
        "csv",
    )

    assert output_file.exists()