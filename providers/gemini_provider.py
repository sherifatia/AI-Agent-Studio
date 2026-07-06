"""Gemini provider — connects to the Google Gemini API.

Uses the standard library ``urllib`` for HTTP so no extra dependency is
required.  The API key is read from the ``GEMINI_API_KEY`` environment
variable; it can also be passed explicitly to the constructor.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from core.logging_setup import get_logger
from core.response import Response
from providers.base_provider import BaseProvider

_logger = get_logger(__name__)

_ENV_KEY: str = "GEMINI_API_KEY"
_DEFAULT_MODEL: str = "gemini-1.5-flash"
_DEFAULT_HOST: str = "https://generativelanguage.googleapis.com"


class GeminiProvider(BaseProvider):
    """Generates responses using the Google Gemini API.

    Args:
        model:   Model name, e.g. ``"gemini-1.5-flash"`` or ``"gemini-pro"``.
        host:    Base URL of the Gemini API.
        api_key: API key.  When ``None`` (default) reads from the
                 ``GEMINI_API_KEY`` environment variable.
    """

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        host: str = _DEFAULT_HOST,
        api_key: str | None = None,
    ) -> None:
        self.model: str = model
        self.host: str = host.rstrip("/")
        self.api_key: str = api_key or os.environ.get(_ENV_KEY, "")

        if not self.api_key:
            _logger.warning(
                "GEMINI_API_KEY is not set — provider will fail at runtime."
            )

    def generate(self, messages: list[dict[str, str]]) -> Response:
        if not self.api_key:
            return Response(
                success=False,
                content="",
                provider=f"Gemini ({self.model})",
            )

        body = self._build_request_body(messages)
        url = (
            f"{self.host}/v1beta/models/{self.model}:generateContent"
            f"?key={urllib.parse.quote(self.api_key)}"
        )
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            _logger.warning("Gemini HTTPError: %s", exc)
            return Response(
                success=False,
                content="",
                provider=f"Gemini ({self.model})",
            )
        except Exception as exc:
            _logger.warning("Gemini request failed: %s", exc)
            return Response(
                success=False,
                content="",
                provider=f"Gemini ({self.model})",
            )

        try:
            content: str = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            _logger.warning("Gemini unexpected response shape: %s", exc)
            return Response(
                success=False,
                content="",
                provider=f"Gemini ({self.model})",
            )

        return Response(
            success=True,
            content=content,
            provider=f"Gemini ({self.model})",
        )

    @staticmethod
    def _build_request_body(
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Convert an OpenAI-format message list to the Gemini request shape.

        Args:
            messages: List of ``{"role": ..., "content": ...}`` dicts.

        Returns:
            A dict ready to serialise as the Gemini API JSON body.
        """
        system_instruction: str | None = None
        contents: list[dict[str, Any]] = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
                continue

            gemini_role = "model" if role == "assistant" else "user"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}],
            })

        body: dict[str, Any] = {
            "contents": contents,
        }
        if system_instruction is not None:
            body["system_instruction"] = {
                "parts": [{"text": system_instruction}],
            }
        return body
