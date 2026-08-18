# Context-Intelligence Pipeline (D-013) — contracts & rollback

The context-intelligence pipeline is ONE system built in bounded units (D-013-R001).
Unit A1 (M0-T063) lays the deterministic foundation the later units build on:
a repository fingerprint + per-file manifest, a crash-safe cache-generation
store, and a baseline harness. This document is the durable contract for those
three pieces; A2–F extend it.

## Layers (D-013-R001)

1. **Content-addressed census / index** — deterministic fingerprint + per-file
   manifest + cache generations (A1 here; incremental indexing in A2).
2. **Bounded context compiler** — deterministic context packs (B).
3. **Closed deterministic ontology** — subsystem resolver (C).
4. **Measurement / status** — benchmarks, views, promotion (E, F).

## A1 contracts

### Repository identity (`tools/repo_fingerprint.py`)
- **Checkout identity** = `sha256(os.path.normcase(realpath(checkout)))`, reused
  from the accepted supervisor convention (`durable_state.checkout_key`) — never
  the folder basename (D-013-R027/R078). One reusable service; no per-feature
  digest invention (D-013-R026).
- **Snapshot fingerprint** binds committed AND uncommitted state (D-013-R028):
  repo-identity namespace + value; HEAD sha + branch + detached flag; a
  dirty-state digest over the sorted porcelain status set; the per-file source
  manifest digest; and the config/parser/schema version set. HEAD alone is never
  sufficient — the dirty digest is always included. The per-file manifest hashes
  the CONTENT of EVERY eligible file, tracked or untracked (matching what the
  code-graph generator indexes), so the snapshot fingerprint uniquely determines
  the generator's output; `tracked` is recorded per file as census metadata, not
  an index-exclusion.
- **Per-file manifest**: for each eligible file (tracked or untracked), a domain-separated
  `raw` digest (exact bytes) and `lf` digest (CRLF→LF normalized, so a pure
  line-ending flip is distinguishable), size, and parse-relevant mode metadata
  (symlink flag, NFC name, casefold name — so a case-only or normalization-only
  rename is a detectable change). Sorted by path; canonically serialized.
- **Eligibility** = the accepted code-graph roots (`code_graph.scan_input_files`);
  the census is NOT widened (D-013-R081).
- **mtime is never proof** (D-013-R030): the module always reads and hashes
  content; mtime is not consulted for any content decision.
- **Unreadable / unresolved-symlink eligible files** are recorded FAILURES with a
  grouped reason, never silently skipped (D-013-R029).

### Census accounting (D-013-R023/R024/R025)
`eligible = indexed + Σ excluded(reason) + Σ failed(reason)` must reconcile.
At the fingerprint layer every eligible file (from the accepted code-graph walk,
which has already applied directory exclusions) is indexed unless it is a
recorded failure, so `excluded` is normally empty here; `failed` reasons are
grouped (`unreadable`, `symlink_unresolved`). "Complete census" only holds when
every eligible file is accounted as indexed or explicitly failed.

### Hash domains (D-013-R029)
Every digest is `sha256(domain \x00 len(part) part …)`; the domain tag plus
length framing make a file-content digest, a manifest digest, and a snapshot
digest non-colliding even on identical bytes. Canonical JSON is
`sort_keys, separators=(",",":"), ensure_ascii`. No wall-clock enters any digest.

