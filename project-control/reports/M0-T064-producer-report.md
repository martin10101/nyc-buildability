# M0-T064 Unit A2 producer report — incremental indexing (D-013)

Producer: orchestrator (D-017 authorizes direct implementation of the context-
intelligence units). Branch `task/M0-T064-incremental-index`, stacked on the
accepted A1 (M0-T063). Governing D-001 + D-013.

## Deliverable
`tools/repo_index_incremental.py` (299 SLOC) on top of accepted A1:
- **Change classification** (`classify_changes`): exact per-file status —
  added / content_modified / metadata_modified / deleted / renamed (a delete+add
  sharing a raw content digest) + global invalidators (parser/config/schema/
  eligibility version change).
- **Affected importer closure** (`affected_closure`): deterministic transitive
  set of files that import a changed file, from the cached code-graph edges.
- **Reuse-or-rebuild** (`build_incremental`): an unchanged snapshot reuses the
  validated cached generation (cache hit; the win = skipping parse/resolve); a
  changed snapshot rebuilds via the same full builder so parity holds by
  construction; a global invalidator forces a full rebuild with a recorded reason.
- **Parity invariant** (D-013-R037/R079): incremental export == clean full
  rebuild, BYTE-IDENTICAL, across every change class — enforced by test.
- **Crash-safety / concurrency**: reuses the A1 cache's fail-closed rules
  (quarantine incomplete/corrupt, single-writer lock, idempotent retry); full
  rebuild always available as reference and recovery.
- **Telemetry** (D-013-R051/R052/R059): files examined/hashed/parsed/reused,
  affected dependents, cache hit/miss, rebuild reason, elapsed; nullable token
  estimate (never fabricated as zero).

## Design note (why parity is guaranteed, not luck)
The A1 fingerprint hashes CONTENT of every eligible file (mtime never trusted),
so the reuse key can't be fooled by a restored mtime; reuse returns the exact
cached full-build bytes; a rebuild uses the same `code_graph.build_graph` the
clean rebuild uses. See `M0-T064-parity-evidence.md`.

## Acceptance scenarios (AS-1..AS-5) — all proven
See the packet; each maps to a passing test in
`tools/test_repo_index_incremental.py` (12 tests). The A/A split (source-002
decisions 4/6) places this incremental build + the byte-identical parity TEST in
A2; A1 delivered the deterministic reference — the DCV explicitly carried this
obligation to A2, and it is discharged here.

## Test evidence (documented_test_commands)
- `python tools/test_repo_index_incremental.py` → 12 passed.
- `python -m pytest tools/test_repo_index_incremental.py -q` → 12 passed.
- Real-repo parity: cold `incremental==full` True; warm reuse `==full` True
  (cache hit, files_parsed=0).
- `python tools/modularity_check.py --check` → 0 failures (module 299 SLOC).

## Scope / forbidden paths
`tools/repo_fingerprint.py`, `tools/repo_index_cache.py`,
`tools/repo_index_baseline.py` (accepted A1) imported read-only, NOT modified;
`tools/agent_supervisor/**`, `tools/code_graph/generate.py|query.py`,
`tools/context_pack.py` untouched. ci.yml change is one additive step in the A1
`context-index-a1` job region (extends it to run the incremental test module).
