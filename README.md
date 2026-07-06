# AI Agent Studio

A desktop application for building, running, and managing AI agents through
a single interface. AI Agent Studio provides a provider-agnostic engine that
can talk to local models (via [Ollama](https://ollama.com)) or hosted APIs
(OpenAI, Gemini, OpenRouter), wrapped in a native Qt desktop UI.

> **Project status:** Build 024 — all eight build targets (017–024) have been
> implemented: Additional Providers, UI Pages, Workflows, Memory, Plugins,
> Embedded Browser, Housekeeping, and Project Finalization. See
> [`docs/development/BUILD_HISTORY.md`](docs/development/BUILD_HISTORY.md)
> for the full log.

---

## Project Overview

AI Agent Studio is organized around a simple idea: the **UI never talks to
an AI provider directly**. Instead:

- The **UI layer** (`ui/`) captures user intent (which page is active, what
  the user typed) and renders responses.
- The **core layer** (`core/`) owns the `AIEngine`, `Session`, `Agent`,
  and `Application` composition root.
- The **provider layer** (`providers/`) implements a common `BaseProvider`
  contract per backend (Ollama, OpenAI, Gemini, OpenRouter).
- **Skills**, **Workflows**, **Plugins**, and **Memory** extend the agent
  with reusable capabilities, multi-step automations, third-party extensions,
  and semantic recall.
- **Browser** module fetches and extracts readable text from web URLs.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     app.py                           │
│     (Application composition root)                   │
├────────┬────────┬────────┬────────┬────────┬────────┤
│  ui/   │ core/  │providers│skills  │memory  │browser │
│ Qt     │Engine  │Ollama  │Builtins│VectorDB│Fetch   │
│ widgets│Agent   │OpenAI  │Fetch   │Embedd. │Parse   │
│ 8 pages│Session │Gemini  │Calc    │        │        │
│        │Runtime │OpenRtr │Time    │        │        │
├────────┴────────┴────────┴────────┴────────┴────────┤
│ workflows/    plugins/    config/    styles/         │
│ Engine        Manager     Settings   QSS (dark/light)│
└─────────────────────────────────────────────────────┘
```

## Packages (all implemented)

| Package | Description | Status |
|---|---|---|
| `core/` | Engine, Agent, Session, Runtime, Exceptions | ✅ |
| `providers/` | Ollama, OpenAI, Gemini, OpenRouter | ✅ |
| `ui/` | 8-page desktop UI (PySide6) | ✅ |
| `skills/` | Skill system with built-in skills | ✅ |
| `workflows/` | Multi-step workflow automation | ✅ |
| `memory/` | Conversation memory, Embeddings, VectorDB | ✅ |
| `plugins/` | Plugin discovery and lifecycle | ✅ |
| `browser/` | URL fetching and HTML-to-text extraction | ✅ |
| `config/` | JSON settings loader | ✅ |
| `styles/` | Dark/light QSS stylesheets | ✅ |

## Folder Structure

```
AI-Agent-Studio/
├── app.py                    # Application entry point
├── requirements.txt
├── core/                     # Engine, Agent, Session, Runtime, Events
├── providers/                # Ollama, OpenAI, Gemini, OpenRouter
├── ui/                       # Qt desktop UI (8 pages, sidebar, status bar)
│   ├── main_window.py
│   ├── theme.py
│   └── widgets/
├── browser/                  # URL fetch / HTML-to-text extraction
├── memory/                   # Conversation memory, Embeddings, VectorDB
├── skills/                   # Skill system + built-in skills (time, calc, fetch)
├── workflows/                # Multi-step workflow engine
├── plugins/                  # Plugin manager
├── styles/                   # dark.qss / light.qss
├── config/                   # settings.py + settings.json
├── tests/                    # pytest test suite (21 tests)
└── docs/                     # Audit, roadmap, build history, coding standard
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

If you plan to use the **Ollama** provider, install and run
[Ollama](https://ollama.com) separately:

```bash
ollama pull llama3
```

For the **OpenAI**, **Gemini**, or **OpenRouter** providers, set the
corresponding environment variable (`OPENAI_API_KEY`, `GEMINI_API_KEY`,
`OPENROUTER_API_KEY`).

## Running

Launch the desktop application:

```bash
python app.py
```

Run the test suite:

```bash
python -m pytest tests/ -v
```

## Providers

| Provider | Status | Notes |
|---|---|---|
| **Ollama** | ✅ | Connects to a local Ollama server (default `http://localhost:11434`) |
| **OpenAI** | ✅ | Uses `urllib`; reads `OPENAI_API_KEY` from env |
| **Gemini** | ✅ | Uses `urllib`; reads `GEMINI_API_KEY` from env |
| **OpenRouter** | ✅ | Uses `urllib`; reads `OPENROUTER_API_KEY` from env |

All providers implement `BaseProvider` (`providers/base_provider.py`).

## Built-in Skills

| Command | Skill | Description |
|---|---|---|
| `/time` | `current_time` | Get the current date and time |
| `/calc` or `/calculate` | `calculator` | Evaluate a mathematical expression |
| `/fetch` | `web_fetch` | Fetch a URL and return readable text |

## Documentation

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — full sprint roadmap
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture deep dive
- [`docs/development/BUILD_HISTORY.md`](docs/development/BUILD_HISTORY.md) — build-by-build log
- [`docs/CODING_STANDARD.md`](docs/CODING_STANDARD.md) — coding conventions
- [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md) — repository audit
