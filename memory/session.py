"""SessionMemory — session-level aggregate statistics.

Tracks totals for the current application run: number of turns, number
of failures, and total time spent waiting for the provider.  Provides a
lightweight summary without duplicating the full turn log held by
``ConversationMemory``.
"""

from __future__ import annotations

from core.task import Task
from core.task_result import TaskResult


class SessionMemory:
    """Aggregate statistics for the current application session.

    Attributes:
        total_turns:    Successful turn count recorded this session.
        failed_turns:   Count of tasks that returned ``success=False``.
        total_duration: Cumulative provider response time in seconds.
    """

    def __init__(self) -> None:
        self.total_turns: int = 0
        self.failed_turns: int = 0
        self.total_duration: float = 0.0

    def update(self, task: Task, result: TaskResult) -> None:
        """Update session counters from a completed task result.

        Args:
            task:   The executed task (currently unused — reserved for
                    future per-skill or per-page breakdowns).
            result: The ``TaskResult`` from ``Agent.run()``.
        """
        if result.success:
            self.total_turns += 1
        else:
            self.failed_turns += 1
        self.total_duration += result.duration

    def clear(self) -> None:
        """Reset all session statistics."""
        self.total_turns = 0
        self.failed_turns = 0
        self.total_duration = 0.0

    @property
    def average_duration(self) -> float:
        """Average provider response time per successful turn, in seconds."""
        if self.total_turns == 0:
            return 0.0
        return self.total_duration / self.total_turns
