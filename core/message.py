"""Chat message model.

Currently defined for future use — `core.engine.AIEngine.ask()` and
provider implementations pass plain `dict[str, str]` objects today rather
than `Message` instances. See docs/PROJECT_AUDIT.md section 7.
"""

from dataclasses import dataclass


@dataclass
class Message:
    """A single chat message.

    Attributes:
        role: The message author, e.g. "user", "assistant", or "system".
        content: The message text.
    """

    role: str
    content: str
