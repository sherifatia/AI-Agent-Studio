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
Full syntax scan (`python3 -c "compile(open('core/agent.py').read(), 'agent.py', 'exec')"`)
and import verification of all changed modules.

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

*(Future Builds: add new entries above this line, using the template
above.)*
