"""Cross-cutting application constants.

Values used by more than one infrastructure module (logging, startup,
window state) live here to avoid magic strings and duplicated literals.
Qt-specific styling constants remain in `ui/theme.py` — this module holds
non-styling, application-wide values only.
"""

from pathlib import Path

from core.app_info import APP_INFO

# ---- Logging ----
LOG_DIR: Path = Path("logs")
LOG_FILE_NAME: str = "application.log"
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# ---- Window state persistence ----
# QSettings organization/application scope — used to store and restore
# window geometry between runs (see ui/main_window.py). Organization name
# is sourced from AppInfo.COMPANY rather than duplicated as a literal.
SETTINGS_ORGANIZATION: str = APP_INFO.COMPANY
SETTINGS_APPLICATION: str = "AIAgentStudioDesktop"
SETTINGS_KEY_WINDOW_GEOMETRY: str = "window/geometry"
SETTINGS_KEY_WINDOW_STATE: str = "window/state"

# ---- Application state (surfaced in the status bar) ----
STATE_READY: str = "Ready"
STATE_BUSY: str = "Busy"
STATE_ERROR: str = "Error"
