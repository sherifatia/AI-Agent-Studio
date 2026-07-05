"""Application entry point.

Boots through a ServiceLoader (see core/startup.py) before handing
control to the Qt event loop. Each startup service is a named, isolated
unit of work. New services (e.g. memory warmup, provider health checks)
can be registered here without touching core/startup.py.
"""

import sys
from typing import Any

from PySide6.QtWidgets import QApplication

from core.app_info import APP_INFO
from core.error_handler import install_global_exception_handler
from core.logging_setup import get_logger, setup_logging
from core.startup import ServiceLoader, StartupPhase
from ui.main_window import MainWindow
from ui.resource_manager import ResourceManager
from ui.theme_manager import ThemeManager

_logger = get_logger(__name__)


def _build_service_loader(context: dict[str, Any]) -> ServiceLoader:
    """Register every boot service and return the loader, not yet run.

    Args:
        context: Shared dict populated by each service. Later services
            may read values written by earlier ones.

    Returns:
        A ServiceLoader ready to have .run() called on it.
    """
    loader = ServiceLoader()

    def _start_logging() -> None:
        setup_logging()
        install_global_exception_handler()

    def _load_configuration() -> None:
        """Read config/settings.json — the only place that does so."""
        try:
            from config.settings import Settings
            settings = Settings()
            context["provider"] = settings.get("provider") or ""
            context["model"] = settings.get("model") or ""
        except Exception:
            _logger.warning(
                "Could not read config/settings.json — using defaults",
                exc_info=True,
            )
            context["provider"] = ""
            context["model"] = ""

    def _log_app_info() -> None:
        _logger.info("Starting %s", APP_INFO.full_version_string)

    def _load_resources() -> None:
        context["resource_manager"] = ResourceManager()

    def _start_engine() -> None:
        """Create the AIEngine and set the configured provider."""
        from core.engine import AIEngine
        from providers.provider_manager import ProviderManager

        engine = AIEngine()
        provider_name = context.get("provider", "ollama") or "ollama"

        try:
            provider = ProviderManager().create(provider_name)
            engine.set_provider(provider)
            _logger.info("Engine started with provider: %s", provider_name)
        except Exception:
            _logger.warning(
                "Could not activate provider '%s' at startup — "
                "engine has no active provider.",
                provider_name,
                exc_info=True,
            )

        context["engine"] = engine

    def _start_user_interface() -> None:
        app = QApplication(sys.argv)

        theme_manager = ThemeManager(context["resource_manager"])
        theme_manager.set_mode(theme_manager.current_mode, app=app)

        window = MainWindow(
            initial_provider=context.get("provider", ""),
            engine=context.get("engine"),
        )
        window.show()

        context["app"] = app
        context["window"] = window
        context["theme_manager"] = theme_manager

    def _mark_ready() -> None:
        _logger.info("Application ready")

    loader.register(StartupPhase.LOGGING,          _start_logging)
    loader.register(StartupPhase.CONFIGURATION,    _load_configuration)
    loader.register(StartupPhase.APPLICATION_INFO, _log_app_info)
    loader.register(StartupPhase.RESOURCES,        _load_resources)
    loader.register("engine",                      _start_engine)
    loader.register(StartupPhase.USER_INTERFACE,   _start_user_interface)
    loader.register(StartupPhase.READY,            _mark_ready)

    return loader


def main() -> None:
    """Run all startup services, then enter the Qt event loop."""
    context: dict[str, Any] = {}
    loader = _build_service_loader(context)
    loader.run()
    sys.exit(context["app"].exec())


if __name__ == "__main__":
    main()
