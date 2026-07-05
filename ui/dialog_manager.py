"""Dialog manager foundation.

Centralizes how the application shows dialogs, so future Builds add new
dialogs here rather than constructing `QMessageBox`/`QDialog` instances
ad hoc throughout the UI layer.

- `show_about()` is fully functional — it has no dependency on any
  unimplemented feature, so it is built for real rather than stubbed.
- `show_settings()` is a placeholder: the Settings page itself
  (`ui/widgets/settings_page.py`) is not implemented yet, so this shows an
  honest "not available yet" message rather than a fake settings UI.
- `confirm()` is generic, reusable infrastructure for any future
  confirmation prompt (e.g. "discard unsaved changes?").
"""

from PySide6.QtWidgets import QMessageBox, QWidget

from core.app_info import APP_INFO
from core.logging_setup import get_logger

_logger = get_logger(__name__)


class DialogManager:
    """Centralized entry point for showing application dialogs."""

    def show_about(self, parent: QWidget | None = None) -> None:
        """Show the About dialog with centralized application metadata.

        Args:
            parent: The parent widget the dialog is shown relative to.
        """
        _logger.debug("Showing About dialog")

        QMessageBox.about(
            parent,
            f"About {APP_INFO.NAME}",
            (
                f"<b>{APP_INFO.NAME}</b><br>"
                f"Version {APP_INFO.full_version_string}<br><br>"
                f"Author: {APP_INFO.AUTHOR}<br>"
                f"Company: {APP_INFO.COMPANY}<br>"
                f"Repository: {APP_INFO.REPOSITORY}"
            ),
        )

    def show_settings(self, parent: QWidget | None = None) -> None:
        """Show the Settings dialog.

        Args:
            parent: The parent widget the dialog is shown relative to.

        Note:
            Placeholder — `ui/widgets/settings_page.py` has no
            implementation yet. This shows an honest "not available yet"
            message instead of a non-functional settings UI. See
            docs/development/FUTURE_FEATURE_POLICY.md.
        """
        _logger.debug("Showing Settings dialog (placeholder)")

        QMessageBox.information(
            parent,
            "Settings",
            "Settings are not implemented yet in this Build.",
        )

    def confirm(
        self, parent: QWidget | None, title: str, message: str
    ) -> bool:
        """Show a Yes/No confirmation dialog.

        Args:
            parent: The parent widget the dialog is shown relative to.
            title: The dialog's title bar text.
            message: The question being asked.

        Returns:
            `True` if the user chose Yes, `False` otherwise.
        """
        result = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes
