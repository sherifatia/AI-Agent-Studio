"""Plugin discovery, loading, and lifecycle management.

``PluginManager`` scans a directory for Python files that export
``BasePlugin`` subclasses, instantiates them, and manages their
activation lifecycle.
"""

from __future__ import annotations

import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Any

from core.logging_setup import get_logger
from plugins.plugin_base import BasePlugin

_logger = get_logger(__name__)


class PluginManager:
    """Discovers, loads, and activates plugins from a directory.

    Usage::

        mgr = PluginManager()
        mgr.discover("path/to/plugins")
        mgr.activate_all(context)
        # ... use the app ...
        mgr.deactivate_all(context)
    """

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self, directory: str | Path) -> list[str]:
        """Scan a directory for plugin modules and register them.

        Each ``.py`` file in ``directory`` is imported and inspected for
        concrete ``BasePlugin`` subclasses.  Discovered plugins are
        stored by name and returned as a list of names.

        Args:
            directory: Path to a directory containing plugin ``.py``
                files.  Non-recursive (only direct children).

        Returns:
            A list of successfully discovered plugin names.

        Raises:
            FileNotFoundError: If ``directory`` does not exist.
        """
        path = Path(directory)
        if not path.is_dir():
            raise FileNotFoundError(
                f"Plugin directory not found: '{directory}'"
            )

        discovered: list[str] = []
        for entry in sorted(path.iterdir()):
            if entry.suffix != ".py" or entry.name.startswith("__"):
                continue

            plugin_names = self._load_module(entry)
            discovered.extend(plugin_names)

        if discovered:
            _logger.info(
                "PluginManager: discovered %d plugin(s): %s",
                len(discovered),
                ", ".join(discovered),
            )
        else:
            _logger.info("PluginManager: no plugins discovered in '%s'", directory)

        return discovered

    def _load_module(self, filepath: Path) -> list[str]:
        """Import one ``.py`` file and register any ``BasePlugin`` subclasses."""
        module_name = filepath.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                return []

            module = importlib.util.module_from_spec(spec)
            # Add to sys.modules so relative imports inside the plugin work.
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        except Exception as exc:
            _logger.warning(
                "PluginManager: failed to load '%s': %s", module_name, exc
            )
            return []

        found: list[str] = []
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BasePlugin)
                and obj is not BasePlugin
                and not inspect.isabstract(obj)
            ):
                try:
                    instance = obj()
                    self.register(instance)
                    found.append(instance.name)
                except Exception as exc:
                    _logger.warning(
                        "PluginManager: failed to instantiate '%s': %s",
                        obj.__name__,
                        exc,
                    )

        return found

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin instance manually.

        Args:
            plugin: A ``BasePlugin`` instance.

        Raises:
            ValueError: If a plugin with the same ``name`` is already
                registered.
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin already registered: '{plugin.name}'")
        self._plugins[plugin.name] = plugin
        _logger.debug("PluginManager: registered '%s' v%s", plugin.name, plugin.version)

    def unregister(self, name: str) -> None:
        """Remove a plugin by name.

        Raises:
            KeyError: If no plugin with that name exists.
        """
        if name not in self._plugins:
            raise KeyError(f"Unknown plugin: '{name}'")
        del self._plugins[name]

    def get(self, name: str) -> BasePlugin | None:
        """Return the registered plugin, or ``None``."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[BasePlugin]:
        """Return every registered plugin, in registration order."""
        return list(self._plugins.values())

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def activate_all(self, context: dict[str, Any]) -> None:
        """Call ``on_activate()`` on every registered plugin.

        If a plugin's ``on_activate()`` raises, the error is logged and
        the plugin is skipped — other plugins are still activated.

        Args:
            context: Dict passed to each plugin's ``on_activate()``.
        """
        for plugin in self._plugins.values():
            try:
                plugin.on_activate(context)
                _logger.info(
                    "Plugin activated: '%s' v%s", plugin.name, plugin.version
                )
            except Exception as exc:
                _logger.warning(
                    "Plugin '%s' failed to activate: %s", plugin.name, exc
                )

    def deactivate_all(self, context: dict[str, Any]) -> None:
        """Call ``on_deactivate()`` on every registered plugin.

        Errors during deactivation are logged but do not prevent other
        plugins from being deactivated.

        Args:
            context: Dict passed to each plugin's ``on_deactivate()``.
        """
        for plugin in self._plugins.values():
            try:
                plugin.on_deactivate(context)
                _logger.debug(
                    "Plugin deactivated: '%s'", plugin.name
                )
            except Exception as exc:
                _logger.warning(
                    "Plugin '%s' failed to deactivate: %s", plugin.name, exc
                )

    def clear(self) -> None:
        """Deactivate and remove all plugins."""
        self._plugins.clear()
        _logger.debug("PluginManager: cleared")
