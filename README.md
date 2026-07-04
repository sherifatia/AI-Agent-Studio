# AI Agent Studio

A desktop application for building, running, and managing AI agents through
a single interface. AI Agent Studio provides a provider-agnostic engine that
can talk to local models (via [Ollama](https://ollama.com)) or hosted APIs,
wrapped in a native Qt desktop UI.

> **Project status:** Early foundation stage (Sprint 4 — Foundation Cleanup).
> The core engine and provider abstraction are functional against Ollama.
> The UI shell, page navigation, and provider stubs for OpenAI, Gemini, and
> OpenRouter exist as scaffolding for upcoming sprints. See
> [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md) for a full breakdown of
> what is implemented versus planned.

---

## Project Overview

AI Agent Studio is organized around a simple idea: the **UI never talks to
an AI provider directly**. Instead:

- The **UI layer** (`ui/`) captures user intent (which page is active, what
  the user typed) and emits signals.
- The **core layer** (`core/`) owns the `AIEngine` and `Session`, and is
  responsible for orchestrating a conversation.
- The **provider layer** (`providers/`) implements a common `BaseProvider`
  contract per backend (Ollama today; OpenAI, Gemini, and OpenRouter are
  reserved for future sprints).

This separation means new providers or new UI pages can be added without
touching the other layers.

## Architecture

```
┌─────────────┐        ┌──────────────┐        ┌───────────────────┐
│   ui/        │  --->  │   core/       │  --->  │   providers/        │
│  Qt widgets  │        │  AIEngine,    │        │  BaseProvider +      │
│  & pages     │        │  Session      │        │  concrete providers  │
└─────────────┘        └──────────────┘        └───────────────────┘
```

- `AIEngine` (`core/engine.py`) holds the active `Session` and the currently
  selected provider. Calling `engine.ask(messages)` delegates directly to
  `provider.generate(messages)`.
- `ProviderManager` (`providers/provider_manager.py`) is a small factory
  that instantiates the correct provider implementation by name
  (`"ollama"`, `"openai"`, `"gemini"`, `"openrouter"`).
- `Session` (`core/session.py`) tracks conversation history and the active
  model/provider for the current run.
- `Settings` (`config/settings.py`) loads user-configurable defaults
  (theme, provider, model, language, startup page) from
  `config/settings.json`.

Reserved packages for upcoming sprints: `browser/`, `memory/`, `skills/`,
`workflows/`, `plugins/`. These currently contain empty placeholder modules
— see `docs/ROADMAP.md`.

## Folder Structure

```
AI-Agent-Studio/
├── app.py                   # Application entry point
├── bootstrap.py              # One-off project structure scaffolder
├── requirements.txt
├── core/                     # Engine, session, message/response models, runtime foundation
│   ├── engine.py
│   ├── session.py
│   ├── message.py
│   ├── response.py
│   ├── runtime.py            # Runtime architecture foundation (Sprint 4)
│   ├── navigation.py          # Reserved
│   └── events.py              # Reserved
├── providers/                 # AI provider implementations
│   ├── base_provider.py
│   ├── provider_manager.py
│   ├── ollama_provider.py     # Implemented
│   ├── openai_provider.py     # TODO provider
│   ├── gemini_provider.py     # TODO provider
│   └── openrouter_provider.py # TODO provider
├── ui/                        # Qt presentation layer
│   ├── main_window.py
│   ├── theme.py
│   └── widgets/               # Sidebar (implemented) + page placeholders
├── browser/                   # Reserved: embedded browser feature
├── memory/                    # Reserved: conversation memory / vector store
├── skills/                    # Reserved: agent skills system
├── workflows/                 # Reserved: workflow automation
├── plugins/                   # Reserved: plugin system
├── styles/                    # Qt stylesheets (dark/light)
├── config/                    # Settings loader + settings.json
└── docs/                      # Audit, architecture, roadmap, coding standard
```

## Installation

Requires **Python 3.12+**.

```bash
git clone https://github.com/sherifatia/AI-Agent-Studio.git
cd AI-Agent-Studio

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

If you plan to use the **Ollama** provider (the only fully implemented
provider today), install and run [Ollama](https://ollama.com) separately,
and pull the model referenced in `config/settings.json` (default: `llama3`):

```bash
ollama pull llama3
```

## Running

Launch the desktop application:

```bash
python app.py
```

To run the standalone engine smoke test (uses a fake in-memory provider,
does not require Ollama to be running):

```bash
python test_engine.py
```

## Providers

| Provider | Status | Notes |
|---|---|---|
| **Ollama** | Implemented | Connects to a local Ollama server (default `http://localhost:11434`) |
| **OpenAI** | TODO | Interface defined, not yet implemented |
| **Gemini** | TODO | Interface defined, not yet implemented |
| **OpenRouter** | TODO | Interface defined, not yet implemented |

All providers implement the `BaseProvider` contract
(`providers/base_provider.py`), so adding a new provider means implementing
a single `generate(messages)` method that returns a `core.response.Response`.

## Future Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full, sprint-by-sprint plan.
At a high level, upcoming work includes:

- Implementing the `AIRuntime` business logic on top of the
  `core/runtime.py` foundation introduced in Sprint 4.
- Building out the empty UI pages (Chat, Models, Browser, Memory, Skills,
  Workflows, Settings).
- Implementing the OpenAI, Gemini, and OpenRouter providers.
- Adding conversation memory and vector storage (`memory/`).
- Adding an agent skills system (`skills/`) and plugin loading
  (`plugins/`).

## Documentation

- [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md) — full repository audit
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture deep dive
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — sprint roadmap
- [`docs/CODING_STANDARD.md`](docs/CODING_STANDARD.md) — coding conventions
- [`docs/SPRINT4_REPORT.md`](docs/SPRINT4_REPORT.md) — Sprint 4 change log
