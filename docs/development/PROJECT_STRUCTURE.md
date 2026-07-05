# Project Structure

This document explains the **responsibility** of every major folder in
AI Agent Studio. It does not describe implementation details (see
`docs/ARCHITECTURE.md` for data flow) and it does not propose any changes
to the current layout.

## `core/`

Owns the application/domain logic that is independent of any specific AI
provider or UI framework: the engine that orchestrates a conversation
(`AIEngine`), the session state for a single run (`Session`), the message
and response data shapes (`Message`, `Response`), and the architectural
foundation for longer-running agent behavior (`runtime.py`). `core/` may
depend on `providers/` (to type against `BaseProvider`), but must never
depend on `ui/`.

## `providers/`

Owns the integration with each individual AI backend. Every provider
implements the shared `BaseProvider` contract (`generate(messages) ->
Response`), and `ProviderManager` is the single factory that resolves a
provider by name. This is the only layer allowed to know about a specific
vendor's SDK or API (e.g. the `ollama` package). `providers/` must never
depend on `core/` or `ui/` beyond the shared `Response` type.

## `browser/`

Reserved for giving an agent the ability to drive an embedded browser
instance (navigation, reading page content, interacting with elements).
Expected to be exposed as a capability the Skills system can invoke, once
both exist.

## `memory/`

Reserved for persisting and recalling conversation content beyond a single
in-memory `Session`: durable conversation storage, embedding generation,
and vector-database-backed semantic recall.

## `skills/`

Reserved for a registry of discrete, invokable agent capabilities — a
`Skill` contract mirroring `providers.base_provider.BaseProvider`, and a
`SkillManager` mirroring `ProviderManager`. Skills are expected to be the
unit that `workflows/` compose together.

## `plugins/`

Reserved for loading third-party extensions into the application at
runtime, once `skills/` and `workflows/` have stable, documented contracts
worth extending.

## `ui/`

Owns the Qt (PySide6) presentation layer: the main window, navigation
(`Sidebar`), theme constants, and the individual workspace pages. `ui/`
is the only layer permitted to import Qt. It may depend on `core/`, and
must never be depended on by `core/` or `providers/`.

## `config/`

Owns loading and exposing user-configurable settings from
`config/settings.json` via the `Settings` class. Any module that needs a
configurable value (theme, active provider, active model, language, etc.)
should go through `config/`, not read a JSON file directly.

## `docs/`

Owns all project documentation: architecture explanations, audits, sprint
reports, and — inside `docs/development/` specifically — the permanent
engineering standards this file is part of. `docs/` contains no executable
application code.

## `styles/`

Owns Qt stylesheet (`.qss`) files for theming. Currently disconnected from
`ui/theme.py`, which holds the active color constants instead — this
duplication is documented in `docs/PROJECT_AUDIT.md` and is not resolved
by this document.

## `workflows/`

Reserved for composing multiple skills and/or providers into a single,
multi-step automation, once `skills/` exists as a stable dependency.
