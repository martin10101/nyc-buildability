# M0-T069 Unit F — benchmark, projection & runbook evidence (D-013)

## Frozen corpus + full case matrix (R054/R056 / AS-1)
- Five deterministic shapes (single-file bug, cross-module, frontend/backend
  boundary, schema change, control-plane-only), each a hermetic git fixture
  with a recorded corpus manifest digest (determinism proven by
  `DeterministicCorpus` — two independent generations digest-identical).
- Method (stated in the report): reference = fresh-cache clean full rebuild by
  the UNMODIFIED builder (the A1-frozen generator; its baseline export digest
  recorded per shape); new = warm incremental over the SAME snapshot at the
  SAME SHA — the implementation-SHA confound is removed.
- Cases executed per shape: cold, warm no-change, one-file change (or the
  control-plane non-eligible change), dependency change, config change
  (frontend shape — documented global invalidator), rename, delete, corrupt
  cache recovery, interrupted write (orphan temp generation quarantined),
  concurrent writer (held lock refuses `concurrent_writer`). **42 rows total
  in the committed report.**

## Promotion evidence (R059 / AS-2) — all six TRUE in the committed report
- `census_accounts_every_eligible_file` (per-shape census reconciles),
  `incremental_matches_clean_full` (42/42 byte-identical export bytes),
  `warm_no_change_reparses_zero`,
  `local_change_no_full_rebuild_without_documented_invalidator` (config and
  schema invalidators recorded with their documented reasons; the
  control-plane-only edit's conservative full rebuild is reported honestly as
  the documented A2 fallback for a non-source fingerprint move, with
  byte-identity preserved), `delete_rename_leave_no_stale_nodes`,
  `corruption_crash_concurrency_preserve_validity`.
- Benchmark CLI exits 2 if ANY evidence item fails (fail closed).

## Honest reporting (R057/R012/R053 / AS-3)
- `correctness_first: true`; timings under `measured_runtime` labeled "never
  byte-identity content" with per-metric sample counts, median, p95
  (samples=3 in the committed run).
- Deterministic reuse metrics separate; provider token savings labeled
  **UNMEASURED**; AS-3 tests assert the label and the absence of any combined
  savings number.

## Decision discipline (R060 / AS-4)
- Three thresholds proposed WITH rationale (byte-identity 100%; warm
  zero-reparse; recovery validity 100%), `proposed_before_owner_decision:
  true`; the report and the runbook both mark the promotion decision
  **PENDING owner/control-plane decision**; no behavior flag changes anywhere
  in the diff.

## Status projection (R061/R062/R063 / AS-5)
- Unit set derives from the D-013 verification registry (authoritative, never
  hand-listed); all R063 fields asserted per node (requirement ids from the
  independent verification, reviewed SHA, G0 rollback point, review-report
  digest, gates with state, roles, implementation files, honest-null branch).
- R062 mapping tested (accepted / corrections required, etc.); Markdown AND
  Mermaid render FROM the same JSON (test asserts the dependency edge and the
  view-not-truth label); generating SHA + Unit C index digests stamped;
  `check` exits 3 after HEAD moves (tested end-to-end via CLI).
- Committed snapshot: `M0-T069-status-projection.{json,md}` (generated at the
  contract commit b086bba; immediately re-checkable — staleness is the
  DESIGNED disclosure, not an error).

## Determinism + fail closed (AS-6)
- Two projection runs at identical state byte-identical (test).
- Unreadable packet → `task_packet_unreadable` (repo-relative detail, no
  absolute paths — tested); registry/gate/submission unreadable codes exist;
  git failure → `git_unavailable`.
- Runbook documents the full R071 rollback path: disable the new index path
  WITHOUT deleting the prior valid generation (fall back to
  `code_graph/generate.py` or `context_pack.py --no-index`), restore
  full-build behavior, quarantine incompatible generations rather than
  reinterpreting, leave committed why-evidence.

## Test + lint evidence (local, Python 3.11.9, ruff 0.13.0 = CI version)
- `python tools/test_context_benchmark.py` → 15 tests, OK.
- `python tools/test_status_projection.py` → 8 tests, OK.
- `python -m pytest tools/test_context_benchmark.py tools/test_status_projection.py -q` → 23 passed.
- `ruff check` on the four new files → All checks passed.
- `python tools/modularity_check.py --check` → failures 0.
- Full benchmark run: `python tools/context_benchmark.py --samples 3 ...` →
  exit 0, 42 cases, all byte-identical (committed report).
