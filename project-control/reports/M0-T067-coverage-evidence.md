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

## G3 round-1 rework (B1 path traversal + O1/O3/O4) — round 2
The round-1 independent review (M0-T067-review-FAIL-round1.md) demonstrated
B1: a `..`-embedded `files[].path` (`services/api/../../../secret.txt`)
resolved, grounded via a SUBSTRING match on digest-controlled evidence_refs,
and entered structural_links pointing outside the repository. Fixes (confined
to memory_digest / memory_grounding / memory_graph message + tests + doc):
- **Schema canonicality (R044)**: `is_canonical_repo_path` — `files[].path`
  must be canonical repo-relative POSIX (no `..`/`.` segments, no
  absolute/drive paths, no backslashes, no doubled slashes) else
  `file_path_not_canonical`. Regression tests cover all 8 shapes including
  the reviewer's exact probe reproduced end-to-end (a REAL file outside the
  repo root): promotion now refuses at validation and the store stays empty.
- **Exact-match evidence grounding (O1/B1)**: `p in ref` substring matching
  removed; an evidence ref grounds only on exact normalized equality (tested:
  a mere mention no longer grounds; the exact ref still does).
- **Grounding defense-in-depth**: non-canonical paths refuse in
  `ground_file_link` itself (`non_canonical_path`) even if a caller bypasses
  the schema.
- **O4**: advisory-tag control-char check now rejects all Unicode category-C
  characters (DEL `\x7f`, format chars like `​`) — tested.
- **O3**: `digest_id_conflict` message now says "digest content or promotion
  context changed".

## Test + lint evidence (round 2; local, Python 3.11.9, ruff 0.13.0 = CI version)
- `python tools/test_memory_graph.py` → 31 tests, OK (25 round-1 + 6
  B1/O1/O4 regression tests).
- `python -m pytest tools/test_memory_graph.py -q` → 31 passed.
- `python tools/test_subsystem_resolver.py` (Unit C regression) → 21 tests, OK.
- `ruff check` on the four new files → All checks passed.
- `python tools/modularity_check.py --check` → failures 0
  (4 pre-existing warnings in unrelated files).
- New module sizes (SLOC): memory_digest ~170, memory_grounding ~70,
  memory_graph ~230, test_memory_graph ~380 — all far below the 600 warn line.
