"""Memory page — browse conversation history and session statistics.

Displays conversation turns and session-level stats (total turns,
failures, duration).  Reads from the ``MemoryManager`` passed in at
construction time; shows a descriptive message when no memory manager
is available.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.logging_setup import get_logger

_logger = get_logger(__name__)


class MemoryPage(QWidget):
    """Conversation history and session statistics page.

    Args:
        memory: The ``MemoryManager`` instance.  ``None`` is safe.
    """

    def __init__(self, memory: object = None) -> None:
        super().__init__()
        self._memory = memory
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        # --- Left: conversation history ---
        left_box = QGroupBox("Conversation History")
        left_layout = QVBoxLayout(left_box)

        self._conv_list = QListWidget()
        self._conv_list.setWordWrap(True)
        self._conv_list.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )
        left_layout.addWidget(self._conv_list)

        root.addWidget(left_box, stretch=2)

        # --- Right: session stats ---
        right_box = QGroupBox("Session Statistics")
        right_layout = QVBoxLayout(right_box)

        self._turns_label = QLabel("Total turns: --")
        right_layout.addWidget(self._turns_label)
        self._failed_label = QLabel("Failed: --")
        right_layout.addWidget(self._failed_label)
        self._duration_label = QLabel("Total duration: --")
        right_layout.addWidget(self._duration_label)
        self._avg_label = QLabel("Avg response: --")
        right_layout.addWidget(self._avg_label)

        right_layout.addStretch()

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._refresh)
        right_layout.addWidget(self._refresh_btn)

        root.addWidget(right_box, stretch=1)

    def _refresh(self) -> None:
        """Reload conversation history and stats from the memory manager."""
        self._conv_list.clear()

        if self._memory is None:
            self._conv_list.addItem("No memory manager available.")
            self._turns_label.setText("Total turns: --")
            self._failed_label.setText("Failed: --")
            self._duration_label.setText("Total duration: --")
            self._avg_label.setText("Avg response: --")
            return

        # --- Conversation turns ---
        try:
            entries = self._memory.conversation.history
            if entries:
                for entry in entries:
                    text = (
                        f"User: {entry.user_input}\n"
                        f"Agent: {entry.agent_response[:120]}"
                        f"{'…' if len(entry.agent_response) > 120 else ''}"
                    )
                    item = QListWidgetItem(text)
                    self._conv_list.addItem(item)
            else:
                self._conv_list.addItem("No conversation history yet.")
        except AttributeError:
            self._conv_list.addItem("Conversation history unavailable.")

        # --- Session statistics ---
        try:
            sess = self._memory.session
            self._turns_label.setText(f"Total turns: {sess.total_turns}")
            self._failed_label.setText(f"Failed: {sess.failed_turns}")
            self._duration_label.setText(
                f"Total duration: {sess.total_duration:.2f}s"
            )
            avg = (
                f"{sess.average_duration:.2f}s"
                if sess.average_duration > 0
                else "--"
            )
            self._avg_label.setText(f"Avg response: {avg}")
        except AttributeError:
            pass

        _logger.debug("MemoryPage refreshed")
