from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate(self, messages):
        pass