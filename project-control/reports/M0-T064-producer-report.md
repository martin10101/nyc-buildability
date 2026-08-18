# M0-T064 Unit A2 producer report — incremental indexing (D-013)

Producer: orchestrator (D-017 authorizes direct implementation of the context-
intelligence units). Branch `task/M0-T064-incremental-index`, stacked on the
accepted A1 (M0-T063). Governing D-001 + D-013.

## Deliverable
Two modules on top of accepted A1:

**`tools/repo_index_assembly.py`** (byte-identical assembly driver) — reproduces
`code_graph.build_graph`'s exported bytes from per-file extraction *bundles*, so
an unchanged file can be reused (its `ast.parse` / TS scan skipped) while the
output stays byte-identical to a clean full rebuild. Reuses the generator's own
internals; **version-guarded** (runs only against the verified
`GENERATOR_VERSION`/`SCHEMA_VERSION`, else raises so the caller uses the real
builder — fail-safe).

**`tools/repo_index_incremental.py`** (incremental orchestration) —
- **Change classification** (`classify_changes`): added / content_modified /
  metadata_modified / deleted / renamed (a delete+add sharing a raw content
  digest) + global invalidators (parser/config/schema/eligibility version).
- **Three build modes**:
  - `reuse` — unchanged snapshot returns the validated generation's exact bytes;
    zero files reparsed (D-013-R059).
  - `incremental` — a local content edit reparses ONLY the changed files, reuses
    every unchanged file's cached bundle, reassembles byte-identically; no full
    rebuild on a local change (D-013-R032/R059).
  - `full` — cold build, structural change (add/delete/rename → the resolution
    index / schema-node set changed), global invalidator, or unrecognized
    generator; rebuilt with a recorded reason. Still byte-identical.
- **Importer closure** (`importer_closure`): the deterministic transitive set of
  files importing a changed file, read from the cached bundles' REAL import edges
  (an internal import resolves `to` a target file path).
- **Parity invariant** (D-013-R037/R079): incremental export == clean full
  rebuild via the REAL `code_graph.build_graph`, BYTE-IDENTICAL, across every
  change class — enforced by test.
- **Run record + telemetry** (D-013-R024/R050/R052): a rich machine-readable run
  record (repo identity, HEAD/branch/dirty digest, source-manifest fingerprint,
  versions, census, change counts, files parsed/reused, graph nodes/edges
  before+after, mode/reason; measured-only fields null, never fabricated),
  appended to an external append-only redacted JSONL log in the per-checkout
  runtime dir (never committed).
- **Crash-safety / concurrency**: reuses the A1 cache's fail-closed rules
  (quarantine incomplete/corrupt, single-writer lock, idempotent retry); a full
  rebuild via the real generator is always available as reference and recovery.

## Why parity is guaranteed, not luck
The A1 fingerprint hashes CONTENT of every eligible file (mtime never trusted), so
the reuse key can't be fooled by a restored mtime. A reused bundle is exact only
while every input its extraction depended on is unchanged: the file's own content,
the resolution index, and the schema-node set. `_PyIndex` is a function of the
Python file-PATH set; `_TsResolver` is a function of the TS file-PATH set PLUS the
tsconfig alias map (`code_graph.CONFIG_INPUTS`); the schema-node set depends on the
schema files' paths + `$id`. The gate reuses a bundle only when the path set,
schema set, AND config inputs are unchanged (a config-input change is folded into
the fingerprint and fires a global invalidator → full rebuild). Only changed files
are re-extracted; the assembly is deterministic. The parity test compares against
the REAL generator (independent reference). See `M0-T064-parity-evidence.md`.

## Selective-reparse correction (this revision)
The first A2 revision full-rebuilt on ANY change (parity-safe but not
incremental), which the consolidated review flagged as not meeting the letter of
R032 ("reparse only changed files plus the smallest proven closure") and R059
("a local change triggers no full rebuild"). This revision implements genuine
selective reparse for content edits (the dominant local-change case), closing
those observations rather than deferring them. It also fixes two inherited
defects: (a) the importer closure used a graph shape that never matched the real
graph (wrong keys) and silently collapsed to the changed set — now read from real
import edges; (b) the prior manifest lacked `config_versions`, spuriously firing a
global invalidator on every rebuild — now merged before classification.

## tsconfig stale-reuse fix (review FAIL → resolved)
The re-review found a real byte-divergence: a tsconfig alias change (which steers
TS `@/` resolution) concurrent with a source edit took the incremental path and
reused stale TS bundles, because tsconfig is a generator `CONFIG_INPUT`, not an
indexed file, so A1's fingerprint never captured it. Fixed by folding a digest of
the generator's `CONFIG_INPUTS` (`repo_index_assembly.config_inputs_version`) into
the fingerprint the incremental layer uses: any config-input change now moves the
cache key (no stale hit, even for a committed tsconfig-only edit) and surfaces as a
global invalidator → full rebuild. Regression: `TsconfigInvalidation` (3 tests),
including the reviewer's exact repro.

## Acceptance scenarios (AS-1..AS-5) — all proven
Each maps to passing tests in `tools/test_repo_index_incremental.py` (25) and
`tools/test_repo_index_assembly.py` (7). The A/A split (source-002 decisions 4/6)
places this incremental build + the byte-identical parity TEST in A2; A1 delivered
the deterministic reference.

## Test evidence (documented_test_commands)
- `python tools/test_repo_index_incremental.py` → 25 passed.
- `python tools/test_repo_index_assembly.py` → 7 passed.
- `python -m pytest tools/test_repo_index_incremental.py tools/test_repo_index_assembly.py -q` → 32 passed.
- Full A1+A2 battery (`pytest tools/test_repo_{fingerprint,index_cache,index_baseline,index_incremental,assembly}.py`) → 66 passed, 1 skipped.
- Real-repo: cold `incremental==full` True (files_parsed=420); warm reuse `==full`
  True (files_parsed=0); warm 1-file edit `==full` True (files_parsed=1).
- `python tools/modularity_check.py --check` → 0 failures (incremental 500 SLOC,
  assembly 317 SLOC).

## Scope / forbidden paths
`tools/repo_fingerprint.py`, `tools/repo_index_cache.py`,
`tools/repo_index_baseline.py` (accepted A1) imported read-only, NOT modified;
`tools/agent_supervisor/**`, `tools/code_graph/generate.py|query.py`,
`tools/context_pack.py` untouched (the assembly driver imports code_graph
internals read-only). ci.yml change adds one step to the A1 `context-index-a1`
job region (runs the assembly test module) and renames the incremental step.
