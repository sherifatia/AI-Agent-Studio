"""ConversationMemory — turn-level conversation history.

Stores every user/assistant exchange as a flat list of ``MemoryEntry``
objects.  Provides the ``History API`` used by the Agent to reconstruct
context for the next Task.

No vector DB, no embeddings — plain in-memory list only (Build 009
scope).  Vector-backed recall is reserved for a future Build.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.task import Task
from core.task_result import TaskResult


@dataclass
class MemoryEntry:
    """A single recorded conversation turn.

    Attributes:
        user_input:    What the user sent.
        agent_response: What the agent replied.
        metadata:      Metadata copied from ``TaskResult`` (provider,
                       duration, etc.).
    """

    user_input: str
    agent_response: str
    metadata: dict[str, object] = field(default_factory=dict)


class ConversationMemory:
    """Ordered list of ``MemoryEntry`` objects for the current session.

    History API
    -----------
    ``as_message_history(max_turns)`` returns the entries as a flat list
    of ``{"role": ..., "content": ...}`` dicts suitable for passing as
    ``Task.history``.
    """

    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def append(self, task: Task, result: TaskResult) -> None:
        """Record a completed turn.

        Args:
            task:   The task that was executed.
            result: The successful ``TaskResult``.
        """
        self._entries.append(
            MemoryEntry(
                user_input=task.input,
                agent_response=result.response,
                metadata=dict(result.metadata),
            )
        )

    def clear(self) -> None:
        """Discard all recorded turns."""
        self._entries.clear()

    # ------------------------------------------------------------------
    # Read (History API)
    # ------------------------------------------------------------------

    @property
    def turn_count(self) -> int:
        """Number of recorded turns."""
        return len(self._entries)

    @property
    def history(self) -> list[MemoryEntry]:
        """All recorded entries, oldest first (read-only copy)."""
        return list(self._entries)

    def as_message_history(
        self, max_turns: int = 20
    ) -> list[dict[str, str]]:
        """Return recent entries as provider-ready message dicts.

        Args:
            max_turns: Maximum number of recent turns to include.
                       Oldest entries are dropped when the list is longer.

        Returns:
            A flat list of ``{"role": ..., "content": ...}`` dicts,
            alternating user/assistant, oldest first.
        """
        recent = self._entries[-max_turns:]
        messages: list[dict[str, str]] = []
        for entry in recent:
            messages.append({"role": "user",      "content": entry.user_input})
            messages.append({"role": "assistant", "content": entry.agent_response})
        return messages
