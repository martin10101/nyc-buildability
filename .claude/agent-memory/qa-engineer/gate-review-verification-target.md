---
name: gate-review-verification-target
description: Where/how a dispatched read-only reviewer runs verification in the D-024 (ctl24) campaign — target the integration checkout, not the reviewer's own worktree
metadata:
  type: feedback
---

When dispatched as a read-only gate reviewer in the D-024 fable-codex-loop campaign, run all read-only verification (pytest, ruff, `tools/modularity_check.py`) against the **integration checkout** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, which is checked out at the reviewed SHA on `control/D-024-fable-codex-loop`. Confirm the checkout SHA with `git worktree list` (run from your own worktree with `git -C <own-worktree>`).

**Why:** the dispatched reviewer's own isolated worktree (`.../worktrees/agent-<id>`) is on a stale generic branch (e.g. d8b3899 `worktree-agent-*`), NOT the deliverables. The deliverables live only in the ctl24 checkout. Reading/testing your own worktree would review the wrong (stale) content.

**How to apply:**
- `Read` of ctl24 absolute paths works directly.
- Non-git commands CAN cd into ctl24: `cd /c/Users/MLFLL/Downloads/nyc-zoning/ctl24 && python -m pytest tools/<file>.py -q` runs fine.
- Git commands that cd into ctl24 are REFUSED by the worktree-isolation guard ("git operations must target its own worktree"). To inspect git state, run `git -C <your-own-worktree>` or rely on the orchestrator-provided SHAs. You cannot run `git status`/`git diff` inside ctl24, so note as a limitation that you verified the checked-out content (assumed == reviewed SHA per `git worktree list`).
- CI/full-suite/mutation evidence that you're told is out-of-scope to run: cite the orchestrator-provided CI-green SHA rather than returning BLOCKED. See [[in-regime-accept-mechanics]] for the acceptance-side rules.
