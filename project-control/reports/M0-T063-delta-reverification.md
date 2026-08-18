# M0-T063 Unit A1 — delta re-verification (round 2) — CONFIRM-CLOSED

Condensed record by the orchestrator (report-preservation rule): the independent
delta re-reviewer's verdict; full verbatim in the session task-notification.
Read-only, at frozen HEAD `c45c39e` (delta `41f84a4..c45c39e`). Producer ≠ verifier.

## VERDICT: CONFIRM-CLOSED — all three round-1 findings genuinely closed.

Scope: `git diff 41f84a4..HEAD --name-only` = exactly the 7 allowed files (the two
modules, their two tests, the pipeline doc, and the two baseline-evidence files);
no supervisor/code_graph change; generator untouched.

- **MAJOR-1 CLOSED.** `compute_fingerprint` indexes every eligible file with
  `tracked` as metadata. Independent collision reproduction: an untracked eligible
  file's content change now MOVES the snapshot fingerprint (round-1 it did not);
  untracked entry indexed (raw_digest present, tracked=False), census reconciles,
  excluded={}, indexed set == code_graph.scan_input_files. `test_repo_fingerprint.py`
  15 tests (14 passed, 1 skip) incl. both new regression tests.
- **MINOR-2 CLOSED.** recover() skips a live-pid temp generation; a dead-pid orphan
  is quarantined. Reproduced (live survived, dead quarantined). `test_repo_index_cache.py`
  13 passed incl. test_live_writer_temp_dir_is_not_quarantined.
- **QA F1 CLOSED.** The regenerated baseline reproduces at HEAD byte-for-byte:
  export_digest `3d64d3b2…c27f758`, nodes 8418, edges 3420, input_files 426,
  census 426/426, source_fingerprint `2ce8b889…8d2a66` all MATCH; only
  snapshot_fingerprint differs (the documented dirty-tree case: uncommitted
  non-eligible ledger files feed the dirty digest; source_fingerprint matching
  proves the indexed corpus is identical, so export_digest is the valid
  reproducible reference).

Cross-cutting: documented pytest suite 34 passed / 1 skipped; modularity_check
--check 244 files, 0 failures (4 pre-existing symbol_ceiling warnings, none in
this delta). Informational: the working tree carries three project-control ledger
files outside the reviewed delta and outside all code-graph roots (explains only
the expected snapshot_fingerprint difference).

**This gate confirms acceptance of M0-T063 Unit A1.**
