"""Workflows page — view and manage multi-step agent workflows.

Displays registered workflow definitions and their steps.  The workflows
package is still under development (see ``docs/ROADMAP.md``); this page
shows a useful placeholder with information about the planned feature.
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


class WorkflowPage(QWidget):
    """Workflow management page.

    Currently shows registered workflows (if any exist) and a description
    of the planned automation system.  Will be expanded in a future Build
    to support editing, composing, and running workflows.

    Args:
        engine: Unused — reserved for future workflow execution.
    """

    def __init__(self, engine: object = None) -> None:
        super().__init__()
        self._engine = engine
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel("Workflows")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        root.addWidget(title)

        desc = QLabel(
            "Workflows let you compose multiple skills and provider calls "
            "into a single automated sequence.  This feature is under "
            "active development — registered workflows appear below once "
            "they exist."
        )
        desc.setWordWrap(True)
        root.addWidget(desc)

        box = QGroupBox("Registered Workflows")
        layout = QVBoxLayout(box)

        self._workflow_list = QListWidget()
        self._workflow_list.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )
        layout.addWidget(self._workflow_list)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status)

        root.addWidget(box, stretch=1)

    def _refresh(self) -> None:
        """Load workflow definitions from the ``workflows`` package."""
        self._workflow_list.clear()

        try:
            from workflows.engine import WorkflowEngine
            engine = WorkflowEngine()
            workflows = engine.list_workflows()
        except (ImportError, AttributeError):
            self._status.setText("Workflow engine not yet available.")
            return

        if workflows:
            for wf in workflows:
                item = QListWidgetItem(f"{wf.name} — {wf.description}")
                self._workflow_list.addItem(item)
            self._status.setText(f"{len(workflows)} workflow(s) registered.")
            _logger.debug("WorkflowPage: %d workflow(s)", len(workflows))
        else:
            self._workflow_list.addItem(
                "No workflows registered yet. "
                "Workflows will appear here once the system is implemented."
            )
            self._status.setText("No workflows registered.")
