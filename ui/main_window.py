"""Application main window."""

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.app_info import APP_INFO
from core.events import Event, EventBus
from core.logging_setup import get_logger
from core.navigation import PageId
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

    Routes sidebar navigation signals to the correct workspace page.
    Pages that have a real implementation are shown via a QStackedWidget;
    pages that are not yet implemented show a placeholder label.

    MainWindow does not read config/settings.json or construct QSettings
    directly. Both are external concerns passed in by the caller.
    """

    def __init__(
        self,
        initial_provider: str = "",
        engine: object = None,
        memory: object = None,
        skill_registry: object = None,
        event_bus: EventBus | None = None,
    ) -> None:
        """Create the main window.

        Args:
            initial_provider: Provider name to display in the status bar
                on startup (e.g. "ollama"). Empty string keeps the default
                placeholder. Passed in from the startup sequence so that
                MainWindow has no dependency on the config layer.
            engine: The running AIEngine instance. Passed to page widgets
                that need it (currently: ModelsPage). None is safe —
                pages handle a missing engine gracefully.
            event_bus: Application-wide ``EventBus``. Created internally if
                ``None``.
        """
        super().__init__()

        self._engine = engine
        self._memory = memory
        self._skill_registry = skill_registry
        self.event_bus = event_bus or EventBus()
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

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the sidebar + workspace stack and wire navigation."""
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        # Stacked workspace — one widget per implemented page.
        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        # Index 0: placeholder for pages not yet implemented.
        self._placeholder = QWidget()
        ph_layout = QVBoxLayout(self._placeholder)
        self.page_title = QLabel(PageId.DASHBOARD.label)
        self.page_title.setStyleSheet(
            "font-size:24px; font-weight:bold; margin:20px;"
        )
        ph_layout.addWidget(self.page_title)
        ph_layout.addStretch()
        self._stack.addWidget(self._placeholder)

        # Status bar must be created before page widgets that connect to it.
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        # Index 1: Chat page — Agent wraps the engine; page never touches engine directly.
        from core.agent import Agent
        from ui.widgets.chat_page import ChatPage
        self._agent = Agent(engine=self._engine, memory=self._memory, skill_registry=self._skill_registry)
        self._chat_page = ChatPage(agent=self._agent)
        self._stack.addWidget(self._chat_page)

        # Index 2: Models page — wired to the engine.
        from ui.widgets.models_page import ModelsPage
        self._models_page = ModelsPage(engine=self._engine)
        self._models_page.provider_changed.connect(self.status_bar.set_provider)
        self._stack.addWidget(self._models_page)

        self.sidebar.page_changed.connect(self._on_page_changed)

    def _build_menu(self) -> None:
        """Construct the menu bar (currently: Help > About)."""
        help_menu = self.menuBar().addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(lambda: self.dialogs.show_about(self))

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    # Maps PageId.value (e.g. "chat") to the widget attribute name in self.
    _PAGE_WIDGETS: dict[str, str] = {
        PageId.CHAT.value:   "_chat_page",
        PageId.MODELS.value: "_models_page",
    }

    def _on_page_changed(self, page_label: str) -> None:
        """Handle a sidebar navigation signal.

        Args:
            page_label: The human-readable page label from the sidebar,
                e.g. ``"Chat"``, ``"Models"``.
        """
        # Resolve the label to a PageId, then use its value for lookup.
        try:
            page_id = PageId.from_label(page_label)
        except ValueError:
            self.page_title.setText(page_label)
            self._stack.setCurrentWidget(self._placeholder)
            return

        attr = self._PAGE_WIDGETS.get(page_id.value)
        if attr and hasattr(self, attr):
            self._stack.setCurrentWidget(getattr(self, attr))
        else:
            self.page_title.setText(page_id.label)
            self._stack.setCurrentWidget(self._placeholder)

        self.status_bar.show_message(f"Switched to {page_id.label}")
        _logger.debug("Page changed to: %s", page_id.value)

        # Broadcast navigation event on the event bus.
        self.event_bus.publish(
            Event(
                name="navigation.changed",
                sender=self,
                data={"page_id": page_id.value, "label": page_id.label},
            )
        )

    def change_page(self, page: str) -> None:
        """Public alias for _on_page_changed, kept for API stability."""
        self._on_page_changed(page)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        """Persist window geometry/state before closing.

        Args:
            event: The Qt close event, accepted after saving state.
        """
        self._window_state.save(self)
        super().closeEvent(event)
