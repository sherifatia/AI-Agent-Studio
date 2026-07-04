"""In-memory conversation session state."""


class Session:
    """Tracks conversation history and the active model/provider.

    This is a plain in-memory record for a single run of the application.
    It does not persist across restarts — see `memory/conversation.py`
    (reserved) for planned persistence.
    """

    def __init__(self) -> None:
        self.history: list[dict[str, str]] = []
        self.active_model: str | None = None
        self.active_provider: str | None = None

    def add_message(self, message: dict[str, str]) -> None:
        """Append a message to the session history.

        Args:
            message: A chat message, e.g. {"role": "user", "content": "..."}.
        """
        self.history.append(message)

    def clear(self) -> None:
        """Discard all messages in the current session history."""
        self.history.clear()
