"""Data models for safe cloud resource cleanup previews."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CleanupAction:
    """A proposed cleanup action for an eligible cloud resource."""

    resource_type: str
    resource_id: str
    region: str
    action: str
    description: str
    account_id: str | None = None
    estimated_savings: float | None = None


@dataclass(frozen=True)
class CleanupPreview:
    """Read-only preview of proposed cleanup actions."""

    actions: tuple[CleanupAction, ...]

    @property
    def total_actions(self) -> int:
        """Return the number of proposed cleanup actions."""

        return len(self.actions)

    @property
    def has_actions(self) -> bool:
        """Return whether the preview contains cleanup candidates."""

        return bool(self.actions)
