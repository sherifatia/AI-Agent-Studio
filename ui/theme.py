"""Static theme constants used by the Qt UI.

Not connected to `styles/dark.qss` / `styles/light.qss` — see
docs/PROJECT_AUDIT.md section 7 for the reconciliation this implies.
"""

from core.app_info import APP_INFO

# Sourced from core.app_info.APP_INFO — the single source of truth for
# application metadata — rather than duplicated as a separate string.
APP_NAME: str = APP_INFO.NAME
WINDOW_TITLE: str = APP_INFO.window_title

WINDOW_WIDTH: int = 1400
WINDOW_HEIGHT: int = 900

MIN_WINDOW_WIDTH: int = 960
MIN_WINDOW_HEIGHT: int = 600

COLORS: dict[str, str] = {
    "background": "#1E1E1E",
    "sidebar": "#252526",
    "workspace": "#1E1E1E",
    "statusbar": "#2D2D30",
    "accent": "#007ACC",
    "text": "#FFFFFF",
}

