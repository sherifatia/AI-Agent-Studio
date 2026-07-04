"""Provider-agnostic AI engine."""

from typing import TYPE_CHECKING

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

    def ask(self, messages: list[dict[str, str]]) -> "Response":
        """Generate a response for the given messages via the active provider.

        Args:
            messages: A list of chat messages, each shaped like
                {"role": "user"|"assistant"|"system", "content": "..."}.

        Returns:
            The `Response` produced by the active provider.

        Raises:
            Exception: If no provider has been set via `set_provider()`.
        """
        if self.provider is None:
            raise Exception("No Provider Selected")

        return self.provider.generate(messages)
