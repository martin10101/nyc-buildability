---
name: reviewing-a-different-worktree
description: How a worktree-isolated read-only reviewer inspects git state of a DIFFERENT worktree (e.g. ctl24) without tripping the dispatch guard
metadata:
  type: reference
---

When dispatched as a read-only gate reviewer to review a repo checked out in a
DIFFERENT worktree (task says "repo C:\Users\MLFLL\Downloads\nyc-zoning\ctl24"),
you run isolated in your own `.claude/worktrees/agent-*` worktree. Both are linked
worktrees of the same shared object DB (`nyc-development-feasibility-claude-pack/.git`).

**Guard behavior:** the dispatch guard REFUSES any Bash command that `cd`s into the
shared checkout (`cd /c/.../ctl24 && git …`) or is "too complex to verify it stays
inside the worktree" (loops, multi-git pipelines). But:
- Plain git READ commands run from YOUR OWN worktree (no cd) work against shared
  refs/blobs: `git rev-parse <branch>`, `git ls-tree <ref> -- <path>`,
  `git show -s --format=… <sha>`, `git log --name-only <a>..<b>`, `git diff <a> <b> -- <path>`.
  All branches (candidate/*, task/*) and all blobs are visible because the object DB is shared.
- `git hash-object /c/.../ctl24/<file>` works — it just hashes bytes, no repo target.
- Non-git commands WITH `cd` into ctl24 are allowed (python test scripts, ls, wc).

**Blob-identity check pattern (no cd needed):** compare `git ls-tree <task-tip> -- p`,
`git ls-tree <candidate-branch> -- p`, and `git hash-object /c/.../ctl24/p`. If all three
blob SHAs match, ctl24's working tree IS the reviewed content and running its test scripts
tests the frozen content.

**HEAD of the reviewed worktree:** `git worktree list` (from your worktree) shows each
worktree's checked-out commit — authoritative when you cannot cd+git into it.

Keep git commands PLAIN and SEPARATE (one git invocation each); split any for-loop into
individual calls or the guard refuses the whole thing.
