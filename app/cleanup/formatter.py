"""Format cleanup previews for terminal output."""

from app.cleanup.models import CleanupPreview


def format_cleanup_preview(preview: CleanupPreview) -> str:
    """Format a cleanup preview without executing any actions."""

    lines = [
        "CLEANUP DRY-RUN PREVIEW",
        "=" * 50,
        "Mode: DRY RUN (No infrastructure changes will be made)",
        f"Eligible resources: {preview.total_actions}",
        "",
    ]

    if not preview.has_actions:
        lines.append("No eligible resources found for cleanup.")
        lines.append("Your cloud infrastructure was not modified.")
        return "\n".join(lines)

    for index, action in enumerate(preview.actions, start=1):
        lines.extend(
            [
                f"Resource #{index}",
                f"  Type: {action.resource_type}",
                f"  ID: {action.resource_id}",
                f"  Region: {action.region}",
                f"  Proposed action: {action.action}",
                f"  Details: {action.description}",
            ]
        )

        if action.estimated_savings is not None:
            lines.append(
                f"  Estimated savings: {action.estimated_savings:.2f}"
            )

        lines.append("")

    lines.append("PREVIEW ONLY: No AWS resources were deleted or modified.")

    return "\n".join(lines)
