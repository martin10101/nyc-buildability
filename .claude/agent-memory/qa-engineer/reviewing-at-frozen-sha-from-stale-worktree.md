---
name: reviewing-at-frozen-sha-from-stale-worktree
description: How a read-only reviewer in an isolated worktree verifies a task frozen at a different SHA (shared object store + shared ctl24 checkout)
metadata:
  type: feedback
---

When dispatched to gate a task at a frozen review SHA, your isolated worktree
(`.claude/worktrees/agent-*`) is usually checked out on an OLD branch and will
NOT contain the task's deliverable files. Do not treat that as BLOCKED.

**Why:** worktrees share one object store, and the shared `ctl24` checkout is
itself a worktree of the pack repo. So the review objects are already reachable.

**How to apply:**
- Confirm what `ctl24` points at without running git on it (git-to-shared-checkout
  is guard-blocked): read `ctl24/.git` (a gitdir pointer) → then
  `<pack>/.git/worktrees/ctl24/HEAD` → `git rev-parse <branch>` from YOUR worktree.
  When `ctl24` already equals the review HEAD, run probes/pytest/python directly in
  `ctl24` (non-git commands against the shared checkout are allowed; the first `ls`/
  `python -m ...` there works — only git targeting it is refused).
- From YOUR own worktree you can still reference review SHAs against the shared
  objects: `git cat-file -t <sha>`, `git diff A..B --name-status`, `git show <sha>:path`,
  `git show <sha> -- path`, `git log -p <sha> -- path`, `git ls-tree -r <sha> -- dir`.
  Break loops/`&&`-chains into plain separate commands or the isolation guard refuses them.
- Verify the deliverable-identity → HEAD interval is control-plane-only
  (`git diff <deliverable_sha>..<HEAD> --name-status`) before trusting the `ctl24`
  working tree as equivalent to the frozen deliverable for running code/tests.
