# Build 001 Review — Senior Architect Audit

**Scope:** Read-only architectural audit of Build 001 ("Professional
Application Shell", commit `e0780c8`). No code was modified to produce
this review, and this document is not committed.

---

## 1. Is QSettings isolated behind one abstraction?

**No.** `QSettings` is instantiated and called directly inside
`ui/main_window.py` — there is no `WindowStateManager` or equivalent
wrapper. It leaks in three places in that file:

- **Construction:** `self._qsettings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)` (`__init__`)
- **Read path:** `_restore_geometry()` calls `self._qsettings.value(...)` twice, directly against the Qt API, then calls `self.restoreGeometry(...)` / `self.restoreState(...)` itself
- **Write path:** `closeEvent()` calls `self._qsettings.setValue(...)` twice, directly

`MainWindow` — a presentation-layer class — therefore owns persistence
logic (constructing a `QSettings` instance, knowing its key names, calling
its read/write API) in addition to its own layout/navigation
responsibilities. There is no interface a non-Qt test or an alternative
persistence backend (e.g. a JSON file, for parity with `config/settings.json`)
could substitute in. This is a direct leak, not an edge case.

## 2. Is AppInfo the single source of truth?

**Mostly, with two caveats — one real duplication and one redundant alias.**

- **No duplicated *value* was found across executable code.** Every
  module that needs `NAME`, `VERSION`, `BUILD_NUMBER`, `AUTHOR`,
  `REPOSITORY`, or `COMPANY` reads it from `core.app_info.APP_INFO`
  (`core/version_manager.py`, `ui/widgets/statusbar.py`,
  `ui/dialog_manager.py`, `ui/theme.py`).
- **Redundant alias, not duplication:** `ui/theme.py` defines
  `APP_NAME: str = APP_INFO.NAME` and
  `WINDOW_TITLE: str = APP_INFO.window_title`. These are computed once at
  import time and copied into `ui.theme`'s module namespace. Because
  `AppInfo` is a frozen dataclass this cannot go stale at runtime, but it
  means there are now **two names for the same value**
  (`core.app_info.APP_INFO.NAME` and `ui.theme.APP_NAME`) rather than one
  canonical accessor. A future refactor of `AppInfo` (e.g. making the name
  configurable) would silently leave `ui.theme.APP_NAME` frozen at the
  value captured on first import.
- **One genuine coincidental duplication inside `AppInfo` itself:**
  `NAME = "AI Agent Studio"` and `COMPANY = "AI Agent Studio"` are two
  distinct fields sharing an identical literal. This is low severity
  (both live in the same class, one edit away from correct if they ever
  diverge) but is, technically, a duplicated constant.
- **Duplication outside code, in documentation:** `README.md` hardcodes
  `"AI Agent Studio"` in prose (not sourced from `AppInfo`). This cannot
  drift silently in a way that breaks the application, but it means the
  app's display name now exists in a place `AppInfo` does not govern.

**Duplicated constants — full list:**
1. `AppInfo.NAME` / `AppInfo.COMPANY` — identical literal, two fields, one class.
2. `ui.theme.APP_NAME` — a frozen copy of `AppInfo.NAME`, not a live reference.
3. `ui.theme.WINDOW_TITLE` — a frozen copy of `AppInfo.window_title`.
4. `README.md`'s three prose occurrences of `"AI Agent Studio"` — outside `AppInfo`'s control entirely.

## 3. Is logging centralized?

**Yes, with one caveat worth flagging.** Exactly one file calls
`logging.getLogger()` directly: `core/logging_setup.py` itself (once
inside `setup_logging()` for the root logger, once inside `get_logger()`).
Every other module obtains a logger via `get_logger(__name__)`:

```
app.py
core/command_manager.py
core/error_handler.py
core/notification_manager.py
core/startup.py
core/version_manager.py
ui/dialog_manager.py
ui/main_window.py
ui/theme_manager.py
```

Zero direct `logging.getLogger()` calls exist outside `core/logging_setup.py`.

**Caveat:** `get_logger()` does not itself guarantee `setup_logging()` has
run. Any module that calls `get_logger(__name__)` and logs before
`app.py`'s `LOGGING` startup phase executes `setup_logging()` will log
through Python's default "handler of last resort" (stderr, WARNING+
only) — silently skipping the file handler and the configured format.
This is not a *decentralization* of logging, but it is a real ordering
dependency that centralization alone does not enforce.

