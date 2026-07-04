"""OpenAI provider — TODO, not yet implemented.

See docs/ROADMAP.md ("Additional Providers") for scope. This stub exists
so that `providers.provider_manager.ProviderManager` can resolve the
provider name without a runtime import error; it does not perform any
request-building or API calls yet.
"""

from core.response import Response
from providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """TODO provider: OpenAI is not implemented yet.

    Calling `generate()` raises `NotImplementedError`. Do not add
    partial request-building logic here ahead of a real implementation —
    see docs/CODING_STANDARD.md ("Provider Contract").
    """

    def generate(self, messages: list[dict[str, str]]) -> Response:
        """Not implemented.

        Args:
            messages: A list of chat messages (unused — not implemented).

        Raises:
            NotImplementedError: Always. OpenAI support is planned but
                not yet built.
        """
        raise NotImplementedError()
