"""MemoryManager — coordinates all memory subsystems.

``MemoryManager`` is the single object that the ``Agent`` uses to write
completed tasks.  It holds one ``ConversationMemory`` (turn-level) and one
``SessionMemory`` (session-level aggregate), and exposes a unified
``record()`` API so the Agent never has to address individual stores.

The UI layer (ChatPage) must never write memory directly — only the Agent
calls ``MemoryManager.record()``.
"""

from __future__ import annotations

from core.logging_setup import get_logger
from core.task import Task
from core.task_result import TaskResult
from memory.conversation import ConversationMemory
from memory.session import SessionMemory

_logger = get_logger(__name__)


class MemoryManager:
    """Facade over ``ConversationMemory`` and ``SessionMemory``.

    Usage::

        memory = MemoryManager()
        memory.record(task, result)          # after each Agent.run()
        turns = memory.conversation.history  # read back
    """

    def __init__(self) -> None:
        self.conversation: ConversationMemory = ConversationMemory()
        self.session: SessionMemory = SessionMemory()

    def record(self, task: Task, result: TaskResult) -> None:
        """Write a completed task/result pair to all memory stores.

        Only successful results are written.  Failed tasks are logged but
        not stored — storing error noise would pollute conversation history.

        Args:
            task:   The task that was executed.
            result: The ``TaskResult`` returned by ``Agent.run()``.
        """
        if not result.success:
            _logger.debug(
                "MemoryManager.record() skipped — task failed: %s", result.error
            )
            return

        self.conversation.append(task, result)
        self.session.update(task, result)
        _logger.debug(
            "MemoryManager recorded turn #%d", self.conversation.turn_count
        )

    def clear(self) -> None:
        """Discard all stored memory (e.g. when the user clears the chat)."""
        self.conversation.clear()
        self.session.clear()
        _logger.debug("MemoryManager cleared")
