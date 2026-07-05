"""Theme manager foundation.

Provides a switchable Light/Dark/Auto architecture on top of the existing
`ui/theme.py` constants and `styles/*.qss` files. Does not add any new
visual styling — `styles/dark.qss` and `styles/light.qss` remain the
placeholders introduced in Sprint 4. This module only defines how a theme
would be selected and applied once real stylesheets exist.
"""

from enum import StrEnum

from PySide6.QtWidgets import QApplication

from core.logging_setup import get_logger
from ui.resource_manager import ResourceManager

_logger = get_logger(__name__)


class ThemeMode(StrEnum):
    """Selectable theme modes."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeManager:
    """Selects and applies a `ThemeMode` to the running `QApplication`.

    "Auto" currently resolves to `DARK` — this project has no OS
    dark/light detection yet; that is future scope, not implemented here.
    """

    def __init__(self, resource_manager: ResourceManager | None = None) -> None:
        self._resources = resource_manager or ResourceManager()
        self._current_mode: ThemeMode = ThemeMode.DARK

    @property
    def current_mode(self) -> ThemeMode:
        """The currently active `ThemeMode`."""
        return self._current_mode

    def resolve_mode(self, mode: ThemeMode) -> ThemeMode:
        """Resolve `AUTO` to a concrete mode; pass other modes through.

        Args:
            mode: The requested mode.

        Returns:
            `DARK` if `mode` is `AUTO` (no OS detection implemented yet);
            otherwise `mode` unchanged.
        """
        if mode is ThemeMode.AUTO:
            return ThemeMode.DARK
        return mode

    def set_mode(self, mode: ThemeMode, app: QApplication | None = None) -> None:
        """Set and apply a theme mode.

        Args:
            mode: The requested `ThemeMode`.
            app: The running `QApplication` to apply the stylesheet to.
                If `None`, only `current_mode` is updated (useful before
                a `QApplication` exists).
        """
        resolved = self.resolve_mode(mode)
        self._current_mode = resolved

        _logger.info("Theme set to: %s (requested: %s)", resolved.value, mode.value)

        if app is not None:
            self._apply(resolved, app)

    def _apply(self, mode: ThemeMode, app: QApplication) -> None:
        """Load and apply the stylesheet file for `mode`, if it exists.

        Args:
            mode: The resolved (non-`AUTO`) theme mode to apply.
            app: The running `QApplication`.
        """
        style_path = self._resources.get_style_path(f"{mode.value}.qss")

        if not style_path.exists():
            _logger.warning("Stylesheet not found for theme '%s': %s", mode.value, style_path)
            return

        stylesheet = style_path.read_text(encoding="utf-8")
        app.setStyleSheet(stylesheet)
