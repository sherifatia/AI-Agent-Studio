"""Sidebar navigation widget."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from core.navigation import PAGE_ORDER, PageId


class Sidebar(QWidget):
    """Vertical navigation list emitting the selected ``PageId``.

    Page identifiers are sourced from ``core.navigation.PageId``, the
    single source of truth, instead of being duplicated as free-form
    strings.
    """

    #: Fixed width when the sidebar is fully expanded (existing behavior).
    EXPANDED_WIDTH = 220

    #: Fixed width when collapsed — see `toggle_collapse()`. Not wired to
    #: any control yet; this is foundation for a future collapse button.
    COLLAPSED_WIDTH = 60

    #: PageId -> icon asset name (icon files are not implemented yet;
    #: see `ui/resource_manager.py`). Reserved so a future Build can wire
    #: real icons in one place instead of scattering asset names.
    PAGE_ICONS: dict[PageId, str] = {
        PageId.DASHBOARD: "dashboard.svg",
        PageId.CHAT: "chat.svg",
        PageId.MODELS: "models.svg",
        PageId.BROWSER: "browser.svg",
        PageId.MEMORY: "memory.svg",
        PageId.SKILLS: "skills.svg",
        PageId.WORKFLOWS: "workflows.svg",
        PageId.SETTINGS: "settings.svg",
    }

    page_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.is_collapsed: bool = False
        self.setFixedWidth(self.EXPANDED_WIDTH)

        self.buttons: dict[str, QPushButton] = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        for page_id in PAGE_ORDER:
            label = page_id.label
            button = QPushButton(label)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(42)

            # Icon assets are not implemented yet (see
            # ui/resource_manager.py) — no setIcon() call until real
            # icon files exist under assets/icons/.

            button.clicked.connect(
                lambda checked=False, p=label: self.change_page(p)
            )

            self.layout.addWidget(button)

            self.buttons[label] = button

        self.layout.addStretch()

        self.change_page(PageId.DASHBOARD.label)

    def change_page(self, page: str) -> None:
        """Mark `page` label as active and emit `page_changed`.

        Args:
            page: The human-readable page label, e.g. ``"Dashboard"``.
        """
        for name, button in self.buttons.items():

            if name == page:
                button.setProperty("active", True)
            else:
                button.setProperty("active", False)

            button.style().unpolish(button)
            button.style().polish(button)

        self.page_changed.emit(page)

    def toggle_collapse(self) -> None:
        """Toggle between `EXPANDED_WIDTH` and `COLLAPSED_WIDTH`.

        Foundation for a future collapse button — nothing currently
        calls this method. Button labels are not hidden when collapsed
        (that requires icon assets, not yet implemented), so this only
        changes the sidebar's width for now.
        """
        self.is_collapsed = not self.is_collapsed
        width = self.COLLAPSED_WIDTH if self.is_collapsed else self.EXPANDED_WIDTH
        self.setFixedWidth(width)
