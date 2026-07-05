"""In-process event bus for cross-cutting application events.

Provides a simple publish/subscribe mechanism that any module can use to
broadcast and listen for application-wide events (e.g. provider changes,
skill execution, navigation).  Intended to be the dispatch mechanism for
``core.runtime.RuntimeEvent`` instances.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from core.logging_setup import get_logger

_logger = get_logger(__name__)

# Type alias for event listeners.
EventListener = Callable[["Event"], None]


@dataclass
class Event:
    """A single event dispatched through the ``EventBus``.

    Attributes:
        name: A short, stable identifier, e.g. ``"provider_changed"``.
        sender: The object that emitted the event, or ``None``.
        data: Arbitrary key/value payload.
    """

    name: str
    sender: object = None
    data: dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Lightweight publish/subscribe event bus.

    Usage::

        bus = EventBus()
        bus.subscribe("provider_changed", my_handler)
        bus.publish(Event("provider_changed", data={"provider": "ollama"}))
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[EventListener]] = {}

    def subscribe(self, event_name: str, listener: EventListener) -> None:
        """Register a listener for a specific event name.

        Args:
            event_name: The event name to listen for.
            listener: A callable accepting a single ``Event``.
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)
        _logger.debug("EventBus: listener registered for '%s'", event_name)

    def unsubscribe(self, event_name: str, listener: EventListener) -> None:
        """Remove a previously registered listener.

        Args:
            event_name: The event name the listener was registered for.
            listener: The listener to remove.

        Raises:
            ValueError: If the listener is not registered for ``event_name``.
        """
        listeners = self._listeners.get(event_name, [])
        if listener not in listeners:
            raise ValueError(
                f"Listener not registered for event '{event_name}'"
            )
        listeners.remove(listener)
        _logger.debug("EventBus: listener unregistered for '%s'", event_name)

    def publish(self, event: Event) -> None:
        """Dispatch ``event`` to all registered listeners.

        Args:
            event: The ``Event`` to dispatch.
        """
        listeners = self._listeners.get(event.name, [])
        if not listeners:
            _logger.debug("EventBus: no listeners for '%s'", event.name)
            return

        _logger.debug(
            "EventBus: publishing '%s' to %d listener(s)",
            event.name,
            len(listeners),
        )
        for listener in listeners:
            try:
                listener(event)
            except Exception:
                _logger.exception(
                    "EventBus: listener failed for event '%s'", event.name
                )

    def clear(self) -> None:
        """Remove all registered listeners."""
        self._listeners.clear()
        _logger.debug("EventBus: all listeners cleared")
