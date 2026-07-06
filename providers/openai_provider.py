"""OpenAI provider — connects to the OpenAI Chat Completions API.

Uses the standard library ``urllib`` for HTTP so no extra dependency is
required.  The API key is read from the ``OPENAI_API_KEY`` environment
variable; it can also be passed explicitly to the constructor.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from core.logging_setup import get_logger
from core.response import Response
from providers.base_provider import BaseProvider

_logger = get_logger(__name__)

_ENV_KEY: str = "OPENAI_API_KEY"
_DEFAULT_MODEL: str = "gpt-3.5-turbo"
_DEFAULT_HOST: str = "https://api.openai.com"


class OpenAIProvider(BaseProvider):
    """Generates responses using the OpenAI Chat Completions API.

    Args:
        model:   Model name, e.g. ``"gpt-3.5-turbo"`` or ``"gpt-4"``.
        host:    Base URL of the OpenAI API.
        api_key: API key.  When ``None`` (default) reads from the
                 ``OPENAI_API_KEY`` environment variable.
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
                "OPENAI_API_KEY is not set — provider will fail at runtime."
            )

    def generate(self, messages: list[dict[str, str]]) -> Response:
        if not self.api_key:
            return Response(
                success=False,
                content="",
                provider=f"OpenAI ({self.model})",
            )

        url = f"{self.host}/v1/chat/completions"
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            _logger.warning("OpenAI HTTPError: %s", exc)
            return Response(
                success=False,
                content="",
                provider=f"OpenAI ({self.model})",
            )
        except Exception as exc:
            _logger.warning("OpenAI request failed: %s", exc)
            return Response(
                success=False,
                content="",
                provider=f"OpenAI ({self.model})",
            )

        try:
            content: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            _logger.warning("OpenAI unexpected response shape: %s", exc)
            return Response(
                success=False,
                content="",
                provider=f"OpenAI ({self.model})",
            )

        return Response(
            success=True,
            content=content,
            provider=f"OpenAI ({self.model})",
        )
