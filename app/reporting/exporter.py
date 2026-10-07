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


def _serialize_finding(finding: Any) -> dict[str, Any]:
    """Convert an audit finding into the documented export structure."""

    if hasattr(finding, "to_dict"):
        data = finding.to_dict()
    elif isinstance(finding, dict):
        data = dict(finding)
    else:
        data = {
            field: getattr(finding, field, None)
            for field in EXPORT_FIELDS
        }

    severity = data.get("severity")
    if hasattr(severity, "value"):
        severity = severity.value

    status = data.get("status")
    if hasattr(status, "value"):
        status = status.value

    metadata = data.get("metadata") or {}

    return {
        "resource_type": data.get("resource_type"),
        "resource_id": data.get("resource_id"),
        "region": data.get("region"),
        "account_id": data.get("account_id"),
        "severity": severity,
        "status": status,
        "finding_type": metadata.get("finding_type"),
        "description": data.get("description"),
        "estimated_cost": data.get("estimated_cost"),
        "estimated_savings": data.get("estimated_savings"),
        "metadata": metadata,
    }


def export_json(
    data: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Export audit data to a JSON file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, default=str)

    return output


def export_csv(
    data: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Export audit records to a CSV file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not data:
        output.write_text("", encoding="utf-8")
        return output

    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=EXPORT_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(data)

    return output


def export_audit_results(
    results: list[Any],
    output_path: str | Path,
    export_format: str,
) -> Path:
    """Export audit results in the requested format."""

    export_format = export_format.lower().strip()

    if export_format not in {"json", "csv"}:
        raise ValueError(
            f"Unsupported export format: {export_format}. "
            "Use 'json' or 'csv'."
        )

    serialized_results = [
        _serialize_finding(result)
        for result in results
    ]

    if export_format == "json":
        return export_json(serialized_results, output_path)

    return export_csv(serialized_results, output_path)