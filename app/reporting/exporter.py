import csv
import json
from pathlib import Path
from typing import Any

from app.audit.models import AuditFinding


SUPPORTED_FORMATS = {"json", "csv"}


def _normalize_results(
    findings: list[AuditFinding],
) -> list[dict[str, Any]]:
    """Convert audit findings into JSON/CSV-compatible dictionaries."""
    return [finding.to_dict() for finding in findings]


def export_json(
    findings: list[AuditFinding],
    output_path: str | Path,
) -> None:
    """Export audit findings to JSON."""
    output = Path(output_path)
    data = _normalize_results(findings)

    with output.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def export_csv(
    findings: list[AuditFinding],
    output_path: str | Path,
) -> None:
    """Export audit findings to CSV."""
    output = Path(output_path)
    data = _normalize_results(findings)

    fieldnames = [
        "resource_type",
        "resource_id",
        "region",
        "severity",
        "description",
        "account_id",
        "status",
        "estimated_cost",
        "estimated_savings",
        "metadata",
    ]

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in data:
            row["metadata"] = json.dumps(row["metadata"])
            writer.writerow(row)


def export_audit_results(
    findings: list[AuditFinding],
    output_path: str | Path,
    export_format: str,
) -> None:
    """Export audit findings as JSON or CSV."""

    normalized_format = export_format.lower().strip()

    if normalized_format not in SUPPORTED_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(
            f"Unsupported export format: '{export_format}'. "
            f"Supported formats: {supported}."
        )

    if normalized_format == "json":
        export_json(findings, output_path)
    else:
        export_csv(findings, output_path)