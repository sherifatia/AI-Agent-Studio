"""Agent — executes Tasks using an AIEngine (optionally via Runtime).

``Agent`` sits between the UI layer and the engine/provider layer.  Its
only job is to take a ``Task``, build the message list, call the engine,
and return a ``TaskResult``.

Rules enforced here:
- Agent NEVER creates a new ``AIEngine`` or ``Session``.
- Agent NEVER talks to a provider directly.
- Agent NEVER imports Qt.
- All skill execution goes through the Agent (Build 010+).
- Skill dispatch happens before LLM call (Build 011+).
- LLM execution goes through Runtime when available (Build 016+).
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from core.logging_setup import get_logger
from core.task import Task
from core.task_result import TaskResult

if TYPE_CHECKING:
    from core.engine import AIEngine
    from core.runtime import Runtime
    from memory.manager import MemoryManager
    from skills.skill_manager import SkillRegistry
    from skills.skill import SkillResult

_logger = get_logger(__name__)

# Maps command-style aliases (e.g. /time) to registered skill names.
_SKILL_ALIASES: dict[str, str] = {
    "time": "current_time",
    "calc": "calculator",
    "calculate": "calculator",
}


class Agent:
    """Executes ``Task`` objects via an ``AIEngine`` or ``Runtime``.

    When a ``Runtime`` is provided, the LLM path delegates to
    ``runtime.run(task)`` for lifecycle-managed execution.  When no runtime
    is available, the Agent falls back to calling ``engine.ask()`` directly.

    The Agent is stateless with respect to conversation history —
    history is part of the ``Task`` submitted by the caller.  Long-term
    memory (Build 009) will be written by the Agent after each completed
    task, not by the UI.

    Args:
        engine: The shared ``AIEngine`` instance.  The engine owns the
                ``Session``; the Agent must not replace it.
    """

    def __init__(
        self,
        engine: "AIEngine",
        memory: "MemoryManager | None" = None,
        skill_registry: "SkillRegistry | None" = None,
        runtime: "Runtime | None" = None,
    ) -> None:
        self._engine = engine
        self._memory: "MemoryManager | None" = memory
        self._skill_registry: "SkillRegistry | None" = skill_registry
        self._runtime: "Runtime | None" = runtime

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, task: Task) -> TaskResult:
        """Execute ``task`` and return its result.

        Workflow when a skill matches::

            Task.input
                ↓  (detect skill)
            SkillRegistry.execute(name, input)
                ↓
            SkillResult wrapped in TaskResult
                ↓
            MemoryManager.record(task, result)
                ↓
            TaskResult

        Workflow when no skill matches (falls through to LLM)::

            Task.input + Task.history
                ↓  (build messages)
            AIEngine.ask(messages)
                ↓  (provider.generate)
            Response → TaskResult
                ↓
            MemoryManager.record(task, result)
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
            # Check for a skill match before calling the LLM.
            skill_hit = self._detect_skill(task.input)
            if skill_hit is not None:
                return self._run_skill(task, skill_hit[0], skill_hit[1], start)

            # No skill matched — delegate to the LLM provider.
            # Use Runtime when available for lifecycle-managed execution.
            if self._runtime is not None:
                task_result = self._runtime.run(task)
            else:
                messages = self._build_messages(task)
                response = self._engine.ask(messages)
                duration = time.monotonic() - start
                task_result = TaskResult(
                    success=True,
                    response=response.content,
                    duration=duration,
                    metadata={
                        "provider": response.provider,
                        **task.metadata,
                    },
                )

            _logger.debug(
                "Agent.run() complete in %.2fs", task_result.duration,
            )
            if self._memory is not None:
                self._memory.record(task, task_result)
            return task_result

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

    def clear_memory(self) -> None:
        """Clear all recorded memory (delegates to ``MemoryManager.clear()``).

        Safe to call even when no memory manager is attached.
        """
        if self._memory is not None:
            self._memory.clear()
            _logger.debug("Agent: memory cleared via clear_memory()")
        else:
            _logger.debug("Agent: clear_memory() called, but no memory manager")

    # ------------------------------------------------------------------
    # Skill dispatch
    # ------------------------------------------------------------------

    def _run_skill(
        self,
        task: Task,
        skill_name: str,
        skill_input: str,
        start: float,
    ) -> TaskResult:
        """Execute a skill and return a TaskResult, without calling the LLM.

        Args:
            task:       The original task (used for history/metadata).
            skill_name: The registered skill name.
            skill_input: Input string forwarded to the skill.
            start:       ``time.monotonic()`` timestamp from ``run()``.

        Returns:
            A ``TaskResult`` wrapping the ``SkillResult``.
        """
        if self._skill_registry is None:
            duration = time.monotonic() - start
            return TaskResult(
                success=False,
                response="",
                error="No skill registry available. Cannot execute skill.",
                duration=duration,
                metadata=dict(task.metadata),
            )

        raw = self._skill_registry.execute(skill_name, skill_input)
        duration = time.monotonic() - start

        skill_result: "SkillResult" = raw

        if skill_result.success:
            task_result = TaskResult(
                success=True,
                response=skill_result.output,
                duration=duration,
                metadata={
                    "skill": skill_name,
                    **skill_result.metadata,
                    **task.metadata,
                },
            )
        else:
            task_result = TaskResult(
                success=False,
                response="",
                error=skill_result.error,
                duration=duration,
                metadata={"skill": skill_name, **task.metadata},
            )

        if self._memory is not None:
            self._memory.record(task, task_result)

        _logger.debug(
            "Skill '%s' executed in %.2fs — success=%s",
            skill_name,
            duration,
            task_result.success,
        )
        return task_result

    @staticmethod
    def _detect_skill(input_text: str) -> tuple[str, str] | None:
        """Check whether ``input_text`` triggers a registered skill.

        Detection rules:
        1. Input must start with ``/`` followed by a command name.
        2. The command name is matched (case-insensitive) against
           ``_SKILL_ALIASES`` and then against all registered skill names.
           *The registry is not consulted here* — alias resolution is
           static so detection remains a pure function.

        Args:
            input_text: The raw user input.

        Returns:
            ``(skill_name, remainder)`` if a skill is detected, or
            ``None`` if no skill matches.
        """
        text = input_text.strip()
        if not text.startswith("/"):
            return None

        # Split "/command rest" into command and remainder.
        parts = text[1:].split(None, 1)
        cmd = parts[0].lower() if parts else ""
        remainder = parts[1].strip() if len(parts) > 1 else ""

        if not cmd:
            return None

        # Check aliases first, then try the command as a direct skill name.
        skill_name = _SKILL_ALIASES.get(cmd, cmd)
        return (skill_name, remainder)

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
