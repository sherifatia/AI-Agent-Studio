"""Central application exception handler.

Installs a global hook that logs any uncaught exception instead of
letting it print an unhandled traceback to a potentially-invisible
console (relevant for a packaged desktop app with no attached terminal).
This module logs only — it does not implement crash reporting (e.g.
sending a report to a remote service); that is future scope, noted below.
"""

import sys
from types import TracebackType

from core.logging_setup import get_logger

_logger = get_logger(__name__)


def _handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    """Log an uncaught exception via the application logger.

    Args:
        exc_type: The exception's type.
        exc_value: The exception instance.
        exc_traceback: The exception's traceback, if any.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Let Ctrl+C behave normally instead of being logged as a crash.
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    _logger.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )

    # Future scope: forward this to a crash-reporting service. Not
    # implemented in this Build — see docs/development/FUTURE_FEATURE_POLICY.md.


def install_global_exception_handler() -> None:
    """Route all uncaught exceptions through the application logger.

    Safe to call once at startup, before the Qt event loop begins.
    """
    sys.excepthook = _handle_uncaught_exception
