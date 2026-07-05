"""Shared page-identifier definitions for UI navigation.

Single source of truth for page names, consumed by both ``Sidebar`` and
``MainWindow``. Replaces the free-form string duplication that existed
before Build 012.
"""

from enum import StrEnum


class PageId(StrEnum):
    """Every navigable page in the application.

    Members are the canonical page identifiers.  The ``.label`` property
    returns the human-readable string shown in the sidebar.
    """

    DASHBOARD = "dashboard"
    CHAT = "chat"
    MODELS = "models"
    BROWSER = "browser"
    MEMORY = "memory"
    SKILLS = "skills"
    WORKFLOWS = "workflows"
    SETTINGS = "settings"

    @property
    def label(self) -> str:
        """Return the human-readable label for this page, e.g. ``"Dashboard"``.

        Maps the enum value (e.g. ``"dashboard"``) to a display name
        (e.g. ``"Dashboard"``) by capitalising the first letter.
        Override in a future Build if non-trivial labels are needed.
        """
        return self.value.capitalize()

    @classmethod
    def from_label(cls, label: str) -> "PageId":
        """Resolve a human-readable label back to a ``PageId``.

        Args:
            label: A human-readable page label, e.g. ``"Dashboard"``.

        Returns:
            The matching ``PageId``.

        Raises:
            ValueError: If no ``PageId`` matches ``label``.
        """
        lower = label.strip().lower()
        for member in cls:
            if member.value == lower:
                return member
        raise ValueError(f"Unknown page label: '{label}'")


# Ordered list of pages as they appear in the sidebar.
PAGE_ORDER: list[PageId] = [
    PageId.DASHBOARD,
    PageId.CHAT,
    PageId.MODELS,
    PageId.BROWSER,
    PageId.MEMORY,
    PageId.SKILLS,
    PageId.WORKFLOWS,
    PageId.SETTINGS,
]
