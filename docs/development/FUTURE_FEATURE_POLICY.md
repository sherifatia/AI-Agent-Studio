# Future Feature Policy

This document governs how new functionality is allowed to enter AI Agent
Studio. It exists to keep the project's actual code matching its actual
needs at every point in time, rather than accumulating speculative
structure that may never be used.

## Features Must Be Implemented Incrementally

Every feature is built in the smallest increment that produces a visible,
verifiable result. A feature is not "started" by scaffolding ten empty
files across five packages — it is started by implementing the first
real, working slice of it, however small, and then extending.

This does not forbid the kind of foundation work done in Sprint 4
(`core/runtime.py`'s class shapes) — that was an explicitly scoped,
one-time exception, requested and bounded by that Build's instructions.
It is not the default way to add a feature.

## No Placeholders Unless Explicitly Requested

Do not create empty files, stub classes, or "reserved for later" modules
as a side effect of implementing something else. Placeholders are only
created when a Build's instructions explicitly ask for architectural
scaffolding ahead of implementation (as Sprint 4 did, deliberately and
narrowly, for the Runtime layer).

If a placeholder already exists (see the many empty modules under
`browser/`, `memory/`, `skills/`, `plugins/`, `workflows/`, and
`ui/widgets/` as of Sprint 4), the correct action when its feature is
finally implemented is to replace the placeholder's docstring-only content
with real code — not to create a second file alongside it.

## No Speculative Code

Do not write code for a use case that hasn't been requested yet, "since
we're in there anyway." This includes:
- Extra configuration options with no current consumer.
- Abstract base classes for a family of implementations where only one
  implementation will ever exist for the foreseeable future.
- Defensive error handling for failure modes that cannot currently occur
  given the code's actual call sites.

If a genuine future need is anticipated, write it down in
`docs/ROADMAP.md` instead of writing code for it.

## No Business Logic Unless Required by the Current Build

A Build should implement exactly the logic its stated scope requires — no
more. If implementing a feature reveals a second, related piece of logic
that would be convenient to add "while we're here," that second piece
belongs in its own Build (see `CLAUDE_RULES.md` rule 6 on atomic commits),
not folded into the current one.

## Explicitly Out of Scope: Future Phases

The following are large, cross-cutting initiatives that are **not** to be
implemented, scaffolded, or designed against until a Build explicitly and
specifically calls for them:

- **Marketplace** — any system for discovering, sharing, or distributing
  skills/plugins/workflows built by third parties.
- **SaaS** — any multi-tenant, hosted, or subscription-billing
  functionality.
- **Business OS** — any broader platform positioning beyond the desktop
  application described in `README.md`.

These are future phases. Do not add configuration keys, database schemas,
UI pages, or abstractions in anticipation of them. If a current Build's
requirements seem to be pulling toward one of these, stop and flag it
rather than proceeding.
