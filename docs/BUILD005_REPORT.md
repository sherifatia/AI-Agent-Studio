# Build 005 Report — Models Management

**Goal:** Create the first real management page: provider selection, model
listing, connection testing, and live provider switching — all wired to the
existing `AIEngine` without recreating the engine or the session.

---

## Files Created

| File | Description |
|---|---|
| `ui/widgets/models_page.py` | Full models management page (replaces the Sprint 4 docstring-only placeholder) |
| `docs/BUILD005_REPORT.md` | This report |

## Files Modified

| File | Change | Why |
|---|---|---|
| `app.py` | Added a new `"engine"` startup service between `resources` and `user_interface`; also reads `"model"` from settings; passes `engine` to `MainWindow` | The engine must exist before `MainWindow` builds the Models page, which needs a reference to it |
| `ui/main_window.py` | Accepts `engine: object = None`; replaces `workspace QWidget + QLabel` with a `QStackedWidget`; creates `ModelsPage`; connects `provider_changed` signal to `status_bar.set_provider()` | The page stack is the minimal structural change needed to show a real page widget without redesigning the sidebar/layout |

---

## Architecture Decisions

**Engine created in the startup sequence, not in the UI.**
`AIEngine` is instantiated in `app.py`'s `"engine"` service, which runs
before the UI service. `MainWindow` receives it via constructor injection
(`engine=context["engine"]`). This keeps the engine out of the UI layer
and makes the dependency explicit and testable.

**Provider switching uses `engine.set_provider()` — engine and session are never recreated.**
`ModelsPage._set_active_provider()` calls `ProviderManager().create(name)`
to get a new provider instance, then calls `engine.set_provider(provider)`.
The `AIEngine` and `Session` objects stay alive for the full application
lifetime. The session's conversation history is intact after a provider
switch — verified in the boot test by checking `id(engine.session)` before
and after the switch.

**`QStackedWidget` replaces the title-label placeholder.**
`MainWindow._stack` holds two widgets:
- Index 0: the original placeholder `QWidget` with `page_title: QLabel` —
  still shown for all pages that are not yet implemented.
- Index 1: `ModelsPage` — shown when "Models" is selected.

Adding a future page (e.g. Chat) means adding one `_stack.addWidget()` call
and one entry in `_PAGE_WIDGETS`. No structural change to the layout is
required.

**`ModelsPage` communicates back via a Qt signal.**
`provider_changed = Signal(str)` is connected in `MainWindow._build_ui()`
to `self.status_bar.set_provider`. The page has no direct reference to the
status bar — it emits an event and the window decides what to do with it.

**Ollama model listing is best-effort.**
`_load_models_for("ollama")` wraps the `client.list()` call in
`try/except`. If Ollama is not running, the model list shows a clear error
message and logs a warning — it does not raise or crash the page.
The library's response shape varies by version (object-style vs dict-style),
so both are handled.

**TODO providers show an honest message.**
Clicking "Set Active Provider" on OpenAI, Gemini, or OpenRouter catches
`NotImplementedError` and shows a clear status message rather than leaving
the user with a silent failure or a misleading success.

---

## Verification Results

| Check | Result |
|---|---|
| Repo-wide syntax scan | 0 errors |
| Full import check (28 modules) | All import cleanly, no circular deps |
| `test_engine.py` | Byte-identical output (unchanged) |
| Headless boot (7 services via ServiceLoader) | All services start, engine created with OllamaProvider |
| Models page navigation | `_stack.currentWidget()` is `ModelsPage` when "Models" selected |
| Placeholder navigation | `page_title.setText("Chat")` when "Chat" selected |
| Provider switch without engine/session recreation | `id(engine.session)` identical before and after `set_provider()` |
| `ModelsPage._refresh()` with Ollama offline | Catches exception, shows error in model list, logs WARNING — no crash |
| `print()` in application code | None |

---

## Known Limitations

- **Ollama must be running for model listing to work.** This is expected
  and by design — the build specification says "only list installed models,
  do NOT download anything." If Ollama is not running, the error is shown
  inside the model list widget, not as a crash.
- **"Test Connection" for Ollama calls `client.list()`**, not a dedicated
  health endpoint. This is the lightest available call on the ollama
  Python library that requires a live server. It is sufficient and fast.
- **Model selection does not yet change the active model on the engine.**
  The user can see installed models, but clicking a model in the list
  does not yet call `OllamaProvider(model=selected)` and re-apply it.
  This is a deliberate scope limit: the build specification asked for
  the model list to be displayed, not for model-switching within a
  provider. Connecting model selection to provider re-instantiation is
  natural scope for a future Build.
- **BUILD004_REPORT.md** was referenced in the build instructions but does
  not exist in this repository (Builds 002–004 happened in a separate
  session). This build used the existing architecture as found, which was
  sufficient.

## Remaining Issues (Pre-existing)

- Chat page (`ui/widgets/chat_page.py`) is still a docstring-only
  placeholder — it shows via the stack's placeholder widget.
- `config/settings.json`'s path is CWD-relative (pre-existing, tracked
  in PROJECT_AUDIT.md).
- No `pytest` suite — `test_engine.py` remains a manual script.
