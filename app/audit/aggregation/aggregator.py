"""Audit finding aggregation utilities."""

from collections import Counter
from collections.abc import Iterable

from app.audit.models import AuditFinding


class AggregatedAuditResult:
    """Unified result containing findings collected from audit scanners."""

    def __init__(self, findings: Iterable[AuditFinding]) -> None:
        """Initialize an aggregated audit result."""

        self.findings = list(findings)

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


def collect_findings(
    scanner_results: Iterable[Iterable[AuditFinding]],
) -> list[AuditFinding]:
    """Collect findings returned by multiple audit scanners."""

    findings: list[AuditFinding] = []

    for scanner_result in scanner_results:
        findings.extend(scanner_result)

    return findings


def aggregate_scanner_results(
    scanner_results: Iterable[Iterable[AuditFinding]],
) -> AggregatedAuditResult:
    """Combine scanner results into a unified audit result."""

    findings = collect_findings(scanner_results)
    return AggregatedAuditResult(findings)