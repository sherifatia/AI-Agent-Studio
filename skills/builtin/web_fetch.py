"""Built-in skill: web page fetching via BrowserManager.

Allows the Agent to fetch web page content by URL through the
``/fetch`` command in Chat.
"""

from __future__ import annotations

from browser.browser_manager import BrowserManager
from skills.skill import BaseSkill, SkillResult


class WebFetchSkill(BaseSkill):
    """Fetch a web page and return its readable text content.

    Usage: ``/fetch <url>``
    """

    @property
    def name(self) -> str:
        return "web_fetch"

    @property
    def description(self) -> str:
        return "Fetch a web page and return its readable text. Usage: /fetch <url>"

    def execute(self, input: str) -> SkillResult:
        url = input.strip()
        if not url:
            return SkillResult(
                success=False,
                output="",
                error="No URL provided. Usage: /fetch <url>",
            )

        browser = BrowserManager()
        page = browser.fetch(url)

        if page.error:
            return SkillResult(
                success=False,
                output="",
                error=page.error,
            )

        # Format a concise summary
        lines = [
            f"Title: {page.title}",
            f"URL: {page.url}",
            "",
            page.text[:2000],  # limit output length
        ]
        if len(page.text) > 2000:
            lines.append("\n… (content truncated)")

        return SkillResult(
            success=True,
            output="\n".join(lines),
        )
