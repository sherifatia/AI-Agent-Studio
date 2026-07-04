# Roadmap

This roadmap reflects the project's own sprint history as recorded in git
and in this codebase, plus the logical next steps implied by the existing
(but empty) package structure. Sprints beyond 4 are not scheduled — they
are ordered by dependency, not by date.

## Completed

- **Sprint 3 — AI Engine Foundation**
  `AIEngine`, `Session`, `Message`, `Response`, `BaseProvider`,
  `ProviderManager`, and a working `OllamaProvider`. Basic Qt shell
  (`MainWindow`, `Sidebar`, `theme.py`) with page navigation stubs.

- **Sprint 4 — Foundation Cleanup + Runtime Preparation** *(this sprint)*
  Repository hygiene: audit, README, `requirements.txt`, `.gitignore`,
  removal of tracked build artifacts, consistent package `__init__.py`
  files, typed and documented provider stubs, and the architectural
  foundation for a future Runtime layer (`core/runtime.py` — classes only,
  no logic). No behavior change and no new features.

## Planned (Not Yet Scheduled)

### AI Runtime Implementation
Build the actual logic behind `Runtime`, `RuntimeContext`, `RuntimeState`,
and `RuntimeEvent` introduced in `core/runtime.py`. This is the immediate
next step after Sprint 4 and is expected to include:
- A defined `RuntimeState` lifecycle (e.g. idle → running → waiting →
  completed/failed).
- An event dispatch mechanism connecting `RuntimeEvent` to `core/events.py`.
- Wiring `AIEngine` to run inside a `Runtime` instead of being called
  directly by the UI.

### Navigation & Event Bus
- Implement `core/navigation.py` as a single source of truth for page
  identifiers (shared by `Sidebar` and `MainWindow`).
- Implement `core/events.py` as a lightweight publish/subscribe event bus.

### UI Pages
Implement the empty page widgets in `ui/widgets/`:
`dashboard_page.py`, `chat_page.py`, `models_page.py`, `browser_page.py`,
`memory_page.py`, `skills_page.py`, `workflow_page.py`, `settings_page.py`,
plus `statusbar.py` and `workspace.py` for shared chrome. Wire
`MainWindow.change_page()` to actually swap these widgets instead of only
updating a title label.

### Additional Providers
Implement `OpenAIProvider`, `GeminiProvider`, and `OpenRouterProvider`
against `BaseProvider`, following the pattern established by
`OllamaProvider`. Marked as `TODO` providers as of Sprint 4 — see
`providers/openai_provider.py`, `providers/gemini_provider.py`, and
`providers/openrouter_provider.py`.

### Memory
Implement `memory/conversation.py` (persistent conversation history,
likely replacing or backing `core.session.Session`), `memory/embeddings.py`,
and `memory/vectordb.py` for semantic recall.

### Skills System
Implement `skills/skill.py` (a `Skill` contract, mirroring
`BaseProvider`'s shape) and `skills/skill_manager.py` (a registry/dispatcher,
mirroring `ProviderManager`).

### Workflows
Implement `workflows/` on top of the Skills system once it exists, to allow
composing multiple skills/providers into a single automation.

### Plugins
Implement `plugins/plugin_manager.py` as a loader for third-party
extensions, once the Skills and Workflow systems have stable contracts to
extend.

### Embedded Browser
Implement `browser/browser_manager.py` to give agents the ability to drive
a browser instance. Depends on the Runtime and Skills systems being in
place first, since browser actions are a natural candidate for a "skill."

### Housekeeping (lower priority, non-blocking)
- Reconcile the two theming mechanisms (`styles/*.qss` vs `ui/theme.py`).
- Replace generic `raise Exception(...)` calls in `core/engine.py` and
  `providers/provider_manager.py` with dedicated exception types.
- Make `config/settings.py`'s file path resolution independent of the
  process's working directory.
- Adopt `pytest` and convert `test_engine.py` into a real test suite.
