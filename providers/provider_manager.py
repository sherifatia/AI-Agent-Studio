"""Factory for resolving a provider implementation by name."""

from typing import TYPE_CHECKING

from core.exceptions import UnknownProviderError

if TYPE_CHECKING:
    from providers.base_provider import BaseProvider


class ProviderManager:
    """Creates a concrete ``BaseProvider`` instance from a provider name.

    This is the single place in the codebase that maps the provider names
    used in ``config/settings.json`` (e.g. ``"ollama"``) to their implementing
    classes.

    Optional ``model`` and ``host`` parameters are forwarded to the provider
    constructor so that callers (e.g. ``Application._start_engine``) do not
    need to know each provider's default values.
    """

    def create(
        self,
        provider_name: str,
        model: str = "",
        host: str = "",
    ) -> "BaseProvider":
        """Instantiate the provider matching the given name.

        Args:
            provider_name: One of ``"ollama"``, ``"openai"``, ``"gemini"``,
                or ``"openrouter"`` (case-insensitive).
            model: Optional model name override.  When empty the provider
                uses its own default.
            host:  Optional host URL override.  When empty the provider
                uses its own default.

        Returns:
            A new instance of the matching ``BaseProvider`` subclass.

        Raises:
            UnknownProviderError: If ``provider_name`` does not match a
                known provider.
        """
        provider_name = provider_name.lower()

        if provider_name == "ollama":
            from providers.ollama_provider import OllamaProvider
            return OllamaProvider(
                model=model or "llama3",
                host=host or "http://localhost:11434",
            )

        if provider_name == "openai":
            from providers.openai_provider import OpenAIProvider
            return OpenAIProvider(
                model=model or "gpt-3.5-turbo",
                host=host or "https://api.openai.com",
            )

        if provider_name == "gemini":
            from providers.gemini_provider import GeminiProvider
            return GeminiProvider(
                model=model or "gemini-1.5-flash",
                host=host or "https://generativelanguage.googleapis.com",
            )

        if provider_name == "openrouter":
            from providers.openrouter_provider import OpenRouterProvider
            return OpenRouterProvider(
                model=model or "openai/gpt-3.5-turbo",
                host=host or "https://openrouter.ai",
            )

        raise UnknownProviderError(
            f"Unknown provider: '{provider_name}'. "
            f"Known providers: ollama, openai, gemini, openrouter."
        )
