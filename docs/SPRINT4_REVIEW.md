# Sprint 4 Review — Self-Assessment

**Scope of this document:** an honest, critical review of the work done in
the "Sprint 4 Foundation Cleanup" commit (`6181969`). This is a review
document only — no source files were touched to produce it, and it is not
committed.

---

## 1. Files Created

| File | Purpose |
|---|---|
| `docs/PROJECT_AUDIT.md` | Baseline audit of the repository as it stood before Sprint 4 |
| `docs/ARCHITECTURE.md` | Layer boundaries and data flow explanation |
| `docs/ROADMAP.md` | Ordered backlog for unimplemented subsystems |
| `docs/CODING_STANDARD.md` | Style/typing/docstring/placeholder conventions |
| `docs/SPRINT4_REPORT.md` | Change log for Sprint 4 itself |
| `README.md` | Project overview, installation, running instructions |
| `requirements.txt` | `PySide6`, `ollama` — the only two third-party imports found |
| `.gitignore` | Standard Python/Qt ignore rules |
| `core/runtime.py` | `Runtime`, `RuntimeContext`, `RuntimeState`, `RuntimeEvent` — structure only, no logic |

## 2. Files Modified

48 files were touched. They fall into four groups:

1. **Package `__init__.py` files (10)** — added a one-line module docstring each. No imports added.
2. **Previously-empty reserved modules (19)** — `core/navigation.py`, `core/events.py`, `browser/browser_manager.py`, `memory/*.py` (3), `skills/*.py` (2), `plugins/plugin_manager.py`, `ui/widgets/*_page.py` and related (10), `styles/*.qss` (2) — added a docstring/comment stating what each is reserved for.
3. **Implemented modules (13)** — `app.py`, `bootstrap.py`, `config/settings.py`, `core/engine.py`, `core/message.py`, `core/response.py`, `core/session.py`, `providers/base_provider.py`, `providers/provider_manager.py`, `providers/ollama_provider.py`, `providers/openai_provider.py`, `providers/gemini_provider.py`, `providers/openrouter_provider.py`, `ui/main_window.py`, `ui/theme.py`, `ui/widgets/sidebar.py`, `test_engine.py` — added type hints and docstrings.
4. **Git-tracking-only changes (11)** — `__pycache__/*.pyc` files removed from tracking (not deleted from disk).

## 3. Why Each File Was Changed

- **Documentation files were created** because none existed before Sprint 4 — there was no audit, no README, no architecture notes, and no coding standard, which made the repository hard to onboard into or reason about.
- **`requirements.txt` and `.gitignore` were created** because their absence was actively causing harm: compiled bytecode was committed to git, and a fresh clone had no way to know which packages to install.
- **`core/runtime.py` was created** because Sprint 4's stated goal was to prepare for an AI Runtime layer without implementing it yet — the class shapes needed to exist somewhere before real logic is written on top of them.
- **`__init__.py` files were touched** to satisfy the explicit instruction to review every package and ensure a "proper" `__init__.py` — interpreted here as "documented," not "populated with re-exports," since the codebase already imports submodules directly (e.g. `from core.engine import AIEngine`) rather than via package-level exports.
- **Empty reserved modules were given docstrings** rather than left silent, on the reasoning (stated in `docs/CODING_STANDARD.md`) that a zero-byte file gives a future contributor no signal about intent, while a one-line docstring does, without inventing behavior.
- **Implemented modules were typed and documented** in direct response to the sprint's explicit typing/docstring quality bar, while deliberately not touching control flow, so behavior would stay identical — verified by re-running `test_engine.py` and a headless run of `app.py`.
- **`.pyc` files were untracked** because compiled bytecode is a build artifact, not source, and should never have been committed in the first place.

## 4. Architecture Weaknesses

Being self-critical rather than restating what Sprint 4 already flagged:

