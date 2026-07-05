"""Qt-specific UI dimension and colour constants.

This module owns layout dimensions (window sizes) and colour tokens.
It does NOT re-export application identity values such as the app name
or window title — import those directly from `core.app_info.APP_INFO`.

Note: `styles/dark.qss` and `styles/light.qss` exist as reserved
placeholders. The COLORS dict below and those files are currently
disconnected; see docs/PROJECT_AUDIT.md section 7.
"""

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
