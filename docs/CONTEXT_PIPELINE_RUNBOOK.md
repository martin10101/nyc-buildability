# Context-intelligence pipeline — operating runbook (M0-T069 Unit F; corrected by M0-T075/D-018)

How to operate, verify, recover, and roll back the accepted context-
intelligence pipeline. Every command below is smoke-tested as written
(M0-T075, D-018-R051). Everything is deterministic code; nothing here
requires or permits an LLM structural decision (R009).

## THE canonical compiler and entry point (one compiler — D-018-R008/R022)

There is ONE context compiler: `tools/context_pack.py` (the integrated
build/emit pipeline: task packet + exact applicable requirement texts +
changed/implementation-path graph seeding + bounded Unit C ontology and
Unit E-class views + ADVISORY Unit D memory + reopened source/test excerpts,
all under one shared budget with enforceable role sufficiency and exact
provenance). The canonical orchestrator-facing command wraps it and adds
grounded model routing:

```
python tools/context_orchestrate.py prepare --task M0-T066 --role worker \
    --provider claude --max-bytes 400000 --out <dir>
python tools/context_orchestrate.py prepare --task M0-T066 --role worker \
    --provider claude --max-bytes 400000 --out <dir> --route \
    --model-config <path-to-protected-config.toml>
```

Exit codes: 0 ok; 2 over-budget split refusal or routing unavailable;
3 packet INSUFFICIENT for the role (missing/unresolved required evidence —
never silent). The dispatch manifest (`dispatch_manifest.json`) carries the
compile summary, the evidence-derived routing signals, the decision, and the
honest supervisor boundary statement.

**Owner-gated boundary (D-018-R026):** automatic controller/supervisor
consumption of these packets remains OWNER-GATED — wiring it would require
changing protected `tools/agent_supervisor/**` files, which is prohibited.
The command above is the canonical NON-protected handoff; the supervisor
keeps building its own review packets until the owner authorizes an
integration change. No automatic supervisor integration is claimed.

## Daily operation (all commands verified)

| Need | Command |
|---|---|
| Compile one bounded context pack directly | `python tools/context_pack.py --task M0-T066 --role worker --provider claude --max-bytes 400000 --out <dir>` |
| Build/refresh the deterministic index | `python -c "import sys; sys.path.insert(0,'.'); from tools.repo_index_incremental import build_incremental; build_incremental('.')"` |
| Repository views (census/changed/card/neighborhood/deep) | `python tools/repo_views_query.py census` · `card SEED` · `deep PATH A B` · `ask about_task M0-T066` |
| Subsystem/ontology resolution | `python tools/subsystem_resolver.py resolve <path...>` · `vocabulary` · `version` · `kinds` |
| Promote a memory digest | `python tools/memory_graph.py promote <digest.json> [--diff-file F]` |
| Status projection (JSON+MD) | `python tools/status_projection.py generate --out-json p.json --out-md p.md` |
| Projection staleness check (exit 3 = stale) | `python tools/status_projection.py check p.json` |
| Index-parity benchmark (Unit F scope) | `python tools/context_benchmark.py --samples 3 --out-json r.json --out-md r.md` |
| END-TO-END compiler benchmark — reproducible clean-checkout, frozen baseline (M0-T076) | `python tools/context_benchmark.py --e2e --baseline project-control/reports/M0-T076-baseline-g0.json --out-json e.json --out-md e.md` |
| Re-capture the frozen clean-state e2e baseline (only when the required evidence legitimately changes) | `python tools/context_benchmark.py --capture-e2e-baseline project-control/reports/M0-T076-baseline-g0.json` |
| Prepare a grounded worker/reviewer packet (canonical orchestrator, frozen G0 diff base) | `python tools/context_orchestrate.py prepare --task M0-Txxx --role reviewer --provider claude --max-bytes 400000 --out <dir>` |

> **Diff base (M0-T076 / D-019-R026).** `context_orchestrate.py` resolves the
> task's frozen G0 reviewed SHA as the default diff base (never a silent `HEAD`),
> so a reviewer packet on a **committed** branch still contains the committed
> hunks. Pass `--diff-base <sha>` to override with a trusted base; if no frozen
> base is recorded and none is given, the orchestrator REFUSES (nonzero) rather
> than diffing `HEAD`. The dispatch manifest records the chosen base SHA, how it
> was resolved, the current head SHA, the dirty/clean state, and the exact diff
> command.
>
> **Reproducible e2e baseline (M0-T076 / D-019-R035..R037).** The e2e benchmark
> compares each frozen hermetic shape's **required-evidence + relevance
> fingerprint** (sufficiency, exit, requirement ids/texts, resolved graph/source
> evidence, ontology, advisory-memory handling) against a clean-captured baseline
> — never a working-tree-diff source-id count. The exact command above exits `0`
> from any clean checkout and runs in permanent CI (`context-pipeline` job).
> M0-T075's baseline is preserved unmodified; see
> `project-control/reports/M0-T075-reconciliation-correction.md` for what the
> earlier dirty-capture "no-worse" result actually demonstrated.

