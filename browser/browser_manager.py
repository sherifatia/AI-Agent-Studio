"""Browser automation manager — fetch, parse, and search web content.

Provides a ``BrowserManager`` that the Agent can invoke (typically via a
skill) to retrieve web page content, extract readable text, and search
within fetched pages.  All HTTP is handled by the standard library
``urllib``; HTML is parsed with ``html.parser`` — no extra dependencies.
"""

from __future__ import annotations

import html.parser
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from core.logging_setup import get_logger

_logger = get_logger(__name__)

# Default user-agent header sent with all requests.
_USER_AGENT: str = "AI-Agent-Studio-Browser/1.0"

# Maximum number of bytes to read from a single page.
_MAX_CONTENT_BYTES: int = 2 * 1024 * 1024  # 2 MB


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass
class PageResult:
    """The result of fetching and parsing a web page.

    Attributes:
        url:         The URL that was fetched (may differ from the
                     requested URL after redirects).
        title:       The page's ``<title>`` text, or empty string.
        text:        Clean, readable text extracted from the HTML body.
        raw_html:    The full raw HTML (truncated to ``_MAX_CONTENT_BYTES``).
        http_status: HTTP status code (200 on success).
        error:       Human-readable error on failure (empty on success).
    """

    url: str
    title: str = ""
    text: str = ""
    raw_html: str = ""
    http_status: int = 200
    error: str = ""


# ---------------------------------------------------------------------------
# HTML -> text extraction (stdlib only)
# ---------------------------------------------------------------------------


class _HTMLToTextParser(html.parser.HTMLParser):
    """Strip HTML tags and extract readable text content."""

    def __init__(self) -> None:
        super().__init__()
        self._result: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"style", "script", "noscript"}:
            self._skip = True
        if tag in {"p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"}:
            self._result.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "script", "noscript"}:
            self._skip = False
        if tag in {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"}:
            self._result.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._result.append(data)

    def text(self) -> str:
        raw = "".join(self._result)
        # Collapse multiple blank lines into one.
        return re.sub(r"\n{3,}", "\n\n", raw).strip()


# ---------------------------------------------------------------------------
# Browser Manager
# ---------------------------------------------------------------------------


class BrowserManager:
    """Fetch web pages and extract readable content.

    Usage::

        browser = BrowserManager()
        page = browser.fetch("https://example.com")
        print(page.title, page.text[:500])
    """

    def __init__(self, user_agent: str = _USER_AGENT) -> None:
        self._user_agent = user_agent

    def fetch(
        self,
        url: str,
        timeout: int = 30,
    ) -> PageResult:
        """Fetch a URL and extract readable text content.

        Args:
            url:     The URL to fetch.  If no scheme is given, ``https://``
                     is prepended.
            timeout: Request timeout in seconds.

        Returns:
            A ``PageResult`` with extracted title and text.
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        req = urllib.request.Request(
            url,
            headers={"User-Agent": self._user_agent},
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(_MAX_CONTENT_BYTES)
                http_status = resp.status
                final_url = resp.url
        except urllib.error.HTTPError as exc:
            _logger.warning("BrowserManager HTTPError: %s", exc)
            return PageResult(
                url=url,
                error=f"HTTP {exc.code}: {exc.reason}",
                http_status=exc.code,
            )
        except urllib.error.URLError as exc:
            _logger.warning("BrowserManager URLError: %s", exc)
            return PageResult(
                url=url,
                error=f"URL error: {exc.reason}",
            )
        except Exception as exc:
            _logger.warning("BrowserManager fetch failed: %s", exc)
            return PageResult(
                url=url,
                error=str(exc),
            )

        # Decode with charset detection.
        content_type = resp.headers.get("Content-Type", "")
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].split(";")[0].strip()
        raw_html = raw.decode(charset, errors="replace")

        # Extract title
        title = ""
        title_match = re.search(
            r"<title[^>]*>(.*?)</title>", raw_html, re.IGNORECASE | re.DOTALL
        )
        if title_match:
            title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()

        # Extract readable text
        parser = _HTMLToTextParser()
        try:
            parser.feed(raw_html)
        except Exception:
            pass
        text = parser.text()

        _logger.debug(
            "BrowserManager fetched %s (%d chars text, %d KB raw)",
            final_url,
            len(text),
            len(raw_html) // 1024,
        )

        return PageResult(
            url=final_url,
            title=title,
            text=text,
            raw_html=raw_html[:50000],  # keep only first 50 KB
            http_status=http_status,
        )
