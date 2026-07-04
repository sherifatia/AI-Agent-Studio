"""Static theme constants used by the Qt UI.

Not connected to `styles/dark.qss` / `styles/light.qss` — see
docs/PROJECT_AUDIT.md section 7 for the reconciliation this implies.
"""

APP_NAME: str = "AI Agent Studio"

WINDOW_WIDTH: int = 1400
WINDOW_HEIGHT: int = 900

COLORS: dict[str, str] = {
    "background": "#1E1E1E",
    "sidebar": "#252526",
    "workspace": "#1E1E1E",
    "statusbar": "#2D2D30",
    "accent": "#007ACC",
    "text": "#FFFFFF",
}
