"""Tests for core.engine.AIEngine."""

from core.engine import AIEngine
from core.exceptions import ProviderNotSelectedError
from core.message import Message
from providers.base_provider import BaseProvider


class FakeProvider(BaseProvider):
    """An in-memory provider returning a canned response."""

    def generate(self, messages):
        return type(
            "Response",
            (),
            {
                "success": True,
                "content": "Hello from FakeProvider",
                "provider": "FakeProvider",
            },
        )()


class TestAIEngine:
    def test_ask_without_provider_raises(self):
        engine = AIEngine()
        import pytest
        with pytest.raises(ProviderNotSelectedError):
            engine.ask([{"role": "user", "content": "hi"}])

    def test_ask_with_provider_returns_response(self):
        engine = AIEngine()
        engine.set_provider(FakeProvider())
        resp = engine.ask([{"role": "user", "content": "hi"}])
        assert resp.success is True
        assert resp.provider == "FakeProvider"
        assert resp.content == "Hello from FakeProvider"

    def test_ask_normalises_message_objects(self):
        engine = AIEngine()
        engine.set_provider(FakeProvider())
        resp = engine.ask([Message(role="user", content="hello")])
        assert resp.success is True
