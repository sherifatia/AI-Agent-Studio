"""Workflows page — view and manage multi-step agent workflows.

Displays registered workflow definitions and their steps.  Reads from
the ``WorkflowEngine`` to show available workflows and their metadata.
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
from workflows.engine import WorkflowEngine

_logger = get_logger(__name__)


class WorkflowPage(QWidget):
    """Workflow management page.

    Shows registered workflows from the ``WorkflowEngine``.  Will be
    expanded in a future Build to support editing, composing, and
    running workflows.

    Args:
        engine: Unused — reserved for future workflow execution.
    """

    def __init__(
        self, engine: object = None,
        workflow_engine: object = None,
    ) -> None:
        super().__init__()
        self._engine = engine
        self._wf_engine = workflow_engine or WorkflowEngine()
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
            "into a single automated sequence.  Each workflow runs its "
            "steps in order, passing the output of each step to the next."
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
        """Load workflow definitions from the ``WorkflowEngine``."""
        self._workflow_list.clear()

        workflows = self._wf_engine.list_workflows()

        if workflows:
            for wf in workflows:
                step_count = len(wf.steps)
                item_text = (
                    f"<b>{wf.name}</b> — {wf.description} "
                    f"({step_count} step{'s' if step_count != 1 else ''})"
                )
                item = QListWidgetItem(item_text)
                self._workflow_list.addItem(item)
            self._status.setText(
                f"{len(workflows)} workflow(s) registered."
            )
            _logger.debug(
                "WorkflowPage: %d workflow(s)", len(workflows)
            )
        else:
            self._workflow_list.addItem(
                "No workflows registered yet. "
                "Workflows will appear here once defined."
            )
            self._status.setText("No workflows registered.")
