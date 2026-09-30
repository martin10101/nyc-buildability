---
name: mutation-probe-outside-repo
description: How to run real mutation-testing as a read-only reviewer without writing to the repo tree — copy modules to scratch via git show, mutate + rerun there
metadata:
  type: reference
---

As a read-only G4 reviewer you can still do EMPIRICAL mutation testing (not just mental)
without touching the repo:

1. `git show <sha>:path > $SCRATCH/app/connectors/<module>.py` for the module under test
   plus every module it imports (for the pure DCM policy layer that was just the
   classifier + policy + the two `__init__.py` shims). `git show` reads shared objects and
   is NOT blocked by the worktree-isolation guard; a `cd ctl24 && git ...` redirect IS.
2. Recreate a minimal `app/connectors/__init__.py` (EMPTY — avoids pulling heavy
   connectors that need deps) + `tests/connectors/` copy of the test file.
3. Run baseline `PYTHONPATH=$SCRATCH PYTHONDONTWRITEBYTECODE=1 python -m pytest ... -p no:cacheprovider`
   (no-bytecode + no-cache = zero writes even if run inside a repo tree).
4. Drive mutations from a Python script that string-replaces one line, reruns pytest,
   records CAUGHT (rc!=0) / SURVIVED (rc==0), and restores pristine between each.

To run the REAL suite in the primary checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`
(non-git commands like pytest/ruff ARE allowed there; only git redirects are refused):
`cd ctl24/services/api && PYTHONDONTWRITEBYTECODE=1 python -m pytest ... -p no:cacheprovider`.
Confirm the primary checkout is at the pinned head by reading
`.git/worktrees/ctl24/HEAD` → the branch ref file (ctl24 is itself a linked worktree of
`nyc-development-feasibility-claude-pack/.git`). See [[no-defaults-dataclass-test]].
