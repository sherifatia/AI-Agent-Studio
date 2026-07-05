"""Skill: current_time — returns the local date and time."""

from __future__ import annotations

from datetime import datetime

from skills.skill import BaseSkill, SkillResult


class CurrentTimeSkill(BaseSkill):
    """Returns the current local date and time as a formatted string."""

    @property
    def name(self) -> str:
        return "current_time"

    @property
    def description(self) -> str:
        return "Return the current local date and time."

    def execute(self, input: str) -> SkillResult:
        """Ignore input; return formatted current datetime.

        Args:
            input: Ignored.

        Returns:
            A successful ``SkillResult`` with the formatted time string.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return SkillResult(
            success=True,
            output=f"Current date and time: {now}",
            metadata={"timestamp": now},
        )
