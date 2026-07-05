# Claude Rules — Development Philosophy

These are the permanent operating rules for any Build performed on AI
Agent Studio, by Claude or any future contributor. They apply above and
in addition to `docs/CODING_STANDARD.md` (which governs style/typing) and
`docs/ARCHITECTURE.md` (which governs layer boundaries). Where any of
those documents conflict with this one, this one wins for anything
concerning *process and judgment*; `CODING_STANDARD.md` wins for style
mechanics.

## 1. Never break existing code

A Build that changes behavior a user or another module currently depends
on — even to fix something ugly — is not a cleanup, it is a feature
change, and must be explicitly scoped and called out as one. If a Build's
instructions say "do not change behavior," the only acceptable proof that
this rule was followed is running whatever exists (smoke tests, a headless
launch, an explicit manual check) *before and after* the change and
comparing the output. "I only changed typing/comments" is not itself
proof; running the code is.

## 2. Never rewrite working modules

If a module already does its one job correctly, the default action is to
extend it, not to replace it wholesale. A full rewrite is only acceptable
when:
- The module is empty or a placeholder (nothing working to break), or
- The Build's instructions explicitly authorize a rewrite of that specific
  module, or
- The existing module cannot satisfy the new requirement through addition
  alone, and this has been stated plainly before doing it.

Rewriting a file "to make it cleaner" while preserving identical behavior
is permitted (Sprint 4 did this for typing/docstrings) but must be
verified against rule 1 — the rewrite's output must be checked, not
assumed identical.

## 3. Prefer extension over replacement

New functionality should, by default, be added as:
- A new file in the appropriate package, or
- A new method on an existing class, or
- A new, additive parameter with a safe default on an existing function.

Only fall back to modifying existing signatures or logic when extension
genuinely cannot express the requirement — and say so explicitly when
that happens.

## 4. Every change must be reversible

Every Build must be a change someone could cleanly revert (`git revert`)
without needing to also hand-fix unrelated files. This means:
- Don't mix unrelated changes into the same commit.
- Don't leave a Build half-applied (e.g. a new class that depends on a
  method in another file that wasn't actually added).
- Don't silently delete data or history that can't be recovered (this is
  why `git rm --cached` was used for `.pyc` files in Sprint 4, not `rm -rf`
  — the files stayed on disk, only tracking was removed).

## 5. Never invent architecture without checking existing one

Before adding a new package, a new abstraction, or a new pattern, check
whether one already exists that does the same job. `docs/ARCHITECTURE.md`
and `docs/PROJECT_STRUCTURE.md` are the first things to read, not the last.
If the existing architecture seems wrong, say so explicitly and propose a
change — do not quietly work around it with a second, competing pattern
(see the `ui/theme.py` vs. `styles/*.qss` duplication in
`docs/PROJECT_AUDIT.md` as an example of what this looks like when it
happens by accident).

## 6. Keep commits atomic

One Build's changes should tell one story. A commit message should be able
to say, truthfully, what the commit did in one sentence, without an "and
also." If a Build produces both a bug fix and a new feature, that is two
commits, not one — even if they happened in the same session.

## 7. Keep features isolated

A new feature should be addable, and removable, without cascading changes
across unrelated packages. Concretely: a change to `skills/` should not
require touching `providers/` unless the feature genuinely spans both
layers, and if it does, that cross-cutting dependency should be visible
and intentional, not incidental.

## 8. Never add dependencies without justification

Before adding a package to `requirements.txt`:
- Confirm the standard library cannot reasonably do the job.
- Confirm no dependency already in `requirements.txt` already does the
  job.
- State, in the Build's report, what the dependency is for and why it was
  chosen over alternatives.

`requirements.txt` must always be derivable from actual `import`
statements in the codebase — never speculative, never "might need later."
