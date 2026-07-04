"""Sidebar navigation widget."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    """Vertical navigation list emitting the selected page name.

    The list of page names is currently duplicated by convention with
    `ui/main_window.py` rather than sharing a single definition — see
    docs/PROJECT_AUDIT.md section 5 and the planned `core/navigation.py`.
    """

    page_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setFixedWidth(220)

        self.buttons: dict[str, QPushButton] = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        pages = [
            "Dashboard",
            "Chat",
            "Models",
            "Browser",
            "Memory",
            "Skills",
            "Workflows",
            "Settings"
        ]

        for page in pages:
            button = QPushButton(page)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(42)

            button.clicked.connect(
                lambda checked=False, p=page: self.change_page(p)
            )

            self.layout.addWidget(button)

            self.buttons[page] = button

        self.layout.addStretch()

        self.change_page("Dashboard")

    def change_page(self, page: str) -> None:
        """Mark `page` as active and emit `page_changed`.

        Args:
            page: The name of the page to activate.
        """
        for name, button in self.buttons.items():

            if name == page:
                button.setProperty("active", True)
            else:
                button.setProperty("active", False)

            button.style().unpolish(button)
            button.style().polish(button)

        self.page_changed.emit(page)
