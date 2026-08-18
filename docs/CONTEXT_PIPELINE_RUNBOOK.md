# Context-intelligence pipeline — operating runbook (M0-T069 Unit F, D-013)

How to operate, verify, recover, and roll back the accepted context-
intelligence pipeline (Units A1/A2/B/C/D/E). Every command is deterministic
code; nothing here requires or permits an LLM structural decision (R009).

## Daily operation

| Need | Command |
|---|---|
| Build/refresh the deterministic index (auto reuse/incremental/full) | `python -c "from tools.repo_index_incremental import build_incremental; build_incremental('.')"` (or any consumer below — they build in-process) |
| Build a bounded context pack (the ONE compiler) | `python tools/context_pack.py --task <ID> --role worker --provider claude --out <dir>` |
| Repository views (census/changed/card/neighborhood/deep) | `python tools/repo_views_query.py census` / `card SEED` / `deep PATH A B` / `ask about_task M0-Txxx` |
| Subsystem/ontology resolution | `python tools/subsystem_resolver.py resolve <path...>` / `vocabulary` / `kinds` |
| Promote a memory digest | `python tools/memory_graph.py promote <digest.json> [--diff-file F]` |
| Status projection (JSON+MD, stale-checked) | `python tools/status_projection.py generate --out-json p.json --out-md p.md` then `check p.json` (exit 3 = stale) |
| Promotion benchmark (full corpus) | `python tools/context_benchmark.py --samples 3 --out-json r.json --out-md r.md` (exit 2 = an R059 evidence item failed) |

Determinism self-proofs: `subsystem_resolver.py check`,
`repo_views_query.py check`, `code_graph/generate.py --check`.

## Storage map (never in the repository — R011/R050)

- Index cache generations: `%LOCALAPPDATA%/NYCBuildabilityContextIndex/<checkout_key>/`
- Memory graph + digest quarantine: `.../NYCBuildabilityContextIndex/memory-graph/<checkout_key>/`
- Committed artifacts are ONLY sanitized reports under `project-control/reports/`.

## Failure recovery (all fail-closed, machine-readable)

- **Corrupt/half-written cache generation**: recovery is automatic on every
  open (`IndexCache.recover()` quarantines it); the next build is a clean
  full rebuild, byte-identical to reference (benchmark case
  `corrupt_cache_recovery`).
- **Interrupted write**: an orphaned temp generation (dead pid) is
  quarantined on the next open; `current` never points at it (benchmark case
  `interrupted_write_recovery`).
- **Concurrent writer**: the single-writer lock refuses
  (`concurrent_writer`); retry after the other writer finishes. A stale lock
  (dead pid past the timeout) is reclaimed automatically.
- **Stale ontology**: a memory digest carrying an outdated resolver/map stamp
  is quarantined whole (`stale_ontology_version`) — re-emit the digest with
  the current `subsystem_resolver.py version` stamp.
- **Stale projection**: `status_projection.py check` exits 3 — regenerate;
  never hand-edit the projection.

## Rollback (D-013-R071)

If the incremental index path must be abandoned:

1. **Disable the new path WITHOUT deleting the prior valid cache
   generation**: consumers fall back to the unmodified full builder — use
   `python tools/code_graph/generate.py --repo .` (the A1-frozen reference
   builder) or the pack's `--no-index` escape hatch
   (`context_pack.py --no-index`, which records a coverage omission instead
   of consuming the index). No cache deletion is required or permitted.
2. **Restore old full-build behavior**: `code_graph/generate.py` +
   `query.py` remain fully functional standalone (accepted M0-T030 behavior,
   never modified by this initiative).
3. **Quarantine incompatible cache generations rather than reinterpreting
   them**: the store already refuses unknown `cache_format_version` and
   quarantines rather than migrating; to force it manually, move the
   generation directory into the store's `quarantine/` — never edit payloads.
4. **Leave committed evidence explaining why**: record the rollback reason as
   a report under `project-control/reports/` and a ledger progress note; the
   Git checkpoint for every unit is its recorded rollback point (the G0
   contract commit in the status projection).

## Promotion decision (D-013-R060)

The benchmark report (`project-control/reports/M0-T069-benchmark-report.md`)
carries the frozen-corpus evidence (42 cases, all byte-identical to the
clean-full reference; every R059 minimum proven) and the threshold proposal
with rationale. Provider token savings are UNMEASURED (no provider-reported
usage in the offline benchmark) and are never inferred from byte estimates
(R012/R053/R057).

**The promotion decision is PENDING the owner/control-plane decision.**
Nothing in Unit F flips a behavior flag; the pipeline operates exactly as
accepted by its unit gates until the owner decides. The thresholds were
proposed BEFORE that decision (no success percentage set after seeing
results).

## Boundaries

- Source files remain authoritative for every material conclusion; index,
  views, and memory are advisory navigation/placement layers.
- `tools/agent_supervisor/**` is untouched by this initiative (R082).
- Tests: `python tools/test_context_benchmark.py`,
  `python tools/test_status_projection.py` (plus the unit suites:
  `test_repo_fingerprint/index/cache`, `test_context_pack*`,
  `test_subsystem_resolver`, `test_memory_graph`, `test_repo_views`).
