"""Skill — base contract for an agent skill.

A ``Skill`` is a discrete, named capability the ``Agent`` can invoke
instead of (or alongside) sending a message to the LLM provider.

Every concrete skill:
1. Subclasses ``BaseSkill``.
2. Declares a unique ``name`` and a human-readable ``description``.
3. Implements ``execute(input: str) -> SkillResult``.

Skills must not import Qt, access the engine directly, or write to memory.
The Agent owns the skill call — it is responsible for feeding the result
back into the conversation if appropriate.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SkillResult:
    """The outcome of a single skill execution.

    Attributes:
        success: ``True`` if the skill ran without an unhandled exception.
        output:  The skill's text output.  Empty string on failure.
        error:   Human-readable failure description.  Empty on success.
        metadata: Skill-supplied key/value annotations (e.g. units, source).
    """

    success: bool
    output: str
    error: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


class BaseSkill(ABC):
    """Abstract base class for all skills.

    Mirrors the shape of ``providers.base_provider.BaseProvider`` so the
    registry and execution patterns stay consistent across the codebase.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique, stable identifier for this skill, e.g. ``"current_time"``."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line human-readable description shown in the UI."""

    @abstractmethod
    def execute(self, input: str) -> SkillResult:
        """Run the skill against the given input string.

        Args:
            input: The raw user input or an extracted parameter string.
                   Skills are responsible for their own input parsing.

        Returns:
            A ``SkillResult`` — always returned, never raised.
        """
