---
name: verify-worktree-baseline-before-editing
description: Before editing, confirm the isolated worktree's HEAD actually contains the task baseline commit — the harness can drop you in a stale worktree that predates it
metadata:
  type: feedback
---

Before starting any producer edit, verify the isolated worktree's HEAD matches (or descends from) the baseline commit named in the packet. The harness can isolate you into a DIFFERENT, older worktree than the one the packet describes.

**Why:** On M0-T058 the packet said "worktree M0-T058-p1, branch task/M0-T058-p1 off 4083d2c." The harness actually isolated me into worktree `agent-a7b03bbed8fa3e025` at `7cc1fed`, which was 41 commits OLDER than `4083d2c` (my HEAD was an *ancestor* of the baseline). The entire defect code path (`child_record_unwritable` in `claude_runner.py`, introduced by a later commit) did not exist in my worktree — so the fix was un-performable there. Editing anyway would have fabricated code against an obsolete tree that lacks the surrounding integration (recovery.py `record_launched_child`/`clear_child_record`), producing a non-integratable diff and a wrong freeze baseline.

**How to apply:** As a first step after `git rev-parse HEAD`, run `git merge-base --is-ancestor <baseline> HEAD` (must succeed) and grep the worktree for a distinctive token from the defect (e.g. the reason code) to confirm the target code is present. If the baseline is NOT an ancestor of HEAD, or the defect code is absent, STOP and return `blocked` to the orchestrator — do not reset/checkout the baseline yourself (that pulls in unrelated commits and is git integration the orchestrator owns), and you cannot edit the correct worktree because cross-worktree git is refused (see [[env-producer-sandbox-no-exec]]).
