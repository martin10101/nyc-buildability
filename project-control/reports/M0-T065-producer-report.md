# M0-T065 Unit B producer report — bounded context compiler (D-013)

Producer: orchestrator (D-017 authorizes direct implementation of the context-
intelligence units). Branch `task/M0-T065-context-compiler`, stacked on the
accepted A2 (M0-T064) merged to main. Governing D-001 + D-013.

## Deliverable
The ONE context pack now (a) consumes the deterministic A1/A2 index under ONE
total budget with coverage/provenance emission and refuse-or-split, and (b) adds
the owner-approved adaptive tier amendment — delivered as a MODULAR decomposition
of the former 850-SLOC `tools/context_pack.py`:

| Module | SLOC | Responsibility |
|---|---|---|
| `context_pack_io.py` | 54 | deterministic hashing / canonical JSON / git / file I/O |
| `context_pack_budget.py` | 171 | 0A.4 budget primitives (drift-locked) + the adaptive tier amendment |
| `context_pack_index.py` | 141 | consumption of the deterministic A1/A2 index (in-process, no subprocess) |
| `context_pack_sources.py` | 293 | Section 12.1 source gathering |
| `context_pack_render.py` | 236 | Section 12.3 meta + `context.md` rendering |
| `context_pack_assembly.py` | 224 | build / overflow / emit + role sufficiency |
| `context_pack.py` (facade) | 116 | thin orchestrator + CLI + preserved public imports |

All modules are < 600 SLOC; `modularity_check --check` → 0 failures. The public
surface (`DEFAULT_*`, `estimate_tokens`, `effective_ceiling_tokens`, and the CLI)
is preserved by the facade, so `tools/test_context_pack.py` (incl. the drift-lock)
keeps passing unchanged.

## What Unit B adds
- **Index consumption (R040).** The compiler builds the code-graph *neighborhoods*
  for the changed/target paths and a *census + provenance* source from the A1/A2
  index IN PROCESS (`build_incremental` + an in-process `GraphIndex`) — no
  subprocess, no cache-rebuild side effect. Dependency breadth is derived from the
  graph's importer edges.
- **One total budget (R039).** `budget.single_total_budget = true`; a single
  effective byte bound governs all sources; no per-source budgets.
- **Adaptive tier amendment (R041/R080; owner decision 7).** small/normal ~5K-8K,
  medium (explicit, justified by dependency breadth, capped at the accepted 32K
  target), large/architectural (split-first). It layers ON TOP of the drift-locked
  constants: `amendment.changes_constants = false`, and the hard ceiling stays
  `min(ordinary, relative)`. Fail-closed honesty: a medium/large candidate without
  a recorded justification does NOT silently upsize — the target is held at normal
  and the withheld larger target is recorded.
- **Coverage/provenance emission (R040/R024/R002/R058).** `context.meta.json`
  carries the census (with `reconciles`), coverage mode, source-manifest digest,
  export digest, HEAD/branch, versions, dependency breadth, per-source digests,
  omitted categories with reasons, truncations, graph query parameters, estimated
  tokens, actual bytes, and the role-sufficiency verdict.
- **Refuse-or-split preserved (R003/R013/R040).** Material that does not fit fails
  closed with a split proposal (exit 2); material is preserved under `evidence/`
  and never silently truncated. `--no-index` is a fail-safe escape hatch that
  records a coverage omission rather than crashing.

## Determinism (load-bearing)
Same source state + args → byte-identical `context.md` AND `context.meta.json`.
The deterministic pack records source-identity provenance that is invariant to
transient working-tree noise (`source_manifest_digest`, `export_digest`,
HEAD/branch, census, versions); the volatile full snapshot fingerprint +
dirty-state digest — which change when `--out` is written inside the repo — are
recorded only in the EXTERNAL run-record JSONL, never in the deterministic
artifact. Cache-state fields (mode/hit-miss/files-parsed) are likewise excluded
from the pack. Enforced by `test_context_pack.py` (determinism + summarized
fixpoint) and `test_context_pack_index.py::AS6_Determinism`.

## Test evidence (documented_test_commands)
- `python tools/test_context_pack.py` → 15 passed (incl. drift-lock + determinism).
- `python tools/test_context_pack_index.py` → 8 passed (AS-1..AS-6 + escape hatch).
- `python -m pytest tools/test_context_pack.py tools/test_context_pack_index.py -q` → 23 passed.
- `python tools/modularity_check.py --check` → 0 failures.
- `ruff check tools/context_pack*.py tools/test_context_pack*.py` → clean.
- Real-repo CLI: tier=normal (target 8000), single_total_budget, census reconciles
  (438 eligible), coverage_mode=census, within_bound; deterministic.

## Scope / forbidden paths
`tools/agent_supervisor/**` (incl. the drift-lock target `review_packet.py`),
`tools/code_graph/generate.py|query.py`, and the accepted A1/A2 modules
(`repo_fingerprint`, `repo_index_cache`, `repo_index_incremental`,
`repo_index_assembly`, `repo_index_baseline`) are imported READ-ONLY, never
modified; `tools/modularity_baseline.json` is not edited. No `.github` change
(the CI wiring of `test_context_pack.py` is the standing M0-T043 residual, carried
forward — the gates run the suites manually).
