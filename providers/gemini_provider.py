from providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):

    def generate(self, messages):
        raise NotImplementedError()