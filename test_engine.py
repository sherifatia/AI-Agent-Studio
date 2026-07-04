"""Manual smoke test for `core.engine.AIEngine` using a fake provider.

Not a `pytest` suite — run directly (`python test_engine.py`) and inspect
the printed output. Does not require Ollama to be running. See
docs/CODING_STANDARD.md ("Tests") and docs/ROADMAP.md for the planned
migration to a real test suite.
"""

from core.engine import AIEngine
from providers.base_provider import BaseProvider


class FakeProvider(BaseProvider):
    """An in-memory provider used only by this smoke test."""

    def generate(self, messages):

        return type(
            "Response",
            (),
            {
                "success": True,
                "content": "AI Agent Studio يعمل بنجاح 🎉",
                "provider": "FakeProvider",
            },
        )()


engine = AIEngine()

engine.set_provider(FakeProvider())

response = engine.ask([
    {
        "role": "user",
        "content": "مرحبا"
    }
])

print(response.success)
print(response.provider)
print(response.content)