## 4. Can StartupSequence register future startup services?

**Partially — steps yes, phases no.**

- **Yes:** `StartupSequence.register_phase(phase, action)` can be called
  any number of times, including multiple times with the *same*
  `StartupPhase` value, and every registered step runs in registration
  order. A future Build can freely add new `action` callables under any
  existing phase (e.g. more `RESOURCES`-phase work) without touching
  `core/startup.py`.
- **No, for genuinely new phase categories:** `StartupPhase` is a closed
  `StrEnum` with exactly six members (`LOGGING`, `CONFIGURATION`,
  `APPLICATION_INFO`, `RESOURCES`, `USER_INTERFACE`, `READY`). A future
  Build cannot introduce a conceptually new phase (e.g. `PROVIDER_HEALTH_CHECK`
  as its own named stage) without modifying the enum in `core/startup.py`
  itself — which is a direct edit to existing, working code, not an
  extension. This is a real constraint on task 1's "prepare startup for
  future loading tasks," not a full solution to it.

## 5. Does StatusBar own state, or is it a passive UI component?

**Passive.** `ui/widgets/statusbar.py`'s `StatusBar` holds no state
variables of its own beyond the `QLabel` widgets' displayed text —
there is no `self.current_provider` field or similar; `set_provider()`
writes straight into `self.provider_label`'s text and nothing reads it
back except Qt's own rendering. It has no reference to `core.engine.AIEngine`,
`core.session.Session`, or any other source of true application state.

Concretely, this means:
- `StatusBar` cannot answer "what is the current provider?" except by
  reading rendered label text — an anti-pattern if any future code needed
  that value programmatically.
- If the active provider changes elsewhere in the app (once `AIEngine` is
  wired to the UI), nothing updates `StatusBar` automatically — it only
  reflects whatever `MainWindow._load_status_from_settings()` pushed into
  it once, at construction time. There is no observer/subscriber
  relationship between `StatusBar` and any state owner. It is a mirror,
  not a source.

## 6. Architecture Weaknesses Introduced by Build 001

1. `QSettings` used directly inside `MainWindow` with no abstraction (see Q1).
2. `config.settings.Settings()` is *also* instantiated directly inside
   `MainWindow` (`_load_status_from_settings()`), meaning `MainWindow` now
   talks to two separate persistence mechanisms (`QSettings` for window
   geometry, `Settings`/JSON for provider display) with no unifying
   abstraction over either.
3. `MainWindow` has grown into a class with five distinct
   responsibilities: layout construction (`build_ui`), menu construction
   (`build_menu`), config loading (`_load_status_from_settings`), window
   state persistence (`_restore_geometry`, `closeEvent`), and navigation
   handling (`change_page`). No single one of these was wrong to add, but
   together they are the beginning of a God Object.
4. `core.constants` now imports `core.app_info` — a "constants" module is
   conventionally expected to be a dependency-free leaf; it no longer is.
5. `CommandManager` and `NotificationManager` are fully built and tested
   in isolation but have zero consumers in the running application —
   dead weight from the application's actual execution graph until a
   future Build wires them in.
6. `StartupPhase` is a closed enum (see Q4) — the extensibility task 1
   asked for is only partially satisfied.
7. `ThemeManager.set_mode()` requires a live `QApplication` instance to
   have any visible effect, coupling theme-selection logic to Qt
   application lifecycle ordering that isn't enforced by any type or
   interface — passing `app=None` silently no-ops instead of raising,
   which could hide a caller's ordering mistake.
