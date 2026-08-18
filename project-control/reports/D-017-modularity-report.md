# D-017 Stage 9 — modularity and large-file control report

Produced by the orchestrator at origin/main 9bf1901 (all D-013 units merged).
Census tool: `python tools/modularity_check.py --report` (deterministic;
261 selected files, **failures 0**, warnings 4 — all pre-existing signals).

## Enforcement in place (permanent, machine-enforced)

- **CI regression gate**: the `modularity` CI job (M0-T073, accepted +
  merged) fails any NEW handwritten production file over the hard threshold
  and unjustified growth of existing oversized files, with a digest-protected
  baseline (`tools/modularity_baseline.json`) and an expiring, path-exact
  exception mechanism (`tools/modularity_exceptions.json`). Legacy debt is
  reported, new regressions FAIL — exactly the D-017 Stage 9 rule.
- **Repository law**: CLAUDE.md §16 + `docs/CODE_MODULARITY_POLICY.md` +
  path-scoped `.claude/rules/code-architecture.md` (600 warn / 750 justify /
  1,000 hard SLOC bands; responsibility separation; facade-preserving splits).

## Largest handwritten production files (SLOC, tracked, excl. tests/generated)

| SLOC | file | disposition |
|---|---|---|
| 2817 | tools/agent_supervisor/cli.py | **Deferred** — R082 prohibits modifying `tools/agent_supervisor/**` under this initiative; pre-existing debt, baseline-covered, symbol-ceiling warning on record |
| 1899 | tools/agent_supervisor/loop.py | Deferred — same R082 freeze |
| 1854 | services/api/app/connectors/mappluto_geometry_arcgis.py | Deferred — accepted legacy connector, baseline-covered; a data-mapping-heavy module (cohesion argument on record), symbol-ceiling warning |
| 1626 | services/api/app/connectors/zoning_features_arcgis.py | Deferred — same class |
| 1593 | services/api/app/connectors/ztldb_soda.py | Deferred — same class |
| 1577 | tools/agent_supervisor/policy.py | Deferred — R082 freeze |
| 1287 | tools/directive_registry.py | Deferred — control-plane core; stable, single-responsibility (registry), high test coverage; flagged for the next control-plane maintenance window |
| 1258 | tools/agent_supervisor/claude_runner.py | Deferred — R082 freeze |
| 1196 | tools/project_control.py | Deferred — ADR-005 control CLI; deliberately single-file authority surface; splitting it changes the audited enforcement boundary and needs its own reviewed task |
| 994 | services/api/app/documents/review_actions.py | Deferred — below hard threshold; justify-band record exists |

## Files refactored by this initiative (before/after)

| file | before | after | how |
|---|---|---|---|
| tools/context_pack.py | 850 SLOC monolith (justify band) | 116 SLOC compatibility facade + 6 focused modules: io 54, budget 171 (now ~223 with tier), index 141 (~181), sources 293 (~365), render 236 (~270), assembly 224 (~280) | Unit B (M0-T065): extract-first behavior-preserving split, public imports + CLI preserved via the facade, drift-lock tests intact; every module < 600 SLOC |

All NEW initiative modules were born modular (SLOC at acceptance):
repo_fingerprint / repo_index_cache / repo_index_incremental (500) /
repo_index_assembly (317) / repo_index_baseline (A1/A2);
subsystem_resolver 227 / subsystem_entities 202 (C);
memory_digest ~170 / memory_grounding ~70 / memory_graph ~230 (D);
repo_views ~300 / repo_views_query ~270 (E);
context_benchmark ~400 / status_projection ~280 (F). Modularity CI: 0
failures at every unit's acceptance and at final main.

## Responsibility / coupling findings

- Domain vs storage vs I/O vs CLI separation holds across the new pipeline:
  identity (fingerprint) / storage (cache) / build (incremental+assembly) /
  compile (context_pack modules) / ontology (resolver+entities) / memory
  (digest+grounding+graph) / retrieval (views+query) / measurement
  (benchmark+projection) are distinct modules with explicit interfaces and
  focused test files (203 tests across the initiative suites).
- Highest-priority non-initiative hotspots remain `tools/agent_supervisor/*`
  (R082-frozen; 4 of the 6 largest files) and the three ArcGIS/SODA
  connectors — all baseline-covered, none grown by this initiative
  (`git diff` on those paths across every unit branch: empty).
- Symbol-ceiling warnings (4) are unchanged from before the initiative and
  belong to the deferred set above.

## Deferred and why

Everything in the "largest files" table above: R082 freeze (supervisor),
accepted-legacy baseline (connectors), or authority-surface risk
(project_control/directive_registry — splitting the enforcement CLI is a
reviewed task of its own, not a drive-by refactor). D-017 Stage 9 explicitly
prohibits turning this into an unrelated whole-repository rewrite; no
severe NEW hotspot was discovered by evidence during the initiative.

## Test coverage before/after (initiative scope)

Before the initiative: `context_pack.py` had 15 tests (incl. drift-lock).
After: 15 (B, preserved) + 8 (B index/tier) + 21 (C) + 31 (D) + 26 (E) +
15 + 8 (F) = **124 tests over the refactored/new pipeline code**, plus the
A1/A2 suites (63 passed/1 skipped battery recorded at A2 acceptance). Every
behavior move was covered by tests before or alongside the move.
