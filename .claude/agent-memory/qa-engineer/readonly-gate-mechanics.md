---
name: readonly-gate-mechanics
description: How to run a strictly read-only G4/QA gate in the worktree-isolated ctl24 environment (git archive to scratch + spot-mutate the scratch copy)
metadata:
  type: feedback
---

For a strictly READ-ONLY gate in a worktree-isolated agent (cannot checkout/modify the repo, only pytest + temp-dir side effects), the workflow that worked on M0-T094 (D-024 unit G):

- Extract the frozen reviewed SHA into scratch with `git archive <sha> | tar -x -C <scratchdir>` (no repository modification; preserves repo-root markers so identity-validation tests pass). Run pytest FROM the scratch dir.
- The worktree git-guard refuses compound/`cd`-into-scratch git commands and pipes it deems "too complex" — keep git calls plain and single-purpose; redirect pytest stdout to a scratch file then tail it.
- To independently confirm producer mutation-kill claims read-only: Edit the SCRATCH copy (temp-dir, allowed), run the affected test class, confirm it FAILS, then Edit it back. Done this for M8 (unknown→0 killed by S2) and M6b (drop `$` anchor → "/loop-statuses" intercepted, killed by S10).

**Why:** the sandbox kills long single-process whole-suite runs (documented in D-024 baselines), and worktree isolation blocks checkout; this keeps the review reproducible and truly non-mutating.
**How to apply:** any G3/G4/G5 gate here where the packet says "READ-ONLY, temp-dir side effects only." Re-run the unit suite + adjacent regression suites (not the whole tree); spot-mutate 1-2 hard invariants in scratch to validate the mutation pass rather than trusting the producer's log.

Related: [[m2t015-python312-and-gate-lessons]] (Python 3.12 vs 3.11 collection risk — the tools/ supervisor suites are stdlib unittest and run fine on 3.11).
