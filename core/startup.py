"""Professional application startup sequence.

Defines a single, ordered path the application boots through, with
clearly named phases that are logged as they run. Additional phases can
be registered by future Builds (e.g. asset preloading, provider health
checks) without changing this module's core loop — see
`StartupSequence.register_phase()`.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from core.logging_setup import get_logger

_logger = get_logger(__name__)


class StartupPhase(StrEnum):
    """Named phases of the application boot sequence, in run order."""

    LOGGING = "logging"
    CONFIGURATION = "configuration"
    APPLICATION_INFO = "application_info"
    RESOURCES = "resources"
    USER_INTERFACE = "user_interface"
    READY = "ready"


@dataclass
class StartupStep:
    """A single named unit of work run during startup.

    Attributes:
        phase: The `StartupPhase` this step belongs to.
        action: A zero-argument callable performing the step's work.
            Exceptions are allowed to propagate — the caller of
            `StartupSequence.run()` decides how to handle a failed step.
    """

    phase: StartupPhase
    action: Callable[[], None]


@dataclass
class StartupSequence:
    """Runs a series of `StartupStep`s in order, logging each phase.

    Built-in phases are registered by the application entry point
    (`app.py`); future Builds can call `register_phase()` before `run()`
    to add additional loading tasks (e.g. preloading resources, checking
    provider connectivity) without modifying this class.
    """

    steps: list[StartupStep] = field(default_factory=list)

    def register_phase(self, phase: StartupPhase, action: Callable[[], None]) -> None:
        """Add a step to the sequence.

        Args:
            phase: The `StartupPhase` this step belongs to.
            action: A zero-argument callable performing the step's work.
        """
        self.steps.append(StartupStep(phase=phase, action=action))

    def run(self) -> None:
        """Execute every registered step in order, logging each phase.

        Raises:
            Exception: Whatever exception a step raises, propagated
                unchanged after being logged. Startup does not swallow
                errors — a failed step should stop the application rather
                than continue in an unknown state.
        """
        _logger.info("Startup sequence beginning (%d step(s))", len(self.steps))

        for step in self.steps:
            _logger.info("Startup phase: %s", step.phase.value)
            try:
                step.action()
            except Exception:
                _logger.exception(
                    "Startup phase '%s' failed", step.phase.value
                )
                raise

        _logger.info("Startup sequence complete")
