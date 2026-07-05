# Final Engineering Report — Builds 006 – 010

**Date:** Build 010 complete
**Branch:** main
**Latest commit:** `91f7632` — Build 010 - Skill Foundation

---

## 1. Files Created

| File | Build | Description |
|---|---|---|
| `core/application.py` | 006 | Composition root — owns Settings, Session, ProviderManager, AIEngine, MemoryManager, SkillRegistry |
| `core/task.py` | 007 | `Task` dataclass — carries user input, history, metadata to the Agent |
| `core/task_result.py` | 007 | `TaskResult` dataclass — success, response, error, duration, metadata |
| `core/agent.py` | 007 | `Agent` — executes Tasks via AIEngine; records to Memory; can call Skills |
| `ui/widgets/chat_page.py` | 008 | Real `ChatPage` widget — conversation view, input, send, clear, status |
| `memory/manager.py` | 009 | `MemoryManager` — unified facade over ConversationMemory and SessionMemory |
| `memory/conversation.py` | 009 | `ConversationMemory` — turn-level history, History API |
| `memory/session.py` | 009 | `SessionMemory` — session-level aggregate statistics |
| `skills/skill.py` | 010 | `BaseSkill` ABC + `SkillResult` dataclass |
| `skills/skill_manager.py` | 010 | `SkillRegistry` + `SkillLoader` |
| `skills/builtin/__init__.py` | 010 | Builtin skills package |
| `skills/builtin/current_time.py` | 010 | `CurrentTimeSkill` — returns local datetime |
| `skills/builtin/calculator.py` | 010 | `CalculatorSkill` — safe AST-based arithmetic evaluator |

## 2. Files Modified

| File | Builds | Reason |
|---|---|---|
| `app.py` | 006, 009, 010 | Simplified to bootstrap: creates `Application`, passes `engine`, `memory`, `skill_registry` to `MainWindow` |
| `ui/main_window.py` | 008, 009, 010 | Accepts `memory` and `skill_registry`; creates `Agent` with all three; wires `ChatPage` into the stack |
| `core/agent.py` | 009, 010 | Added optional `memory` (009) and `skill_registry` (010) parameters |
| `core/application.py` | 009, 010 | Added `MemoryManager` (009) and `SkillRegistry` + `_load_skills()` (010) |

## 3. Architecture Decisions

**`Application` as composition root (Build 006).**
A single `Application` object creates every long-lived dependency in
`__init__` and wires them in `initialise()`. `app.py` becomes a thin
bootstrap (create one `Application`, run the `ServiceLoader`, enter the
Qt event loop). No engine, provider, or settings logic survives in
`app.py`. This satisfies the "MainWindow receives dependencies" requirement
and eliminates the scattered inline construction that existed in the
previous `app.py`.

**`Session` is never recreated.**
`Session` is created once in `Application.__init__()` and lives for the
full application lifetime. `Application.switch_provider()` and
`engine.set_provider()` replace only the provider reference —
`engine.session` is never touched. The `initialise()` guard (warns and
returns on second call) enforces this. Smoke tests verify `id(session)`
is identical before and after a provider switch.

**`Agent` is the only writer to `Memory` (Build 009).**
`ChatPage` calls `agent.run(task)` and receives a `TaskResult`. It never
calls `memory.record()`. The Agent calls `memory.record(task, result)` in
`run()`, but only on success — failed tasks are logged and excluded so
error noise does not pollute conversation history.

**`Task` carries history, not the Agent (Build 007).**
The Agent is stateless — it has no internal message buffer. The caller
(ChatPage) maintains `self._history` and includes it in each `Task`. This
makes the Agent reusable by any future page or service without coupling it
to a specific history source.

**`SkillRegistry` is open, `SkillLoader` is separate (Build 010).**
Following the `ProviderManager`/`BaseProvider` pattern: `SkillRegistry`
dispatches by name; `SkillLoader` handles bulk registration. Future
discovery mechanisms (plugin-based, directory scan) replace only
`SkillLoader` without touching the registry or existing skill contracts.
The `CalculatorSkill` uses a safe AST evaluator (whitelist of allowed
node types) — no `eval()` is called.

