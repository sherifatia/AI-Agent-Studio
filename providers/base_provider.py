"""Abstract contract that every AI provider must implement."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.response import Response


class BaseProvider(ABC):
    """Base class for all AI provider implementations.

    A provider's only responsibility is turning a list of chat messages
    into a `Response`. Providers must not depend on `core.engine` or the
    UI layer.
    """

    @abstractmethod
    def generate(self, messages: list[dict[str, str]]) -> "Response":
        """Generate a response for the given messages.

        Args:
            messages: A list of chat messages, each shaped like
                {"role": "user"|"assistant"|"system", "content": "..."}.

        Returns:
            A `Response` describing the outcome of the generation.
        """
        pass
