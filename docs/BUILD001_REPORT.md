# Build 001 Report — Professional Application Shell

**Goal:** Transform AI Agent Studio from a project skeleton into a real
desktop application shell — logging, startup, metadata, and management
foundations — without touching Runtime, Memory, Skills, Browser,
Workflows, Marketplace, SaaS, or Business OS, and without regressing any
existing behavior.

This Build followed `docs/development/BUILD_WORKFLOW.md`: Planning →
Implementation → Verification → Review → Commit. Push was explicitly
withheld per this Build's instructions.

---

## Files Created

| File | Responsibility |
|---|---|
| `core/app_info.py` | Single source of truth for app metadata (name, version, build number, author, repository, company, window title) |
| `core/constants.py` | Cross-cutting, non-styling constants (log paths/format, `QSettings` keys, status strings) |
| `core/logging_setup.py` | Configures the root logger with console + `logs/application.log` file handlers |
| `core/startup.py` | `StartupPhase`, `StartupStep`, `StartupSequence` — the ordered boot path |
| `core/error_handler.py` | Installs a global `sys.excepthook` that logs uncaught exceptions |
| `core/command_manager.py` | `Command`/`CommandManager` — register/execute named actions by ID |
| `core/notification_manager.py` | `NotificationLevel`/`Notification`/`NotificationManager` — tracks and logs notifications, with a subscriber hook |
| `core/version_manager.py` | Thin service over `AppInfo` for version/build access and a reserved `check_for_updates()` |
| `ui/resource_manager.py` | Resolves expected paths for icons/styles/fonts/future assets (no assets implemented) |
| `ui/theme_manager.py` | `ThemeMode` (Light/Dark/Auto) + `ThemeManager` — switchable architecture, applies existing (empty) `styles/*.qss` |
| `ui/dialog_manager.py` | Centralized dialogs: functional About, placeholder Settings, generic Yes/No confirm |

## Files Modified

| File | Change | Why |
|---|---|---|
| `app.py` | Rebuilt `main()` around `_build_startup_sequence()` | Task 1 — one startup path with named phases |
| `ui/main_window.py` | Added: window title from `AppInfo`, minimum size, `QSettings`-backed geometry/state persistence, `StatusBar` wiring, `Help > About` menu, provider display sourced from `config/settings.json` | Tasks 6, 7 |
| `ui/theme.py` | `APP_NAME`/`WINDOW_TITLE` now sourced from `core.app_info.APP_INFO` instead of a duplicated literal; added `MIN_WINDOW_WIDTH`/`MIN_WINDOW_HEIGHT` | Task 3 (centralize metadata), Task 4 (no duplicated values) |
| `ui/widgets/sidebar.py` | Added `PAGE_ICONS` mapping (icon placeholders, no icon files), `EXPANDED_WIDTH`/`COLLAPSED_WIDTH` constants, `toggle_collapse()` | Task 8 |
| `ui/widgets/statusbar.py` | Implemented (was an empty Sprint 4 placeholder docstring — no working logic existed to break) | Task 7 |

No other existing file's behavior was changed. `core/engine.py`,
`core/session.py`, `core/message.py`, `core/response.py`, every
`providers/*.py` file, and `test_engine.py` were **not touched** in this
Build.

---

## Architecture Decisions

- **`AppInfo` is a frozen dataclass singleton (`APP_INFO`).** Every module
  needing app metadata imports this one instance rather than re-declaring
  strings. `ui/theme.py`'s pre-existing `APP_NAME` now reads from it
  instead of duplicating the literal — this was a deliberate, minimal
  change to an existing file, justified by `docs/development/CLAUDE_RULES.md`
  rule 8's "no duplicated values" and verified not to change the string's
  actual value (`"AI Agent Studio"` either way).
- **`VersionManager` wraps `AppInfo` rather than storing its own version.**
  This avoids the version number existing in two places, at the cost of
  `VersionManager` having very little logic of its own today — acceptable
  since its stated purpose (task 14) is to be the place future
  update-check behavior attaches to, not to own the value itself.
- **`StartupSequence` is a generic step-runner, not a hardcoded boot
  script.** `app.py`'s `_build_startup_sequence()` registers six phases
  as closures over a shared `context` dict, so a future Build can call
  `sequence.register_phase(...)` to insert new loading work (e.g. asset
  preloading, provider health checks) without modifying `core/startup.py`
  itself — directly satisfying task 1's "prepare startup for future
  loading tasks."
- **Window geometry persistence uses `QSettings`, not a custom file.**
  This is the standard Qt mechanism for exactly this purpose, avoids
  inventing a new persistence format, and writes to the OS's native
  config location (verified at `~/.config/AI Agent Studio/AIAgentStudioDesktop.conf`
  in this environment), not inside the repository.
- **`ResourceManager` resolves paths only — it does not load or cache
  anything.** Per task 5's explicit "do NOT implement assets," it is a
  pure path function with no dependency on files actually existing yet.
  `ThemeManager._apply()` checks `Path.exists()` before reading, so
  calling it today (with only the Sprint 4 placeholder `.qss` comments in
  place) safely no-ops rather than erroring.
- **`DialogManager.show_about()` is fully implemented; `show_settings()`
  is an honest placeholder.** About has no unimplemented dependency, so
  building it for real (rather than stubbing it) was the more
  professional choice and gives an immediately visible, working result
  (`Help > About` in the menu bar). Settings depends on
  `ui/widgets/settings_page.py`, which remains an empty reserved module —
  so `show_settings()` shows a plain "not implemented yet" message rather
  than a fake settings UI, per `docs/development/FUTURE_FEATURE_POLICY.md`.
