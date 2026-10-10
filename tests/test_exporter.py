
import csv
import json
from pathlib import Path

import pytest

from app.audit.models import (
    AuditFinding,
    FindingSeverity,
    FindingStatus,
)
from app.reporting.exporter import (
    EXPORT_FIELDS,
    export_audit_results,
    export_csv,
    export_json,
)


SAMPLE_RESULTS = [
    {
        "resource_type": "EC2",
        "resource_id": "i-1234567890",
        "region": "us-east-1",
        "account_id": "123456789012",
        "severity": "HIGH",
        "status": "OPEN",
        "description": "Unused EC2 instance",
        "estimated_cost": 25.50,
        "estimated_savings": 25.50,
        "metadata": {"instance_type": "t3.medium"},
    },
    {
        "resource_type": "EBS",
        "resource_id": "vol-1234567890",
        "region": "us-east-1",
        "account_id": "123456789012",
        "severity": "MEDIUM",
        "status": "OPEN",
        "description": "Unused EBS volume",
        "estimated_cost": 10.00,
        "estimated_savings": 10.00,
        "metadata": {"volume_type": "gp3"},
    },
]


@pytest.fixture
def sample_findings() -> list[AuditFinding]:
    """Provide realistic audit findings using the project data model."""

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


def test_export_json(tmp_path: Path):
    output_file = tmp_path / "audit_results.json"

    result = export_json(SAMPLE_RESULTS, output_file)

    assert result == output_file
    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))

    assert len(data) == 2
    assert data[0]["resource_type"] == "EC2"
    assert data[0]["resource_id"] == "i-1234567890"
    assert data[0]["estimated_cost"] == 25.50
    assert data[0]["estimated_savings"] == 25.50
    assert data[0]["metadata"]["instance_type"] == "t3.medium"


def test_export_json_from_audit_findings(
    tmp_path: Path,
    sample_findings: list[AuditFinding],
):
    output_file = tmp_path / "findings.json"

    export_json(sample_findings, output_file)

    data = json.loads(output_file.read_text(encoding="utf-8"))

    assert len(data) == 2
    assert data[0]["resource_id"] == "i-123456"
    assert data[0]["severity"] == "HIGH"
    assert data[0]["status"] == "OPEN"
    assert data[0]["account_id"] == "123456789012"
    assert data[0]["estimated_cost"] == 120.50
    assert data[0]["estimated_savings"] == 45.25


def test_export_csv(tmp_path: Path):
    output_file = tmp_path / "audit_results.csv"

    result = export_csv(SAMPLE_RESULTS, output_file)

    assert result == output_file
    assert output_file.exists()

    with output_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["resource_type"] == "EC2"
    assert rows[0]["resource_id"] == "i-1234567890"
    assert rows[0]["region"] == "us-east-1"
    assert rows[0]["account_id"] == "123456789012"
    assert rows[0]["severity"] == "HIGH"
    assert rows[0]["estimated_cost"] == "25.5"
    assert rows[0]["estimated_savings"] == "25.5"

    metadata = json.loads(rows[0]["metadata"])
    assert metadata["instance_type"] == "t3.medium"


def test_export_csv_from_audit_findings(
    tmp_path: Path,
    sample_findings: list[AuditFinding],
):
    output_file = tmp_path / "findings.csv"

    export_csv(sample_findings, output_file)

    with output_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["resource_id"] == "i-123456"
    assert rows[0]["severity"] == "HIGH"
    assert rows[0]["status"] == "OPEN"
    assert rows[0]["estimated_cost"] == "120.5"
    assert rows[0]["estimated_savings"] == "45.25"


def test_export_json_empty_results(tmp_path: Path):
    output_file = tmp_path / "empty.json"

    export_json([], output_file)

    assert output_file.exists()
    assert json.loads(output_file.read_text(encoding="utf-8")) == []


def test_export_csv_empty_results(tmp_path: Path):
    output_file = tmp_path / "empty.csv"

    export_csv([], output_file)

    assert output_file.exists()

    with output_file.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.reader(file)
        header = next(reader)

    assert header == EXPORT_FIELDS


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


def test_export_format_is_case_insensitive(tmp_path: Path):
    output_file = tmp_path / "results.json"

    export_audit_results(
        SAMPLE_RESULTS,
        output_file,
        "JSON",
    )

    assert json.loads(output_file.read_text(encoding="utf-8"))


def test_unsupported_export_format(tmp_path: Path):
    output_file = tmp_path / "results.xml"

    with pytest.raises(
        ValueError,
        match="Unsupported export format",
    ):
        export_audit_results(
            SAMPLE_RESULTS,
            output_file,
            "xml",
        )

    assert not output_file.exists()