8. `get_logger()` does not enforce that `setup_logging()` has already
   run (see Q3) — a latent footgun for any future entry point that isn't
   `app.py`'s `main()`.

## 7. SOLID Principle Violations

- **Single Responsibility Principle — violated.** `MainWindow` (see
  weakness 3 above) mixes UI layout, menu construction, two different
  persistence mechanisms, and navigation dispatch in one class.
- **Open/Closed Principle — violated.** `StartupPhase`'s closed enum
  (Q4) means adding a new *category* of startup work requires modifying
  `core/startup.py` rather than extending it purely by registration.
- **Dependency Inversion Principle — violated.** `MainWindow` directly
  constructs its own concrete dependencies — `QSettings(...)`,
  `Settings()`, `DialogManager()`, `StatusBar()` — inside `__init__`
  rather than receiving any of them via constructor injection or an
  abstraction. A high-level class (the window) is wired directly to
  low-level, concrete implementations, with no seam for substituting a
  fake `Settings` or a fake window-state store in a test.
- **Interface Segregation Principle — not violated by this Build.** No
  new interface/abstract base class introduced in Build 001
  (`BaseProvider` predates it) forces a consumer to depend on methods it
  doesn't use.
- **Liskov Substitution Principle — not violated by this Build.**
  `StatusBar(QStatusBar)` and the various dataclasses/enums added do not
  alter or narrow any inherited contract in a way that would break
  substitutability.

## 8. Unnecessary Coupling

1. `ui/main_window.py` ↔ `config.settings.Settings` — direct import and
   instantiation of a concrete config-loading class inside a UI class.
2. `ui/main_window.py` ↔ `PySide6.QtCore.QSettings` — direct use of a
   concrete Qt persistence API inside a UI class (see Q1).
3. `core/constants.py` ↔ `core/app_info.py` — a constants module, which
   should be a dependency-free leaf, now imports another core module
   (justified to avoid a literal duplication, per Q2, but still a
   coupling that didn't exist before Build 001).
4. `ui/theme_manager.py` ↔ `PySide6.QtWidgets.QApplication` — theme mode
   *selection* (a plain enum decision) is coupled to a concrete Qt
   application object for *application*, with no interface separating
   "decide the mode" from "apply the mode to a Qt app."
5. `ui/main_window.py`'s fan-in: the class now directly imports from five
   different modules outside its own package
   (`config.settings`, `core.constants`, `core.logging_setup`,
   `ui.dialog_manager`, `ui.widgets.statusbar`) in addition to its
   pre-existing `ui.widgets.sidebar` and `ui.theme` imports — reinforcing
   weakness 3 (SRP) as a coupling metric, not just a responsibility count.

## 9. Can Build 002 start safely?

**YES**

No broken imports, no syntax errors, no regressions in `test_engine.py`
or existing provider/engine behavior were found — Build 001 is
functionally sound and its own verification claims check out under this
audit. The issues listed above (Q1, Q2, Q6, Q7, Q8) are coupling and
responsibility-boundary problems, not correctness defects, and none of
them currently produce incorrect behavior.

This is a conditional yes, not an unconditional one: Build 002 should not
deepen the `MainWindow` God-Object trend (weakness 3) by wiring further
business logic (e.g. Runtime or Skills hooks) directly into it, and
should not add a second, competing settings-persistence mechanism beyond
the two (`QSettings`, `config.settings.Settings`) that already exist
uncoordinated inside that class. Extracting a `WindowStateManager` (to
own `QSettings`, per Q1) and routing `MainWindow`'s config reads through
a constructor-injected settings dependency (per the DIP violation in Q7)
are the two highest-leverage fixes, and are recommended as the first
items of Build 002 or a dedicated Build 001.5 cleanup — but their absence
does not block Build 002 from starting.
