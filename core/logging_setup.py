"""Centralized application logging.

Configures the root logger once, at startup, with both a console handler
and a rotating-free file handler writing to `logs/application.log`. Every
other module should obtain a logger via `get_logger(__name__)` rather than
using `print()` — see docs/development/CODING_GUIDELINES.md ("Logging
Rules").
"""

import logging
import sys

from core.constants import LOG_DATE_FORMAT, LOG_DIR, LOG_FILE_NAME, LOG_FORMAT

_configured: bool = False


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with console + file handlers.

    Safe to call more than once — subsequent calls are a no-op, so
    modules and tests can call it defensively without duplicating
    handlers.

    Args:
        level: The minimum log level to emit (default `logging.INFO`).
    """
    global _configured

    if _configured:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / LOG_FILE_NAME

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call `setup_logging()` once before this.

    Args:
        name: Typically `__name__` of the calling module.

    Returns:
        A `logging.Logger` configured with the application's handlers.
    """
    return logging.getLogger(name)
