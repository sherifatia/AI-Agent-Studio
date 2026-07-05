# Coding Guidelines

Concrete, mechanical rules for writing code in AI Agent Studio. This
document is the enforceable companion to `docs/CODING_STANDARD.md` (which
explains the *why* behind the existing style) — where they overlap, they
must agree; this file is meant to be checkable line-by-line during review.

## Naming Conventions

- **Modules and packages**: `snake_case` (e.g. `provider_manager.py`,
  `ollama_provider.py`).
- **Classes**: `PascalCase` (e.g. `AIEngine`, `BaseProvider`,
  `OllamaProvider`).
- **Functions and methods**: `snake_case` (e.g. `set_provider`,
  `change_page`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g. `APP_NAME`, `WINDOW_WIDTH`).
- **Private/internal attributes**: prefix with a single underscore
  (`_internal_state`) only when the attribute is genuinely not meant to be
  read from outside the class. Do not prefix attributes that are already
  treated as public elsewhere in the codebase (e.g. `AIEngine.session` and
  `AIEngine.provider` are accessed directly today and should stay
  unprefixed for consistency, unless a Build deliberately encapsulates
  them).
- **Provider class names** follow the pattern `<Name>Provider`
  (`OllamaProvider`, `OpenAIProvider`) — never `<Name>Client` or
  `<Name>Backend`, to stay consistent with `BaseProvider`.

## Typing Rules

- Target Python 3.12 typing syntax: built-in generics (`list[str]`,
  `dict[str, str]`), the `X | None` union form, and `StrEnum` where an
  enum's values are meant to be used as plain strings (as in
  `core.runtime.RuntimeState`).
- Every public function, method, and `__init__` must have parameter and
  return type hints.
- Use `TYPE_CHECKING` imports to type against a class that would otherwise
  create a circular import (see `core/engine.py`'s reference to
  `providers.base_provider.BaseProvider`) rather than restructuring the
  package layout solely to satisfy a type checker.
- Prefer `@dataclass` for plain data containers (`Message`, `Response`,
  `RuntimeEvent`, `RuntimeContext`) over hand-written `__init__` methods
  that only assign fields.

## Documentation Rules

- Every module starts with a one-line (or short paragraph) docstring
  stating its purpose. A placeholder/reserved module's docstring states
  what it is reserved for, not just that it is empty.
- Every public class and method gets a docstring. Trivial getters/setters
  may use a one-line docstring; anything with non-obvious behavior gets
  `Args:` / `Returns:` / `Raises:` sections.
- Do not write a docstring that only restates the function name (e.g.
  `"""Get the value."""` on `get_value()`) — add information a reader
  couldn't get from the signature alone.
- Reference `docs/ROADMAP.md` from a placeholder module's docstring so a
  reader knows where the planned scope lives, rather than duplicating that
  scope inline.

## Error Handling

- Never use a bare `except:`. Always catch the narrowest exception type
  that makes sense for the failure being handled.
- Where a generic `Exception` is already raised intentionally in existing
  code (`core/engine.py`, `providers/provider_manager.py`), do not silently
  narrow or change it as a side effect of an unrelated change — introducing
  a dedicated exception type is a deliberate, separately-scoped Build (see
  `docs/ROADMAP.md`), not something to slip in opportunistically.
- A provider that is not implemented must raise `NotImplementedError`,
  never return a fake/placeholder `Response`.

## Logging Rules

- No logging framework is set up in the project yet. Until one is added
  deliberately (a Build of its own, choosing between the standard library
  `logging` module and any alternative), do not introduce ad hoc `print()`
  debugging into application code (`core/`, `providers/`, `ui/`,
  `config/`). `print()` is acceptable only in standalone scripts that are
  explicitly not part of the application runtime (e.g. `test_engine.py`,
  `bootstrap.py`).
- When a logging framework is introduced, it must be configured in one
  place and imported from there — not instantiated ad hoc per module.

## Dependency Rules

- `requirements.txt` must only ever list packages that are actually
  imported somewhere in the codebase. Before adding a new one, see
  `CLAUDE_RULES.md` rule 8.
- Do not pin exact versions speculatively (i.e. do not write a version
  number that was never actually verified against the installed
  environment) — either verify and pin, or leave unpinned with a comment
  explaining why, as `requirements.txt` currently does.

## Import Rules

- Import submodules directly (`from core.engine import AIEngine`), not
  through a package's `__init__.py`. Package `__init__.py` files in this
  project intentionally contain only a docstring, no re-exports — see
  `docs/CODING_STANDARD.md` ("Package Structure").
- Avoid wildcard imports (`from module import *`), with the one existing,
  deliberate exception of `ui/main_window.py`'s `from .theme import *`,
  which is scoped to a module that only ever contains simple UPPER_CASE
  constants. Do not extend this pattern to any module containing functions
  or classes.
- Group imports in the conventional order: standard library, then
  third-party packages, then local (`core.*`, `providers.*`, `ui.*`,
  `config.*`) imports, each group separated by a blank line.

## Folder Organization

- New source files belong in the package matching their responsibility as
  defined in `docs/development/PROJECT_STRUCTURE.md` — do not create a new
  top-level package without checking that document first and stating why
  none of the existing ones fit.
- Tests, once introduced, belong alongside the module they test or in a
  dedicated `tests/` package mirroring the source layout — this project
  has not yet decided which; the first Build that introduces `pytest`
  should make and document that decision (see `docs/ROADMAP.md`).
