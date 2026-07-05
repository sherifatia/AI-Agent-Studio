"""Application bootstrap.

Creates one ``Application`` instance, runs the ``ServiceLoader`` startup
sequence, then hands control to the Qt event loop.

``app.py`` is intentionally thin — no engine, provider, or settings logic
lives here.  All of that belongs to ``core.application.Application``.
"""

import sys
from typing import Any

from PySide6.QtWidgets import QApplication

from core.application import Application
from core.app_info import APP_INFO
from core.error_handler import install_global_exception_handler
from core.events import EventBus
from core.logging_setup import get_logger, setup_logging
from core.startup import ServiceLoader, StartupPhase
from ui.main_window import MainWindow
from ui.resource_manager import ResourceManager
from ui.theme_manager import ThemeManager

_logger = get_logger(__name__)


def _build_service_loader(
    app: Application,
    context: dict[str, Any],
) -> ServiceLoader:
    """Register boot services and return the loader, unrun.

    Args:
        app:     The single ``Application`` instance for this run.
        context: Shared dict for services to exchange Qt objects
                 (QApplication, MainWindow, ThemeManager).

    Returns:
        A ``ServiceLoader`` ready to call ``.run()``.
    """
    loader = ServiceLoader()

    def _start_logging() -> None:
        setup_logging()
        install_global_exception_handler()

    def _initialise_application() -> None:
        _logger.info("Starting %s", APP_INFO.full_version_string)
        app.initialise()

    def _initialise_event_bus() -> None:
        context["event_bus"] = EventBus()

    def _load_resources() -> None:
        context["resource_manager"] = ResourceManager()

    def _start_user_interface() -> None:
        qt_app = QApplication(sys.argv)

        theme_manager = ThemeManager(context["resource_manager"])
        theme_manager.set_mode(theme_manager.current_mode, app=qt_app)

        from core.runtime import Runtime, RuntimeContext
        runtime = Runtime(
            RuntimeContext(
                engine=app.engine,
                session=app.engine.session,
                event_bus=context["event_bus"],
            )
        )

        window = MainWindow(
            initial_provider=app.active_provider_name,
            engine=app.engine,
            memory=app.memory,
            skill_registry=app.skill_registry,
            settings=app.settings,
            event_bus=context["event_bus"],
            runtime=runtime,
        )
        window.show()

        context["qt_app"] = qt_app
        context["window"] = window
        context["theme_manager"] = theme_manager

    def _mark_ready() -> None:
        _logger.info("Application ready")

    loader.register(StartupPhase.LOGGING,          _start_logging)
    loader.register(StartupPhase.APPLICATION_INFO, _initialise_application)
    loader.register("event_bus",                   _initialise_event_bus)
    loader.register(StartupPhase.RESOURCES,        _load_resources)
    loader.register(StartupPhase.USER_INTERFACE,   _start_user_interface)
    loader.register(StartupPhase.READY,            _mark_ready)

    return loader


def main() -> None:
    """Entry point: bootstrap and run."""
    app = Application()
    context: dict[str, Any] = {}

    loader = _build_service_loader(app, context)
    loader.run()

    sys.exit(context["qt_app"].exec())


if __name__ == "__main__":
    main()
