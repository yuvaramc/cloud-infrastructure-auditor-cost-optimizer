
"""Audit finding aggregation utilities."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from app.audit.models import AuditFinding


@dataclass(frozen=True)
class ScannerFailure:
    """Details about a scanner that failed during aggregation."""

    scanner_index: int
    error_type: str
    message: str


class AggregatedAuditResult:
    """Unified result containing findings collected from audit scanners."""

    def __init__(
        self,
        findings: Iterable[AuditFinding],
        scanner_failures: Iterable[ScannerFailure] | None = None,
    ) -> None:
        """Initialize an aggregated audit result."""

        self.findings = list(findings)
        self.scanner_failures = list(scanner_failures or [])

    @property
    def total_findings(self) -> int:
        """Return the total number of findings."""

        return len(self.findings)

    @property
    def findings_by_resource_type(self) -> dict[str, int]:
        """Return the number of findings grouped by resource type."""

        return dict(Counter(finding.resource_type for finding in self.findings))

    @property
    def findings_by_finding_type(self) -> dict[str, int]:
        """Return the number of findings grouped by finding type."""

        return dict(
            Counter(
                finding.metadata.get("finding_type", "unknown")
                for finding in self.findings
            )
        )

    @property
    def findings_by_severity(self) -> dict[str, int]:
        """Return the number of findings grouped by severity."""

        return dict(Counter(finding.severity.value for finding in self.findings))

    @property
    def total_potential_savings(self) -> float:
        """Return the total estimated savings across all findings."""

        return sum(
            finding.estimated_savings or 0.0
            for finding in self.findings
        )

    @property
    def potential_savings_by_resource_type(self) -> dict[str, float]:
        """Return estimated savings grouped by resource type."""

        savings: dict[str, float] = {}

        for finding in self.findings:
            resource_type = finding.resource_type
            estimated_savings = finding.estimated_savings

            if estimated_savings is not None:
                savings[resource_type] = (
                    savings.get(resource_type, 0.0) + estimated_savings
                )

        return savings


def collect_findings(
    scanner_results: Iterable[Iterable[AuditFinding] | None],
) -> list[AuditFinding]:
    """Collect findings while safely ignoring empty scanner results."""

    findings: list[AuditFinding] = []

    for scanner_result in scanner_results:
        if scanner_result is None:
            continue

        findings.extend(scanner_result)

    return findings


def aggregate_scanner_results(
    scanner_results: Iterable[Iterable[AuditFinding] | None],
) -> AggregatedAuditResult:
    """Aggregate scanner findings while recording individual scanner failures."""

    findings: list[AuditFinding] = []
    scanner_failures: list[ScannerFailure] = []

    for scanner_index, scanner_result in enumerate(scanner_results, start=1):
        if scanner_result is None:
            continue

        try:
            # Collect each scanner's complete output before adding it.
            # This prevents partial results from a failed scanner being included.
            scanner_findings = list(scanner_result)
        except Exception as exc:
            scanner_failures.append(
                ScannerFailure(
                    scanner_index=scanner_index,
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            continue

        findings.extend(scanner_findings)

    return AggregatedAuditResult(
        findings=findings,
        scanner_failures=scanner_failures,
    )