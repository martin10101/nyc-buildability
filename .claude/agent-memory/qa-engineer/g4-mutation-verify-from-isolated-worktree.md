---
name: g4-mutation-verify-from-isolated-worktree
description: How to independently run the scoped suite + mutation matrix at a frozen SHA when the reviewer worktree lacks the material commit (git-archive into scratchpad)
metadata:
  type: feedback
---

For a G4 gate, LIVE-verify mutations yourself instead of trusting the producer's harvest table — even when your isolated worktree does NOT contain the material commit.

**Why:** the material commit is often a disjoint peer not in the reviewer worktree's history, and the reviewer must stay read-only (no repo writes, `git diff` empty). Trusting the harvest table without reproduction is the failure mode the gate exists to catch.

**How to apply:**
1. `git -C <worktree> archive <material-sha> services/api | tar -x` into the scratchpad → a throwaway copy fully outside the repo.
2. Verify each extracted file with `git hash-object` == the frozen blob id (`git rev-parse <sha>:<path>`). git-archive+tar preserves LF, so hashes match on Windows with no CRLF fixups.
3. `cp store.py store.py.bak` (record D_cand hash), then per mutant: `sed -i '<LINE>s|.*|<mutant>|'`, run the AFFECTED tests only with `-x --tb=line` (targeted `-k` runs are seconds vs a full slow suite), record the FIRST failing assertion file:line, `cp` the backup back, re-hash == D_cand before the next.
4. Run the full scoped suite once for the count (it can be slow — background it; M5-T069's 77-test suite took ~31 min while the targeted 2-test run was 0.1s).

The repo is never touched (all work in scratchpad), so the read-only constraint holds automatically. Confirmed on M5-T069 (three rows A1/B1/C1 first-failed exactly at the predicted records.py:878/:907).
