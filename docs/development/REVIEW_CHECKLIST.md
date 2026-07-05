# Review Checklist

This checklist is mandatory before every commit, per
`docs/development/BUILD_WORKFLOW.md`'s Review stage. Every item must be
checked honestly against the actual Build — not assumed.

## Compatibility

- [ ] Does it break any existing public method signature, class name, or
      module path that other code depends on?
- [ ] Does it change the observable behavior of anything the Build did not
      explicitly set out to change?
- [ ] Was that behavior actually re-run and compared before/after, not
      just reasoned about?

## Architecture

- [ ] Is the change in the correct package per
      `docs/development/PROJECT_STRUCTURE.md`?
- [ ] Does it respect the dependency direction (`ui/` → `core/` →
      `providers/`, never the reverse)?
- [ ] Does it introduce a second way of doing something that already has
      an established pattern (e.g. a second theming mechanism, a second
      provider-dispatch mechanism)? If so, is that intentional and
      documented, or accidental?
- [ ] Does it invent new architecture without checking whether an existing
      pattern already covers it?

## Code Quality

- [ ] Does it introduce duplicate logic that already exists elsewhere in
      the codebase?
- [ ] Are all imports actually used? Are unused imports removed?
- [ ] Are import groups ordered per `CODING_GUIDELINES.md` (standard
      library → third-party → local)?
- [ ] Is every new/changed public function, method, and `__init__` fully
      typed?
- [ ] Does every new/changed module, class, and public method have a
      docstring that adds information beyond the name?
- [ ] Are comments explaining *why*, not restating *what* the code already
      makes obvious?
- [ ] Is there any dead code (unreachable branches, unused variables,
      commented-out code left in place)?

## Dependencies

- [ ] Does it add a new third-party dependency? If so, is the
      justification documented per `CLAUDE_RULES.md` rule 8?
- [ ] Does `requirements.txt` still match the actual imports in the
      codebase exactly — no more, no less?

## Testability

- [ ] Is the feature/change testable in isolation (does it require a live
      external service that can't be faked, with no fallback)?
- [ ] If it is new behavior, was it actually exercised at least once (a
      manual run, a script, a test) and is that evidence recorded in the
      Build's report?
- [ ] Is the change isolated enough that it could be reverted without
      requiring changes to unrelated files?

## Secrets & Safety

- [ ] Are there any credentials, tokens, API keys, or secrets in any file
      being committed?
- [ ] Does `.gitignore` still correctly exclude `.env`, caches, and other
      local-only artifacts?

## Documentation

- [ ] If the change affects architecture, is `docs/ARCHITECTURE.md` (or
      `docs/development/PROJECT_STRUCTURE.md`) updated to match?
- [ ] If the change closes an item from `docs/ROADMAP.md`, is that
      reflected there?
- [ ] Has an entry been added to `docs/development/BUILD_HISTORY.md`?

## Commit Hygiene

- [ ] Does the commit contain only the files relevant to this Build?
- [ ] Is the commit message an accurate, specific summary — not "misc" or
      "fixes"?
- [ ] Could this commit be cleanly reverted on its own?
