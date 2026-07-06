"""Models Management page.

Allows the user to view available providers, select and activate a
provider, test the connection, and (for Ollama) see the list of locally
installed models.

This page communicates state changes back to the main window via Qt
signals rather than holding references to other top-level components.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.logging_setup import get_logger
from providers.provider_manager import ProviderManager

_logger = get_logger(__name__)

# All known provider names, in display order.
_PROVIDERS: list[str] = ["ollama", "openai", "gemini", "openrouter"]

# Maps internal name to readable label.
_PROVIDER_LABELS: dict[str, str] = {
    "ollama":      "Ollama  (local)",
    "openai":      "OpenAI  (API key required)",
    "gemini":      "Gemini  (API key required)",
    "openrouter":  "OpenRouter  (API key required)",
}

# Environment variable hints per provider.
_ENV_HINTS: dict[str, str] = {
    "ollama":      "",
    "openai":      "Set OPENAI_API_KEY",
    "gemini":      "Set GEMINI_API_KEY",
    "openrouter":  "Set OPENROUTER_API_KEY",
}


class ModelsPage(QWidget):
    """Provider and model management workspace page.

    Signals:
        provider_changed: Emitted with the new provider name when the
            active provider is successfully changed. MainWindow connects
            this to StatusBar.set_provider().
    """

    provider_changed = Signal(str)

    def __init__(self, engine: object) -> None:
        """Create the models page.

        Args:
            engine: The running AIEngine instance. Typed as object to
                avoid a circular import at module level; the page calls
                engine.set_provider() and reads engine.provider.
        """
        super().__init__()
        self._engine = engine
        self._provider_manager = ProviderManager()
        self._build_ui()
        self._refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)
        root.addWidget(self._build_provider_panel(), stretch=1)
        root.addWidget(self._build_model_panel(), stretch=2)

    def _build_provider_panel(self) -> QGroupBox:
        box = QGroupBox("Provider")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        self._current_provider_label = QLabel("Active: --")
        self._current_provider_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._current_provider_label)

        self._provider_list = QListWidget()
        self._provider_list.setMaximumHeight(200)
        for name in _PROVIDERS:
            item = QListWidgetItem(_PROVIDER_LABELS[name])
            item.setData(256, name)
            self._provider_list.addItem(item)
        self._provider_list.currentItemChanged.connect(
            self._on_provider_selection_changed
        )
        layout.addWidget(self._provider_list)

        self._set_provider_btn = QPushButton("Set Active Provider")
        self._set_provider_btn.setEnabled(False)
        self._set_provider_btn.clicked.connect(self._set_active_provider)
        layout.addWidget(self._set_provider_btn)

        self._test_btn = QPushButton("Test Connection")
        self._test_btn.clicked.connect(self._test_connection)
        layout.addWidget(self._test_btn)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._refresh)
        layout.addWidget(self._refresh_btn)

        layout.addStretch()

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        return box

    def _build_model_panel(self) -> QGroupBox:
        box = QGroupBox("Models")
        layout = QVBoxLayout(box)

        self._models_info_label = QLabel("Select a provider to see its models.")
        layout.addWidget(self._models_info_label)

        self._model_list = QListWidget()
        layout.addWidget(self._model_list)

        return box

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_provider_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self._set_provider_btn.setEnabled(current is not None)
        if current is not None:
            self._load_models_for(current.data(256))

    def _set_active_provider(self) -> None:
        """Instantiate the selected provider and pass it to the engine."""
        item = self._provider_list.currentItem()
        if item is None:
            return

        name: str = item.data(256)

        try:
            provider = self._provider_manager.create(name)
            self._engine.set_provider(provider)

            display = _PROVIDER_LABELS.get(name, name)
            self._current_provider_label.setText(f"Active: {display}")
            self._set_status(f"Provider set to: {name}", ok=True)
            self.provider_changed.emit(name)
            _logger.info("Active provider changed to: %s", name)
            self._load_models_for(name)

        except NotImplementedError:
            self._set_status(
                f"{name} is not fully implemented yet.",
                ok=False,
            )
            _logger.warning("Cannot activate TODO provider: %s", name)

        except Exception as exc:
            self._set_status(f"Error: {exc}", ok=False)
            _logger.exception("Failed to set provider: %s", name)

    def _test_connection(self) -> None:
        """Test connectivity to the currently active provider."""
        provider = getattr(self._engine, "provider", None)
        if provider is None:
            self._set_status("No active provider. Set one first.", ok=False)
            return

        try:
            from providers.ollama_provider import OllamaProvider
            if isinstance(provider, OllamaProvider):
                provider.client.list()
                self._set_status("Ollama: Connected", ok=True)
                _logger.info("Ollama connection test: OK")
            else:
                # Other providers: try a minimal generate call.
                result = provider.generate(
                    [{"role": "user", "content": "test"}]
                )
                if result.success:
                    self._set_status("Connected — response received", ok=True)
                else:
                    hint = _ENV_HINTS.get(
                        type(provider).__name__
                        .replace("Provider", "")
                        .lower(),
                        "",
                    )
                    msg = f"Connection failed. {hint}" if hint else "Connection failed."
                    self._set_status(msg, ok=False)

        except NotImplementedError:
            self._set_status("Provider not implemented yet.", ok=False)

        except Exception as exc:
            self._set_status(f"Connection failed: {exc}", ok=False)
            _logger.warning("Connection test failed: %s", exc)

    def _refresh(self) -> None:
        """Reload current provider state and model list."""
        provider = getattr(self._engine, "provider", None)

        if provider is None:
            self._current_provider_label.setText("Active: --")
            self._model_list.clear()
            self._models_info_label.setText("No active provider.")
            return

        try:
            from providers.ollama_provider import OllamaProvider
            if isinstance(provider, OllamaProvider):
                self._current_provider_label.setText("Active: Ollama (local)")
                self._highlight_active_provider("ollama")
                self._load_models_for("ollama")
                return
        except Exception:
            pass

        # Fallback for any other active provider type.
        type_name = type(provider).__name__.replace("Provider", "").lower()
        self._current_provider_label.setText(f"Active: {_PROVIDER_LABELS.get(type_name, type_name)}")
        self._highlight_active_provider(type_name)
        self._load_models_for(type_name)

    def _load_models_for(self, provider_name: str) -> None:
        """Populate the model list for the given provider.

        For Ollama: queries the local server for installed models.
        For all other providers: shows a 'not available' message.

        Args:
            provider_name: Internal provider name, e.g. "ollama".
        """
        self._model_list.clear()

        if provider_name == "ollama":
            self._load_ollama_models()
        else:
            self._models_info_label.setText(
                f"Model listing is not available for {provider_name}."
            )

    def _load_ollama_models(self) -> None:
        """Query and display Ollama's locally installed models."""
        provider = getattr(self._engine, "provider", None)

        try:
            from providers.ollama_provider import OllamaProvider
            if isinstance(provider, OllamaProvider):
                result = provider.client.list()
            else:
                from ollama import Client
                result = Client(host="http://localhost:11434").list()

            if hasattr(result, "models"):
                models = [
                    getattr(m, "model", None) or getattr(m, "name", str(m))
                    for m in result.models
                ]
            else:
                models = [
                    m.get("model") or m.get("name", str(m))
                    for m in result.get("models", [])
                ]

            if models:
                for model_name in models:
                    self._model_list.addItem(str(model_name))
                self._models_info_label.setText(
                    f"{len(models)} model(s) installed:"
                )
            else:
                self._models_info_info_label.setText(
                    "No models installed. Run: ollama pull <model>"
                )

            _logger.info("Listed %d Ollama model(s)", len(models))

        except Exception as exc:
            self._models_info_label.setText("Could not reach Ollama server.")
            self._model_list.addItem(f"Error: {exc}")
            _logger.warning("Failed to list Ollama models: %s", exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _highlight_active_provider(self, provider_name: str) -> None:
        for i in range(self._provider_list.count()):
            item = self._provider_list.item(i)
            if item and item.data(256) == provider_name:
                self._provider_list.setCurrentItem(item)
                return

    def _set_status(self, message: str, *, ok: bool) -> None:
        self._status_label.setText(message)
        colour = "#4ec9b0" if ok else "#f48771"
        self._status_label.setStyleSheet(f"color: {colour};")
