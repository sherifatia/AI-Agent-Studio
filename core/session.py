class Session:

    def __init__(self):
        self.history = []
        self.active_model = None
        self.active_provider = None

    def add_message(self, message):
        self.history.append(message)

    def clear(self):
        self.history.clear()