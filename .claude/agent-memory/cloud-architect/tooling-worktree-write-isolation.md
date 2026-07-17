---
name: tooling-worktree-write-isolation
description: Write tool is hard-isolated to the agent's own harness worktree; other task worktrees are read-only; drive letter must be uppercase C: in write paths
metadata:
  type: reference
---

On this Windows repo, producer agents get a harness worktree (`.claude/worktrees/agent-<hash>`) and the Write/Edit tools REJECT any path outside it — including the task-named worktree (e.g. `.claude/worktrees/M0-T010`) even when the orchestrator's task prompt says to write there. Reads from other worktrees work fine.

Also: a Write to the correct isolation worktree with a lowercase drive letter (`c:\...`) was rejected with the same isolation error; retrying with uppercase `C:\...` succeeded (observed 2026-07-17, M0-T010 Phase 2).

**How to apply:** write deliverables at the correct repo-relative paths inside your own isolation worktree, disclose the path discrepancy in the producer report, and let the orchestrator transplant/commit onto the task branch. Always use `C:` uppercase in absolute Write paths. Related: [[tooling-grep-glob-gotcha]].