### Cache generations (`tools/repo_index_cache.py`, D-013-R031/R035/R036)
- Live OUTSIDE the worktree, under `%LOCALAPPDATA%\NYCBuildabilityContextIndex\
  <checkout-sha256>\` (POSIX: `$XDG_STATE_HOME/…`). A location inside the
  checkout is refused.
- **Atomic promotion**: write to `tmp/<fp>.<pid>`, self-validate (recorded digest
  == digest of payload), then `os.replace` the directory into `generations/<fp>`,
  then advance the `current.json` pointer. A crash leaves either the prior valid
  generation or a complete new one — never a half-index as current.
- **Recovery** (run on every open): an incomplete temp generation is quarantined
  (`quarantine/<fp>.incomplete`); a promoted generation whose digest no longer
  matches its payload is quarantined (`.corrupt`). The prior valid generation
  stays loadable.
- **Single-writer lock** (atomic mkdir): a concurrent writer is refused; a lock
  whose recorded pid is dead and whose age exceeds `LOCK_STALE_SECONDS` is
  reclaimed. Retry is idempotent.
- **Bounded retention** (`prune(keep=N)`): the current generation and the N most
  recent are kept, so a prior valid generation is available for rollback
  (D-013-R071).

### Baseline harness (`tools/repo_index_baseline.py`, D-013-R049/R050/R054/R055)
- Runs the UNMODIFIED code-graph generator (`code_graph.build_graph`) and records
  the export digest (over the generator's own canonical bytes) + node/edge/input
  counts + the generator's `source_fingerprint` (a content fingerprint of the
  whole input corpus, NOT a generator-code identity) — the REFERENCE that A2's
  incremental output must match byte-for-byte.
- **Two storage classes**: (a) committed evidence — a bounded, sanitized JSON+MD
  summary (digests + counts + census only; no raw graph; no private absolute
  path); (b) external telemetry — an append-only, redacted JSONL run record in
  the per-checkout cache dir outside the repo, with measured-only fields null
  when unavailable (never fabricated as zero; D-013-R051).

### Incremental indexing (`tools/repo_index_incremental.py` + `tools/repo_index_assembly.py`, A2, D-013-R032/R037/R059/R079)
- **Three build modes**, recorded per run as `mode`/`rebuild_reason`:
  - `reuse` — an unchanged snapshot (its content-hashed fingerprint already has a
    validated generation) returns that generation's exact bytes; **zero files
    reparsed** (D-013-R059).
  - `incremental` — a local content edit reparses **only the changed files**
    (`ast.parse` / TS scan re-run for those), reuses every unchanged file's
    cached per-file extraction *bundle*, and reassembles the exact generator
    output; **no full rebuild on a local change** (D-013-R032/R059).
  - `full` — a cold build, a structural change (add/delete/rename, which alters
    the global resolution index or the schema-node set), or a global invalidator
    (parser/config/schema/eligibility version, **or a change to the generator's
    `CONFIG_INPUTS`** — e.g. `apps/web/tsconfig.json`, which steers TS `@/` alias
    resolution) rebuilds via the same driver with a recorded reason. A structural
    change is a documented invalidator of the resolution index, so a full rebuild
    is the deterministically-safe closure (D-013-R032 "smallest deterministically
    proven invalidation closure").
  - **Config-input guard**: tsconfig is not an indexed file, so a digest of the
    generator's `CONFIG_INPUTS` is folded into the fingerprint the incremental
    layer uses (`repo_index_assembly.config_inputs_version`); a config-input change
    moves the cache key (no stale hit) and fires a global invalidator. Without it,
    a reused TS bundle would keep stale alias-resolved edges — a byte divergence.
- **Byte-identical assembly** (`repo_index_assembly.drive`): reproduces
  `code_graph.build_graph`'s exported bytes from per-file bundles. It reuses the
  generator's own extraction internals (`_extract_py/_ts`, `_PyIndex`,
  `_TsResolver`, `_contract_edges`, `_EdgeSet`) and is **version-guarded** — it
  runs only against the exact `GENERATOR_VERSION`/`SCHEMA_VERSION` it was
  verified for; any other version raises and the caller falls back to the real
  `build_graph` (fail-safe, never fail-wrong).
- **Parity invariant** (enforced by test): the incremental export is
  BYTE-IDENTICAL to a clean full rebuild produced by the REAL
  `code_graph.build_graph` — an independent reference, across cold / warm-reuse /
  every change class. If the generator is bumped, the parity test fails until the
  replica (and its known-version constants) are updated in lock-step.
- **Change classification**: added / content_modified / metadata_modified /
  deleted / renamed (a delete+add sharing a raw content digest), plus global
  invalidators.
- **Affected importer closure**: the deterministic transitive set of files that
  import a changed file, read from the cached bundles' real import edges (an
  internal import resolves `to` a target file path).
- **Run record + telemetry** (D-013-R024/R050/R052): each build emits a rich
  machine-readable run record (repo identity, HEAD/branch/dirty digest,
  source-manifest fingerprint, versions, census, change counts, files
  parsed/reused, graph nodes/edges before+after, mode/reason; measured-only
  fields are null, never fabricated) and appends it to an external, append-only,
  redacted JSONL log in the per-checkout runtime dir (never committed; identity
  is a sha, never an absolute path).
- **Crash-safety / concurrency**: reuses the A1 cache's fail-closed rules; a full
  rebuild is always available as reference and recovery. mtime is never trusted.

## Rollback (D-013-R071)
A1 adds only NEW modules and one additive CI step; nothing changes the generator
or any existing behavior. To roll back:
1. Revert the A1 commit(s); the code-graph generator and every existing test are
   untouched, so the tree returns to its prior identity.
2. Delete the external cache directory if desired — it lives outside the repo
   (`%LOCALAPPDATA%\NYCBuildabilityContextIndex\<sha>\`); a prior valid
   generation is never needed once A1 is reverted, and no repository state
   depends on it. Never use a destructive broad filesystem command; remove only
   that one per-checkout directory.
3. No quarantine reinterpretation: quarantined generations are left in place as
   evidence; they are never loaded.
