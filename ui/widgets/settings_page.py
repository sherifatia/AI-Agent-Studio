"""Settings page — view current configuration."""

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.logging_setup import get_logger

_logger = get_logger(__name__)


class SettingsPage(QWidget):
    """Displays current application settings in a read-only view.

    A future Build should add editing capability.  See
    ``docs/ROADMAP.md``.

    Args:
        settings: The ``Settings`` instance.  ``None`` is safe.
    """

    def __init__(self, settings: object = None) -> None:
        super().__init__()
        self._settings = settings
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel("Settings")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        root.addWidget(title)

        self._box = QGroupBox("Configuration (read-only)")
        layout = QVBoxLayout(self._box)

        self._theme_label = QLabel("Theme: --")
        layout.addWidget(self._theme_label)
        self._provider_label = QLabel("Provider: --")
        layout.addWidget(self._provider_label)
        self._model_label = QLabel("Model: --")
        layout.addWidget(self._model_label)
        self._language_label = QLabel("Language: --")
        layout.addWidget(self._language_label)
        self._startup_label = QLabel("Startup page: --")
        layout.addWidget(self._startup_label)

        notice = QLabel(
            "<i>Editing settings is not implemented yet in this Build.</i>"
        )
        notice.setStyleSheet("color: #888;")
        layout.addWidget(notice)

        root.addWidget(self._box)
        root.addStretch()

    def _refresh(self) -> None:
        if self._settings is None:
            self._theme_label.setText("Theme: -- (no settings)")
            return

        try:
            data = self._settings.data
        except AttributeError:
            self._theme_label.setText("Theme: -- (invalid settings)")
            return

        self._theme_label.setText(f"Theme: {data.get('theme', '--')}")
        self._provider_label.setText(f"Provider: {data.get('provider', '--')}")
        self._model_label.setText(f"Model: {data.get('model', '--')}")
        self._language_label.setText(f"Language: {data.get('language', '--')}")
        self._startup_label.setText(
            f"Startup page: {data.get('startup_page', '--')}"
        )
        _logger.debug("SettingsPage refreshed")
