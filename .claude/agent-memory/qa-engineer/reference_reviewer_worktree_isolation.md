---
name: reviewer-worktree-isolation
description: A dispatched reviewer's own worktree sits at an OLD base; the review target is in ctl24/wt-* at the frozen SHA
metadata:
  type: reference
---

A dispatched G3 reviewer here is isolated into `.claude/worktrees/agent-<id>` whose HEAD is an OLD base commit (e.g. d8b3899f), NOT the frozen reviewed SHA. The task's "verify HEAD == <SHA>" instruction assumes the Bash cwd is the shared `ctl24` checkout, but the harness isolates you elsewhere.

**How to apply:** Do NOT stop just because your own worktree HEAD differs. Run `git -C <own worktree> worktree list` (read-only, allowed) to locate the checkout at the frozen SHA — the shared `ctl24` (candidate branch) and the producer's `wt-m5t010`-style worktree both sit at it. Read/run the files there, and prove content identity with `git hash-object <ctl24 file>` vs `git rev-parse <SHA>:<path>`. The bash git-guard refuses any command that `cd`s into the shared checkout for git, or any "too complex" multi-git command — run plain single `git -C <own worktree> ...` commands only. Running pytest / python from `ctl24` (non-git) is allowed. See [[mutation-probe-technique]].
