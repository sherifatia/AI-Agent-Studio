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
        context: Shared dict that services populate. Downstream services
            may read values written by earlier ones (e.g. USER_INTERFACE
            reads the ResourceManager placed by RESOURCES).

    Returns:
        A ServiceLoader ready to have .run() called on it.
    """
    loader = ServiceLoader()

    def _start_logging() -> None:
        setup_logging()
        install_global_exception_handler()

    def _load_configuration() -> None:
        """Read config/settings.json and store relevant values in context.

        This is the only place that reads settings.json — downstream
        services and the MainWindow receive values from context rather
        than reading config directly.
        """
        try:
            from config.settings import Settings
            settings = Settings()
            context["provider"] = settings.get("provider") or ""
        except Exception:
            _logger.warning(
                "Could not read config/settings.json — using defaults",
                exc_info=True,
            )
            context["provider"] = ""

    def _log_app_info() -> None:
        _logger.info("Starting %s", APP_INFO.full_version_string)

    def _load_resources() -> None:
        context["resource_manager"] = ResourceManager()

    def _start_user_interface() -> None:
        app = QApplication(sys.argv)

        theme_manager = ThemeManager(context["resource_manager"])
        theme_manager.set_mode(theme_manager.current_mode, app=app)

        window = MainWindow(initial_provider=context.get("provider", ""))
        window.show()

        context["app"] = app
        context["window"] = window
        context["theme_manager"] = theme_manager

    def _mark_ready() -> None:
        _logger.info("Application ready")

    loader.register(StartupPhase.LOGGING, _start_logging)
    loader.register(StartupPhase.CONFIGURATION, _load_configuration)
    loader.register(StartupPhase.APPLICATION_INFO, _log_app_info)
    loader.register(StartupPhase.RESOURCES, _load_resources)
    loader.register(StartupPhase.USER_INTERFACE, _start_user_interface)
    loader.register(StartupPhase.READY, _mark_ready)

    return loader


def main() -> None:
    """Run all startup services, then enter the Qt event loop."""
    context: dict[str, Any] = {}

    loader = _build_service_loader(context)
    loader.run()

    sys.exit(context["app"].exec())


if __name__ == "__main__":
    main()
