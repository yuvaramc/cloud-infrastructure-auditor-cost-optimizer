"""Audit finding aggregation utilities."""

from collections.abc import Iterable

from app.audit.models import AuditFinding


def collect_findings(
    scanner_results: Iterable[Iterable[AuditFinding]],
) -> list[AuditFinding]:
    """Collect findings returned by multiple audit scanners.

    Each scanner result is expected to contain AuditFinding objects.
    Scanner results that contain no findings contribute nothing to
    the collected result.
    """

    findings: list[AuditFinding] = []

    for scanner_result in scanner_results:
        findings.extend(scanner_result)

    return findings
