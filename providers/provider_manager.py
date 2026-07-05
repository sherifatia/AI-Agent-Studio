"""Factory for resolving a provider implementation by name."""

from typing import TYPE_CHECKING

from core.exceptions import UnknownProviderError

if TYPE_CHECKING:
    from providers.base_provider import BaseProvider


class ProviderManager:
    """Creates a concrete `BaseProvider` instance from a provider name.

    This is the single place in the codebase that maps the provider names
    used in `config/settings.json` (e.g. "ollama") to their implementing
    classes.
    """

    def create(self, provider_name: str) -> "BaseProvider":
        """Instantiate the provider matching the given name.

        Args:
            provider_name: One of "ollama", "openai", "gemini", or
                "openrouter" (case-insensitive).

        Returns:
            A new instance of the matching `BaseProvider` subclass.

        Raises:
            Exception: If `provider_name` does not match a known provider.
        """
        provider_name = provider_name.lower()

        if provider_name == "ollama":
            from providers.ollama_provider import OllamaProvider
            return OllamaProvider()

        if provider_name == "openai":
            from providers.openai_provider import OpenAIProvider
            return OpenAIProvider()

        if provider_name == "gemini":
            from providers.gemini_provider import GeminiProvider
            return GeminiProvider()

        if provider_name == "openrouter":
            from providers.openrouter_provider import OpenRouterProvider
            return OpenRouterProvider()

        raise UnknownProviderError(
            f"Unknown provider: '{provider_name}'. "
            f"Known providers: ollama, openai, gemini, openrouter."
        )
