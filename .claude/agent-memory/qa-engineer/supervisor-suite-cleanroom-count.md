---
name: supervisor-suite-cleanroom-count
description: How the whole agent_supervisor pytest suite count shifts in a git-archive clean-room (no .git) vs a real checkout, and how to reconcile it
metadata:
  type: project
---

When G4-reviewing the D-024 supervisor recert suite (`tools/test_agent_supervisor_*.py`) from a
clean-room extracted via `git archive <sha> | tar -x` (which has **no `.git`**), the whole-suite
count is **-2 passed / +2 skipped** versus a real checkout that has `.git`.

**Why:** two tests in `tools/test_agent_supervisor_os_acl.py` (the "defective blob unreachable" pair,
around lines 790 and ~1043) are decorated `@unittest.skipUnless(IS_WINDOWS and powershell and git,...)`.
`git` IS on PATH in the clean-room so the decorator does NOT skip; the test body then runs
`git show <blob>:path` with `cwd=REPO` (`REPO = HERE.parent` = extraction root). With no `.git` that
`git show` returns non-zero, so the body calls `self.skipTest("defective blob ... unreachable")`. In a
real checkout the blob resolves and the two tests PASS instead.

**How to apply:** if the producer reports e.g. `3,043 passed / 2 skipped / 0 failed / 3,045 collected`
(run in `ctl24` which has `.git`), a clean-room `git archive` run should reconcile to
`3,041 passed / 4 skipped / 0 failed / 3,045 collected`. Same collected count, 0 failed — the delta is
exactly the 2 blob tests moving passed->skipped. This is an environment artifact, NOT a regression.
Alternatively, run in a checkout WITH `.git` (detached checkout of the frozen SHA in your own
worktree) to reproduce the producer count exactly. Set `PYTHONPATH=.`; the whole suite is ~10 min.
