"""Build read-only cleanup previews from audit results."""

from collections.abc import Iterable

from app.audit.aggregation.aggregator import AggregatedAuditResult
from app.audit.models import AuditFinding
from app.cleanup.eligibility import get_cleanup_actions
from app.cleanup.models import CleanupPreview


def build_cleanup_preview(
    audit_results: AggregatedAuditResult | Iterable[AuditFinding],
) -> CleanupPreview:
    """Build a preview without modifying cloud infrastructure."""

    if isinstance(audit_results, AggregatedAuditResult):
        findings = audit_results.findings
    else:
        findings = audit_results

    actions = get_cleanup_actions(findings)

    return CleanupPreview(actions=tuple(actions))
