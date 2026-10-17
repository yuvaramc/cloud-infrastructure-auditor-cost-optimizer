
import csv
import json
import math
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "resource_type",
    "resource_id",
    "region",
    "severity",
    "description",
}


def load_audit_results(input_path: str | Path) -> list[dict[str, Any]]:
    """Load and validate audit findings from a JSON or CSV file."""
    path = Path(input_path)
    suffix = path.suffix.lower()

    if suffix not in {".json", ".csv"}:
        raise ValueError(
            "Unsupported input file format. Use a .json or .csv file."
        )

    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            if suffix == ".json":
                data = json.load(file)
            else:
                data = list(csv.DictReader(file))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Unable to read audit results: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Audit results must contain a list of findings.")

    for index, finding in enumerate(data):
        if not isinstance(finding, dict):
            raise ValueError(
                f"Finding at index {index} must be an object."
            )

        missing = REQUIRED_FIELDS - finding.keys()
        if missing:
            fields = ", ".join(sorted(missing))
            raise ValueError(
                f"Finding at index {index} is missing required fields: {fields}."
            )

        for field in REQUIRED_FIELDS:
            if not isinstance(finding[field], str) or not finding[field].strip():
                raise ValueError(
                    f"Finding at index {index} has an invalid '{field}' value."
                )

        for field in ("estimated_cost", "estimated_savings"):
            value = finding.get(field)
            if value in (None, ""):
                continue

            try:
                amount = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Finding at index {index} has an invalid '{field}' value."
                ) from exc

            if not math.isfinite(amount):
                raise ValueError(
                    f"Finding at index {index} has an invalid '{field}' value."
                )

            if amount < 0:
                raise ValueError(
                    f"Finding at index {index} has a negative '{field}' value."
                )

        metadata = finding.get("metadata")
        if isinstance(metadata, str):
            try:
                finding["metadata"] = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Finding at index {index} has invalid metadata JSON."
                ) from exc

    return data
