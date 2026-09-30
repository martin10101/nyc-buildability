---
name: isolated-reviewer-git-diff-target
description: An isolated review worktree's own HEAD is usually a divergent branch (often stale main); to check "later commits are ledger-only" diff the reviewed SHA against the candidate branch tip, not HEAD
metadata:
  type: feedback
---

When a G3/G4 review task says "reviewed head <SHA>; later commits = ledger records only; verify with `git diff --name-status <SHA> HEAD`", do NOT trust your dispatched review worktree's own HEAD as the comparison target.

**Why:** A dispatched reviewer runs in an auto-isolated worktree whose branch (e.g. `worktree-agent-xxxx`) frequently points at a divergent commit — often the stale `main` tip. In the M0-T140 review my worktree HEAD was `d8b3899f` (= `refs/heads/main`, an OLD divergent branch), and `git diff 704df814 HEAD` showed dozens of spurious deletions/modifications — nothing to do with the closure. The real candidate branch tip was `8da429c8` (`candidate/D-024-mrl-option-b`), whose ONLY commit past the reviewed `704df814` touched ledger files (G2 gate json, report json, state.json, task json).

**How to apply:** Find the true comparison target with `git for-each-ref refs/heads refs/remotes` + `git branch --contains <reviewed-sha>`. Diff `<reviewed-sha>..<candidate-tip>`, confirm the interim commits are ledger-only. Read tracked artifacts at the reviewed SHA via `git show <sha>:path` (worktrees share the object store, so any commit is reachable). The `cd`-into-shared-checkout and complex-piped-git commands are blocked by the worktree guard — run plain `git show <sha>:path > scratchfile` then parse the scratch copy. Related: [[supervisor-mrl-canary-evidence]].