**`ChatPage` uses `Agent`, `ModelsPage` uses `engine` directly (Build 008).**
`ModelsPage` was introduced in Build 005 with direct engine access for
provider switching — this is intentional. `ChatPage` never touches the
engine. Each page is responsible for the narrowest interface it needs.

## 4. Remaining Technical Debt

- **`config/settings.py` path is CWD-relative.** `Settings.__init__` opens
  `"config/settings.json"` relative to the process working directory, not
  the package. Breaks if the app is launched from a different directory or
  packaged. Fix: use `Path(__file__).parent / "settings.json"`.
- **`ChatPage` history is local state, not backed by `MemoryManager`.**
  `ChatPage._history` is a plain list in the widget. On conversation
  clear, only the widget's list is reset — `MemoryManager.clear()` is not
  called. A future Build should either wire the clear to `MemoryManager`,
  or rebuild `Task.history` from `memory.conversation.as_message_history()`
  instead of maintaining a separate list.
- **Agent does not yet invoke skills.** `Agent` holds a `SkillRegistry`
  reference but `run()` does not yet parse the user's input to decide
  whether to call a skill or forward to the LLM. Skill dispatch logic
  (keyword matching, prefix detection, or LLM-based routing) is the natural
  next Build.
- **No automated test suite.** `test_engine.py` is a manual print-based
  smoke test. All Build verification was done by inline `python3 -c "..."`
  scripts and headless Qt boot tests. `pytest` should be adopted before the
  skill dispatch logic is implemented.
- **Generic `raise Exception(...)` in `core/engine.py` and
  `providers/provider_manager.py`.** Flagged since the Sprint 4 audit.
  Dedicated exception types (`ProviderNotSelectedError`, etc.) are still
  missing.
- **`core/message.py` `Message` dataclass is unused.** The engine and all
  providers pass plain `dict[str, str]`. Either adopt `Message` and type
  the engine accordingly, or remove the dataclass.
- **`ui/theme.py` / `styles/*.qss` disconnect.** The `.qss` files are
  still empty; theming is handled by Python constants. One mechanism should
  be chosen and the other removed.
- **`MainWindow` SRP is still stretched.** It constructs `Agent`, wires
  `ChatPage`, `ModelsPage`, and `StatusBar`, and handles navigation. Each
  page widget gaining constructor complexity makes `MainWindow._build_ui()`
  harder to reason about. A `PageFactory` or `PageManager` object would
  confine page-construction responsibility.

## 5. Next Recommended Build

**Build 011 — Skill Dispatch.**
Wire the `Agent.run()` path to check for a skill trigger before calling
the LLM. Recommended design:
- Add a lightweight `SkillDetector` that inspects the task input for a
  registered skill name or a prefix (e.g. `/time`, `/calc 2+3`).
- If a skill is triggered: call `skill_registry.execute(name, input)`,
  wrap the `SkillResult` in a `TaskResult`, record it to memory, and
  return — without calling the LLM.
- If no skill matches: fall through to the existing `engine.ask()` path.
- Also fix `ChatPage._clear_conversation()` to call `memory.clear()`.

## 6. Known Limitations

- **Ollama must be running** for the Chat page and the Ollama model list to
  produce real output. All other paths (calculator, current time, failed
  task display) work offline.
- **No threading.** All provider calls block the Qt event loop. For
  Ollama with large models this can cause the window to appear frozen
  during generation. Threading was explicitly excluded from the scope of
  these Builds.
- **Skills are not surfaced in the UI.** The skill system exists in
  `core` and `skills/` but the Chat page offers no skill-selection UI and
  the Models page has no Skills tab. Build 011 (skill dispatch via prefix)
  would make skills usable without a UI change; a Skills Management page
  is a later Build.
- **`MemoryManager` is in-memory only.** History does not survive an
  application restart. File or database persistence is reserved for a
  future Build (`memory/vectordb.py`).
- **Calculator is limited to numeric arithmetic.** Functions (`sqrt`,
  `sin`, etc.) are not supported by design — they require an `ast.Call`
  node, which is explicitly rejected by the safe evaluator.
