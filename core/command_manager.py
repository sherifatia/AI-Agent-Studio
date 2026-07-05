"""Command system foundation.

A simple, UI-agnostic registry mapping a command identifier to a callable.
This is infrastructure only: it lets future Builds register actions once
(e.g. "app.show_about", "file.new_session") and invoke them uniformly from
menus, toolbar buttons, or — in a future Build — keyboard shortcuts. This
module does not implement any shortcut binding or menu wiring itself.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from core.logging_setup import get_logger

_logger = get_logger(__name__)


@dataclass
class Command:
    """A single registered, invokable action.

    Attributes:
        command_id: A unique, stable identifier, e.g. "app.show_about".
        name: A short, human-readable label (for future menu/UI display).
        action: A callable executed when the command runs.
    """

    command_id: str
    name: str
    action: Callable[..., Any]


class CommandManager:
    """Registers and executes named `Command`s.

    Future Builds may attach keyboard shortcuts to a registered command's
    `command_id` without changing how commands are registered or run.
    """

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register_command(
        self, command_id: str, name: str, action: Callable[..., Any]
    ) -> None:
        """Register a new command.

        Args:
            command_id: A unique, stable identifier, e.g. "app.show_about".
            name: A short, human-readable label.
            action: A callable to invoke when the command executes.

        Raises:
            ValueError: If `command_id` is already registered.
        """
        if command_id in self._commands:
            raise ValueError(f"Command already registered: {command_id}")

        self._commands[command_id] = Command(
            command_id=command_id, name=name, action=action
        )
        _logger.debug("Registered command: %s (%s)", command_id, name)

    def execute_command(self, command_id: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a registered command by its identifier.

        Args:
            command_id: The identifier passed to `register_command()`.
            *args: Positional arguments forwarded to the command's action.
            **kwargs: Keyword arguments forwarded to the command's action.

        Returns:
            Whatever the command's action returns.

        Raises:
            KeyError: If `command_id` has not been registered.
        """
        if command_id not in self._commands:
            raise KeyError(f"Unknown command: {command_id}")

        _logger.debug("Executing command: %s", command_id)
        return self._commands[command_id].action(*args, **kwargs)

    def list_commands(self) -> list[Command]:
        """Return every currently registered command."""
        return list(self._commands.values())