- **`CommandManager` and `NotificationManager` are registered as
  standalone infrastructure, not yet wired into the UI.** Task 10 and 11
  ask for "foundation" and "infrastructure" specifically, and no task in
  this Build's list asked for a command palette, toolbar, or toast
  widget. Wiring them into the UI now would have been scope creep beyond
  what was requested — they are verified working in isolation (see
  Verification Results) and ready for a future Build to attach to actual
  UI controls.
- **A minimal `Help` menu was added to `MainWindow`.** This was not
  explicitly listed as a task, but was the only reasonable way to give
  `DialogManager.show_about()` a real, user-reachable entry point without
  which "About" would only be callable from code — and a menu bar is
  standard, expected chrome for "a real desktop application," consistent
  with the Build's stated goal. It does not redesign the existing
  sidebar/workspace layout; it is purely additive.

## Technical Debt

Carried over, unchanged, from `docs/PROJECT_AUDIT.md`:
- Generic `raise Exception(...)` in `core/engine.py` /
  `providers/provider_manager.py`.
- `config/settings.py`'s working-directory-relative file path (this
  Build's use of `Settings()` in `MainWindow._load_status_from_settings()`
  inherits this limitation — wrapped in a `try/except` so it degrades to
  a placeholder display rather than crashing the window).
- `core/message.py`'s `Message` dataclass remains unused.

New, introduced by this Build:
- `CommandManager` and `NotificationManager` currently have no consumer
  in the running application — they exist, are tested in isolation, but
  nothing calls `execute_command()` or `notify()` from the UI yet. This
  is intentional scope discipline (see Architecture Decisions above), but
  it is still dead-from-the-UI's-perspective code until a future Build
  wires it in.
- `ThemeManager` can switch modes and would apply a real stylesheet if one
  existed, but `styles/dark.qss` / `styles/light.qss` are still the empty
  Sprint 4 placeholders — so switching themes today has no visual effect.
  This is the expected, documented state per task 9's "no advanced
  styling."
- The sidebar's `PAGE_ICONS` mapping references icon file names
  (`dashboard.svg`, etc.) that do not exist under `assets/icons/` — no
  `assets/` directory was created in this Build, consistent with task 5's
  "do NOT implement assets."

## Known Limitations

- **Headless verification and real desktop geometry differ.** Window
  geometry save/restore was verified working end-to-end via `QSettings`,
  but the exact pixel values observed in this session were affected by
  the `offscreen` Qt platform's small virtual screen (800×800) used for
  headless testing in this environment. The persistence mechanism itself
  is standard Qt behavior and unaffected by this; a real display will not
  have this constraint.
- **The `LOGGING` startup phase's own announcement is not captured in the
  log file.** `StartupSequence.run()` logs "Startup phase: logging"
  *before* invoking that phase's action, but log handlers are attached
  *inside* that action (`setup_logging()`). Every subsequent phase logs
  correctly; only this first line is lost. Cosmetic, not a functional
  issue — noted here rather than silently left for someone else to
  puzzle over.
- **`NotificationManager` and `CommandManager` have no persistence.**
  Both are in-memory only for the lifetime of the process, which is
  correct for their current scope (no requirement to persist either was
  stated).

## Future Improvements

(Explicitly out of scope for this Build; see
`docs/development/FUTURE_FEATURE_POLICY.md` and `docs/ROADMAP.md`.)

- Wire `CommandManager` to real menu items/toolbar actions and (per task
  10's stated future direction) keyboard shortcuts.
- Wire `NotificationManager` to a visible UI surface (status bar
  transient messages already exist via `StatusBar.show_message()`; a
  toast/banner widget would be the natural next step).
- Implement real icon assets under `assets/icons/` and wire them into
  `Sidebar.PAGE_ICONS` via `ResourceManager.get_icon_path()`.
- Implement real `styles/dark.qss` / `styles/light.qss` content so
  `ThemeManager` has a visible effect.
- Implement the Settings page (`ui/widgets/settings_page.py`) and replace
  `DialogManager.show_settings()`'s placeholder message with a real
  dialog or workspace page.
- Fix the `LOGGING` phase's self-announcement ordering, if ever judged
  worth the added complexity of a bootstrap-level console handler.

## Verification Results

| Check | Result |
|---|---|
| Full syntax scan (`ast.parse`, every `.py` file) | 0 errors |
| Full import verification (29 modules, all layers) | All import cleanly |
| `test_engine.py` output before vs. after this Build | Byte-identical (`True` / `FakeProvider` / `AI Agent Studio يعمل بنجاح 🎉`) |
| Headless application boot (`QT_QPA_PLATFORM=offscreen`) through the real `_build_startup_sequence()` | Boots cleanly; log file shows all phases except the first (see Known Limitations); window title, status bar provider/version, and theme all populate correctly |
| Window geometry persistence across two separate process runs | Confirmed via `QSettings`, written to `~/.config/AI Agent Studio/AIAgentStudioDesktop.conf` (outside the repository) |
| `Sidebar.toggle_collapse()` | Confirmed: 220px ⇄ 60px width toggle works |
| `CommandManager` register/execute | Confirmed via isolated script (register + execute + error on unknown ID) |
| `NotificationManager` notify + subscriber | Confirmed via isolated script (listener received the raised notification) |
| `VersionManager` | Confirmed returns values matching `AppInfo` exactly |
| `git status` before commit | Only the files listed above changed; no unrelated files touched |
