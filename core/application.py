"""Application layer — central owner of all long-lived dependencies.

``Application`` is the single object that creates and holds ``Settings``,
``Session``, ``ProviderManager``, and ``AIEngine``.  ``app.py`` becomes a
thin bootstrap that creates one ``Application`` instance and hands it to
the Qt event loop.

No business logic lives here — ``Application`` is a *composition root*,
not a service.  It wires things together and exposes them so the UI and
startup sequence never have to construct engine or provider objects
themselves.
"""

from __future__ import annotations

from config.settings import Settings
from core.engine import AIEngine
from core.logging_setup import get_logger
from core.session import Session
from memory.manager import MemoryManager
from providers.provider_manager import ProviderManager
from skills.skill_manager import SkillLoader, SkillRegistry

_logger = get_logger(__name__)


class Application:
    """Composition root: owns Settings, Session, ProviderManager and AIEngine.

    Lifecycle
    ---------
    1. Create ``Application()``.
    2. Call ``initialise()`` once — reads settings, creates the engine,
       activates the configured provider.
    3. Pass ``self`` (or individual attributes) to the UI layer.

    The ``Session`` is never replaced after ``initialise()`` — switching
    providers only calls ``engine.set_provider()``, keeping session history
    intact.
    """

    def __init__(self) -> None:
        self.settings: Settings | None = None
        self.session: Session = Session()
        self.provider_manager: ProviderManager = ProviderManager()
        self.engine: AIEngine = AIEngine()
        self.memory: MemoryManager = MemoryManager()
        self.skill_registry: SkillRegistry = SkillRegistry()

        # Convenience properties populated by initialise()
        self.active_provider_name: str = ""
        self.active_model: str = ""
        self.active_host: str = ""

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def initialise(self) -> None:
        """Load configuration and wire the engine to the configured provider.

        Safe to call only once.  Subsequent calls are a no-op with a
        warning so that accidental double-initialisation does not silently
        reset provider state.
        """
        if self.engine.provider is not None:
            _logger.warning(
                "Application.initialise() called more than once — ignored"
            )
            return

        self._load_settings()
        self._start_engine()
        self._load_skills()
        _logger.info(
            "Application initialised — provider: %s, model: %s",
            self.active_provider_name,
            self.active_model,
        )

    def _load_settings(self) -> None:
        try:
            self.settings = Settings()
            self.active_provider_name = self.settings.get("provider") or "ollama"
            self.active_model = self.settings.get("model") or ""
            self.active_host = self.settings.get("host") or ""
        except Exception:
            _logger.warning(
                "Could not read config/settings.json — using defaults",
                exc_info=True,
            )
            self.active_provider_name = "ollama"
            self.active_model = ""
            self.active_host = ""

    def _start_engine(self) -> None:
        """Wire the engine to the provider named in settings.

        The engine's Session is *not* recreated here — it was created once
        in ``__init__`` and must survive the lifetime of the application.
        """
        try:
            provider = self.provider_manager.create(
                self.active_provider_name,
                model=self.active_model,
                host=self.active_host,
            )
            self.engine.set_provider(provider)
            _logger.info(
                "Engine wired to provider: %s", self.active_provider_name
            )
        except Exception:
            _logger.warning(
                "Could not activate provider '%s' — engine has no active "
                "provider until one is selected in the UI.",
                self.active_provider_name,
                exc_info=True,
            )

    # ------------------------------------------------------------------
    # Runtime helpers
    # ------------------------------------------------------------------

    def switch_provider(self, provider_name: str) -> None:
        """Replace the active provider without touching the Session.

        Args:
            provider_name: Internal provider name, e.g. ``"ollama"``.

        Raises:
            Exception: If the provider name is unknown or the provider
                raises on construction (e.g. TODO providers).
        """
        provider = self.provider_manager.create(provider_name)
        self.engine.set_provider(provider)
        self.active_provider_name = provider_name
        _logger.info("Provider switched to: %s", provider_name)

    def _load_skills(self) -> None:
        """Register the built-in demo skills into the skill registry."""
        from skills.builtin.current_time import CurrentTimeSkill
        from skills.builtin.calculator import CalculatorSkill

        loader = SkillLoader(self.skill_registry)
        loader.load([CurrentTimeSkill(), CalculatorSkill()])
        _logger.info(
            "Skills loaded: %s",
            [s.name for s in self.skill_registry.all_skills()],
        )
