"""Chat page — the primary conversational interface.

Workflow::

    User types input and clicks Send (or presses Enter)
            ↓
    ChatPage builds a Task (input + current history)
            ↓
    Agent.run(task)
            ↓
    AIEngine.ask(messages)
            ↓
    Provider.generate(messages)
            ↓
    TaskResult returned synchronously
            ↓
    ChatPage appends both turns to the conversation view

Rules:
- ChatPage never calls engine or provider directly.
- ChatPage never writes to memory directly (Memory layer — Build 009).
- No threading, no asyncio, no streaming.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.agent import Agent
from core.logging_setup import get_logger
from core.task import Task

_logger = get_logger(__name__)

_ROLE_PREFIX: dict[str, str] = {
    "user":      "You:   ",
    "assistant": "Agent: ",
    "system":    "System:",
    "error":     "Error: ",
}


class ChatPage(QWidget):
    """Conversational UI page.

    Args:
        agent: The shared ``Agent`` instance.  ``ChatPage`` only calls
               ``agent.run(task)``; it never touches the engine directly.
    """

    def __init__(self, agent: Agent) -> None:
        super().__init__()
        self._agent = agent
        self._history: list[dict[str, str]] = []
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # Title bar
        title_row = QHBoxLayout()
        title = QLabel("Chat")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        title_row.addWidget(title)
        title_row.addStretch()
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setFixedWidth(70)
        self._clear_btn.clicked.connect(self._clear_conversation)
        title_row.addWidget(self._clear_btn)
        root.addLayout(title_row)

        # Conversation view
        self._conversation = QListWidget()
        self._conversation.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self._conversation.setWordWrap(True)
        self._conversation.setSpacing(4)
        root.addWidget(self._conversation, stretch=1)

        # Status line
        self._status = QLabel("Ready")
        self._status.setStyleSheet("color: #888; font-size: 12px;")
        root.addWidget(self._status)

        # Input row
        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a message and press Enter…")
        self._input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._input.returnPressed.connect(self._send)
        input_row.addWidget(self._input)

        self._send_btn = QPushButton("Send")
        self._send_btn.setFixedWidth(70)
        self._send_btn.clicked.connect(self._send)
        input_row.addWidget(self._send_btn)

        root.addLayout(input_row)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _send(self) -> None:
        """Read the input, run the Agent, display the result."""
        user_text = self._input.text().strip()
        if not user_text:
            return

        self._input.clear()
        self._input.setEnabled(False)
        self._send_btn.setEnabled(False)
        self._set_status("Thinking…")

        # Display the user turn immediately
        self._append_message("user", user_text)

        # Build and execute the task synchronously
        task = Task(input=user_text, history=list(self._history))
        result = self._agent.run(task)

        if result.success:
            self._history.append({"role": "user",      "content": user_text})
            self._history.append({"role": "assistant", "content": result.response})
            self._append_message("assistant", result.response)
            provider = result.metadata.get("provider", "")
            timing = f"{result.duration:.2f}s"
            self._set_status(
                f"Done — {provider} — {timing}" if provider else f"Done — {timing}"
            )
            _logger.debug("Chat turn complete in %s via %s", timing, provider)
        else:
            self._append_message("error", result.error)
            self._set_status(f"Error: {result.error}")
            _logger.warning("Chat task failed: %s", result.error)

        self._input.setEnabled(True)
        self._send_btn.setEnabled(True)
        self._input.setFocus()
        self._scroll_to_bottom()

    def _clear_conversation(self) -> None:
        """Remove all messages from the view and reset history."""
        self._conversation.clear()
        self._history.clear()
        self._set_status("Conversation cleared")
        _logger.debug("Chat conversation cleared")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _append_message(self, role: str, text: str) -> None:
        prefix = _ROLE_PREFIX.get(role, f"{role}: ")
        item = QListWidgetItem(f"{prefix}{text}")

        if role == "user":
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        elif role == "error":
            item.setForeground(Qt.GlobalColor.red)

        self._conversation.addItem(item)

    def _scroll_to_bottom(self) -> None:
        self._conversation.scrollToBottom()

    def _set_status(self, message: str) -> None:
        self._status.setText(message)