- **`core/runtime.py` was added with no consumer.** Nothing in the codebase constructs a `Runtime` or references `RuntimeState` outside of the module itself. This is defensible as "foundation before implementation," but it also means the shape hasn't been validated against a real use case yet — `RuntimeContext` bundling exactly `(engine, session)` is a guess about what a runtime will need, not something derived from an actual runtime loop. There's a real risk this shape gets revised once Sprint 5 tries to use it.
- **The typing added is shallow in places.** `core/engine.py` and `providers/base_provider.py` type `Response` and `BaseProvider` only under `TYPE_CHECKING`, which avoids a circular import but also means a static type checker (mypy/pyright) run in strict mode would still flag the runtime-unavailable forward references as strings rather than resolved types in some configurations. This works, but it is a workaround, not a structural fix — the actual fix would be breaking the `core` ↔ `providers` coupling more deliberately (e.g. moving `Response` to a shared, dependency-free module).
- **Navigation is still stringly-typed.** Sprint 4 documented the `Sidebar`/`MainWindow` page-name duplication in the audit but did not fix it, and `core/navigation.py` still has no enum. This was a deliberate scope decision (the sprint explicitly said "do not add features"), but it means the weakness identified in the audit is still live in the code, just now written down.
- **No dependency injection boundary for `Settings`.** `config/settings.py` still reads a hardcoded relative path at construction time with no override hook (env var, constructor argument). Typing it did not address this; it only made the existing fragility more visible via a docstring note.
- **The Runtime foundation has no tests to constrain it.** Because `Runtime.__init__` has no observable behavior beyond storing two values, there was nothing meaningful to test — but that also means Sprint 5 will be the first time this shape is exercised at all.

## 5. Technical Debt Remaining

Carried over from `docs/PROJECT_AUDIT.md`, none of it resolved in Sprint 4
by design:

- Generic `raise Exception(...)` in `core/engine.py` and `providers/provider_manager.py` instead of dedicated exception types.
- `config/settings.py`'s working-directory-relative file path.
- Two parallel, disconnected theming mechanisms (`ui/theme.py` constants vs. `styles/*.qss`, the latter still empty).
- `core/message.py`'s `Message` dataclass remains unused — messages are still passed as raw `dict` objects everywhere.
- No navigation constant/enum shared between `Sidebar` and `MainWindow`.
- No event bus behind `core/events.py`.

New debt introduced by Sprint 4 itself:

- `core/runtime.py` is now sitting unused in the tree, which is itself a small form of debt (dead code, even if intentionally so) until Sprint 5 consumes it.
- 19 modules now contain "reserved" docstrings pointing at `docs/ROADMAP.md`. If the roadmap is ever restructured, all 19 will have stale cross-references — a maintenance cost of the documentation approach chosen here.

## 6. Shortcuts Taken

- **`requirements.txt` has no version pins.** This was a deliberate choice (documented in the file itself) rather than guessing numbers, but it is still a shortcut — a real production dependency file should pin versions, and this one does not.
- **No `pyproject.toml` / packaging metadata was added.** The project still has no way to be installed as a package (`pip install .`); `requirements.txt` alone doesn't provide that.
- **Static analysis was manual, not tooled.** Task 12 asked for a "static review" — this was done via `ast.parse` syntax checks and manual import-graph tracing, not an actual linter/type-checker run (no `ruff`, `mypy`, or `pyright` was executed, and none of the three is set up as a project dependency or config file).
- **`bootstrap.py` was typed but not reconciled with `.gitignore`.** It creates a `logs/` and `data/` folder on demand; `.gitignore` excludes both, which is consistent, but nothing documents that `bootstrap.py` and `.gitignore` need to stay in sync if either list changes.
- **The QSS files were given header comments, not removed.** Given they are unused and empty, a stricter cleanup would have either implemented loading them or deleted them; adding a comment is a middle-ground shortcut that defers the actual decision.

## 7. Missing Tests

