from providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):

    def generate(self, messages):
        raise NotImplementedError()