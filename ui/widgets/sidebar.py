from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)

        self.buttons = {}

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

    def change_page(self, page):

        for name, button in self.buttons.items():

            if name == page:
                button.setProperty("active", True)
            else:
                button.setProperty("active", False)

            button.style().unpolish(button)
            button.style().polish(button)

        self.page_changed.emit(page)