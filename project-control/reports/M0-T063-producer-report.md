# M0-T063 Unit A1 producer report — fingerprint, manifest, cache, baseline (D-013)

Producer: orchestrator (D-017 authorizes direct implementation of the context-
intelligence units; the live supervised-runtime execution + `doctor --live` +
digest-bound supervised start remain owner-present actions bundled at the end).
Branch `task/M0-T063-context-index-a1`; governing D-001 + D-013 (existing packet).

## Deliverables (requirement → artifact)

| Rows | Artifact | Content |
|---|---|---|
| R026/R027/R028/R029/R030/R078 | `tools/repo_fingerprint.py` (402 SLOC) | one reusable fingerprint service: canonical-path checkout identity (reused from durable_state), snapshot fingerprint binding HEAD + dirty digest + version set + per-file manifest digest, per-file domain-separated raw/lf digests + mode metadata, mtime never proof, unreadable/unresolved-symlink → recorded failure |
| R023/R024/R025 | same | complete census: eligible / indexed / excluded(reason) / failed(reason) / stale, reconciles |
| R081 | same | eligibility reuses the accepted code-graph roots; census not widened |
| R031/R035/R036/R071 | `tools/repo_index_cache.py` (323 SLOC) | cache generations OUTSIDE the worktree (per-checkout LOCALAPPDATA sha256 namespace), lock + temp + validate + atomic os.replace promotion + current pointer, crash recovery quarantines incomplete/corrupt generations, prior valid generation stays loadable, single-writer lock with dead-pid stale reclaim, bounded retention |
| R049/R050/R051/R054/R055 | `tools/repo_index_baseline.py` (200 SLOC) | baseline from the UNMODIFIED code-graph generator: export digest + node/edge/input counts + generator source fingerprint; bounded sanitized committed evidence; append-only redacted JSONL telemetry outside the repo, nullable-not-zero measured fields |
| R029/R050/R064 | `docs/CONTEXT_INTELLIGENCE_PIPELINE.md` | the durable A1 contracts + rollback runbook |
| (additive) | `.github/workflows/ci.yml` | new `context-index-a1` job running the three test modules; existing jobs byte-untouched |
| evidence | `project-control/reports/M0-T063-baseline-evidence.md` | bounded sanitized reference digest + counts + census |

## Acceptance scenarios (packet AS-1..AS-5)

- **AS-1 fingerprint determinism + sensitivity** — `test_repo_fingerprint.py::DeterminismAndSensitivity`: two unchanged runs byte-identical; a single file byte, a config version, dirty state, and HEAD each move the fingerprint in isolation; hashes domain-separated; manifest canonically serialized sorted.
- **AS-2 census complete** — `CensusAccounting`: counts reconcile; an untracked eligible file is excluded with a reason; an unreadable/unresolved eligible file is a recorded failure, never a silent skip.
- **AS-3 atomic cache + crash recovery** — `test_repo_index_cache.py`: incomplete temp generation quarantined; corrupt promoted generation quarantined; prior valid generation stays loadable; retry idempotent; concurrent writer refused; dead-pid stale lock reclaimed, live lock not; no half-index observable as current.
- **AS-4 baseline frozen before behavior change** — `test_repo_index_baseline.py`: captured from the EXISTING unmodified generator; committed evidence bounded + sanitized (no raw graph, no absolute path); telemetry append-only, redacted, nullable-not-zero.
- **AS-5 mtime never proof** — `MtimeNeverProof`: a content change whose mtime is restored is still detected by the content digest.

## Test evidence (documented_test_commands, all green)
- `python tools/test_repo_fingerprint.py` → 14 passed (1 skipped: symlink test needs OS privilege).
- `python tools/test_repo_index_cache.py` → 12 passed.
- `python tools/test_repo_index_baseline.py` → 7 passed.
- `python -m pytest tools/test_repo_fingerprint.py tools/test_repo_index_cache.py tools/test_repo_index_baseline.py -q` → 32 passed, 1 skipped.
- `python tools/modularity_check.py --check` → 0 failures (each new module < 600 SLOC).

## Scope / forbidden paths
Not modified: `tools/agent_supervisor/**` (imported read-only for the checkout
identity), `tools/code_graph/generate.py` and `query.py` (imported read-only for
eligibility + the baseline), `tools/context_pack.py`. The three modules are
NEW; the ci.yml change is one additive job. Baseline captured from the unmodified
generator (AS-4 / D-013 s10/s11).

## Owner-present continuation (not part of this repository unit)
Running A1 through the supervised Codex-Claude loop (`doctor --live`, digest-bound
supervised start against the repaired live controller) is a live-controller
deployment + runtime-activation step — bundled in the final OWNER_ACTION_BUNDLE,
not performed here. This unit delivers the repository implementation.
