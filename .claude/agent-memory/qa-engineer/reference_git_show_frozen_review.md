---
name: git-show-frozen-sha-review
description: How a worktree-isolated read-only reviewer inspects a frozen reviewed SHA that lives in another checkout
metadata:
  type: reference
---

A dispatched reviewer runs in its OWN worktree (e.g. `.claude/worktrees/agent-<id>`),
usually at a different SHA/branch than the reviewed HEAD (which lives in the shared
`ctl24` checkout). The git guard refuses any command that `cd`s to the shared checkout
or is "too complex to verify it stays inside the worktree".

Working pattern (all read-only, ADR-005 compliant):
- The worktree SHARES the object database with the shared checkout, so every reviewed
  commit (the frozen HEAD, producer commits, pre-digest commits) is reachable:
  `git -C <my-worktree> cat-file -t <sha>` returns `commit`.
- Extract frozen file bytes with `git -C <my-worktree> show <sha>:<path> > scratchpad/<name>`
  (single simple redirect passes the guard; chained/compound commands do not — split them).
- Analyse the scratchpad copies with Read/Grep and offline `python` probes
  (`PYTHONDONTWRITEBYTECODE=1`), never pytest/ruff.
- The Read tool CAN read the shared `ctl24` path directly (packet JSON etc.), but for a
  frozen-SHA review prefer `git show <sha>:` so you analyse the exact reviewed bytes, not
  a possibly-drifted working tree.

Related: [[collected-case-counting]].
