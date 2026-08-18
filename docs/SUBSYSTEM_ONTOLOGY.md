# Subsystem ontology — versioned deterministic resolver (M0-T066 Unit C, D-013)

The canonical, versioned, deterministic subsystem/ontology mapping for memory
placement. Established BEFORE any session/task memory digest may reference a
subsystem (D-013-R043): Unit D digests must stamp the version this layer
exports and may never invent placement.

## The closed vocabulary (D-013-R008)

There is NO second free-form taxonomy. A subsystem id **is** an existing
repo-relative directory prefix, enforced structurally:

- `tools/subsystem_map.json` holds ordered rules `{subsystem_id, prefix}`;
  the resolver **fails closed** on any rule where `subsystem_id != prefix`
  (`free_form_subsystem_id`) or where the prefix is not an existing directory
  (`prefix_not_in_tree`). Inventing a name is impossible without failing the
  load, and every vocabulary entry stays a fact the repository tree already
  states.
- Vocabulary v1 (11 subsystems, all existing directories): `services/api`,
  `apps/web`, `packages/contracts`, `tools/code_graph`,
  `tools/agent_supervisor`, `tools`, `docs`, `project-control`, `supabase`,
  `.github`, `.claude`.
- A path matching no rule (e.g. a repo-root file like `CLAUDE.md`) resolves to
  `unresolved` with reason `no_matching_subsystem_rule` — never to a guessed
  bucket.

## Deterministic resolution (D-013-R009/R045)

`tools/subsystem_resolver.py` — pure code, no model anywhere:

- `load_map(repo_root)` → validated map + `map_digest` (sha256 over the exact
  map bytes). Malformed JSON, unknown `map_schema_version`, duplicate or
  non-normalized prefixes all raise `SubsystemMapError` (machine-readable
  code); the CLI exits `2` with an error document. Never a silent default.
- `resolve_path(path, loaded)` → longest-prefix match on whole path segments
  (`tools/code_graph/query.py` → `tools/code_graph`, not `tools`;
  `toolsandmore/x.py` matches nothing).
- `version_stamp(loaded)` → `{resolver_version, map_schema_version,
  map_version, map_digest}` — the ontology-version binding downstream
  fingerprints (D-013-R028) and Unit D memory digests (R044) must embed.
- CLI: `resolve`, `vocabulary`, `version`, `kinds`, `check` (two-run
  byte-identity self-proof). Bump `RESOLVER_VERSION` on any behavior change;
  bump `map_version` on any vocabulary change.

## Entity validation + two-pass linking (D-013-R045/R046)

`tools/subsystem_entities.py`:

- **Pass 1 — extraction proposes**: `propose(candidates)` normalizes bounded
  candidate facts into typed proposals (`milestone|task|directive|requirement|
  path|symbol`) with evidence references. A future authorized LLM extractor
  may only ever produce proposals — it can never mint a structural link.
- **Pass 2 — resolver validates/derives**: `resolve_proposals(...)` derives
  every structural link from authoritative repository facts only:
  task → milestone via the task packet + `master_plan.json`;
  requirement → directive via `project-control/directives/`;
  path → subsystem via the versioned map; files → existing code-graph nodes
  when indexed; symbols only by exact node-id membership in a provided graph.
  Anything unverifiable lands in `unresolved_links[]` with a machine-readable
  reason (`unknown_task_id`, `path_not_in_source_tree`,
  `no_matching_subsystem_rule`, `graph_not_provided`, ...). Nothing is
  guessed or silently dropped.
- A missing/malformed authoritative index raises `EntityIndexError` (fail
  closed). `AuthoritativeIndexes.digests()` exports the task-index and
  directive-index sha256 digests Unit D digests must bind (R044).

## Honest graph kinds (D-013-R018)

The accepted code graph defines node kinds `py_module`, `class`, `function`,
`method`, `ts_module`, `ts_symbol`, `contract_schema`, `external` and edge
types `import`, `reexport`, `dynamic_import`, `contract_ref` — **there is no
subsystem node kind, and this layer never injects one**. "Subsystem" exists
only at the resolver layer, derived from the path. `subsystem_resolver.py
kinds` reports the kinds ACTUALLY present in the current index export
(consumed read-only, in process, from the A1/A2 deterministic index) and
states `subsystem_node_kind_in_graph: false`.

## Boundaries

- Advisory placement layer: source files remain authoritative; this maps
  facts, it never decides compliance, acceptance, or legal meaning.
- Unit C establishes the resolver + versions ONLY. Session/task memory
  digests, their storage, and promotion are Unit D (M0-T067), sequenced after
  this unit (R043).
- Tests: `python tools/test_subsystem_resolver.py` (AS-1..AS-6 + edge cases).
