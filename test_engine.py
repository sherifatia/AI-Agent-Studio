from core.engine import AIEngine
from providers.base_provider import BaseProvider


class FakeProvider(BaseProvider):

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