from core.session import Session


class AIEngine:

    def __init__(self):
        self.session = Session()
        self.provider = None

    def set_provider(self, provider):
        self.provider = provider

    def ask(self, messages):

        if self.provider is None:
            raise Exception("No Provider Selected")

        return self.provider.generate(messages)