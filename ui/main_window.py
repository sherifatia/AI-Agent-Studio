from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)

from .theme import *
from .widgets.sidebar import Sidebar


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.build_ui()

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()

        # Workspace
        self.workspace = QWidget()

        workspace_layout = QVBoxLayout(self.workspace)

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
            margin:20px;
        """)

        workspace_layout.addWidget(self.page_title)
        workspace_layout.addStretch()

        root.addWidget(self.sidebar)
        root.addWidget(self.workspace)

        self.sidebar.page_changed.connect(self.change_page)

    def change_page(self, page):
        self.page_title.setText(page)