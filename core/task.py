"""Task — a single unit of work submitted to an Agent.

A ``Task`` carries everything the ``Agent`` needs to produce a result:
the user's input, optional conversation history to include as context,
and an optional metadata dict for caller-specific annotations.

``Task`` is a plain dataclass — no logic, no Qt, no provider knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A discrete unit of work for the Agent to execute.

    Attributes:
        input:    The user's text prompt or instruction.
        history:  Prior conversation turns to include as context when
                  building the message list sent to the provider.
                  Each entry must be shaped like
                  ``{"role": "user"|"assistant", "content": "..."}``.
        metadata: Caller-supplied key/value annotations (e.g. page name,
                  skill hint).  Not sent to the provider.
    """

    input: str
    history: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
