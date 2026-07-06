"""Workflow and Step models for multi-step agent automation.

A ``Workflow`` is a named, ordered collection of ``Step`` objects.
Each step produces a ``StepResult``; the ``WorkflowEngine`` passes
context between steps so that later steps can reference outputs from
earlier ones.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from skills.skill import SkillResult


# ---------------------------------------------------------------------------
# Step types
# ---------------------------------------------------------------------------


@dataclass
class StepResult:
    """The outcome of a single workflow step.

    Attributes:
        success:    Whether the step completed without an error.
        output:     Text output produced by this step.
        error:      Human-readable error on failure (empty on success).
        metadata:   Step-supplied key/value annotations.
    """

    success: bool
    output: str
    error: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


class Step(ABC):
    """Abstract base for a single workflow step.

    Subclasses must implement ``execute(context)`` and provide a
    human-readable ``description``.
    """

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description of what this step does."""

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> StepResult:
        """Run this step with the given execution context.

        Args:
            context: A mutable dict shared across all steps in the
                     workflow.  Steps may read from and write to this
                     dict (e.g. to pass data between steps).

        Returns:
            A ``StepResult`` — always returned, never raised.
        """


class SkillStep(Step):
    """A step that executes a registered skill.

    Args:
        skill_name: The name of the skill to execute (must be registered
            in the ``SkillRegistry``).
        input_template: Optional string template for the skill input.
            ``"{previous_output}"`` is replaced with the previous step's
            output; ``"{input}"`` is replaced with the workflow input.
    """

    def __init__(
        self,
        skill_name: str,
        input_template: str = "{input}",
    ) -> None:
        self._skill_name = skill_name
        self._input_template = input_template

    @property
    def description(self) -> str:
        return f"Run skill: {self._skill_name}"

    def execute(self, context: dict[str, Any]) -> StepResult:
        from skills.skill_manager import SkillRegistry

        registry: SkillRegistry | None = context.get("skill_registry")
        if registry is None:
            return StepResult(
                success=False,
                output="",
                error="No skill registry in context.",
            )

        raw_input = self._input_template.format(
            input=context.get("input", ""),
            previous_output=context.get("_last_output", ""),
        )

        result: SkillResult = registry.execute(self._skill_name, raw_input)
        return StepResult(
            success=result.success,
            output=result.output,
            error=result.error,
            metadata=dict(result.metadata),
        )


class PromptStep(Step):
    """A step that sends a prompt to the active LLM provider.

    Args:
        prompt_template: String template for the prompt sent to the LLM.
            ``"{previous_output}"`` is replaced with the previous step's
            output; ``"{input}"`` is replaced with the workflow input.
    """

    def __init__(self, prompt_template: str = "{input}") -> None:
        self._prompt_template = prompt_template

    @property
    def description(self) -> str:
        return "Send prompt to LLM"

    def execute(self, context: dict[str, Any]) -> StepResult:
        from core.engine import AIEngine

        engine: AIEngine | None = context.get("engine")
        if engine is None:
            return StepResult(
                success=False,
                output="",
                error="No engine in context.",
            )

        prompt = self._prompt_template.format(
            input=context.get("input", ""),
            previous_output=context.get("_last_output", ""),
        )

        messages = [{"role": "user", "content": prompt}]
        try:
            response = engine.ask(messages)
            return StepResult(
                success=response.success,
                output=response.content,
                error="" if response.success else "Provider returned failure",
            )
        except Exception as exc:
            return StepResult(
                success=False,
                output="",
                error=str(exc),
            )


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------


@dataclass
class Workflow:
    """A named, ordered collection of steps.

    Attributes:
        name:        Unique identifier for this workflow.
        description: Human-readable summary.
        steps:       Ordered list of ``Step`` instances to execute.
    """

    name: str
    description: str
    steps: list[Step] = field(default_factory=list)
