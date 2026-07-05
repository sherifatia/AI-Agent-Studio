# Build 001.1 Report — Foundation Stabilization

**Type:** Foundation cleanup — no new features, no behavior changes.
**Based on:** `docs/BUILD001_REVIEW.md` (Senior Architect Audit of Build 001).
**Status at completion:** All verification checks pass. No commit, no push.

---

## Files Modified

| File | What changed | Why |
|---|---|---|
| `core/app_info.py` | Removed `COMPANY` as a duplicate field; made it a `@property` returning `NAME` | Eliminated the duplicate `"AI Agent Studio"` literal that existed in two fields of the same class. `COMPANY` and `NAME` share one canonical value; if they ever diverge a field can be promoted in one place. |
| `core/logging_setup.py` | Added an ordering guard inside `get_logger()`: if `setup_logging()` has not yet been called, call it with defaults before returning | Fixed the footgun identified in the architect review: modules that obtain a logger at import time (before the LOGGING startup service runs) now always get a functional logger with handlers attached, not Python's silent last-resort stderr handler. |
| `core/startup.py` | Replaced `StartupSequence` + closed `StrEnum StartupPhase` with `ServiceLoader` + open string constants `StartupPhase` | The closed enum was the primary structural weakness identified in the review (Q4). Future Builds can now register a new service with any string name without touching this file. `StartupPhase` is now a plain class of string constants — readable at call sites, not constrained to enum members. `StartupSequence` is kept as a backward-compatibility alias (delegates to `ServiceLoader`) so no existing code breaks. |
| `ui/theme.py` | Removed `APP_NAME` and `WINDOW_TITLE` — both were frozen copies of `AppInfo` values, not theme constants. Removed the `core.app_info` import entirely. | `ui/theme.py` is the home of Qt layout dimensions and colour tokens. Identity metadata (name, title) belongs in `core.app_info.APP_INFO`. The two aliases were documented as a duplication issue in the review (Q2); they are now gone. No other file imported them from `theme.py` directly — `main_window.py` used them via wildcard import, and the wildcard import itself is also removed (see `ui/main_window.py`). |
| `ui/main_window.py` | Replaced direct `QSettings` usage with `WindowStateManager`; removed `config.settings.Settings()` direct instantiation; removed wildcard `from .theme import *`; changed signature to `__init__(self, initial_provider: str = "")` | Three distinct fixes: (1) QSettings is now fully isolated in `WindowStateManager` — `MainWindow` has zero QSettings call sites. (2) Settings loading moves to the CONFIGURATION startup service (where it belongs), and `MainWindow` receives the result as a constructor argument, satisfying DIP. (3) Wildcard import replaced with explicit named imports from `ui.theme`, eliminating invisible name pollution. |
| `app.py` | Updated to use `ServiceLoader` instead of `StartupSequence`; moved `config/settings.json` reading into the CONFIGURATION service; passes `initial_provider` to `MainWindow` | Consistent with the new `ServiceLoader` API. Config reading now happens in the named configuration phase, not inside a UI class's `__init__`. `MainWindow` receives its startup data from the loader context, not by reaching into the config layer itself. |

## Files Created

| File | Responsibility |
|---|---|
| `ui/window_state.py` | `WindowStateManager` — wraps all `QSettings` read/write behind a clean abstraction. Owns the two keys (`window/geometry`, `window/state`), the QSettings organization/application scope (from `core.constants`), and all `saveGeometry`/`restoreGeometry` calls. `MainWindow` calls only `save(window)` and `restore(window)` — it never constructs or calls `QSettings` directly. |

---

## Architecture Decisions

**`COMPANY` as a property vs. separate field.**
`@dataclass(frozen=True)` supports properties alongside fields. Making
`COMPANY` a property that returns `NAME` keeps the field count accurate
(one identity concept, one field) while preserving the `APP_INFO.COMPANY`
access pattern used by `core/constants.py`. If `COMPANY` and `NAME` ever
need to diverge, one field promotion handles it in one place.

**`StartupPhase` as a plain class of constants, not removed.**
Removing `StartupPhase` entirely would have forced every call site in
`app.py` to use raw strings (`loader.register("logging", ...)`) with no
typo protection. Keeping it as a plain class of string constants preserves
readability and discoverability while no longer constraining the loader to
only those six values. Any string is a valid service name in `ServiceLoader`.

