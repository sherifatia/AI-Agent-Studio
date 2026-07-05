"""Skill Registry — discovery, registration, and execution of skills.

``SkillRegistry`` is the single place that knows which skills exist.
``SkillLoader`` populates the registry from a list of ``BaseSkill``
instances.  The ``Agent`` will call ``registry.execute(name, input)``
to run a skill by name.

Mirrors the shape of ``providers.provider_manager.ProviderManager`` for
consistency.
"""

from __future__ import annotations

from core.logging_setup import get_logger
from skills.skill import BaseSkill, SkillResult

_logger = get_logger(__name__)


class SkillRegistry:
    """Stores registered skills and dispatches execution by name.

    Usage::

        registry = SkillRegistry()
        registry.register(CurrentTimeSkill())
        result = registry.execute("current_time", "")
    """

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        """Add a skill to the registry.

        Args:
            skill: A concrete ``BaseSkill`` instance.

        Raises:
            ValueError: If a skill with the same ``name`` is already registered.
        """
        if skill.name in self._skills:
            raise ValueError(f"Skill already registered: '{skill.name}'")
        self._skills[skill.name] = skill
        _logger.debug("Skill registered: %s", skill.name)

    def has(self, name: str) -> bool:
        """Return ``True`` if a skill with ``name`` is registered."""
        return name in self._skills

    def get(self, name: str) -> BaseSkill:
        """Return the skill registered under ``name``.

        Raises:
            KeyError: If no skill with that name exists.
        """
        if name not in self._skills:
            raise KeyError(f"Unknown skill: '{name}'")
        return self._skills[name]

    def all_skills(self) -> list[BaseSkill]:
        """Return every registered skill, in registration order."""
        return list(self._skills.values())

    def execute(self, name: str, input: str) -> SkillResult:
        """Execute the named skill and return its result.

        Args:
            name:  The skill's ``name`` property.
            input: Raw input forwarded to ``BaseSkill.execute()``.

        Returns:
            A ``SkillResult``.  If the skill name is unknown, returns a
            failed ``SkillResult`` rather than raising.
        """
        if name not in self._skills:
            _logger.warning("SkillRegistry: unknown skill '%s'", name)
            return SkillResult(
                success=False, output="", error=f"Unknown skill: '{name}'"
            )

        try:
            result = self._skills[name].execute(input)
            _logger.debug(
                "Skill '%s' executed — success=%s", name, result.success
            )
            return result
        except Exception as exc:
            _logger.exception("Skill '%s' raised unexpectedly", name)
            return SkillResult(success=False, output="", error=str(exc))


class SkillLoader:
    """Loads ``BaseSkill`` instances into a ``SkillRegistry``.

    The separation between ``SkillLoader`` and ``SkillRegistry`` mirrors
    ``ProviderManager`` vs ``BaseProvider``: the loader is responsible for
    discovering and instantiating skills; the registry is responsible for
    dispatching them.

    A future Build may replace ``SkillLoader`` with a plugin-based
    discovery mechanism without changing ``SkillRegistry``.
    """

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def load(self, skills: list[BaseSkill]) -> None:
        """Register each skill in ``skills``.

        Args:
            skills: A list of instantiated ``BaseSkill`` objects.
        """
        for skill in skills:
            self._registry.register(skill)
        _logger.info("SkillLoader: loaded %d skill(s)", len(skills))
