"""Application main window."""

from PySide6.QtCore import QSettings
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from config.settings import Settings
from core.constants import (
    SETTINGS_APPLICATION,
    SETTINGS_KEY_WINDOW_GEOMETRY,
    SETTINGS_KEY_WINDOW_STATE,
    SETTINGS_ORGANIZATION,
)
from core.logging_setup import get_logger
from ui.dialog_manager import DialogManager
from ui.widgets.statusbar import StatusBar

from .theme import *
from .widgets.sidebar import Sidebar

_logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Top-level window: hosts the sidebar and the current workspace page.

    `change_page()` currently only updates a placeholder title label —
    swapping in real page widgets from `ui/widgets/*_page.py` is planned,
    see docs/ROADMAP.md.

    Window geometry is remembered across runs via `QSettings`. The window
    is otherwise a plain `QMainWindow`; `QMainWindow` natively supports
    `QDockWidget`-based docking, so no structural change is needed here to
    add real dock widgets in a future Build once there is content to dock.
    """

    def __init__(self) -> None:
        super().__init__()

        self.dialogs = DialogManager()
        self._qsettings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)

        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.build_ui()
        self.build_menu()
        self._restore_geometry()
        self._load_status_from_settings()

    def build_ui(self) -> None:
        """Construct the sidebar + workspace layout and wire navigation."""
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

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def build_menu(self) -> None:
        """Construct the menu bar (currently: Help > About)."""
        help_menu = self.menuBar().addMenu("&Help")

        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(lambda: self.dialogs.show_about(self))

    def change_page(self, page: str) -> None:
        """Handle a sidebar navigation event.

        Args:
            page: The name of the page that was selected, e.g. "Chat".
        """
        self.page_title.setText(page)
        self.status_bar.show_message(f"Switched to {page}")

    def _load_status_from_settings(self) -> None:
        """Populate the status bar's provider field from settings.json.

        Best-effort only: if settings cannot be loaded for any reason,
        the status bar keeps its default placeholder rather than the
        window failing to start.
        """
        try:
            settings = Settings()
            provider = settings.get("provider")
            if provider:
                self.status_bar.set_provider(str(provider))
        except Exception:
            _logger.warning(
                "Could not load config/settings.json for status bar; "
                "using default provider display.",
                exc_info=True,
            )

    def _restore_geometry(self) -> None:
        """Restore previously saved window geometry/state, if any."""
        geometry = self._qsettings.value(SETTINGS_KEY_WINDOW_GEOMETRY)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self._qsettings.value(SETTINGS_KEY_WINDOW_STATE)
        if state is not None:
            self.restoreState(state)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Persist window geometry/state before closing.

        Args:
            event: The Qt close event, accepted unchanged after saving.
        """
        self._qsettings.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, self.saveGeometry())
        self._qsettings.setValue(SETTINGS_KEY_WINDOW_STATE, self.saveState())
        super().closeEvent(event)
