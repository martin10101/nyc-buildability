# M0-T066 Unit C — closed-vocabulary, determinism & fail-closed evidence (D-013)

## Closed vocabulary is structural, not stylistic (R008 / AS-1)
- `load_map` refuses `subsystem_id != prefix` with code `free_form_subsystem_id`
  (`AS1ClosedVocabulary::test_free_form_name_fails_closed`) and refuses any
  prefix that is not an existing directory with `prefix_not_in_tree`
  (`test_nonexistent_prefix_fails_closed`). Duplicates refuse
  (`duplicate_rule_prefix`).
- The shipped map (`tools/subsystem_map.json`, map_version 1.0.0) holds 11
  rules; `test_real_map_every_id_is_existing_prefix` proves every id equals its
  prefix AND is a real directory. All 11 prefixes contain committed files
  (verified via `git ls-files`), so a fresh CI clone always contains them.

## Versioned determinism (R028/R044 binding / AS-2)
- `AS2VersionedDeterminism::test_two_runs_byte_identical_and_stamped`: two full
  load+vocabulary+resolve runs produce byte-identical canonical JSON; the
  version stamp carries `resolver_version` (1.0.0), `map_schema_version`,
  `map_version`, and `map_digest` — independently recomputed in the test as
  sha256 over CRLF-normalized map bytes (the A1 fingerprint convention, so
  Windows/CRLF and CI/LF checkouts stamp the identical ontology digest):
  `a569d502d54fb08f9f2333d6840c7d65a2043cb32c5340e26cfc3fe6b8f3c0ab`.
- CLI self-proof: `python tools/subsystem_resolver.py check` runs the pipeline
  twice and byte-compares (exit 0 = PASS; `test_cli_check_passes`).
- `AuthoritativeIndexes.digests()` exports `task_index_digest` +
  `directive_index_digest` (sha256 over canonical JSON) for Unit D digests.

## Derived parents, two-pass, nothing dropped (R009/R045/R046 / AS-3, AS-4)
- `AS3DerivedParents`: path→subsystem (`services/api/x.py` → `services/api`),
  task→milestone (`M0-T001` → `M0` from the packet, validated against the
  master plan), requirement→directive (`D-900-R001` → `D-900`) — all from
  authoritative fixtures, zero model involvement. A task whose packet names a
  milestone absent from the master plan is UNRESOLVED
  (`milestone_not_in_master_plan`), never silently linked.
- `AS4TwoPass`: 10 mixed proposals → `len(links) + len(unresolved_links) == 10`
  (nothing silently dropped); reasons asserted per kind: `unknown_task_id`,
  `path_not_in_source_tree`, `unknown_requirement_id`, `unknown_directive_id`,
  `unknown_milestone_id`, `no_matching_subsystem_rule`, `graph_not_provided`.
  `propose()` normalizes (`./x`, backslashes) and dedupes deterministically;
  evidence references survive onto links.

## Honest graph kinds (R018 / AS-5)
- `AS5HonestGraphKinds`: on a hermetic git fixture the report enumerates the
  kinds ACTUALLY present (`py_module`, `function`, edge `import`), records the
  index `export_digest`, and asserts `subsystem` is NOT a node kind
  (`subsystem_node_kind_in_graph == false`). Graph bytes are consumed
  read-only via `build_incremental`; nothing is injected.

## Fail closed (R013 / AS-6)
- Malformed JSON map → `map_malformed_json`; unknown `map_schema_version` →
  `unknown_map_schema_version`; missing map → `map_unreadable`; non-object map
  via CLI → exit 2 + `{"error":{"code":"map_not_object"}}`; missing
  `master_plan.json` → `master_plan_unreadable`; missing a directive's
  `requirements.json` → `requirements_unreadable`. All tested.

## Edge cases
- Longest prefix on WHOLE segments: `tools/code_graph/query.py` →
  `tools/code_graph` (not `tools`); `toolsandmore/file.py` matches nothing
  (`no_matching_subsystem_rule`) — no substring false positives.
- Repo-root files (`CLAUDE.md`) are honestly unresolved, never bucketed.
- Symbols resolve only by exact node-id membership in a provided graph;
  without a graph the reason is `graph_not_provided` (null, never fabricated).

## Test + lint evidence (local, Python 3.11.9, ruff 0.13.0 = CI version)
- `python tools/test_subsystem_resolver.py` → 21 tests, OK.
- `python -m pytest tools/test_subsystem_resolver.py -q` → 21 passed.
- `ruff check tools/subsystem_resolver.py tools/subsystem_entities.py
  tools/test_subsystem_resolver.py` → All checks passed.
- `python tools/modularity_check.py --check` → 252 files; failures 0 (the 4
  warnings are pre-existing signals in unrelated files).
- New module sizes: `subsystem_resolver.py` ~250 SLOC,
  `subsystem_entities.py` ~230 SLOC, `test_subsystem_resolver.py` ~290 SLOC —
  all far below the 600-SLOC warn line.
