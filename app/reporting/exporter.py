
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


EXPORT_FIELDS = [
    "resource_type",
    "resource_id",
    "region",
    "account_id",
    "severity",
    "status",
    "finding_type",
    "description",
    "estimated_cost",
    "estimated_savings",
    "metadata",
]

SUPPORTED_FORMATS = {"json", "csv"}


def _serialize_finding(finding: Any) -> dict[str, Any]:
    """Convert a dictionary or AuditFinding into a JSON/CSV-safe record."""

    if hasattr(finding, "to_dict"):
        data = finding.to_dict()
    elif isinstance(finding, dict):
        data = dict(finding)
    else:
        data = {
            field: getattr(finding, field, None)
            for field in EXPORT_FIELDS
        }

    # Normalize enum fields such as FindingSeverity.HIGH.
    severity = data.get("severity")
    if hasattr(severity, "value"):
        severity = severity.value

    status = data.get("status")
    if hasattr(status, "value"):
        status = status.value

    metadata = data.get("metadata") or {}

    if not isinstance(metadata, dict):
        metadata = {"value": metadata}

    # Preserve finding_type if it is already a top-level field.
    finding_type = data.get("finding_type")
    if finding_type is None:
        finding_type = metadata.get("finding_type")

    if hasattr(finding_type, "value"):
        finding_type = finding_type.value

    return {
        "resource_type": data.get("resource_type"),
        "resource_id": data.get("resource_id"),
        "region": data.get("region"),
        "account_id": data.get("account_id"),
        "severity": severity,
        "status": status,
        "finding_type": finding_type,
        "description": data.get("description"),
        "estimated_cost": data.get("estimated_cost"),
        "estimated_savings": data.get("estimated_savings"),
        "metadata": metadata,
    }


def export_json(
    data: list[Any],
    output_path: str | Path,
) -> Path:
    """Export audit findings to a JSON file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    records = [_serialize_finding(item) for item in data]

    with output.open("w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return output


def export_csv(
    data: list[Any],
    output_path: str | Path,
) -> Path:
    """Export audit findings to a CSV file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    records = [_serialize_finding(item) for item in data]

    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=EXPORT_FIELDS,
            extrasaction="ignore",
        )

        # Write the header even when there are no audit findings.
        writer.writeheader()

        for record in records:
            row = dict(record)

            # CSV cells are text, so encode nested metadata as JSON.
            row["metadata"] = json.dumps(
                row.get("metadata") or {},
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )

            writer.writerow(row)

    return output


def export_audit_results(
    results: list[Any],
    output_path: str | Path,
    export_format: str,
) -> Path:
    """Export audit results in JSON or CSV format."""

    normalized_format = export_format.strip().lower()

    if normalized_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported export format: {normalized_format}. "
            "Use 'json' or 'csv'."
        )

    if normalized_format == "json":
        return export_json(results, output_path)

    return export_csv(results, output_path)
