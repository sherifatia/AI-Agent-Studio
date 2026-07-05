"""Centralized application logging.

Configures the root logger once, at startup, with both a console handler
and a rotating-free file handler writing to logs/application.log. Every
other module must obtain a logger via get_logger(__name__) — never via
logging.getLogger() directly, and never via print().

get_logger() guarantees that setup_logging() has been called at least
once with default settings before returning, so modules that import a
logger at module scope are safe even if app.py's LOGGING service has not
yet run. The application entry point should still call setup_logging()
explicitly as the first startup service so that level and handlers are
controlled intentionally.
"""

import logging
import sys

from core.constants import LOG_DATE_FORMAT, LOG_DIR, LOG_FILE_NAME, LOG_FORMAT

_configured: bool = False


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with console + file handlers.

    Idempotent: subsequent calls are a no-op, so modules and tests can
    call it defensively without duplicating handlers.

    Args:
        level: The minimum log level to emit (default logging.INFO).
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
    """Return a named logger, guaranteed to have handlers attached.

    Calls setup_logging() with default settings if it has not yet been
    called, so that a logger obtained at module import time is always
    functional — even when it is called before app.py's startup
    sequence has run the LOGGING service.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A logging.Logger with the application's format and handlers.
    """
    if not _configured:
        setup_logging()

    return logging.getLogger(name)
