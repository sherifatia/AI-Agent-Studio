"""Service loader — application startup sequence.

Provides a ServiceLoader that boots the application through a named,
ordered sequence of services. Service names are plain strings (not
constrained to a closed enum), so future Builds can register entirely new
service categories (e.g. "provider_health_check", "memory_warmup") without
modifying this file.

StartupPhase provides conventional names for the built-in boot services.
It is a plain class of string constants, not a StrEnum, so it is open:
external code can define additional phase name strings freely alongside it.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from core.logging_setup import get_logger

_logger = get_logger(__name__)


class StartupPhase:
    """Conventional service name constants for the built-in boot phases.

    These are plain strings, not enum members. Any string is a valid
    service name in ServiceLoader — these constants exist for readability
    and to prevent typos at call sites, not to constrain what names
    are allowed.
    """

    LOGGING: str = "logging"
    CONFIGURATION: str = "configuration"
    APPLICATION_INFO: str = "application_info"
    RESOURCES: str = "resources"
    USER_INTERFACE: str = "user_interface"
    READY: str = "ready"


@dataclass
class _Service:
    """Internal record of a registered service.

    Attributes:
        name: Unique service identifier string.
        loader: Zero-argument callable that initialises the service.
    """

    name: str
    loader: Callable[[], None]


class ServiceLoader:
    """Runs a series of named services in registration order.

    Usage::

        loader = ServiceLoader()
        loader.register("logging", setup_logging)
        loader.register("ui", build_window)
        loader.run()

    Services run in the order they are registered. Any exception raised
    by a service is logged and re-raised — startup does not swallow
    errors, since continuing with a partially-initialised application is
    worse than failing fast.

    Future Builds may register additional services (e.g. "memory",
    "browser", "plugins") without touching this file. No business logic
    lives here — only the run loop.
    """

    def __init__(self) -> None:
        self._services: list[_Service] = []
        self._names: set[str] = set()

    def register(self, name: str, loader: Callable[[], None]) -> None:
        """Register a named service.

        Args:
            name: A unique service identifier, e.g. "logging",
                "provider_health_check". Any non-empty string is valid.
            loader: A zero-argument callable that initialises the service.

        Raises:
            ValueError: If `name` is empty or already registered.
        """
        if not name:
            raise ValueError("Service name must not be empty")
        if name in self._names:
            raise ValueError(f"Service already registered: '{name}'")

        self._services.append(_Service(name=name, loader=loader))
        self._names.add(name)

    def run(self) -> None:
        """Execute every registered service in order.

        Raises:
            Exception: Whatever a service raises, after logging it.
        """
        _logger.info(
            "ServiceLoader starting (%d service(s))", len(self._services)
        )

        for service in self._services:
            _logger.info("Starting service: %s", service.name)
            try:
                service.loader()
            except Exception:
                _logger.exception(
                    "Service '%s' failed to start", service.name
                )
                raise

        _logger.info("All services started successfully")


# ---------------------------------------------------------------------------
# Backward-compatibility alias
# ---------------------------------------------------------------------------
# Build 001 registered phases via StartupSequence.register_phase(phase, fn).
# ServiceLoader.register(name, fn) is the new API. The alias below keeps
# any code that instantiated StartupSequence working without change.

class StartupSequence(ServiceLoader):
    """Deprecated alias for ServiceLoader — kept for backward compatibility.

    New code should use ServiceLoader directly. This alias will be removed
    once no callers remain.
    """

    def register_phase(
        self, phase: str, action: Callable[[], None]
    ) -> None:
        """Alias for ServiceLoader.register() using Build001 naming.

        Args:
            phase: Service name (was StartupPhase enum value in Build001).
            action: Loader callable.
        """
        self.register(name=phase, loader=action)
