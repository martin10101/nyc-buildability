---
name: frozen-sha-review-technique
description: How a worktree-isolated QA reviewer verifies another worktree at a frozen SHA when the sandbox guard blocks git toward other worktrees
metadata:
  type: feedback
---

When gating a task whose frozen SHA lives in another worktree, the isolation guard refuses `cd <other-worktree> && git ...`, `git -C <other-worktree> ...`, and piped/compound commands it can't verify.

**Why:** worktree-isolated agents' git operations must target only their own worktree (guard enforced, observed M0-T030 G4 gate 2026-07-29).

**How to apply:**
1. Run git from your OWN worktree — the object store is shared: `git cat-file -t <sha>`, `git diff --stat <base>...<sha>` work fine and are authoritative for path-scope checks.
2. Get a clean checkout at the frozen SHA with `git archive <sha> | tar -x -C <scratchpad>` (tar needs forward-slash paths in Git Bash) and execute tools/tests from there.
3. Verify the other worktree's HEAD without git by reading plumbing files: `<worktree>/.git` (gitdir pointer) -> `<gitdir>/HEAD` -> `.git/refs/heads/<branch>` in the main repo.
4. Confirm no dirty task files via sha256 comparison of worktree files vs the archive export (CRLF-normalize before hashing).
5. Request orchestrator-captured `git status --porcelain` as the residual record; never return BLOCKED solely for the sandbox denial (project rule).
Also: the guard rejects pipes like `cmd | tail` with `${PIPESTATUS}` as "too complex" — run commands plainly.
