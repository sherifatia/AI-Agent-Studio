"""TaskResult — the outcome of an Agent executing a Task.

``TaskResult`` is what the Agent returns to its caller (e.g. ChatPage).
It is a plain dataclass — no Qt, no provider, no logging.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskResult:
    """The outcome of executing a single ``Task``.

    Attributes:
        success:   ``True`` if the Agent produced a response without an
                   unhandled exception.
        response:  The text content of the response.  Empty string on
                   failure.
        error:     Human-readable error description when ``success`` is
                   ``False``.  Empty string on success.
        duration:  Wall-clock seconds the execution took, measured by the
                   Agent.  ``0.0`` if not measured.
        metadata:  Arbitrary key/value annotations set by the Agent (e.g.
                   provider name, model name, token estimates).
    """

    success: bool
    response: str
    error: str = ""
    duration: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)
