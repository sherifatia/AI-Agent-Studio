"""Base contract that every plugin must implement.

A ``BasePlugin`` subclass is the entry point for a third-party extension.
Plugins can register skills, workflows, or providers during their
``on_activate()`` hook and clean up in ``on_deactivate()``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Abstract base class for all plugins.

    Subclasses must provide ``name``, ``version``, and implement
    ``on_activate()``.  The ``on_deactivate()`` hook is optional but
    should be used to unregister any resources the plugin added.

    Usage::

        class MyPlugin(BasePlugin):
            name = "my_plugin"
            version = "1.0.0"
            description = "Adds custom skills"

            def on_activate(self, context):
                context["skill_registry"].register(MySkill())

            def on_deactivate(self, context):
                pass
    """

    # --- Metadata (override in subclass) ---

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique, stable plugin identifier, e.g. ``"my_plugin"``."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version string, e.g. ``"1.0.0"``."""

    @property
    def description(self) -> str:
        """One-line human-readable summary (defaults to ``name``)."""
        return self.name

    # --- Lifecycle hooks ---

    @abstractmethod
    def on_activate(self, context: dict[str, Any]) -> None:
        """Called when the plugin is loaded and activated.

        Args:
            context: A dict shared across all active plugins.
                     Typical keys: ``"skill_registry"``,
                     ``"workflow_engine"``, ``"provider_manager"``,
                     ``"event_bus"``, ``"engine"``.
        """

    def on_deactivate(self, context: dict[str, Any]) -> None:
        """Called when the plugin is deactivated.

        Override to unregister skills, workflows, or other resources
        that were added during ``on_activate()``.  Default is a no-op.

        Args:
            context: The same dict that was passed to ``on_activate()``.
        """
