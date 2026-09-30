---
name: bound-worktree-git-guard
description: When the orchestrator binds a producer to a worktree other than the harness isolation dir, the isolation guard refuses compound/looped shell commands that contain git (or look complex); plain single commands work
metadata:
  type: project
---

When a packet binds work to a named worktree (e.g. `wt-m5t080`) that differs from the harness isolation
directory, the worktree-isolation guard refuses any Bash call it cannot verify: `for` loops around
`git show`, pipelines mixing several git calls, and even long python heredocs with many piped steps.
Plain `cd <bound-wt> && git <one command>` calls pass.

**Why:** the guard only whitelists commands it can prove stay inside a worktree; complexity alone trips it
(seen on M5-T080 rework A, 2026-09-24).

**How to apply:** extract files at a pinned sha with one `git show <sha>:<path> > <scratchpad file>` per
call, then grep/sed the scratch copies; run checker scripts as separate `python <script>` calls; never
retry the refused compound form. Related: [[property-profile-frontend-rules]].
