# Build Workflow

This defines the mandatory lifecycle for every future Build on AI Agent
Studio. "Build" here means any unit of work delivered in one session —
whether it adds a feature, fixes a bug, or performs cleanup (like
Sprint 4).

```
Planning
   │
   ▼
Implementation
   │
   ▼
Verification
   │
   ▼
Review
   │
   ▼
Commit
   │
   ▼
Push
```

No stage may be skipped. A Build that goes straight from Implementation to
Commit, for example, has no Verification or Review step and is not
following this workflow.

---

## 1. Planning

Before writing any code:
- Read the relevant existing modules. Do not assume behavior from the
  file name — open the file.
- Check `docs/PROJECT_STRUCTURE.md` to confirm which package the work
  belongs in.
- Check `docs/ROADMAP.md` to confirm the work is scheduled and not
  jumping ahead of a dependency (e.g. don't implement `skills/` before
  `providers/` patterns it's meant to mirror are stable).
- State the scope of the Build explicitly: what will change, what will
  not change, and which files will be touched.

## 2. Implementation

- Follow `docs/development/CLAUDE_RULES.md` and
  `docs/development/CODING_GUIDELINES.md` while writing.
- Prefer the smallest change that satisfies the stated scope.
- If the Build's actual scope turns out to be larger than planned (a
  hidden dependency, a missing prerequisite), stop and re-state the scope
  rather than silently expanding it.

## 3. Verification

Every Build must be verified before it is considered done. At minimum:
- **Syntax check**: every changed `.py` file must parse cleanly
  (`ast.parse` or equivalent).
- **Import check**: every changed module must import without error, with
  its actual dependencies installed.
- **Behavior check**: if the Build claims not to change behavior, prove it
  by running whatever exists (`test_engine.py`, a headless app launch,
  etc.) before and after, and compare output.
- **New behavior check**: if the Build adds behavior, it must be exercised
  at least once (a manual run, a new test) and the actual output recorded
  in the Build's report — not just described.

A Build with no verification step is incomplete, regardless of how correct
the code looks.

## 4. Review

Before committing, walk through
`docs/development/REVIEW_CHECKLIST.md` explicitly, item by item. This is
a self-review — the same review a second engineer would be expected to
perform, performed honestly against your own work.

## 5. Commit

- One Build, one commit (or a small number of clearly-scoped commits if
  the Build's own instructions call for it — see `CLAUDE_RULES.md` rule 6
  on atomic commits).
- Commit messages should be a short, accurate summary — not "misc fixes,"
  not "Sprint N" alone with no further context available elsewhere. If the
  Build corresponds to a named Sprint, the commit message may reference
  it (e.g. "Sprint 4 Foundation Cleanup"), but the *why* must live in a
  Build report in `docs/`, not only in the commit message.
- Append an entry to `docs/development/BUILD_HISTORY.md` (see that file's
  template) before or as part of the commit.

## 6. Push

- Confirm the target branch before pushing.
- Never push using credentials pasted directly into a chat or terminal
  session without immediately treating that credential as compromised
  afterward (see the Sprint 4 session history for a live example of this
  happening and being flagged).
- After push, confirm the remote actually received the commit (e.g.
  `git log` against the remote, or the push command's own confirmation
  output) rather than assuming success.

---

## Quality Gates Before Every Commit

A Build may not be committed unless all of the following are true:

- [ ] Every changed file parses without a syntax error.
- [ ] Every changed module imports cleanly with its dependencies present.
- [ ] If behavior was supposed to stay the same, it was proven to stay the
      same (not just asserted).
- [ ] If behavior changed, the change was in scope and is described in a
      Build report.
- [ ] No unrelated files were touched.
- [ ] No credentials, tokens, or secrets are present in any file being
      committed.
- [ ] `requirements.txt` still accurately reflects actual imports (only
      touch it if dependencies actually changed).
- [ ] `docs/development/REVIEW_CHECKLIST.md` has been walked through.
- [ ] `docs/development/BUILD_HISTORY.md` has an entry for this Build.
