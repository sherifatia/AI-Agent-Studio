"""Browser page — fetch and display web page content.

Provides a simple web-fetching interface: enter a URL, click Fetch,
and view the page content as clean, readable text.  HTTP requests run
in a background ``QThread`` to keep the UI responsive.
"""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from browser.browser_manager import BrowserManager
from core.logging_setup import get_logger

_logger = get_logger(__name__)


class _FetchWorker(QThread):
    """Fetches a URL in a background thread and emits the result."""

    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, url: str, timeout: int = 30) -> None:
        super().__init__()
        self._url = url
        self._timeout = timeout
        self._browser = BrowserManager()

    def run(self) -> None:
        page = self._browser.fetch(self._url, timeout=self._timeout)
        if page.error:
            self.failed.emit(page.error)
        else:
            output = f"Title: {page.title}\nURL: {page.url}\n\n{page.text}"
            self.finished.emit(output)


class BrowserPage(QWidget):
    """Web page fetcher interface.

    Args:
        engine: Unused — reserved for future browser automation.
    """

    def __init__(self, engine: object = None) -> None:
        super().__init__()
        self._engine = engine
        self._worker: _FetchWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel("Browser")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        root.addWidget(title)

        desc = QLabel(
            "Fetch a web page and view its content as plain text. "
            "You can also use ``/fetch <url>`` in Chat."
        )
        desc.setWordWrap(True)
        root.addWidget(desc)

        nav = QHBoxLayout()
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://example.com")
        self._url_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._url_input.returnPressed.connect(self._fetch)
        nav.addWidget(self._url_input)

        self._fetch_btn = QPushButton("Fetch")
        self._fetch_btn.setFixedWidth(80)
        self._fetch_btn.clicked.connect(self._fetch)
        nav.addWidget(self._fetch_btn)
        root.addLayout(nav)

        self._content = QPlainTextEdit()
        self._content.setReadOnly(True)
        self._content.setPlaceholderText("Fetched content appears here…")
        root.addWidget(self._content, stretch=1)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #888; font-size: 12px;")
        root.addWidget(self._status)

    def _fetch(self) -> None:
        url = self._url_input.text().strip()
        if not url:
            return

        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self._url_input.setText(url)

        self._fetch_btn.setEnabled(False)
        self._content.setPlainText("Fetching…")
        self._status.setText(f"Fetching {url} …")

        self._worker = _FetchWorker(url)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()
        _logger.debug("BrowserPage: fetching %s", url)

    def _on_finished(self, content: str) -> None:
        self._content.setPlainText(content)
        self._status.setText(f"Done — {len(content)} characters")
        self._fetch_btn.setEnabled(True)
        self._worker = None

    def _on_failed(self, error: str) -> None:
        self._content.setPlainText("")
        self._status.setText(f"Error: {error}")
        self._status.setStyleSheet("color: #f48771; font-size: 12px;")
        self._fetch_btn.setEnabled(True)
        self._worker = None
        _logger.warning("BrowserPage fetch failed: %s", error)
