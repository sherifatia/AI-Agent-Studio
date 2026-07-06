"""WorkflowEngine — register and execute multi-step workflows.

``WorkflowEngine`` is the central coordinator for workflow execution.
It holds a registry of named ``Workflow`` definitions and provides
``run(name, input, context)`` to execute one synchronously.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.logging_setup import get_logger
from workflows.workflow import StepResult, Workflow

_logger = get_logger(__name__)


@dataclass
class WorkflowResult:
    """The outcome of executing an entire workflow.

    Attributes:
        success:     ``True`` if every step completed successfully.
        step_results: Ordered list of per-step ``StepResult`` objects.
        final_output: The output of the last step (empty on failure).
    """

    success: bool
    step_results: list[StepResult] = field(default_factory=list)
    final_output: str = ""


class WorkflowEngine:
    """Registry and executor for ``Workflow`` definitions.

    Usage::

        engine = WorkflowEngine()
        engine.register(my_workflow)
        result = engine.run("my_workflow", input="hello", context={...})
    """

    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, workflow: Workflow) -> None:
        """Register a workflow definition.

        Args:
            workflow: The ``Workflow`` to register.

        Raises:
            ValueError: If a workflow with the same ``name`` is already
                registered.
        """
        if workflow.name in self._workflows:
            raise ValueError(
                f"Workflow already registered: '{workflow.name}'"
            )
        self._workflows[workflow.name] = workflow
        _logger.debug("Workflow registered: %s", workflow.name)

    def has(self, name: str) -> bool:
        """Return ``True`` if a workflow with ``name`` is registered."""
        return name in self._workflows

    def get(self, name: str) -> Workflow:
        """Return the registered workflow with the given name.

        Raises:
            KeyError: If no workflow with that name exists.
        """
        if name not in self._workflows:
            raise KeyError(f"Unknown workflow: '{name}'")
        return self._workflows[name]

    def list_workflows(self) -> list[Workflow]:
        """Return every registered workflow, in registration order."""
        return list(self._workflows.values())

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(
        self,
        name: str,
        input: str = "",
        context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """Execute the named workflow synchronously.

        Each step runs in order.  If a step fails, the remaining steps
        are skipped and the result reflects the failure.

        Args:
            name:    The registered workflow name.
            input:   The input string passed to each step.
            context: Optional dict shared across all steps.  If ``None``,
                     an empty dict is created.  The context is populated
                     with ``"input"``, ``"engine"``, and
                     ``"skill_registry"`` from the provided context.

        Returns:
            A ``WorkflowResult`` summarising the run.
        """
        if name not in self._workflows:
            _logger.warning("WorkflowEngine: unknown workflow '%s'", name)
            return WorkflowResult(
                success=False,
                step_results=[],
                final_output="",
            )

        workflow = self._workflows[name]
        ctx: dict[str, Any] = dict(context or {})
        ctx.setdefault("input", input)
        step_results: list[StepResult] = []

        _logger.info(
            "Running workflow '%s' (%d step(s))",
            name,
            len(workflow.steps),
        )

        for i, step in enumerate(workflow.steps):
            _logger.debug(
                "Workflow step %d/%d: %s",
                i + 1,
                len(workflow.steps),
                step.description,
            )
            result = step.execute(ctx)
            step_results.append(result)

            ctx["_last_output"] = result.output if result.success else ""

            if not result.success:
                _logger.warning(
                    "Workflow '%s' failed at step %d: %s",
                    name,
                    i + 1,
                    result.error,
                )
                return WorkflowResult(
                    success=False,
                    step_results=step_results,
                    final_output="",
                )

        final = step_results[-1].output if step_results else ""
        _logger.info("Workflow '%s' completed successfully", name)
        return WorkflowResult(
            success=True,
            step_results=step_results,
            final_output=final,
        )
