# M0-T076 — Coverage evidence (D-019)

## Post-change full context-pipeline suite (14 files) — 252 passed, 1 skipped
Run: `python -m pytest -q tools/test_context_integration.py tools/test_context_pack.py
tools/test_context_pack_index.py tools/test_subsystem_resolver.py
tools/test_memory_graph.py tools/test_repo_views.py tools/test_context_benchmark.py
tools/test_status_projection.py tools/test_repo_index_cache.py
tools/test_repo_index_incremental.py tools/test_model_routing.py
tools/test_repo_index_assembly.py tools/test_repo_fingerprint.py
tools/test_repo_index_baseline.py` → **252 passed, 1 skipped in ~239s**.

The one skip is the environment-gated symlink/junction test (unprivileged Windows
without developer mode); its static counterpart runs unconditionally.

## New tests added this task (23; 0 existing removed/skipped/weakened)
- `test_memory_graph.py`: `D019LockPublicationRace` (5) + advisory-memory (2) — lock
  publication window, partial metadata, token/release, two-writer no-lost-node,
  useful+bounded advisory rows.
- `test_context_integration.py`: `D019ContainmentRedactionInsufficiency` (3),
  `D019RacedEscapingLink` (1), `D019FrozenDiffBase` (3),
  `D019UnitEConsumptionAndSeedOrder` (3), `D019HonestRouting` (3).
- `test_context_benchmark.py`: `D019FrozenBaseline` (3).

## Independent reproductions (clean clone @ branch head)
- e2e `--baseline M0-T076-baseline-g0.json` → exit 0, exit 0 (twice).
- clean M0-T066 compile → 4 `allowed_impl` seeds + 1 prose before any
  docs/control-plane; Unit E primitive `repo_views.neighborhood_edges` consumed.
- projection staleness tests pass (module unchanged).
- index-parity integrity (R059) all True.

## Gate suites (non-context, unaffected)
Modularity `--check`: 0 failures. Directive validator `--check`: exit 0.
Forbidden-path diff vs G0 base `3c10894`: EMPTY.
