"""JSON-backed application settings loader."""

import json
from pathlib import Path
from typing import Any

_SETTINGS_PATH: Path = Path(__file__).parent / "settings.json"


class Settings:
    """Loads and exposes key/value settings from ``config/settings.json``.

    The file path is resolved relative to this module's location, so the
    application can be launched from any working directory.
    """

    def __init__(self) -> None:
        with open(
            _SETTINGS_PATH,
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
