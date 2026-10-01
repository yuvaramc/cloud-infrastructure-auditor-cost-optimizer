"""Audit finding aggregation package."""

from app.audit.aggregation.aggregator import (
    AggregatedAuditResult,
    aggregate_scanner_results,
    collect_findings,
)

__all__ = [
    "AggregatedAuditResult",
    "aggregate_scanner_results",
    "collect_findings",
]
