# Project Audit — AI Agent Studio

**Date:** Sprint 4 — Foundation Cleanup + Runtime Preparation
**Scope:** Full repository review prior to building the AI Runtime layer.
**Method:** Static review of every tracked file, import graph inspection, and
Python syntax validation (Python 3.12).

---

## 1. Architecture Overview

AI Agent Studio is a desktop application built with **PySide6 (Qt for
Python)**. The codebase follows a layered package structure:

```
app.py            Entry point — builds the QApplication and MainWindow
bootstrap.py       One-off helper that scaffolds the folder structure
core/               Application/domain layer (engine, session, message, response)
providers/          AI provider abstraction (Ollama, OpenAI, Gemini, OpenRouter)
ui/                 Qt presentation layer (main window, theme, widgets/pages)
browser/            Reserved for an embedded browser feature (empty)
memory/             Reserved for conversation memory / vector storage (empty)
skills/             Reserved for an agent "skills" system (empty)
workflows/          Reserved for workflow automation (empty)
plugins/            Reserved for a plugin system (empty)
styles/             Qt stylesheets (dark.qss / light.qss) (empty)
config/             JSON-backed settings loader
```

The intended design is a **provider-agnostic AI engine**: `AIEngine` holds a
`Session` and delegates message generation to whichever `BaseProvider`
implementation is injected via `ProviderManager`. The UI is decoupled from
the engine — `MainWindow` currently only manages navigation between pages
and does not yet call into `core/` or `providers/`.

This is a sound, conventional architecture for the stated goal. The concern
at this stage is **not** the design — it is that most of the tree is
scaffolding rather than implementation.

---

## 2. Completed Modules

These modules are implemented and internally consistent:

| Module | Status | Notes |
|---|---|---|
| `core/session.py` | Complete (minimal) | Simple in-memory history list |
| `core/message.py` | Complete (minimal) | `Message` dataclass — **currently unused** anywhere in the codebase |
| `core/response.py` | Complete (minimal) | `Response` dataclass, used by `OllamaProvider` |
| `core/engine.py` | Complete (minimal) | Delegates to a provider; no session persistence wired in yet |
| `providers/base_provider.py` | Complete | Clean `ABC` contract |
| `providers/provider_manager.py` | Complete | Simple factory/dispatcher |
| `providers/ollama_provider.py` | Complete | Only provider with a real implementation |
| `providers/provider_manager.py` → `ollama` path | Complete | Only functioning provider |
| `config/settings.py` / `config/settings.json` | Complete (minimal) | No validation or defaults if a key is missing |
| `ui/main_window.py` | Complete (minimal) | Builds layout, wires sidebar navigation signal |
| `ui/widgets/sidebar.py` | Complete | Functional navigation list with active-state styling |
| `ui/theme.py` | Complete (minimal) | Static constants only |
| `test_engine.py` | Complete | Ad-hoc smoke test using a `FakeProvider`; not part of a test framework (no `pytest`) |
| `bootstrap.py` | Complete | Idempotent folder/package scaffolder |

## 3. Incomplete Modules

| Module | Status | Notes |
|---|---|---|
| `providers/openai_provider.py` | Stub | `generate()` raises `NotImplementedError` |
| `providers/gemini_provider.py` | Stub | `generate()` raises `NotImplementedError` |
| `providers/openrouter_provider.py` | Stub | `generate()` raises `NotImplementedError` |
| `core/navigation.py` | Empty | No navigation/router logic yet — `MainWindow` currently handles this ad hoc via a Qt signal |
| `core/events.py` | Empty | No event bus / event types defined |
| `browser/browser_manager.py` | Empty | No browser embedding logic |
| `memory/conversation.py`, `memory/embeddings.py`, `memory/vectordb.py` | Empty | No persistence or retrieval logic |
| `skills/skill.py`, `skills/skill_manager.py` | Empty | No skill contract or registry |
| `plugins/plugin_manager.py` | Empty | No plugin loading mechanism |
| `workflows/` | Empty (package only) | No workflow model yet |
| `ui/widgets/dashboard_page.py`, `chat_page.py`, `models_page.py`, `browser_page.py`, `memory_page.py`, `skills_page.py`, `workflow_page.py`, `settings_page.py`, `statusbar.py`, `workspace.py` | Empty | Sidebar can navigate to these labels, but no page widgets exist to render — `MainWindow.change_page()` only updates a title label today |
| `styles/dark.qss`, `styles/light.qss` | Empty | Referenced by intent (`settings.json` has a `"theme": "dark"` key) but not loaded or applied anywhere in code |

## 4. Empty Files (0 bytes)

Confirmed via direct inspection, grouped by package:

```
browser/browser_manager.py
config/__init__.py
core/__init__.py
core/events.py
core/navigation.py
memory/__init__.py
memory/conversation.py
memory/embeddings.py
memory/vectordb.py
plugins/__init__.py
plugins/plugin_manager.py
skills/__init__.py
skills/skill.py
skills/skill_manager.py
styles/dark.qss
styles/light.qss
ui/__init__.py
ui/widgets/__init__.py
ui/widgets/browser_page.py
ui/widgets/chat_page.py
ui/widgets/dashboard_page.py
ui/widgets/memory_page.py
ui/widgets/models_page.py
ui/widgets/settings_page.py
ui/widgets/skills_page.py
ui/widgets/statusbar.py
ui/widgets/workflow_page.py
ui/widgets/workspace.py
workflows/__init__.py
```

