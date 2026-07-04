"""Architectural foundation for the future AI Runtime layer.

This module defines the shape of the Runtime system that will eventually
sit above `core.engine.AIEngine` to coordinate longer-running agent
behavior (multi-step tool use, state transitions, event dispatch). It
intentionally contains **no business logic** — no step loop, no event
dispatch, no tool execution. See docs/ROADMAP.md ("AI Runtime
Implementation") for what each class is expected to grow into, and
docs/SPRINT4_REPORT.md for why this foundation was introduced now rather
than implemented directly.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.engine import AIEngine
    from core.session import Session


class RuntimeState(StrEnum):
    """Lifecycle states a `Runtime` instance can be in.

    Transition rules between these states are not defined yet — that is
    part of the implementation work tracked in docs/ROADMAP.md.
    """

    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RuntimeEvent:
    """A single event emitted by a `Runtime` during execution.

    Intended to be the payload type dispatched through `core.events`
    (reserved) once an event bus exists. No dispatch mechanism exists
    yet — this is a data shape only.

    Attributes:
        name: A short identifier for the event, e.g. "state_changed".
        payload: Event-specific data. Shape is intentionally
            unstandardized until real events are implemented.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeContext:
    """The set of collaborators a `Runtime` instance operates on.

    Groups together the objects a runtime will need once implemented,
    without defining how they are used.

    Attributes:
        engine: The `AIEngine` the runtime will drive.
        session: The `Session` the runtime will read from and write to.
    """

    engine: "AIEngine"
    session: "Session"


class Runtime:
    """Foundation for the future AI Runtime.

    Currently defines only the runtime's shape: its context and its
    current lifecycle state. Does not implement any execution behavior.
    See docs/ROADMAP.md ("AI Runtime Implementation") for the planned
    next steps.
    """

    def __init__(self, context: RuntimeContext) -> None:
        """Store the runtime's context and initialize its state.

        Args:
            context: The engine/session collaborators this runtime will
                operate on once execution logic is implemented.
        """
        self.context: RuntimeContext = context
        self.state: RuntimeState = RuntimeState.IDLE
