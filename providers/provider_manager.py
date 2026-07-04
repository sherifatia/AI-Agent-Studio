class ProviderManager:

    def create(self, provider_name):

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

        raise Exception(f"Unknown provider: {provider_name}")