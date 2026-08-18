# M0-T064 Unit A2 — parity + selective-reparse evidence (D-013-R032/R037/R059/R079)

Two invariants carry the unit:

1. **Parity (load-bearing, R037/R079)** — the incremental export is BYTE-IDENTICAL
   to a clean full rebuild produced by the REAL `code_graph.build_graph` (an
   independent reference), for the same snapshot and effective versions, across
   cold / warm-reuse / every change class.
2. **Selective reparse (R032/R059)** — a warm no-change run reparses ZERO files; a
   local content edit reparses ONLY the changed files (unchanged files' cached
   per-file extraction bundles are reused) and triggers no full rebuild.

## How the two hold together (not luck)
- The byte-identical **assembly driver** (`tools/repo_index_assembly.drive`)
  reproduces `build_graph`'s output from per-file *bundles* (each file's exact
  slice of nodes + import edges + contract edges + externals; every edge a file
  contributes has `from == that file`, so bundles partition the graph with no
  cross-file key collision). On a content-only edit the global resolution index
  (`_PyIndex`/`_TsResolver`, a function of the file-PATH set) and the schema-node
  set are unchanged, so a reused bundle is provably still exact; only the changed
  files are re-extracted.
- The driver is **version-guarded**: it runs only against the exact
  `GENERATOR_VERSION`/`SCHEMA_VERSION` it was verified for (`1.1.0`/`1.0.0`); any
  other version raises `UnknownGeneratorError` and the caller falls back to the
  real `build_graph` — fail-safe, never fail-wrong.
- Structural changes (add/delete/rename) alter the resolution index or schema-node
  set, so unchanged files' edges could re-resolve; those force a full rebuild (the
  deterministically-safe closure), still byte-identical.

## Real-repo proof (deterministic; reproduce with the harness below)
```
generator:        1.1.0/1.0.0  (recognized)
cold build:       mode=full         export == clean_full (real build_graph) = True   files_parsed=420  files_reused=0    inputs=430
warm no-change:   mode=reuse        export == clean_full = True                        files_parsed=0    files_reused=430
warm 1-file edit: mode=incremental  export == clean_full = True                        files_parsed=1    (only the edited file)
contract-edge partition == real _contract_edges = True (318 edges)
```
Reproduce:
`python -c "import tools.repo_index_assembly as a, tools.code_graph.generate as g; \
r=a.drive('.'); import"` and `python tools/test_repo_index_assembly.py` +
`python tools/test_repo_index_incremental.py`.

## Test proof (`tools/test_repo_index_incremental.py`, 22 tests · `tools/test_repo_index_assembly.py`, 7 tests)
- `ParityInvariant.test_cold_build_matches_full` / `test_warm_reuse_matches_full`
  — cold and warm-reuse both == clean full (real generator).
- `ParityInvariant.test_parity_holds_after_each_change_class` — parity re-verified
  after a content edit (mode=incremental, files_parsed=1), an add and a delete
  (mode=full); each `== clean_full`.
- `SelectiveReparse.test_warm_no_change_reparses_zero` — R059: zero reparse.
- `SelectiveReparse.test_local_edit_reparses_only_changed_no_full_rebuild` — R032:
  one edit → files_parsed=1, files_reused=4, mode=incremental, `== clean_full`.
- `SelectiveReparse.test_two_file_edit_reparses_two`.
- `GeneratorFallback.*` — an unrecognized generator version falls back to the real
  builder (byte-identical) and the assembly driver refuses to run.
- `ChangeClassification.*` — rename (not add+delete), global invalidator, metadata.
- `ImporterClosure.test_importer_closure_is_transitive_and_deterministic` and
  `test_closure_on_real_bundles` — closure over the REAL import edges.
- `RunRecordAndTelemetry.*` — required run-record fields present, no absolute path,
  append-only JSONL, disable-able.
- `ReuseAndRecovery.*` — reuse (files_parsed=0), idempotent retry, corrupt
  generation recovered + rebuilt, full rebuild always available.
- `RealRepoSmoke.test_parity_on_this_repo` (files_parsed=0 on warm).
- Assembly suite: cold export+meta match real, warm 0/1-file parity, contract-edge
  partition guard, generator guard, real-repo cold parity.

## Telemetry (D-013-R024/R050/R052)
Each build emits a machine-readable run record: schema/run id, unit id, repo
identity (sha), HEAD/branch/dirty digest, source-manifest fingerprint, snapshot
fingerprint, versions, generator identity, census (eligible/indexed/excluded/
failed/stale), change-set counts, mode, cache hit/miss, rebuild reason,
files examined/parsed/reused, affected dependents, graph nodes+edges before and
after, export digest. Measured-only fields (`estimated_tokens`,
`provider_tokens`) are null — never fabricated. The record is appended to an
external, append-only, redacted JSONL log in the per-checkout runtime dir
(outside the repo, never committed; `elapsed_seconds` appears only there, never
in a byte-identity artifact).
