---
name: gate-reviewer-worktree-vs-shared-checkout
description: A dispatched gate reviewer's own worktree is isolated on a STALE origin/main base far behind the reviewed SHA; review the shared ctl24 checkout at its ref instead, and know which git ops the bash guard allows.
metadata:
  type: feedback
---

When dispatched as an independent gate reviewer, the isolated worktree I run in
(`.claude/worktrees/agent-*`) is checked out on branch `worktree-agent-*` at a
STALE `origin/main` base that can be hundreds of commits behind the reviewed SHA.
Its working files are NOT the content under review. The system-prompt `gitStatus`
block shows the shared checkout's branch/HEAD (e.g. candidate/... at 99cd3dad),
not my worktree's actual HEAD (verify with `git -C <my-worktree> rev-parse HEAD`).

**Why:** dispatched agents auto-isolate off origin/main which lags the integration
branch (see [[producer-worktree-base-and-stop-hazard]]). As a read-only reviewer I
am forbidden from `git reset`, so I cannot bring my worktree to the reviewed SHA.

**How to apply:** review the SHARED checkout (`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`)
directly — it sits on the integration branch at the reviewed SHA. Confirm its ref by
reading `<pack>/.git/worktrees/ctl24/HEAD` then `<pack>/.git/refs/heads/<branch>`.
Run test suites whose paths resolve via `$PSScriptRoot`/`__file__` against ctl24's
absolute script paths (cwd-independent), or `cd` into ctl24 for cwd-relative python
checks. All worktrees share one object store, so read committed content with
`git -C <my-worktree> show <sha>:path` and confirm no shared-tree drift by CR-normalized
diff against ctl24's working file.

**Bash worktree guard behavior observed:** it REFUSES any git command that targets the
shared checkout (`git -C <ctl24> ...` or `cd <ctl24> && git ...`) and refuses commands
"too complex to verify" (process substitution, `$env:` in Join-Path, multi-statement
Test-Path). It ALLOWS: non-git commands with `cd <ctl24>`, `git -C <my-own-worktree> ...`
(including `show <sha>:path` / `rev-parse` reads that pull from the shared object DB),
and plain single-statement powershell. Split compound commands into plain separate calls.
