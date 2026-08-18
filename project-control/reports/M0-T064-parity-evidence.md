# M0-T064 Unit A2 — byte-identical parity evidence (D-013-R037/R079)

The load-bearing invariant: the incremental build's exported bytes are
BYTE-IDENTICAL to a clean full rebuild for the same snapshot. Guaranteed by
construction (an unchanged snapshot returns the exact cached full-build bytes; a
changed snapshot rebuilds via the same `code_graph.build_graph`), and enforced by
test across every change class.

## Real-repo proof (deterministic; reproduce with the harness below)
```
cold build:  reused=False  parity incremental==clean_full = True
warm build:  reused=True   warm==clean_full = True   (cache hit; files_parsed=0, files_reused=429)
```
Reproduce: `python -c "import tools.repo_index_incremental as inc; ...
r=inc.build_incremental('.', cache_base=<tmp>); assert r.export_bytes==inc.clean_full_build_bytes('.')"`.

## Test proof (`tools/test_repo_index_incremental.py`, 12 tests)
- `ParityInvariant.test_cold_build_matches_full` — cold incremental == clean full.
- `ParityInvariant.test_warm_reuse_matches_full` — warm reuse == clean full == first build.
- `ParityInvariant.test_parity_holds_after_each_change_class` — parity re-verified
  after a content change, an add, and a delete (each `== clean_full`).
- `ChangeClassification.test_rename_is_detected_by_content_digest` — a rename is
  classified as `renamed` (not add+delete) and parity still holds.
- `ChangeClassification.test_global_invalidator_forces_full_rebuild` — a
  parser/config/schema/eligibility version change is a global invalidator.
- `ChangeClassification.test_metadata_only_change_is_classified_separately`.
- `AffectedClosure.test_importer_closure_is_transitive_and_deterministic`.
- `ReuseAndRecovery` — unchanged reuses (files_parsed=0); idempotent retry; a
  corrupt generation is recovered + rebuilt cleanly; full rebuild always available.
- `RealRepoSmoke.test_parity_on_this_repo`.

## How parity is guaranteed (not luck)
1. The A1 snapshot fingerprint hashes CONTENT of every eligible file (mtime never
   trusted), so the reuse decision can never be fooled by a restored mtime.
2. Unchanged snapshot → return the validated cached generation verbatim (the exact
   bytes of a prior full build).
3. Changed snapshot → rebuild via the same full builder the clean rebuild uses, so
   the output matches by construction; the change set + affected importer closure
   are derived and reported for telemetry and future partial-parse optimization; a
   global invalidator forces a full rebuild with a recorded reason.

## Telemetry (D-013-R051/R052/R059)
Per build: files_examined, files_hashed, files_parsed, files_reused,
affected_dependents, cache_result (hit/miss), rebuild_reason, elapsed_seconds;
`estimated_tokens` is null (not applicable to a deterministic build) — never
fabricated as zero.
