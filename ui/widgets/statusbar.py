"""Application status bar widget."""

from PySide6.QtWidgets import QLabel, QStatusBar, QWidget

from core.app_info import APP_INFO
from core.constants import STATE_READY


class StatusBar(QStatusBar):
    """Status bar showing the active provider, application state, and version.

    All fields are independently updateable via `set_provider()`,
    `set_state()`, and `show_message()`. Version is fixed for the
    lifetime of the window (sourced from `core.app_info.APP_INFO`).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.provider_label = QLabel("Provider: —")
        self.state_label = QLabel(STATE_READY)
        self.version_label = QLabel(f"v{APP_INFO.VERSION}")

        self.addWidget(self.provider_label)
        self.addWidget(self.state_label, 1)
        self.addPermanentWidget(self.version_label)

    def set_provider(self, provider_name: str) -> None:
        """Update the displayed active provider name.

        Args:
            provider_name: e.g. "Ollama", "OpenAI".
        """
        self.provider_label.setText(f"Provider: {provider_name}")

    def set_state(self, state: str) -> None:
        """Update the displayed application state.

        Args:
            state: e.g. `core.constants.STATE_READY`, `STATE_BUSY`,
                `STATE_ERROR`, or a short custom status string.
        """
        self.state_label.setText(state)

    def show_message(self, message: str, timeout_ms: int = 4000) -> None:
        """Show a transient message that reverts to the state label after a timeout.

        Args:
            message: The message to display.
            timeout_ms: How long to show the message, in milliseconds.
                Pass 0 to show indefinitely until replaced.
        """
        self.showMessage(message, timeout_ms)