28 of the ~48 tracked source files are placeholders with no content. This is
expected for a project that has only completed "Sprint 3" of its own
roadmap, but it means roughly 58% of the tree is not yet functional.

## 5. Duplicated Logic

No meaningful duplicated *logic* was found — the codebase is too small and
too sparse for real duplication to have accumulated yet. Two structural
overlaps are worth flagging before they turn into duplication later:

- **Navigation is defined in two places.** `ui/widgets/sidebar.py` owns the
  list of page names (`"Dashboard"`, `"Chat"`, ... `"Settings"`) and emits
  them as free-form strings. `ui/main_window.py` consumes those same
  strings by convention, with no shared enum/constant. Once `core/navigation.py`
  is implemented, page identifiers should be defined once (likely as an
  `Enum`) and imported by both the sidebar and the window.
- **Provider dispatch is duplicated in shape.** `ProviderManager.create()`
  and `config/settings.json`'s `"provider"` key both encode the same set of
  valid provider names, but nothing ties the two together — an invalid
  string in `settings.json` will only fail at runtime inside
  `ProviderManager.create()`.

## 6. Missing Dependencies

No `requirements.txt` or `pyproject.toml` existed prior to this sprint.
Cross-referencing every `import` statement in the codebase against the
Python 3.12 standard library, exactly two third-party packages are
actually used:

| Package | Used by |
|---|---|
| `PySide6` | `app.py`, `ui/main_window.py`, `ui/widgets/sidebar.py` |
| `ollama` | `providers/ollama_provider.py` |

These have been captured in `requirements.txt` (see Task 3). No version
pins were guessed — see that file for details.

## 7. Technical Debt

- **Tracked `__pycache__` / `.pyc` files.** 11 compiled bytecode files were
  committed to git under `core/`, `providers/`, `ui/`, and `ui/widgets/`.
  These are environment-specific build artifacts and should never be
  version-controlled. Removed from tracking in this sprint (Task 5).
- **No `.gitignore`.** Directly caused the above. Added in this sprint.
- **No dependency manifest.** Anyone cloning the repo has to guess which
  packages to install. Fixed in this sprint.
- **No `README.md`.** No onboarding path for a new contributor. Fixed in
  this sprint.
- **Bare `except`/`raise Exception(...)` usage.** `core/engine.py` raises a
  generic `Exception("No Provider Selected")` and `ProviderManager.create()`
  raises a generic `Exception(f"Unknown provider: {provider_name}")`.
  Generic exceptions make error handling by callers unnecessarily broad.
  Left unchanged in this sprint per the "no behavior change" constraint,
  but flagged as a candidate for dedicated exception classes
  (e.g. `ProviderNotSelectedError`, `UnknownProviderError`) in a future
  sprint.
- **`config/settings.py` uses a hardcoded relative path**
  (`"config/settings.json"`), which only works if the process is launched
  from the repository root. This will break if the app is packaged or
  invoked from another working directory. Flagged for a future sprint —
  not changed now to avoid altering runtime behavior.
- **`core/message.py`'s `Message` dataclass is unused.** `AIEngine.ask()`
  and `test_engine.py` both pass plain `dict` objects instead. Either the
  engine should be typed to accept `Message` objects, or the dataclass
  should be wired in — left as-is this sprint, flagged for the Runtime
  work.
- **No automated test framework.** `test_engine.py` is a standalone script
  (not `pytest`-based, no assertions — it just prints values for manual
  inspection). Fine for a proof of concept, not sustainable once more
  providers/pages exist.
- **Qt stylesheets exist but are disconnected.** `styles/dark.qss` and
  `styles/light.qss` are empty and never loaded; `ui/theme.py` hardcodes
  colors as Python constants instead. The two theming mechanisms should be
  reconciled before the UI grows further.

## 8. Recommendations (Non-Breaking, for Future Sprints)

1. Implement `core/navigation.py` as the single source of truth for page
   identifiers (likely a `StrEnum`), consumed by both `Sidebar` and
   `MainWindow`.
2. Wire `core/events.py` as a lightweight in-process event bus before
   `browser/`, `memory/`, `skills/`, `plugins/`, and `workflows/` start
   emitting cross-cutting events — this will be the natural consumer of
   `core/runtime.py`'s `RuntimeEvent`, introduced this sprint.
3. Replace the two `raise Exception(...)` call sites with dedicated
   exception types once behavior changes are in scope.
4. Move `config/settings.py`'s file path resolution to be relative to the
   package (e.g. `Path(__file__).parent / "settings.json"`) instead of the
   process's current working directory.
5. Decide on one theming mechanism (QSS files *or* Python constants) and
   remove the other before the UI pages are implemented.
6. Adopt `pytest` once there is more than one test, and convert
   `test_engine.py` into real assertions.
7. Only after the above: begin implementing the empty page widgets and the
   `AIRuntime` business logic on top of the `core/runtime.py` foundation
   added in this sprint.

---

*This audit reflects the state of the repository at the start of Sprint 4,
before any cleanup changes were applied. See `docs/SPRINT4_REPORT.md` for
exactly what changed as a result.*
