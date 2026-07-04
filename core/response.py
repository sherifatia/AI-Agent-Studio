from dataclasses import dataclass


@dataclass
class Response:
    success: bool
    content: str
    provider: str = ""