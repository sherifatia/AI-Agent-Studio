"""Provider response model."""

from dataclasses import dataclass


@dataclass
class Response:
    """The result of a single `BaseProvider.generate()` call.

    Attributes:
        success: Whether the provider call completed successfully.
        content: The generated text content.
        provider: The name of the provider that produced this response.
    """

    success: bool
    content: str
    provider: str = ""
