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
  sufficient — the dirty digest is always included.
- **Per-file manifest**: for each eligible tracked file, a domain-separated
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
Excluded reasons are grouped (e.g. `untracked`); failures are grouped
(`unreadable`, `symlink_unresolved`). "Complete census" only holds when every
eligible file is accounted as indexed or explicitly excluded/failed.

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
  counts + the generator's source fingerprint — the REFERENCE that A2's
  incremental output must match byte-for-byte.
- **Two storage classes**: (a) committed evidence — a bounded, sanitized JSON+MD
  summary (digests + counts + census only; no raw graph; no private absolute
  path); (b) external telemetry — an append-only, redacted JSONL run record in
  the per-checkout cache dir outside the repo, with measured-only fields null
  when unavailable (never fabricated as zero; D-013-R051).

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
