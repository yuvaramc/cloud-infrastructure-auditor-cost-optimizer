"""Audit finding aggregation package."""

from app.audit.aggregation.aggregator import (
    AggregatedAuditResult,
    collect_findings,
)

__all__ = ["AggregatedAuditResult", "collect_findings"]