- **No `pytest` (or any test framework) is a project dependency.** `test_engine.py` remains a manual script with `print()` statements and no assertions — Sprint 4 documented this but did not fix it.
- **No test exists for any of the newly typed code paths**, including:
  - `core/runtime.py` — zero test coverage of `Runtime`, `RuntimeContext`, `RuntimeState`, `RuntimeEvent`.
  - `providers/provider_manager.py`'s `create()` — no test asserts it raises on an unknown provider name, or returns the correct type for each known one.
  - The three TODO providers — no test asserts they consistently raise `NotImplementedError`.
  - `config/settings.py` — no test covers a missing key returning `None`, or a malformed/missing `settings.json`.
  - `ui/main_window.py` / `ui/widgets/sidebar.py` — no test (even a headless Qt smoke test) is committed to the repo, despite one having been run manually during this sprint's verification.
- **No CI configuration exists** (no GitHub Actions workflow, no pre-commit config) to run any of the above automatically, even once written.

## 8. What Should Be Done in Sprint 5

In priority order:

1. **Adopt `pytest`** and convert `test_engine.py` into real assertions; add it to `requirements.txt` (or a new `requirements-dev.txt`).
2. **Add a minimal test suite** for `providers/provider_manager.py`, the TODO providers' `NotImplementedError` behavior, and `config/settings.py`'s missing-key handling, before writing any new logic on top of them.
3. **Implement the first real behavior in `core/runtime.py`** — most likely a minimal `Runtime.run()` or state-transition method — so the foundation added in Sprint 4 is validated against an actual use case instead of sitting inert.
4. **Wire `core/events.py`** as the dispatch mechanism for `RuntimeEvent`, since `Runtime` will need somewhere to publish events once it does anything.
5. **Introduce a CI workflow** (even a minimal one running syntax checks and the new `pytest` suite) so future sprints don't rely on manual verification the way Sprint 4 did.
6. Only after the above: begin implementing one empty UI page (`chat_page.py` is the natural first candidate, since it's the most direct consumer of `AIEngine`) to start closing the gap between the UI shell and the working engine.

## 9. Sprint 4 Score

**Score: 7 / 10**

**Justification:**

What earns the 7:
- The sprint did exactly what it said it would do — no scope creep, no unauthorized redesign, no provider implementations that were explicitly out of bounds, no behavior change (verified by re-running the smoke test and a headless app launch before and after).
- Every deliverable listed in the original task list was produced: audit, README, requirements, gitignore, cache removal, three docs files, package review, provider review, UI review, the runtime foundation, typing pass, static review, and this report.
- The documentation is specific to this codebase rather than generic boilerplate — it references real file names, real line-level issues, and real open questions rather than templated advice.

What holds it back from higher:
- **Nothing was actually fixed at a behavioral level** — every piece of technical debt identified in `docs/PROJECT_AUDIT.md` is still present after Sprint 4. This was in-scope per the instructions ("do NOT change existing behavior"), but it means the sprint is entirely additive/organizational, not corrective. A "9" or "10" sprint would have paired the audit with at least one safe, behavior-preserving structural fix (e.g. the navigation-string duplication, which could have been resolved with a shared constant without changing observable behavior).
- **The static review (task 12) was manual rather than tool-driven.** A stronger execution would have added `ruff`/`mypy` configuration as part of "production-ready" preparation, even without requiring the codebase to pass strict mode yet.
- **`core/runtime.py` is speculative.** It is honest, minimal, and matches the letter of the instructions, but its class shapes are a guess about future needs rather than something pressure-tested against a real Sprint 5 use case. There is a real chance it gets partially reshaped once implementation starts.
- **No CI, no pinned dependencies, and no automated tests** — three things that are conventionally part of "production-ready," and none of which were addressed, even though `requirements.txt` and `.gitignore` (also conventionally part of "production-ready") were.

A 7 reflects clean, disciplined execution of a narrow, well-scoped cleanup sprint, with the honest caveat that "cleanup" here means "documented and typed," not "hardened" — the codebase is easier to reason about after Sprint 4, but not yet meaningfully more robust.