Determinism self-proofs: `python tools/subsystem_resolver.py check`,
`python tools/repo_views_query.py check`,
`python tools/code_graph/generate.py --repo . --check`.

## Path containment (D-018-R031..R034)

Every context-related file read (compiler `--include`, deep views,
graph/view seeds, ontology inputs, memory evidence paths, task-derived
paths) goes through ONE shared rule (`tools/context_paths.py`): canonical
repo-relative form only (no absolute/drive paths, no `.`/`..`, no doubled
separators, no backslashes) plus real-path containment (symlinks/junctions
resolving outside the checkout refuse). Errors never disclose a private
absolute path.

## Storage map + retention (never in the repository — R011/R050, D-018-R035/R036)

- Index cache generations: `%LOCALAPPDATA%/NYCBuildabilityContextIndex/<checkout_key>/`
  — bounded generation retention runs on every build (current + rollback
  generations preserved; older pruned under the writer lock).
- Memory graph + digest quarantine: `.../NYCBuildabilityContextIndex/memory-graph/<checkout_key>/`
  — retention runs inside the promotion transaction.
- External telemetry (`incremental_telemetry.jsonl`) and routing decisions
  (`model_routing.jsonl`) are bounded/rotated (`<name>.1` keeps recent
  history); redaction preserved.
- Committed artifacts are ONLY sanitized reports under `project-control/reports/`.

## Failure recovery (all fail-closed, machine-readable)

- **Corrupt/half-written cache generation**: quarantined automatically on the
  next open; the next build is a clean full rebuild, byte-identical.
- **Interrupted write**: an orphaned temp generation (dead pid) is
  quarantined; `current` never points at it.
- **Concurrent writer**: the single-writer transaction refuses
  (`concurrent_writer`); retry after the other writer finishes (memory
  promotion accepts `retries=N`). Stale locks (dead pid past timeout)
  self-reclaim.
- **Stale ontology**: a memory digest carrying an outdated resolver/map stamp
  quarantines whole (`stale_ontology_version`) — re-emit with the current
  `subsystem_resolver.py version` stamp.
- **Insufficient packet (exit 3)**: the meta's `sufficiency.reason` names the
  missing evidence (requirement resolution, code evidence, primary-source
  diff); fix the input, never override the exit.
- **Stale projection (exit 3)**: any material control-plane input changed —
  regenerate; a file on disk is a committed/historical snapshot, never the
  current projection.

## Rollback (D-013-R071)

1. **Disable the new index path WITHOUT deleting the prior valid cache
   generation**: use `python tools/code_graph/generate.py --repo .` (the
   A1-frozen reference builder) or `python tools/context_pack.py ... --no-index`
   (records a coverage omission instead of consuming the index).
2. **Restore old full-build behavior**: `code_graph/generate.py` + `query.py`
   remain fully functional standalone.
3. **Quarantine incompatible cache generations rather than reinterpreting
   them**: unknown `cache_format_version` refuses and quarantines; to force
   manually, move the generation directory into the store's `quarantine/`.
4. **Leave committed evidence explaining why**: a report under
   `project-control/reports/` + a ledger progress note; each unit's rollback
   point is its G0 contract commit (see the status projection).

## Promotion decision (D-013-R060) — still owner-pending

The index-parity benchmark (42/42 byte-identical; M0-T069) and the M0-T075
end-to-end benchmark (five shapes through the ACTUAL compiler, all checks
true, no-worse-than-baseline) are on file with the threshold proposal.
Provider token savings remain UNMEASURED (no provider-reported usage).
**The promotion decision is PENDING the owner/control-plane decision**;
nothing in this pipeline flips a behavior flag on its own.

## Tests

`python tools/test_context_integration.py` (integration + adversarial) plus
the unit suites: `test_context_pack.py`, `test_context_pack_index.py`,
`test_subsystem_resolver.py`, `test_memory_graph.py`, `test_repo_views.py`,
`test_context_benchmark.py`, `test_status_projection.py`,
`test_repo_fingerprint/index_cache/index_incremental/index_assembly/
index_baseline.py`. The permanent `context-pipeline` CI job runs the
Units B–F suites + the integration suite on every push/PR.
