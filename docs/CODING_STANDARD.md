# Coding Standard

These conventions are derived from the style already present in the
codebase, made explicit so future contributions stay consistent. Sprint 4
brought existing code up to this standard without changing behavior; new
code should follow it from the start.

## Style

- Follow **PEP 8**. Four-space indentation, no tabs.
- One blank line between methods inside a class; two blank lines between
  top-level definitions, matching the existing files.
- Prefer explicit imports (`from providers.base_provider import
  BaseProvider`) over wildcard imports, with one existing, deliberate
  exception: `ui/main_window.py` imports constants from `ui/theme.py` via
  `from .theme import *`, because `theme.py` only ever contains simple
  UPPER_CASE constants meant to be used unqualified (`APP_NAME`,
  `WINDOW_WIDTH`, `COLORS`, ...). Do not extend this pattern to modules
  that contain functions or classes.

## Typing

- Target **Python 3.12** typing syntax:
  - Use built-in generics (`list[str]`, `dict[str, str]`) instead of
    `typing.List` / `typing.Dict`.
  - Use the `X | None` union syntax instead of `typing.Optional[X]`.
  - Use `from __future__ import annotations` is not required on 3.12 for
    these forms, and is intentionally omitted for consistency with the
    module style already in the codebase.
- Every public method and function should have parameter and return type
  hints. Constructors (`__init__`) should be typed even when they only
  assign attributes.
- Dataclasses (`core/message.py`, `core/response.py`) should keep using
  `@dataclass` with typed fields rather than plain classes with manual
  `__init__` methods.

## Docstrings

- Every module should open with a one-line docstring describing its
  purpose, even placeholder modules (a placeholder's docstring should say
  what it is reserved for).
- Every public class and method should have a docstring. Keep them short —
  one sentence for simple methods, a short paragraph plus `Args`/`Returns`
  for anything with non-obvious behavior.
- Do not add docstrings that restate the method name without adding
  information (e.g. avoid `"""Get the value."""` on a method called
  `get_value`) — prefer explaining *why* or *what shape* is returned.

## Errors

- Raise specific exceptions where they already exist. Where only a
  generic `Exception` exists today (`core/engine.py`,
  `providers/provider_manager.py`), leave it as-is until a dedicated
  exception type is introduced deliberately — do not silently swallow or
  narrow error handling as a side effect of unrelated changes.
- Never use a bare `except:`. Catch the narrowest exception type that
  makes sense.

## Package Structure

- Every package must have an `__init__.py` with a one-line module
  docstring describing the package's purpose.
- `__init__.py` files should **not** import from their own submodules
  unless there is a specific, documented reason to expose a shortened
  import path. The codebase currently imports submodules directly
  (e.g. `from core.engine import AIEngine`, not `from core import AIEngine`),
  and `__init__.py` files should stay empty of logic to match.

## Placeholders

- An empty file reserved for future work should not be left with zero
  bytes silently. It should contain a module docstring stating what it
  will hold and, where useful, a one-line comment pointing to the relevant
  section of `docs/ROADMAP.md`. It should **not** contain speculative
  classes, TODO-driven stub methods, or fake implementations — an empty
  module with an honest docstring is preferable to a half-written one.

## Provider Contract

- Every provider must subclass `providers.base_provider.BaseProvider` and
  implement `generate(self, messages: list[dict[str, str]]) -> Response`.
- A provider that is not yet implemented must raise `NotImplementedError`
  from `generate()` with a message identifying the provider by name, and
  must be documented as a "TODO provider" in both its own docstring and in
  `README.md`'s provider table. It must not contain partial or fake
  request-building logic ahead of a real implementation.

## Tests

- `test_engine.py` is a manual smoke-test script today, not a `pytest`
  suite. New test coverage should be added as real `pytest` tests once the
  project adopts the dependency (see `docs/ROADMAP.md`); do not grow the
  manual-script pattern further.
