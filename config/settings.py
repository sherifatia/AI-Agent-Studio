"""JSON-backed application settings loader."""

import json
from typing import Any


class Settings:
    """Loads and exposes key/value settings from `config/settings.json`.

    Note: the settings file path is resolved relative to the process's
    current working directory, not this module's location — the
    application must be launched from the repository root. See
    docs/PROJECT_AUDIT.md section 7.
    """

    def __init__(self) -> None:
        with open(
            "config/settings.json",
            "r",
            encoding="utf-8"
        ) as f:

            self.data: dict[str, Any] = json.load(f)

    def get(self, key: str) -> Any:
        """Return the value for `key`, or `None` if it is not present.

        Args:
            key: A top-level key from `config/settings.json`.

        Returns:
            The stored value, or `None` if `key` is missing.
        """
        return self.data.get(key)
