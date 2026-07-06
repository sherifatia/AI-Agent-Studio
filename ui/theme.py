"""Qt-specific UI dimension and colour constants.

This module owns layout dimensions (window sizes), colour tokens, and
QSS stylesheet loading.  It is the single point through which all
visual theming flows — the ``styles/dark.qss`` and ``styles/light.qss``
files are loaded at runtime by ``load_stylesheet()`` and applied to
``QApplication`` via ``MainWindow``.
"""

from __future__ import annotations

from pathlib import Path

WINDOW_WIDTH: int = 1400
WINDOW_HEIGHT: int = 900

MIN_WINDOW_WIDTH: int = 960
MIN_WINDOW_HEIGHT: int = 600

# ── Colour tokens (used by Python code, e.g. inline styling) ──

DARK_COLORS: dict[str, str] = {
    "background": "#1E1E1E",
    "sidebar": "#252526",
    "workspace": "#1E1E1E",
    "statusbar": "#2D2D30",
    "accent": "#007ACC",
    "text": "#CCCCCC",
    "border": "#3C3C3C",
    "input_bg": "#3C3C3C",
    "button_bg": "#0E639C",
    "button_hover": "#1177BB",
    "button_pressed": "#094771",
}

LIGHT_COLORS: dict[str, str] = {
    "background": "#FFFFFF",
    "sidebar": "#F3F3F3",
    "workspace": "#FFFFFF",
    "statusbar": "#F3F3F3",
    "accent": "#007ACC",
    "text": "#333333",
    "border": "#E0E0E0",
    "input_bg": "#FFFFFF",
    "button_bg": "#007ACC",
    "button_hover": "#1A8AD4",
    "button_pressed": "#005A9E",
}


def load_stylesheet(theme_name: str = "dark") -> str:
    """Read the QSS file for *theme_name* and return its content.

    Args:
        theme_name: ``"dark"`` (default) or ``"light"``.

    Returns:
        The raw stylesheet string, or an empty string if the file
        cannot be read.
    """
    qss_path = Path(__file__).resolve().parent.parent / "styles" / f"{theme_name}.qss"
    try:
        return qss_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def get_colors(theme_name: str = "dark") -> dict[str, str]:
    """Return the colour token dict for *theme_name*."""
    return DARK_COLORS if theme_name == "dark" else LIGHT_COLORS