**`StartupSequence` kept as a backward-compatibility alias.**
`StartupSequence` is used by no file in this repo other than `app.py`
(which has already been updated), but keeping the alias costs nothing and
makes a future git bisect or branch merge safer. It is marked deprecated
in its docstring.

**`WindowStateManager` is not injected into `MainWindow`.**
The review recommended constructor injection for QSettings. `MainWindow`
creates its own `WindowStateManager` internally — this is a pragmatic
choice for this Build: `WindowStateManager` has no interface yet, so
injecting it would require creating an abstract base class or a protocol
purely for the sake of testability, which is speculative abstraction per
`docs/development/FUTURE_FEATURE_POLICY.md`. What matters today is that
`QSettings` is gone from `MainWindow`'s code. If `MainWindow` needs to be
tested with a fake window-state store in a future Build, a `Protocol` can
be added then.

**Config reading in CONFIGURATION service, not MainWindow.**
`_load_configuration()` in `app.py` now reads `settings.json` and places
the result in the shared context dict. `MainWindow` receives
`initial_provider` as a plain string constructor argument. This cleanly
separates the config-reading concern (startup layer) from the display
concern (UI layer) without redesigning the window or adding a new
abstraction.

---

## Verification Results

| Check | Result |
|---|---|
| Repo-wide syntax scan (`ast.parse`, every `.py` file) | 0 errors |
| Full import check (28 modules across all layers) | All import cleanly, no circular dependencies |
| `test_engine.py` output | Byte-identical (`True` / `FakeProvider` / `AI Agent Studio يعمل بنجاح 🎉`) |
| Headless boot via real `ServiceLoader` (6 services) | All 6 services log and complete; `logs/application.log` confirms correct sequence |
| Window title | `"AI Agent Studio — v0.1.0"` (from `APP_INFO.window_title`, not a copy) |
| Status bar provider | `"Provider: ollama"` (read in CONFIGURATION service, passed to `MainWindow`) |
| `WindowStateManager.save()` | Called without error on a live headless `QMainWindow` |
| `print()` in application code | None (only in `test_engine.py` and `bootstrap.py`, both non-application scripts) |
| `QSettings` call sites outside `window_state.py` | None (only docstring/comment references in `main_window.py` and `constants.py`) |
| `logging.getLogger()` outside `logging_setup.py` | None |
| Duplicate `"AI Agent Studio"` literals in application code | One — `AppInfo.NAME` field definition (the canonical source; not a duplication) |

---

## Remaining Issues

These are known, pre-existing issues **not introduced** by this Build.
They are carried forward from `docs/BUILD001_REVIEW.md` and
`docs/PROJECT_AUDIT.md`.

- **`ui/theme.py` / `styles/*.qss` disconnect** — two theming mechanisms
  exist in parallel. Neither was changed here. Reconciliation is tracked
  in the Roadmap.
- **`MainWindow` still has multiple responsibilities** — layout, menu,
  navigation, and delegation to `WindowStateManager` and `DialogManager`.
  The God-Object trend is reduced (config reading and QSettings are
  gone) but not eliminated. Extracting a proper page router once real
  page widgets exist will be the natural next step.
- **`CommandManager` and `NotificationManager` have no UI consumers** —
  they are infrastructure awaiting a Build that wires them in.
- **`WindowStateManager` is not injected** — `MainWindow` constructs it
  internally. Testability via a fake store requires a Protocol, deferred
  to a future Build per the policy on speculative abstraction.
- **No `pytest` suite** — `test_engine.py` remains a manual print-based
  smoke test. Tracked in Roadmap as the first item of the next dedicated
  cleanup Build.
- **`SETTINGS_APPLICATION = "AIAgentStudioDesktop"`** in
  `core/constants.py` is a plain string not derived from `AppInfo`. It is
  an internal opaque key (must never change once in production, or saved
  geometry is lost), so sourcing it from `AppInfo` would be inappropriate.
  Documented here for completeness; no fix required.

## Known Limitations

- The `LOGGING` service's own "Starting service: logging" line is logged
  by `core.startup` before `setup_logging()` runs inside the service
  action. This means it appears in the console (via the get_logger guard)
  but uses the default format, not the application's configured format.
  All subsequent service lines log correctly. This is a cosmetic ordering
  artefact, not a functional issue.
- Headless geometry-restore testing is constrained by the Qt offscreen
  platform's 800×800 virtual screen. The `WindowStateManager` mechanism
  itself is standard Qt and behaves correctly on a real display.

---

*No commit. No push. Waiting for review.*
