from ollama import Client

from providers.base_provider import BaseProvider
from core.response import Response


class OllamaProvider(BaseProvider):

    def __init__(self, host="http://localhost:11434", model="llama3"):
        self.client = Client(host=host)
        self.model = model

    def generate(self, messages):

        response = self.client.chat(
            model=self.model,
            messages=messages
        )

        return Response(
            success=True,
            content=response["message"]["content"],
            provider="Ollama"
        )