import json


class Settings:

    def __init__(self):

        with open(
            "config/settings.json",
            "r",
            encoding="utf-8"
        ) as f:

            self.data = json.load(f)

    def get(self, key):
        return self.data.get(key)