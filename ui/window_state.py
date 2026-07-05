"""Window state persistence manager.

Isolates every `QSettings` read and write behind a single abstraction so
that `MainWindow` never constructs or calls `QSettings` directly. This
satisfies the architecture requirement identified in `docs/BUILD001_REVIEW.md`
(Q1): QSettings must not leak into presentation-layer classes.

The manager is deliberately narrow: it saves and restores only Qt window
geometry and state. Unrelated persistent values (e.g. user preferences,
active provider) belong in `config/settings.json` via `config.settings`,
not here.
"""

from PySide6.QtCore import QByteArray, QSettings
from PySide6.QtWidgets import QMainWindow

from core.constants import (
    SETTINGS_APPLICATION,
    SETTINGS_KEY_WINDOW_GEOMETRY,
    SETTINGS_KEY_WINDOW_STATE,
    SETTINGS_ORGANIZATION,
)
from core.logging_setup import get_logger

_logger = get_logger(__name__)


class WindowStateManager:
    """Saves and restores a `QMainWindow`'s geometry and dock/toolbar state.

    Usage (inside `QMainWindow`):

        self._state = WindowStateManager()
        self._state.restore(self)     # call after UI is built
        ...
        self._state.save(self)        # call in closeEvent
    """

    def __init__(self) -> None:
        self._store = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)

    def save(self, window: QMainWindow) -> None:
        """Persist `window`'s current geometry and state.

        Args:
            window: The `QMainWindow` to snapshot.
        """
        self._store.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, window.saveGeometry())
        self._store.setValue(SETTINGS_KEY_WINDOW_STATE, window.saveState())
        _logger.debug("Window state saved")

    def restore(self, window: QMainWindow) -> None:
        """Apply previously saved geometry and state to `window`, if any.

        A missing or incompatible saved value is silently ignored — the
        window falls back to its default size and position.

        Args:
            window: The `QMainWindow` to restore into.
        """
        geometry: QByteArray | None = self._store.value(SETTINGS_KEY_WINDOW_GEOMETRY)
        if geometry is not None:
            window.restoreGeometry(geometry)

        state: QByteArray | None = self._store.value(SETTINGS_KEY_WINDOW_STATE)
        if state is not None:
            window.restoreState(state)

        _logger.debug("Window state restored")
