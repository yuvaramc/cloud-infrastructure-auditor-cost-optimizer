from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def export_json(
    data: Any,
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

    fieldnames = list(data[0].keys())

    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(data)

    return output


def export_audit_results(
    results: list[dict[str, Any]],
    output_path: str | Path,
    export_format: str,
) -> Path:
    """Export audit results in the requested format."""

    export_format = export_format.lower().strip()

    if export_format == "json":
        return export_json(results, output_path)

    if export_format == "csv":
        return export_csv(results, output_path)

    raise ValueError(
        f"Unsupported export format: {export_format}. "
        "Use 'json' or 'csv'."
    )