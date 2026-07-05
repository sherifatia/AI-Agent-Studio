"""Centralized application metadata.

Single source of truth for the application's identity. Any module that
needs the app name, version, build number, author, repository, company,
or window title should import from here rather than hardcoding a
duplicate value.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppInfo:
    """Static, immutable application metadata.

    Attributes:
        NAME: The application's display name.
        VERSION: Semantic version of the application.
        BUILD_NUMBER: Monotonically increasing build identifier, distinct
            from VERSION — incremented per Build per
            docs/development/BUILD_WORKFLOW.md, independent of semantic
            version bumps.
        AUTHOR: The project's lead developer / maintainer.
        REPOSITORY: The public repository URL.
        COMPANY: The organization the application is published under.
    """

    NAME: str = "AI Agent Studio"
    VERSION: str = "0.1.0"
    BUILD_NUMBER: str = "001"
    AUTHOR: str = "Sherif Atia"
    REPOSITORY: str = "https://github.com/sherifatia/AI-Agent-Studio"
    COMPANY: str = "AI Agent Studio"

    @property
    def window_title(self) -> str:
        """Return the title used for the main application window."""
        return f"{self.NAME} — v{self.VERSION}"

    @property
    def full_version_string(self) -> str:
        """Return version and build number combined, e.g. '0.1.0 (build 001)'."""
        return f"{self.VERSION} (build {self.BUILD_NUMBER})"


# Module-level singleton — the one instance every other module should import.
APP_INFO = AppInfo()
