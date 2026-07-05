"""Provider-agnostic AI engine."""

from typing import TYPE_CHECKING

from core.exceptions import ProviderNotSelectedError
from core.message import Message
from core.session import Session

if TYPE_CHECKING:
    from core.response import Response
    from providers.base_provider import BaseProvider


class AIEngine:
    """Orchestrates a conversation against a single active provider.

    The engine itself holds no provider-specific logic — it only tracks
    the active `Session` and delegates message generation to whichever
    `BaseProvider` has been set via `set_provider()`.
    """

    def __init__(self) -> None:
        self.session: Session = Session()
        self.provider: "BaseProvider | None" = None

    def set_provider(self, provider: "BaseProvider") -> None:
        """Set the provider used by subsequent `ask()` calls.

        Args:
            provider: A concrete `BaseProvider` implementation.
        """
        self.provider = provider

    def ask(self, messages: list[Message | dict[str, str]]) -> "Response":
        """Generate a response for the given messages via the active provider.

        Args:
            messages: A list of chat messages, each shaped like
                ``{"role": ..., "content": ...}`` or a ``Message`` instance.

        Returns:
            The ``Response`` produced by the active provider.

        Raises:
            ProviderNotSelectedError: If no provider has been set via
                ``set_provider()``.
        """
        if self.provider is None:
            raise ProviderNotSelectedError(
                "No provider selected. Call set_provider() before ask()."
            )

        # Normalise Message instances to plain dicts for the provider.
        raw: list[dict[str, str]] = [
            {"role": m.role, "content": m.content}
            if isinstance(m, Message)
            else m
            for m in messages
        ]
        return self.provider.generate(raw)
