"""Notification manager foundation.

A UI-agnostic registry of notifications the application wants to surface
to the user (information, warning, error, success). This module only
tracks and logs notifications — it does not render any toast, banner, or
popup; a future Build's UI layer can subscribe to `NotificationManager`
to display them.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from core.logging_setup import get_logger

_logger = get_logger(__name__)


class NotificationLevel(StrEnum):
    """Severity/category of a notification."""

    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class Notification:
    """A single notification event.

    Attributes:
        level: The notification's `NotificationLevel`.
        message: The human-readable notification text.
    """

    level: NotificationLevel
    message: str


class NotificationManager:
    """Records notifications and forwards them to the application logger.

    Subscribers (e.g. a future status-bar or toast widget) can register a
    listener via `subscribe()` to be called whenever a notification is
    raised.
    """

    def __init__(self) -> None:
        self._history: list[Notification] = []
        self._listeners: list[Callable[[Notification], None]] = []

    def subscribe(self, listener: Callable[[Notification], None]) -> None:
        """Register a callback invoked whenever a notification is raised.

        Args:
            listener: A callable accepting a single `Notification`.
        """
        self._listeners.append(listener)

    def notify(self, level: NotificationLevel, message: str) -> Notification:
        """Raise a notification: log it, store it, and notify listeners.

        Args:
            level: The notification's `NotificationLevel`.
            message: The human-readable notification text.

        Returns:
            The `Notification` that was raised.
        """
        notification = Notification(level=level, message=message)
        self._history.append(notification)

        log_by_level = {
            NotificationLevel.INFORMATION: _logger.info,
            NotificationLevel.WARNING: _logger.warning,
            NotificationLevel.ERROR: _logger.error,
            NotificationLevel.SUCCESS: _logger.info,
        }
        log_by_level[level]("[%s] %s", level.value, message)

        for listener in self._listeners:
            listener(notification)

        return notification

    def history(self) -> list[Notification]:
        """Return every notification raised so far, oldest first."""
        return list(self._history)
