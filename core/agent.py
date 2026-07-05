"""Agent — executes Tasks using an AIEngine.

``Agent`` sits between the UI layer and the engine/provider layer.  Its
only job is to take a ``Task``, build the message list, call the engine,
and return a ``TaskResult``.

Rules enforced here:
- Agent NEVER creates a new ``AIEngine`` or ``Session``.
- Agent NEVER talks to a provider directly.
- Agent NEVER imports Qt.
- All skill execution goes through the Agent (Build 010+).
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from core.logging_setup import get_logger
from core.task import Task
from core.task_result import TaskResult

if TYPE_CHECKING:
    from core.engine import AIEngine

_logger = get_logger(__name__)


class Agent:
    """Executes ``Task`` objects via an ``AIEngine``.

    The ``Agent`` is stateless with respect to conversation history —
    history is part of the ``Task`` submitted by the caller.  Long-term
    memory (Build 009) will be written by the Agent after each completed
    task, not by the UI.

    Args:
        engine: The shared ``AIEngine`` instance.  The engine owns the
                ``Session``; the Agent must not replace it.
    """

    def __init__(self, engine: "AIEngine") -> None:
        self._engine = engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, task: Task) -> TaskResult:
        """Execute ``task`` and return its result.

        Workflow::

            Task.input + Task.history
                ↓  (build messages)
            AIEngine.ask(messages)
                ↓  (provider.generate)
            Response
                ↓
            TaskResult

        Args:
            task: The ``Task`` to execute.

        Returns:
            A ``TaskResult`` — always returned, never raised.  Check
            ``TaskResult.success`` to distinguish success from failure.
        """
        _logger.debug("Agent.run() — input length: %d chars", len(task.input))
        start = time.monotonic()

        try:
            messages = self._build_messages(task)
            response = self._engine.ask(messages)
            duration = time.monotonic() - start

            _logger.debug(
                "Agent.run() complete in %.2fs via %s",
                duration,
                response.provider,
            )
            return TaskResult(
                success=True,
                response=response.content,
                duration=duration,
                metadata={
                    "provider": response.provider,
                    **task.metadata,
                },
            )

        except Exception as exc:
            duration = time.monotonic() - start
            _logger.warning("Agent.run() failed after %.2fs: %s", duration, exc)
            return TaskResult(
                success=False,
                response="",
                error=str(exc),
                duration=duration,
                metadata=dict(task.metadata),
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_messages(task: Task) -> list[dict[str, str]]:
        """Combine history and the current input into a provider message list.

        Args:
            task: The task whose history and input are combined.

        Returns:
            A list of ``{"role": ..., "content": ...}`` dicts.
        """
        messages: list[dict[str, str]] = list(task.history)
        messages.append({"role": "user", "content": task.input})
        return messages
