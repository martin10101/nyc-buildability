# M0-T066 producer report — Unit C: versioned deterministic subsystem/ontology resolver

Producer: orchestrator (single writer, wt-m0t064, branch
`task/M0-T066-subsystem-resolver`). Stacked on accepted Unit B (M0-T065,
merged to main 1d159a8).

## What was built (allowed_paths only)

1. **`tools/subsystem_map.json`** — the versioned closed-vocabulary mapping
   (map_schema_version 1.0.0, map_version 1.0.0). 11 ordered rules; every
   `subsystem_id` IS its `prefix` and every prefix is an existing directory
   with committed files. The vocabulary is therefore a restatement of facts
   the repository tree already contains — no second free-form taxonomy is
   possible (D-013-R008 enforced structurally, not by convention).
2. **`tools/subsystem_resolver.py`** (~250 SLOC) — fail-closed map load +
   validation (7 machine-readable error codes), deterministic longest-prefix
   whole-segment path→subsystem resolution, the ontology version stamp
   (`RESOLVER_VERSION` 1.0.0 + map version + sha256 map digest) for
   D-013-R028/R044 downstream binding, the honest graph-kinds report
   (D-013-R018; consumes the A1/A2 index read-only in process), and a bounded
   CLI (`resolve|vocabulary|version|kinds|check`) where `check` is a two-run
   byte-identity determinism self-proof.
3. **`tools/subsystem_entities.py`** (~230 SLOC) — the D-013-R046 two-pass
   API: `propose()` (pass 1, extraction proposes typed candidate facts with
   evidence refs) and `resolve_proposals()` (pass 2, the deterministic
   resolver validates existence against the authoritative project-control
   indexes and derives every structural link: task→milestone,
   requirement→directive, path→subsystem, file→graph-node, symbol→graph-node).
   Unvalidatable proposals land in `unresolved_links[]` with machine-readable
   reasons. Missing/malformed authoritative indexes fail closed
   (`EntityIndexError`). Exports task-index/directive-index sha256 digests for
   Unit D (R044).
4. **`tools/test_subsystem_resolver.py`** — 21 tests: executable AS-1..AS-6
   packs plus edge cases (segment-boundary prefix matching, root files,
   symbol resolution, evidence preservation, propose normalization/dedupe).
5. **`docs/SUBSYSTEM_ONTOLOGY.md`** — the ontology contract: closed
   vocabulary law, resolution law, version-binding duties for Unit D, honest
   statement of the ACTUAL code-graph node/edge kinds (no subsystem node kind
   exists in the graph and none is injected), and the Unit C/D boundary.

## Key design decisions

- **Vocabulary = existing path prefixes, enforced at load.** The R008 risk in
  any ontology is name invention. Here the resolver rejects a rule whose id is
  not literally its existing-directory prefix, so the closed vocabulary cannot
  drift from repository facts without failing closed.
- **Existence validation is separated from bucket derivation** (two-pass,
  R046): `resolve_path` is a pure mapping; the entity layer decides existence
  against the tree/indexes/graph — so a future LLM extractor can propose
  freely while the resolver alone mints links (R009/R045).
- **No graph mutation, no new node kind** (R018): subsystem lives only at the
  resolver layer; the kinds report proves the graph's actual vocabulary and
  records the export digest.
- **Unit D boundary preserved** (R043): no memory digest schema, storage, or
  promotion logic exists in this unit; M0-T067 depends on M0-T066.

## Self-check results (all commands from documented_test_commands)

- `python tools/test_subsystem_resolver.py` → **21 tests OK**.
- `python -m pytest tools/test_subsystem_resolver.py -q` → **21 passed**.
- `python tools/modularity_check.py --check` → **failures 0** (252 files).
- `ruff check` (0.13.0, CI-matching) on the three new Python files → clean.
- CLI smoke: `vocabulary` (11 subsystems + version stamp), `resolve`
  (services/api hit, docs hit, root-file honest miss), `check` → PASS.

## Scope compliance

- Diff touches ONLY allowed_paths (new files + the packet's own reports).
- `tools/agent_supervisor/**`, all A1/A2 index modules, all Unit B context-pack
  modules, `.github/`, `services/`, `apps/`, `.claude/` untouched (R082 +
  forbidden_paths).

Evidence details: `M0-T066-coverage-evidence.md`; per-requirement map:
`M0-T066-evidence-map.json`.
