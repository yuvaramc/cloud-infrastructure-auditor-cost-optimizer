from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class FindingSeverity(str, Enum):
    """Severity level of an audit finding."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingStatus(str, Enum):
    """Current status of an audit finding."""

    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


@dataclass
class AuditFinding:
    """Common data model for an AWS infrastructure audit finding."""

    resource_type: str
    resource_id: str
    region: str
    severity: FindingSeverity
    description: str
    account_id: str | None = None
    status: FindingStatus = FindingStatus.OPEN
    estimated_cost: float | None = None
    estimated_savings: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate required and numeric finding data."""

        if not self.resource_type.strip():
            raise ValueError("resource_type cannot be empty.")

        if not self.resource_id.strip():
            raise ValueError("resource_id cannot be empty.")

        if not self.region.strip():
            raise ValueError("region cannot be empty.")

        if not self.description.strip():
            raise ValueError("description cannot be empty.")

        if self.estimated_cost is not None and self.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative.")

        if self.estimated_savings is not None and self.estimated_savings < 0:
            raise ValueError("estimated_savings cannot be negative.")

    def to_dict(self) -> dict[str, Any]:
        """Convert the finding into a JSON-compatible dictionary."""

        data = asdict(self)
        data["severity"] = self.severity.value
        data["status"] = self.status.value
        return data