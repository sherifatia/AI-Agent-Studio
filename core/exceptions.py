"""Application-specific exception types."""


class ProviderNotSelectedError(Exception):
    """Raised when ``AIEngine.ask()`` is called with no provider set."""


class UnknownProviderError(Exception):
    """Raised when ``ProviderManager.create()`` receives an unknown name."""
