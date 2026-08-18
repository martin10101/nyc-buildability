# M0-T067 Unit D — closed schema, grounding, quarantine & promotion evidence (D-013)

## Closed schema fail-closed (R044/R013 / AS-1) — 8 tests
- Unknown field → `closed_schema_violation`; missing required → `missing_required_field`;
  agent outside the repo-derived allowlist → `agent_not_in_allowlist`; outcome outside
  the enum → `outcome_not_in_enum`; drifted id → `digest_id_mismatch`; oversize note →
  `note_too_long`. A fully valid digest validates.
- Allowlist derivation proven deterministic: fixture `.claude/agents` (2 files) →
  exactly `["code-reviewer", "orchestrator", "qa-engineer"]`.
- `digest_id` is content-derived (sha256 over the canonical doc without the id);
  `compute_digest_id` is the only mint.

## Derived parents + two-pass (R045/R046 / AS-2)
- Promotion derives task→milestone (`M0-T001`→`M0` via packet + master plan),
  requirement→directive (`D-900-R001`→`D-900` via registry), path→subsystem
  (`services/api/x.py`→`services/api` via the versioned Unit C map). The node stamps
  the ontology version (`resolver_version` 1.0.0 + map version/digest) and the
  task/directive index digests.
- Same digest + same repository state → byte-identical generation fingerprints on
  two independent stores (deterministic promotion; no wall clock anywhere).

## Grounding default-deny + quarantine (R047 / AS-3) — 5 tests
- `docs/OUTSIDE.md` EXISTS in the tree but is outside task scope/diff/evidence →
  `ungrounded_file_link`, never in `structural_links`.
- `D-900-R999` (nonexistent) → `unknown_requirement_id`; `D-901-R001` (EXISTS in the
  registry but its directive is not cited by the task packet) →
  `ungrounded_requirement_link`.
- A claimed file digest that no longer matches → `stale_file_link`.
- A stale ontology stamp quarantines the WHOLE digest (`stale_ontology_version`)
  with an external record under `<store>/digest-quarantine/`; the graph stays empty.
- `diff_files` grounding admits a file with basis `diff` (bases are recorded per link).

## Atomic / idempotent / replay-safe / concurrency-safe (R048 / AS-4, AS-6) — 5 tests
- Double promotion → `already_promoted`, identical generation, exactly 1 node.
- Injected crash (patched `os.replace`) before atomic promotion → prior state intact
  (fresh store still empty; no half-written current); replay completes to the
  byte-identical fingerprint of a clean run on a separate store.
- Same `digest_id` with a different grounding outcome → fail closed
  (`digest_id_conflict`), never silent overwrite.
- A held single-writer lock → `concurrent_writer` refusal, store unchanged; promotion
  succeeds after release. An in-repo store base → `cache_inside_repo` refusal.
- Store machinery is the ACCEPTED A2 `IndexCache` (temp + validate + atomic
  `os.replace`, recovery, quarantine) reused under the separate external
  `memory-graph` base — no new locking/atomicity code was invented.

## Advisory separation (R048/R045/R038 / AS-5)
- A digest carrying `"bad\x00tag"` PROMOTES; the tag lands in
  `discarded_advisory_tags` with `advisory_tag_control_chars`; valid tags stay in
  `advisory_tags`; no tag ever appears among `structural_links`.

## Edge cases
- Unknown task id quarantines the whole digest (`digest_task_unresolved`) BEFORE
  grounding (the packet is the grounding authority).
- CLI: `promote` exit 0 + status document; malformed digest file → exit 2 +
  machine-readable error; `show` reports nodes + generation fingerprint;
  a second digest extends the graph to 2 nodes.

## Test + lint evidence (local, Python 3.11.9, ruff 0.13.0 = CI version)
- `python tools/test_memory_graph.py` → 25 tests, OK.
- `python -m pytest tools/test_memory_graph.py -q` → 25 passed.
- `python tools/test_subsystem_resolver.py` (Unit C regression) → 21 tests, OK.
- `ruff check` on the four new files → All checks passed.
- `python tools/modularity_check.py --check` → selected 254 files; failures 0
  (4 pre-existing warnings in unrelated files).
- New module sizes (SLOC): memory_digest 157, memory_grounding 64,
  memory_graph 227, test_memory_graph 315 — all far below the 600 warn line.
