"""AI Runtime — coordinates long-running agent execution.

Sits above ``AIEngine`` to manage state transitions, event dispatch, and
multi-step task execution.  The ``Runtime`` owns the lifecycle of a single
execution run, from IDLE through RUNNING to COMPLETED or FAILED.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from core.logging_setup import get_logger
from core.task import Task
from core.task_result import TaskResult

if TYPE_CHECKING:
    from core.engine import AIEngine
    from core.events import EventBus
    from core.session import Session

_logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


class RuntimeState(StrEnum):
    """Lifecycle states a ``Runtime`` instance can be in.

    Transition rules (enforced by ``Runtime._transition``)::

        IDLE ──→ RUNNING ──→ WAITING ──→ RUNNING ──→ ... ──→ COMPLETED
                                       │                      FAILED
                                       └────→ FAILED
    """

    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def _valid_transitions(cls) -> dict[RuntimeState, set[RuntimeState]]:
        return {
            cls.IDLE:     {cls.RUNNING},
            cls.RUNNING:  {cls.COMPLETED, cls.FAILED, cls.WAITING},
            cls.WAITING:  {cls.RUNNING, cls.FAILED},
            cls.COMPLETED: set(),
            cls.FAILED:    set(),
        }

    def can_transition_to(self, target: RuntimeState) -> bool:
        """Return ``True`` if a transition from ``self`` to ``target`` is valid."""
        return target in self._valid_transitions().get(self, set())


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


@dataclass
class RuntimeEvent:
    """An event emitted by a ``Runtime`` during execution.

    Dispatched through the ``EventBus`` when one is available.

    Attributes:
        name: Short identifier, e.g. ``"state_changed"``.
        runtime_state: The runtime's ``RuntimeState`` at the time of emission.
        payload: Event-specific data.
    """

    name: str
    runtime_state: RuntimeState = RuntimeState.IDLE
    payload: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@dataclass
class RuntimeContext:
    """The set of collaborators a ``Runtime`` instance operates on.

    Attributes:
        engine: The ``AIEngine`` the runtime will drive.
        session: The ``Session`` the runtime reads from and writes to.
        event_bus: Optional ``EventBus`` for dispatching ``RuntimeEvent``
            instances.  ``None`` is safe — events are logged but not
            dispatched.
    """

    engine: "AIEngine"
    session: "Session"
    event_bus: "EventBus | None" = None


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


class Runtime:
    """Coordinates execution of a ``Task`` through its full lifecycle.

    Usage::

        ctx = RuntimeContext(engine=engine, session=session, event_bus=bus)
        runtime = Runtime(ctx)
        result = runtime.run(task)
    """

    def __init__(self, context: RuntimeContext) -> None:
        self.context: RuntimeContext = context
        self.state: RuntimeState = RuntimeState.IDLE
        self._current_task: Task | None = None
        self._start_time: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, task: Task) -> TaskResult:
        """Execute ``task`` through its full lifecycle and return a result.

        This is the main entry point.  It manages state transitions,
        delegates to the engine, and dispatches runtime events at each
        stage.

        Args:
            task: The ``Task`` to execute.

        Returns:
            A ``TaskResult`` — always returned, never raised.
        """
        self._current_task = task
        self._start_time = time.monotonic()

        self._transition(RuntimeState.RUNNING)
        self._emit("execution.started", payload={
            "input_length": len(task.input),
            "history_turns": len(task.history),
        })

        try:
            messages: list[dict[str, str]] = list(task.history)
            messages.append({"role": "user", "content": task.input})

            response = self.context.engine.ask(messages)
            duration = time.monotonic() - self._start_time

            result = TaskResult(
                success=True,
                response=response.content,
                duration=duration,
                metadata={"provider": response.provider, **task.metadata},
            )

            self.context.session.add_message({"role": "user", "content": task.input})
            self.context.session.add_message(
                {"role": "assistant", "content": response.content}
            )

            self._transition(RuntimeState.COMPLETED)
            self._emit("execution.completed", payload={
                "duration": duration,
                "provider": response.provider,
            })
            return result

        except Exception as exc:
            duration = time.monotonic() - self._start_time
            _logger.warning("Runtime.run() failed after %.2fs: %s", duration, exc)

            result = TaskResult(
                success=False,
                response="",
                error=str(exc),
                duration=duration,
                metadata=dict(task.metadata),
            )

            self._transition(RuntimeState.FAILED)
            self._emit("execution.failed", payload={
                "duration": duration,
                "error": str(exc),
            })
            return result

        finally:
            self._current_task = None

    @property
    def is_running(self) -> bool:
        """Return ``True`` when the runtime is actively executing."""
        return self.state in (RuntimeState.RUNNING, RuntimeState.WAITING)

    @property
    def current_task(self) -> Task | None:
        """The task currently being executed, or ``None``."""
        return self._current_task

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _transition(self, target: RuntimeState) -> None:
        """Validate and apply a state transition, dispatching an event.

        Args:
            target: The target ``RuntimeState``.

        Raises:
            RuntimeError: If the transition is not allowed by the state
                machine rules.
        """
        if not self.state.can_transition_to(target):
            raise RuntimeError(
                f"Invalid state transition: {self.state.value} → "
                f"{target.value}"
            )

        previous = self.state
        self.state = target
        _logger.debug(
            "Runtime state: %s → %s", previous.value, target.value
        )
        self._emit("state_changed", payload={
            "from": previous.value,
            "to": target.value,
        })

    def _emit(self, name: str, payload: dict[str, Any] | None = None) -> None:
        """Create a ``RuntimeEvent`` and dispatch it on the event bus.

        Args:
            name: Event name.
            payload: Optional key/value data.
        """
        event = RuntimeEvent(
            name=name,
            runtime_state=self.state,
            payload=payload or {},
        )

        if self.context.event_bus is not None:
            # Bridge RuntimeEvent → core.events.Event for the EventBus.
            from core.events import Event
            self.context.event_bus.publish(
                Event(
                    name=f"runtime.{name}",
                    sender=self,
                    data={
                        "runtime_state": self.state.value,
                        **event.payload,
                    },
                )
            )

        _logger.debug(
            "Runtime event: %s (state=%s)", name, self.state.value
        )
