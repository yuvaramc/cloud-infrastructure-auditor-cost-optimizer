"""Determine which audit findings are safe cleanup candidates."""

from collections.abc import Iterable

from app.audit.models import AuditFinding, FindingStatus
from app.cleanup.models import CleanupAction


SUPPORTED_CLEANUP_ACTIONS = {
    "EBS Volume": "Delete unattached EBS volume",
}


def is_cleanup_eligible(finding: AuditFinding) -> bool:
    """Check whether an audit finding qualifies for cleanup preview."""

    if finding.status != FindingStatus.OPEN:
        return False

    action = SUPPORTED_CLEANUP_ACTIONS.get(finding.resource_type)

    if action is None:
        return False

    if finding.resource_type == "EBS Volume":
        return finding.metadata.get("state") == "available"

    return False


def get_cleanup_actions(
    findings: Iterable[AuditFinding],
) -> list[CleanupAction]:
    """Convert eligible audit findings into proposed cleanup actions."""

    actions = []

    for finding in findings:
        if not is_cleanup_eligible(finding):
            continue

        action = SUPPORTED_CLEANUP_ACTIONS[finding.resource_type]

        actions.append(
            CleanupAction(
                resource_type=finding.resource_type,
                resource_id=finding.resource_id,
                region=finding.region,
                action=action,
                description=(
                    f"{finding.resource_type} {finding.resource_id} "
                    "is unattached and available."
                ),
                account_id=finding.account_id,
                estimated_savings=finding.estimated_savings,
            )
        )

    return actions
