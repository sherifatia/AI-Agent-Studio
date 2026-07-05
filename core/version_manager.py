"""Version manager.

A thin service layer over `core.app_info.APP_INFO` for version-related
operations. Does not duplicate version/build values — it reads them from
`AppInfo`, the single source of truth, and adds behavior on top (today:
formatting; in the future: update checks).
"""

from core.app_info import APP_INFO
from core.logging_setup import get_logger

_logger = get_logger(__name__)


class VersionManager:
    """Exposes the current version/build and reserves future update checks."""

    def get_version(self) -> str:
        """Return the current semantic version, e.g. '0.1.0'."""
        return APP_INFO.VERSION

    def get_build_number(self) -> str:
        """Return the current build number, e.g. '001'."""
        return APP_INFO.BUILD_NUMBER

    def get_full_version_string(self) -> str:
        """Return version and build combined, e.g. '0.1.0 (build 001)'."""
        return APP_INFO.full_version_string

    def check_for_updates(self) -> None:
        """Reserved for future update-checking support.

        Not implemented in this Build — see
        docs/development/FUTURE_FEATURE_POLICY.md. Calling this today
        only logs that a check was requested.
        """
        _logger.info(
            "check_for_updates() called — update checking is not "
            "implemented yet (current version: %s)",
            self.get_full_version_string(),
        )
