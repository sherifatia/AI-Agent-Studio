"""Centralized application metadata.

Single source of truth for the application's identity. Any module that
needs the app name, version, build number, author, repository, or
window title should import from here rather than hardcoding a duplicate.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppInfo:
    """Static, immutable application metadata.

    Attributes:
        NAME: The application's display name.
        VERSION: Semantic version of the application.
        BUILD_NUMBER: Monotonically increasing build identifier per
            docs/development/BUILD_WORKFLOW.md, independent of VERSION.
        AUTHOR: The project's lead developer / maintainer.
        REPOSITORY: The public repository URL.
    """

    NAME: str = "AI Agent Studio"
    VERSION: str = "0.1.0"
    BUILD_NUMBER: str = "023.0"
    AUTHOR: str = "Sherif Atia"
    REPOSITORY: str = "https://github.com/sherifatia/AI-Agent-Studio"

    @property
    def COMPANY(self) -> str:
        """The organization that publishes this application.

        Derived from NAME rather than stored as a separate literal —
        they share the same value today. If they ever diverge, promote
        COMPANY to a field with its own default.
        """
        return self.NAME

    @property
    def window_title(self) -> str:
        """The title displayed in the application's main window title bar."""
        return f"{self.NAME} — v{self.VERSION}"

    @property
    def full_version_string(self) -> str:
        """Version and build combined, e.g. '0.1.0 (build 001.1)'."""
        return f"{self.VERSION} (build {self.BUILD_NUMBER})"


# Module-level singleton. Every other module imports this instance.
APP_INFO = AppInfo()
