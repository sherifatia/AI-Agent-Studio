"""Application entry point.

Boots through a single, ordered startup sequence (see `core/startup.py`)
before handing control to the Qt event loop.
"""

import sys
from typing import Any

from PySide6.QtWidgets import QApplication

from core.app_info import APP_INFO
from core.error_handler import install_global_exception_handler
from core.logging_setup import get_logger, setup_logging
from core.startup import StartupPhase, StartupSequence
from ui.main_window import MainWindow
from ui.resource_manager import ResourceManager
from ui.theme_manager import ThemeManager

_logger = get_logger(__name__)


def _build_startup_sequence(context: dict[str, Any]) -> StartupSequence:
    """Register every boot phase and return the sequence, unrun.

    Args:
        context: A shared dict that phase actions populate (the running
            `QApplication` and `MainWindow`, once created).

    Returns:
        A `StartupSequence` ready to have `.run()` called on it.
    """
    sequence = StartupSequence()

    def _init_logging() -> None:
        setup_logging()
        install_global_exception_handler()

    def _init_configuration() -> None:
        # Reserved: this is where future global configuration loading
        # will run. Per-window settings (active provider, etc.) are
        # currently loaded defensively inside MainWindow itself — see
        # ui/main_window.py's _load_status_from_settings().
        _logger.info("No global configuration load required yet")

    def _init_application_info() -> None:
        _logger.info("Starting %s", APP_INFO.full_version_string)

    def _init_resources() -> None:
        context["resource_manager"] = ResourceManager()

    def _init_user_interface() -> None:
        app = QApplication(sys.argv)

        theme_manager = ThemeManager(context["resource_manager"])
        theme_manager.set_mode(theme_manager.current_mode, app=app)

        window = MainWindow()
        window.show()

        context["app"] = app
        context["window"] = window
        context["theme_manager"] = theme_manager

    def _mark_ready() -> None:
        _logger.info("Application ready")

    sequence.register_phase(StartupPhase.LOGGING, _init_logging)
    sequence.register_phase(StartupPhase.CONFIGURATION, _init_configuration)
    sequence.register_phase(StartupPhase.APPLICATION_INFO, _init_application_info)
    sequence.register_phase(StartupPhase.RESOURCES, _init_resources)
    sequence.register_phase(StartupPhase.USER_INTERFACE, _init_user_interface)
    sequence.register_phase(StartupPhase.READY, _mark_ready)

    return sequence


def main() -> None:
    """Run the startup sequence, then the Qt event loop."""
    context: dict[str, Any] = {}

    sequence = _build_startup_sequence(context)
    sequence.run()

    sys.exit(context["app"].exec())


if __name__ == "__main__":
    main()
