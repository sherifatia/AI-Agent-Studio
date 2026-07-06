"""Tests for provider_manager and provider construction."""

import pytest
from core.exceptions import UnknownProviderError
from providers.base_provider import BaseProvider
from providers.provider_manager import ProviderManager


class TestProviderManager:
    def _assert_valid_provider(self, provider, expected_model_start):
        assert isinstance(provider, BaseProvider)
        assert provider.model.startswith(expected_model_start)

    def test_create_ollama(self):
        pm = ProviderManager()
        self._assert_valid_provider(pm.create("ollama"), "llama")

    def test_create_openai(self):
        pm = ProviderManager()
        self._assert_valid_provider(pm.create("openai"), "gpt")

    def test_create_gemini(self):
        pm = ProviderManager()
        self._assert_valid_provider(pm.create("gemini"), "gemini")

    def test_create_openrouter(self):
        pm = ProviderManager()
        self._assert_valid_provider(pm.create("openrouter"), "openai")

    def test_create_unknown_raises(self):
        pm = ProviderManager()
        with pytest.raises(UnknownProviderError):
            pm.create("nonexistent")

    def test_create_case_insensitive(self):
        pm = ProviderManager()
        self._assert_valid_provider(pm.create("OLLAMA"), "llama")

    def test_model_param_forwarded(self):
        pm = ProviderManager()
        provider = pm.create("ollama", model="llama2")
        assert provider.model == "llama2"
