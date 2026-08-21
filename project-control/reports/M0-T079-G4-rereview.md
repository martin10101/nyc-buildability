# M0-T079 round-2 full-tree G4 re-check (orchestrator-captured evidence)

Reviewed identity: `68adb6bf73870bf405bad79295167872f0cbba2f` (round-2 task commit `41d0490`).
The round-1 independent G4 review (PASS, full tree 2261/0/3) stands; this is the orchestrator's
re-run of the full `tools/` tree against the corrected identity, since the round-2 corrections are
additive-refusal + redaction + new focused modules.

## Result

`python -m pytest tools/ -q --no-header` (full tree, run under concurrent multi-agent load):
**1 failed, 2305 passed, 3 skipped in 2588.93s.**

The single failure was `tools/test_repo_index_incremental.py::RealRepoSmoke::test_parity_on_this_repo`
— **classified as an environmental concurrency artifact, NOT a T079 regression**, on four grounds:

1. The test is a live-repo smoke test that indexes **this working tree** and checks
   incremental-vs-full-index parity. During the 43-minute run the orchestrator was committing
   evidence-only ledger files and other team agents were writing scratch files, so the repo state
   shifted between the test's two index passes.
2. Reproduced in isolation on a quiescent tree (`git status --short` = 0 changes): **3/3 clean
   passes** (`1 passed in ~12s` each).
3. T079 touches **zero** repo-index files (`git diff --name-only HEAD | grep -c repo_index` = 0);
   its entire surface is `tools/agent_supervisor/**` + supervisor tests, unrelated to repo-index
   parity logic.
4. The two other tree-state-sensitive smoke tests (`test_context_integration.py`, flagged by the
   T080 producer for the same mechanism) pass 24/24 on the committed campaign branch — same root
   cause, same clean result once the tree is quiescent.

Effective full-tree result at the frozen identity: **2306 passed / 0 real failures / 3 pre-existing
skips** (the three skips are the two supervisor platform-conditional skips + repo_fingerprint symlink
skip, all pre-existing and unrelated to T079). Matches round-1 G4's clean tree (2261/0) plus T079's
+45 new tests.

## Note

The `RealRepoSmoke` parity test's sensitivity to a mutating working tree during a long concurrent
run is a test-harness robustness observation (it should snapshot or run against a fixed rev), not a
product defect. Pooled as an infrastructure note, not a T079 finding.
