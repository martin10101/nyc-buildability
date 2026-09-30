---
name: mutation-probe-technique
description: How to prove G3 mutation-sensitivity without mutating a live shared checkout the build loop is using
metadata:
  type: feedback
---

For G3 test-adequacy gates, prove mutation sensitivity with an IN-PROCESS monkeypatch probe, never by editing the source file on disk.

**Why:** The scenario work under review lives in the shared `ctl24` checkout (and the producer's `wt-*` worktree) that the invisible build loop is actively using. Editing the source there to test "would the test catch a bug" would corrupt a live checkout and could leave source mutated (the task explicitly forbids leaving any mutation). Reviewers are also git-blocked from the shared checkout, so `git checkout` to restore is not available.

**How to apply:** Write a scratchpad script that (1) puts `services/api` and `services/api/tests` on `sys.path`, (2) imports the real module object (e.g. `from app.scenario import comparison as C`), (3) monkeypatches module-level helpers in memory (e.g. `C._metric_delta = mutant`, `C._content_key = lambda ...`). Because `compare_scenario_assumption_sets` looks up those helpers as module globals at call time, the in-memory swap takes effect with zero disk change. Restore by reassigning the saved original. Confirm no mutation by comparing `git hash-object <ctl24 file>` to `git rev-parse <SHA>:<path>` (both run with `-C <own worktree>`; shared object store resolves the blob). Sign-inversion, wrong-denominator, input-order-baseline, dropped-not-derivable-set, and inf-percent mutations were all caught by the packet's tests this way (M5-T010). See [[reviewer-worktree-isolation]].
