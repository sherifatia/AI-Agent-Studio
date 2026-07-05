"""Dashboard page — session overview."""

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.app_info import APP_INFO
from core.logging_setup import get_logger

_logger = get_logger(__name__)


class DashboardPage(QWidget):
    """Shows session statistics and application overview.

    Args:
        memory: The ``MemoryManager`` instance.  ``None`` is safe.
        engine: The ``AIEngine`` instance (used to show active provider).
    """

    def __init__(
        self, memory: object = None, engine: object = None
    ) -> None:
        super().__init__()
        self._memory = memory
        self._engine = engine
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        root.addWidget(title)

        # App info box
        info_box = QGroupBox("Application")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel(f"<b>{APP_INFO.NAME}</b>"))
        info_layout.addWidget(QLabel(f"Version: {APP_INFO.full_version_string}"))
        info_layout.addWidget(
            QLabel(f"Author: {APP_INFO.AUTHOR}")
        )
        info_layout.addWidget(
            QLabel(f"Repository: {APP_INFO.REPOSITORY}")
        )
        root.addWidget(info_box)

        # Session stats box
        self._stats_box = QGroupBox("Session Statistics")
        stats_layout = QVBoxLayout(self._stats_box)
        self._turns_label = QLabel("Turns: --")
        stats_layout.addWidget(self._turns_label)
        self._failed_label = QLabel("Failed: --")
        stats_layout.addWidget(self._failed_label)
        self._duration_label = QLabel("Total duration: --")
        stats_layout.addWidget(self._duration_label)
        self._avg_label = QLabel("Avg response: --")
        stats_layout.addWidget(self._avg_label)
        self._provider_label = QLabel("Active provider: --")
        stats_layout.addWidget(self._provider_label)
        root.addWidget(self._stats_box)

        root.addStretch()

    def _refresh(self) -> None:
        # Session stats
        turns = "--"
        failed = "--"
        total_dur = "--"
        avg_dur = "--"
        provider = "--"

        if self._memory is not None:
            try:
                sess = self._memory.session
                turns = str(sess.total_turns)
                failed = str(sess.failed_turns)
                total_dur = f"{sess.total_duration:.2f}s"
                avg_dur = (
                    f"{sess.average_duration:.2f}s"
                    if sess.average_duration > 0
                    else "--"
                )
            except AttributeError:
                pass

        if self._engine is not None:
            try:
                p = self._engine.provider
                provider = type(p).__name__ if p else "None"
            except AttributeError:
                pass

        self._turns_label.setText(f"Turns: {turns}")
        self._failed_label.setText(f"Failed: {failed}")
        self._duration_label.setText(f"Total duration: {total_dur}")
        self._avg_label.setText(f"Avg response: {avg_dur}")
        self._provider_label.setText(f"Active provider: {provider}")

        _logger.debug("DashboardPage refreshed")
