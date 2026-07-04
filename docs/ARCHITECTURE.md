# Architecture

This document describes how AI Agent Studio is structured internally and
why, independent of which features are implemented yet. For a snapshot of
what is actually finished versus placeholder, see `PROJECT_AUDIT.md`.

## Layers

The application is split into three layers with a strict one-directional
dependency rule: **UI depends on Core, Core depends on Providers. Providers
never depend on Core or UI.**

```
ui/  ──depends on──>  core/  ──depends on──>  providers/
```

### 1. Providers (`providers/`)

The lowest layer. Each provider is a concrete implementation of
`BaseProvider`, an abstract class with a single required method:

```python
class BaseProvider(ABC):
    @abstractmethod
    def generate(self, messages: list[dict[str, str]]) -> Response: ...
```

A provider's only responsibility is: given a list of chat messages, return
a `Response`. Providers know nothing about `Session`, the UI, or each
other. `ProviderManager` is the single place that knows how to map a
provider name (string) to a concrete class.

### 2. Core (`core/`)

The application/domain layer. `AIEngine` is the central object: it owns a
`Session` and a reference to the active provider, and exposes `ask()` as
the only entry point for producing a response. `Session` is a plain
in-memory record of conversation history and the active model/provider —
it has no knowledge of Qt or providers' internals.

`core/runtime.py` (introduced in Sprint 4) defines the architectural
foundation for a future **Runtime** layer that will sit above `AIEngine`
and coordinate longer-running agent behavior (multi-step tool use, agent
state transitions, event dispatch). It intentionally contains **no
business logic** yet — only the class shapes that future sprints will
implement against. See `ROADMAP.md`.

### 3. UI (`ui/`)

A Qt (PySide6) presentation layer. `MainWindow` builds the window chrome
and wires the `Sidebar`'s `page_changed` signal to a handler. Pages
(`ui/widgets/*_page.py`) are intended to be independent `QWidget`
subclasses that `MainWindow` swaps into the workspace area — this wiring is
not implemented yet, so today `MainWindow.change_page()` only updates a
title label.

The UI layer is expected to call into `core.engine.AIEngine`, never
directly into `providers/`.

## Configuration

`config/settings.py` loads `config/settings.json` at construction time and
exposes a single `get(key)` accessor. There is currently no schema
validation, no defaults for missing keys, and no environment-variable
override mechanism — flagged in `PROJECT_AUDIT.md` as a candidate for a
future sprint.

## Data Flow (Once Fully Wired)

```
User input (ui/widgets/chat_page.py)
        │
        ▼
AIEngine.ask(messages)      (core/engine.py)
        │
        ▼
BaseProvider.generate(...)   (providers/*)
        │
        ▼
Response                     (core/response.py)
        │
        ▼
Session.add_message(...)     (core/session.py)
        │
        ▼
UI re-render                 (ui/widgets/chat_page.py)
```

This flow is the target design. As of Sprint 4, the engine and provider
halves of this pipeline work in isolation (see `test_engine.py`), but the
UI half is not yet connected to it.

## Reserved Subsystems

These packages exist as empty placeholders and are intentionally out of
scope for Sprint 4. Each will get its own design pass when implementation
begins:

- `browser/` — an embedded browser the agent can drive
- `memory/` — conversation persistence and vector-based recall
- `skills/` — a registry of discrete, invokable agent capabilities
- `workflows/` — multi-step automations composed of skills/providers
- `plugins/` — third-party extension loading

No architectural decisions have been made for these yet beyond the folder
boundaries themselves.
