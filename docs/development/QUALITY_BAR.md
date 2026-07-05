# Quality Bar

This defines the minimum acceptance criteria every Build must meet before
it can be committed. This is a stricter, pass/fail companion to
`docs/development/REVIEW_CHECKLIST.md` — the checklist is for judgment
calls; this document is for hard gates.

A Build that fails any item below is not done, regardless of how complete
its feature work looks.

## No Warnings

- No deprecation warnings introduced by new code.
- No Qt-level warnings introduced beyond what already exists in the
  current UI shell (e.g. the pre-existing `propagateSizeHints()` warning
  observed when running headlessly is a known, pre-Sprint-4 condition —
  new code must not add to that list).
- If a warning cannot be avoided (e.g. it originates from a third-party
  library), it must be documented in the Build's report, not silently
  ignored.

## No Syntax Errors

- Every changed `.py` file must parse cleanly (`ast.parse` or equivalent)
  before commit. This is non-negotiable and takes seconds to check.

## No Broken Imports

- Every changed module must import successfully with its actual
  dependencies installed. This must be verified by actually importing it
  in this Build's session, not inferred from reading the code.

## No Dead Code

- No unreachable branches.
- No unused variables, imports, or parameters left behind after a change.
- No commented-out code left in place "just in case" — if it needs to
  come back, git history already has it.

## No Duplicated Code

- Before writing new logic, check whether an equivalent already exists
  elsewhere in the codebase (see `REVIEW_CHECKLIST.md`'s "Does it
  introduce duplicate logic?").
- Two modules solving the same problem in different ways (e.g. the
  `ui/theme.py` / `styles/*.qss` situation) is acceptable only when it is
  pre-existing and already documented as technical debt — never
  acceptable as something newly introduced by a Build.

## No Unnecessary Abstraction

- Do not introduce an interface, base class, or factory for something that
  has, and will foreseeably continue to have, exactly one implementation.
- `BaseProvider` and `ProviderManager` are justified because there are
  multiple real (or explicitly planned) providers. A hypothetical
  `BaseThemeLoader` for a single theme source would not be.

## No Feature Without a Visible Result

- A feature is not complete until it produces something observable: a
  passing test, a script's printed output, a UI element that actually
  renders, or an API that can actually be called and returns a real
  value.
- "The code is written but I haven't run it" does not meet this bar. See
  `docs/development/BUILD_WORKFLOW.md`'s Verification stage — every Build
  must show, in its report, the actual output of running the new or
  changed behavior.
