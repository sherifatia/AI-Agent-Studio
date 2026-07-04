"""Ollama provider — connects to a local Ollama server."""

from ollama import Client

from core.response import Response
from providers.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """Generates responses using a local Ollama server.

    This is currently the only fully implemented provider. See
    docs/PROJECT_AUDIT.md for the status of the other providers.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3",
    ) -> None:
        """Create a provider bound to a specific Ollama host and model.

        Args:
            host: Base URL of the Ollama server.
            model: Name of the Ollama model to use for generation.
        """
        self.client = Client(host=host)
        self.model = model

    def generate(self, messages: list[dict[str, str]]) -> Response:
        """Generate a response by calling the Ollama chat API.

        Args:
            messages: A list of chat messages, each shaped like
                {"role": "user"|"assistant"|"system", "content": "..."}.

        Returns:
            A `Response` with the generated content on success.
        """
        response = self.client.chat(
            model=self.model,
            messages=messages
        )

        return Response(
            success=True,
            content=response["message"]["content"],
            provider="Ollama"
        )
