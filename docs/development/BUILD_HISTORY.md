# Build History

This is the running log of every Build performed on AI Agent Studio going
forward. Every Build must append one entry here as part of its Commit
stage (see `docs/development/BUILD_WORKFLOW.md`). This file is a template
— it starts empty and grows one entry per Build.

> **Note on history prior to this template:** Sprint 3 ("AI Engine
> foundation") and Sprint 4 ("Foundation Cleanup") both happened before
> this file existed. They are not backfilled here to keep this log
> accurate to its own process (every entry below was written as part of
> the Build it describes). Their details live in `docs/PROJECT_AUDIT.md`,
> `docs/SPRINT4_REPORT.md`, and `docs/SPRINT4_REVIEW.md` instead.

---

## Entry Template

Copy this block for each new Build:

```
### Build <N> — <short title>
**Date:** <date>
**Type:** <Feature | Fix | Cleanup | Docs>

**Scope:**
<one or two sentences on what this Build was for>

**Files created:**
- ...

**Files modified:**
- ...

**Verification performed:**
<what was actually run/checked to confirm correctness>

**Follow-ups / known limitations:**
- ...

**Commit:** <commit hash and message>
```

---

## Log

### Build 001 — Professional Application Shell
**Date:** 2026-07-05
**Type:** Feature (infrastructure/shell, no AI features)

**Scope:**
Transform the project skeleton into a real desktop application shell:
centralized logging, a professional startup sequence, centralized app
metadata, and management-layer foundations (theme, resources, dialogs,
commands, notifications, version, error handling) — plus visible,
functional improvements to the main window, status bar, and sidebar. No
Runtime, Memory, Skills, Browser, Workflows, Marketplace, SaaS, or
Business OS work, per this Build's explicit instructions.

**Files created:**
- `core/app_info.py`, `core/constants.py`, `core/logging_setup.py`,
  `core/startup.py`, `core/error_handler.py`, `core/command_manager.py`,
  `core/notification_manager.py`, `core/version_manager.py`
- `ui/resource_manager.py`, `ui/theme_manager.py`, `ui/dialog_manager.py`

**Files modified:**
- `app.py` (startup sequence wiring)
- `ui/main_window.py` (title, min size, geometry persistence, status bar,
  About menu)
- `ui/theme.py` (centralized `APP_NAME`/title from `AppInfo`, added
  min-size constants)
- `ui/widgets/sidebar.py` (icon placeholders, collapsible foundation)
- `ui/widgets/statusbar.py` (implemented — was an empty Sprint 4
  placeholder)

**Verification performed:**
Full syntax scan (0 errors), full import verification (29 modules),
`test_engine.py` re-run with byte-identical output, and a real headless
boot through the actual `_build_startup_sequence()` — confirmed logging
to `logs/application.log`, theme application, window title/status bar
population from `config/settings.json`, and window geometry persistence
across two separate process runs via `QSettings`.

**Follow-ups / known limitations:**
- The `LOGGING` phase's own "Startup phase: logging" log line is not
  captured, since log handlers are attached partway through that phase's
  action. Cosmetic; every other phase logs correctly.
- Window geometry restoration was verified functionally, but exact pixel
  values were affected by the headless Qt `offscreen` platform's small
  (800×800) virtual screen — expected on a real display.
- See `docs/BUILD001_REPORT.md` for full detail.

**Commit:** `Build 001 - Professional Application Shell`

---

### Build 011 — Skill Dispatch
**Date:** 2026-07-06
**Type:** Feature

**Scope:**
Wire the Agent.run() path to check for a skill trigger (leading `/` prefix)
before calling the LLM. If a skill matches, execute it directly, wrap the
SkillResult in a TaskResult, and record to memory — without calling the
provider. Also fix ChatPage._clear_conversation() to call memory.clear().

**Files modified:**
- `core/agent.py` — added `_detect_skill()`, `_run_skill()`, skill-aware
  `run()`, and `clear_memory()`
- `ui/widgets/chat_page.py` — calls `agent.clear_memory()` on clear

**Verification performed:**
Full syntax scan and import verification of all changed modules.

**Follow-ups / known limitations:**
- Skills that need the full conversation context (e.g. "summarize my last
  5 messages") will not work via `/skill` prefix since only the remainder
  after the command is passed as input, not the history. A future Build
  could pass history as part of the skill input.
- Skill detection uses a static alias table. Dynamic discovery (e.g.
  querying the SkillRegistry for all registered names) is a future
  improvement.
- No UI exists to show the user which skills are available. The
  Models page is a natural home for a Skills tab.

**Commit:** `Build 011 - Skill Dispatch`

---

### Build 012 — Navigation & Event Bus
**Date:** 2026-07-06
**Type:** Feature (infrastructure)

**Scope:**
Implement `core/navigation.py` as the single source of truth for page
identifiers (`PageId` StrEnum + `PAGE_ORDER`), replacing the free-form
string duplication between Sidebar and MainWindow. Implement
`core/events.py` as a lightweight publish/subscribe EventBus. Wire
both into the sidebar, main window, and startup sequence.

**Files created:**
- `core/navigation.py` — `PageId` StrEnum, `PAGE_ORDER`, `from_label()`
- `core/events.py` — `Event` dataclass, `EventBus` pub/sub

**Files modified:**
- `ui/widgets/sidebar.py` — uses `PageId` + `PAGE_ORDER` instead of
  hardcoded string list
- `ui/main_window.py` — accepts `EventBus`, uses `PageId` for navigation,
  publishes `navigation.changed` events
- `app.py` — registers `event_bus` startup service, passes bus to
  `MainWindow`

**Verification performed:**
Full syntax scan and import verification of all changed modules.

**Follow-ups / known limitations:**
- The EventBus is not yet wired to `RuntimeEvent` dispatch; that is
  part of the AI Runtime Implementation roadmap item.
- `MainWindow.change_page()` retains the old string-parameter signature
  for backward compatibility.

**Commit:** `Build 012 - Navigation & Event Bus`

---

### Build 013 — UI Pages (Skills, Dashboard, Settings)
**Date:** 2026-07-06
**Type:** Feature

**Scope:**
Implement three formerly-empty page widgets with real content: SkillsPage
lists registered skills from the SkillRegistry; DashboardPage shows
session statistics from MemoryManager and active provider info;
SettingsPage displays current config/settings.json values in a read-only
view. Wire all three into MainWindow's stacked workspace and navigation.

**Files created:**
- `ui/widgets/skills_page.py` — lists registered skills with descriptions
- `ui/widgets/dashboard_page.py` — session stats, app info, active provider
- `ui/widgets/settings_page.py` — read-only config display

**Files modified:**
- `ui/main_window.py` — creates and wires SkillsPage, DashboardPage,
  SettingsPage; accepts `settings` parameter
- `app.py` — passes `app.settings` to `MainWindow`

**Verification performed:**
Full syntax scan and import verification of all new and changed modules.

**Follow-ups / known limitations:**
- Settings page is read-only; editing is reserved for a future Build.
- Browser, Memory, and Workflow pages remain as placeholder stubs.
- Dashboard stats update only when the page is first shown; a periodic
  refresh or event-driven update is future scope.

**Commit:** `Build 013 - UI Pages (Skills, Dashboard, Settings)`

---

### Build 014 — Housekeeping (exceptions, settings path, Message dataclass)
**Date:** 2026-07-06
**Type:** Cleanup

**Scope:**
Address three long-standing technical debt items from the Sprint 4 audit:
replace generic `raise Exception(...)` in engine.py and
provider_manager.py with dedicated exception types; make
config/settings.py's file path resolution package-relative instead of
CWD-relative; wire core/message.py's Message dataclass into AIEngine.ask()
so it accepts both Message objects and plain dicts.

**Files created:**
- `core/exceptions.py` — `ProviderNotSelectedError`, `UnknownProviderError`

**Files modified:**
- `core/engine.py` — uses `ProviderNotSelectedError`, accepts `Message`
  instances in `ask()` via normalisation to dicts
- `providers/provider_manager.py` — uses `UnknownProviderError` instead of
  generic `Exception`
- `config/settings.py` — path resolved via `Path(__file__).parent` instead
  of relative to CWD

**Verification performed:**
Full syntax scan and import verification of all changed modules.

**Follow-ups / known limitations:**
- `test_engine.py` and `application.py` still catch generic `Exception`
  around provider calls; they could be updated to catch the specific types
  in a future Build.
- The `Message` dataclass now works in the engine but providers still
  receive plain dicts (normalised by `ask()`). A future Build could type
  the provider interface to accept `Message` directly.

**Commit:** `Build 014 - Housekeeping (exceptions, settings path, Message)`

---

### Build 015 — AI Runtime Implementation
**Date:** 2026-07-06
**Type:** Feature (infrastructure)

**Scope:**
Implement the actual business logic behind `Runtime`, `RuntimeContext`,
`RuntimeState`, and `RuntimeEvent`. Adds validated state machine transitions
(IDLE → RUNNING → WAITING → RUNNING/COMPLETED/FAILED), event dispatch via
the EventBus, and a `run(task)` method that coordinates the full execution
lifecycle (delegating to AIEngine, recording to Session, emitting lifecycle
events).

**Files modified:**
- `core/runtime.py` — complete rewrite with real logic:
  - `RuntimeState.can_transition_to()` — validates state machine rules
  - `Runtime.run(task)` — full lifecycle: start, execute, complete/fail
  - `Runtime._transition()` — validates and applies state changes
  - `Runtime._emit()` — dispatches RuntimeEvent through EventBus
  - `RuntimeContext` gains optional `event_bus` field
  - `RuntimeEvent.runtime_state` field added for context

**Verification performed:**
Full syntax scan and import verification.

**Follow-ups / known limitations:**
- `Runtime` is not yet wired into the application startup or Agent — the
  ChatPage and Agent still call `engine.ask()` directly. Wiring Runtime as
  the execution layer between Agent and Engine is the natural next Build.
- No timeout mechanism for RUNNING or WAITING states.
- `RuntimeEvent` is dispatched via `core.events.Event` bridge; no direct
  listener exists yet.

**Commit:** `Build 015 - AI Runtime Implementation`

---

### Build 016 — Wire Runtime into Agent & App Startup
**Date:** 2026-07-06
**Type:** Feature (infrastructure)

**Scope:**
Wire the Runtime into the Agent as the LLM execution layer, and into
app startup so a Runtime is created and passed down to MainWindow.
Agent.run() now delegates to runtime.run(task) when a Runtime is
available, falling back to direct engine.ask() otherwise.

**Files modified:**
- `core/agent.py` — accepts optional `Runtime` parameter, delegates LLM
  path to `runtime.run(task)` when available, falls back to `engine.ask()`
- `ui/main_window.py` — accepts `runtime` parameter, passes it to `Agent`
- `app.py` — creates `Runtime` with `RuntimeContext(engine, session, event_bus)`,
  passes it to `MainWindow`

**Verification performed:**
Syntax check on all three changed modules.

**Follow-ups / known limitations:**
- No timeout mechanism for RUNNING or WAITING states.
- RuntimeEvent is dispatched but no direct listener consumes it yet.
- The Runtime is created with the engine's session, which is the same
  session shared by the engine — Runtime writes messages to it.

**Commit:** `Build 016 - Wire Runtime into Agent & App Startup`

---

### Build 017 — Additional Providers (OpenAI, Gemini, OpenRouter)
**Date:** 2026-07-06
**Type:** Feature

**Scope:**
Replace the three stub providers (OpenAI, Gemini, OpenRouter) that raised
``NotImplementedError`` with real HTTP-based implementations using the
standard library ``urllib``.  Each provider reads its API key from an
environment variable (``OPENAI_API_KEY``, ``GEMINI_API_KEY``,
``OPENROUTER_API_KEY``) and falls back gracefully when the key is missing.

Also updated ``ProviderManager.create()`` to accept optional ``model`` and
``host`` parameters and forward them to each provider's constructor, and
updated ``Application._start_engine()`` to pass the configured values from
``config/settings.json``.

**Files modified:**
- ``providers/openai_provider.py`` — complete rewrite with real logic
- ``providers/gemini_provider.py`` — complete rewrite with real logic
- ``providers/openrouter_provider.py`` — complete rewrite with real logic
- ``providers/provider_manager.py`` — ``create()`` now accepts ``model``
  and ``host`` parameters, forwarding them to provider constructors
- ``core/application.py`` — ``_start_engine()`` passes ``active_model`` and
  ``active_host`` to ``ProviderManager.create()``; added ``active_host``
  attribute
- ``ui/widgets/models_page.py`` — updated labels from ``(TODO)`` to
  ``(API key required)``; improved connection test to handle all providers

**Verification performed:**
Syntax check (ast.parse) and import verification on all six changed
modules.  Existing ``test_engine.py`` smoke test unchanged.

**Follow-ups / known limitations:**
- API keys are read from environment variables only — there is no UI for
  setting them yet.
- No streaming support (all providers return complete responses).
- The ``_models_info_label`` typo in ``_load_ollama_models()`` was not
  fixed to keep the diff minimal (pre-existing).

**Commit:** `Build 017 - Additional Providers (OpenAI, Gemini, OpenRouter)`
