from providers.base_provider import BaseProvider


class OpenRouterProvider(BaseProvider):

    def generate(self, messages):
        raise NotImplementedError()