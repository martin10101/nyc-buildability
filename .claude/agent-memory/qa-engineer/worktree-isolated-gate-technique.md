---
name: worktree-isolated-gate-technique
description: How to reproduce an independent gate at a frozen reviewed SHA when the deliverable commit lives in a different checkout than the reviewer's worktree
metadata:
  type: feedback
---

When dispatched as a read-only reviewer, the reviewed deliverable commit often lives in a
DIFFERENT checkout (e.g. repo root `ctl24`) than the reviewer's own worktree, and the
worktree HEAD is unrelated. The commit is still reachable in the shared git object DB.

Rule: reproduce at the exact frozen SHA with `git archive <sha> | tar -x -C <scratch>` into the
session scratchpad, then run pytest / self-test scripts from that clean extract. This gives a
byte-exact checkout at the reviewed identity, isolated from any working tree.

**Why:** a clean extract at the frozen SHA is the correct read-only reproduction surface — it
cannot be contaminated by an unrelated worktree HEAD and matches what the orchestrator/CI review.
**How to apply:** (1) `git archive <sha>` to scratch; (2) run `python -m pytest <targets>` and any
self-test scripts from that extract; (3) put helper/mutation-check scripts in scratch and run them
as one plain `python <path>` call; (4) `modularity_check.py --check` needs a git index, so on an
archive extract compute SLOC directly via its `source_lines()` and compare to HARD_SLOC=1000 /
WARN=600 instead. Confirm the reviewed-SHA-vs-HEAD delta is control/gate-records-only before
trusting any shared working tree. Related: [[named-spawns-are-readonly]].
