"""Application main window."""

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from core.app_info import APP_INFO
from core.logging_setup import get_logger
from ui.dialog_manager import DialogManager
from ui.theme import (
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from ui.widgets.sidebar import Sidebar
from ui.widgets.statusbar import StatusBar
from ui.window_state import WindowStateManager

_logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Top-level window: sidebar navigation + workspace area.

    Responsibilities: build and own the Qt widget tree, handle navigation
    signals, delegate window-state persistence to WindowStateManager.

    MainWindow does not read config/settings.json or construct QSettings
    directly. Both are external concerns passed in by the caller.

    change_page() currently updates a placeholder title label. Swapping
    real page widgets from ui/widgets/*_page.py is tracked in ROADMAP.md.
    """

    def __init__(self, initial_provider: str = "") -> None:
        """Create the main window.

        Args:
            initial_provider: The active provider name to display in the
                status bar on startup, e.g. "ollama". Empty string keeps
                the default placeholder. Read from config/settings.json
                by the startup sequence and passed in here so that
                MainWindow has no dependency on the config layer.
        """
        super().__init__()

        self._window_state = WindowStateManager()
        self.dialogs = DialogManager()

        self.setWindowTitle(APP_INFO.window_title)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._build_ui()
        self._build_menu()
        self._window_state.restore(self)

        if initial_provider:
            self.status_bar.set_provider(initial_provider)

    def _build_ui(self) -> None:
        """Construct the sidebar + workspace layout and wire navigation."""
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()

        self.workspace = QWidget()
        workspace_layout = QVBoxLayout(self.workspace)

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(
            "font-size:24px; font-weight:bold; margin:20px;"
        )

        workspace_layout.addWidget(self.page_title)
        workspace_layout.addStretch()

        root.addWidget(self.sidebar)
        root.addWidget(self.workspace)

        self.sidebar.page_changed.connect(self._on_page_changed)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def _build_menu(self) -> None:
        """Construct the menu bar (currently: Help > About)."""
        help_menu = self.menuBar().addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(lambda: self.dialogs.show_about(self))

    def _on_page_changed(self, page: str) -> None:
        """Handle a sidebar navigation signal.

        Args:
            page: The name of the page selected, e.g. "Chat".
        """
        self.page_title.setText(page)
        self.status_bar.show_message(f"Switched to {page}")
        _logger.debug("Page changed to: %s", page)

    def change_page(self, page: str) -> None:
        """Public alias for _on_page_changed, kept for API stability."""
        self._on_page_changed(page)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Persist window geometry/state before closing.

        Args:
            event: The Qt close event, accepted after saving state.
        """
        self._window_state.save(self)
        super().closeEvent(event)
