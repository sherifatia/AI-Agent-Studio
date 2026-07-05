"""Skills page — lists registered agent skills."""

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.logging_setup import get_logger

_logger = get_logger(__name__)


class SkillsPage(QWidget):
    """Displays every registered skill with its name and description.

    Args:
        skill_registry: The ``SkillRegistry`` instance.  ``None`` is safe
                        — the page shows an appropriate message.
    """

    def __init__(self, skill_registry: object = None) -> None:
        super().__init__()
        self._registry = skill_registry
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel("Skills")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        root.addWidget(title)

        desc = QLabel(
            "Skills are discrete capabilities the Agent can invoke "
            "instead of calling the LLM.  Type <b>/skillname</b> in "
            "Chat to trigger one."
        )
        desc.setWordWrap(True)
        root.addWidget(desc)

        box = QGroupBox("Registered Skills")
        layout = QVBoxLayout(box)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        layout.addWidget(self._list)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status)

        root.addWidget(box, stretch=1)

    def _refresh(self) -> None:
        self._list.clear()

        if self._registry is None:
            self._status.setText("No skill registry available.")
            return

        try:
            skills = self._registry.all_skills()
        except AttributeError:
            self._status.setText("Skill registry does not support listing.")
            return

        if not skills:
            self._status.setText("No skills registered.")
            return

        for s in skills:
            item_text = f"<b>{s.name}</b> — {s.description}"
            item = QListWidgetItem(item_text)
            self._list.addItem(item)

        self._status.setText(f"{len(skills)} skill(s) registered.")
        _logger.debug("SkillsPage: displayed %d skill(s)", len(skills))
