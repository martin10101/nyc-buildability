---
name: interrupt-resets-shell-to-primary
description: After a user/coordinator interruption, the Bash shell can reset from your isolated worktree back to the PRIMARY checkout; a bare `git reset --hard` then silently hits the orchestrator's control branch
metadata:
  type: feedback
---

After a mid-task interruption (coordinator injects a course-correction), the Bash
tool's working directory can silently RESET from your auto-isolated worktree
(`agent-<id>`) back to the PRIMARY checkout — and the isolated worktree may even
be torn down (gone from disk and from `git worktree list`). A bare
`git reset --hard <sha>` (no `cd`, no `git -C`) then runs in the primary checkout
and moves the ORCHESTRATOR's control branch, not yours. This actually happened on
M0-T061 (P6): a coordinator-authorized "reset your own worktree to 4083d2c" landed
on the primary `control/session14-m0t055-accept`, moving it 94e243e→4083d2c.

**Why:** the harness re-initializes the shell from the user profile after an
interrupt; working-dir persistence is not guaranteed across an interrupt. The
worktree-isolation guard still *claims* you belong to `agent-<id>` (and refuses
`cd`/`git -C` redirects into any other worktree, calling them "shared checkout"),
yet that directory can be absent while your actual cwd is the primary.

**How to apply:** after ANY interruption, BEFORE running git, run `pwd` +
`git rev-parse --abbrev-ref HEAD` and confirm you are in your own `agent-<id>`
worktree on your task branch. If cwd is the primary checkout (branch is a
`control/*` session branch) or your `agent-<id>` dir is missing, DO NOT run
`git reset`/edits/commits — STOP and report BLOCKED: you have no writable isolated
worktree and must not touch the orchestrator's checkout. If you already moved a
control branch, it is recoverable: `git reflog <branch>` then
`git reset --hard <prior-sha>` restores it (reflog @{1} is the pre-mistake commit).
Never prefix git with `cd <other-worktree> &&` or `git -C <other-worktree>` — the
guard refuses both. Related: [[env-producer-sandbox-no-exec]].
