# M0-T068 Unit E — coverage modes, records, truncation & determinism evidence (D-013)

## Coverage modes (R023 / AS-1) — 4 tests
- `census`: 3-eligible fixture fully accounted (`eligible == indexed == 3`,
  `reconciles` true), bounded file enumeration with marker.
- `changed`: reports the deterministic classification vs the prior cache
  generation; a stated fingerprint equal to the current snapshot yields
  `no_change_by_identity` with empty lists; any OTHER stated base refuses
  (`unsupported_base_fingerprint`) — never a guessed diff.
- `neighborhood`: bounded, seed-resolved (`user.py → thing.py [import]`).
- `deep`: exact excerpt `["line two", "line three"]` at lines 2-3, whole-file
  CRLF-normalized sha256 independently recomputed in the test.

## Coverage records (R024 / AS-2) — every view, every field group
- One builder (`coverage_record`) used by all five views; AS-2 asserts 16
  deterministic keys on each (identity, fingerprints, dirty digest, census
  groups, versions + `versions.ontology.map_digest`, generator identity,
  export digest, graph counts, `views_version`, exact `query_params`,
  `limits`), plus the separate runtime section labeled
  `cache_state_non_identity` carrying cache hit/miss.

## Truncation never silent (R003/R039/R042 / AS-3) — 3 tests
- neighborhood `edge_limit=1` on a 2-importer node → `omitted: 1`,
  `truncated: true`; census `file_limit=1` → `omitted: 2`; deep `max_lines=1`
  over a 3-line request → `omitted: 2`. Marker shape
  `{limit, returned, omitted, truncated}` recorded in content; limits echoed
  in the coverage record.

## Honesty (R009/R018/R045/R051 / AS-4) — 7 tests
- Unknown seed → `seed_not_in_graph`; unknown requirement →
  `unknown_requirement_id` (machine-readable no-answers, never guesses).
- Card reports the ACTUAL graph kind (`py_module`) and subsystem ONLY via the
  versioned Unit C resolver (`services/api`).
- Memory reads advisory + labeled: empty store → `store_empty` with `[]`;
  after a REAL Unit D promotion (full pipeline in-test) the digest surfaces
  for both `about_file` and task filtering with outcome/agent.
- `who_imports` returns exactly the two real importers.

## Fail closed (R013 / AS-5) — 4 tests
- Non-git dir → `index_unavailable`; traversal deep path →
  `non_canonical_path`; missing file → `path_not_in_tree`; unknown task →
  `task_packet_unreadable`; CLI exit 2 with a machine-readable error doc.

## Determinism (AS-6) — 3 tests
- Cold vs warm: deterministic sections (content + coverage) of
  census/card/neighborhood/deep byte-identical across a cold full build and a
  warm cache reuse, while `runtime.cache_result` observably differs
  (`miss` → `hit`) — proving the non-identity separation is real.
- The changed view is cache-relative BY DESIGN (disclosed via its `base`
  label): warm no-change → empty; after a real edit → exactly
  `content_modified == ["services/api/thing.py"]`.
- CLI `check` self-proof passes (two-run byte-compare; changed view
  documented-excluded).

## G3 round-1 rework (two blocking findings) — round 2
The round-1 independent review (M0-T068-review-FAIL-round1.md) found:
- **Finding 1 (R024)**: "files removed" carried in NEITHER coverage section.
  Fixed: `change_set` counts (incl. `deleted` = removed, renamed, modified,
  invalidators) now ride in the labeled `cache_state_non_identity` section
  (cache-relative, so that is the correct section); AS-2 asserts
  `change_set.deleted` presence on every view.
- **Finding 2 (R013, security)**: `about_task` accepted a traversal task id
  and read a JSON file OUTSIDE the repository with exit 0. Fixed: the id must
  match the exact `M<n>-T<n>` ledger pattern BEFORE any filesystem access
  (`invalid_task_id`); regression test reproduces the reviewer's probe with a
  real out-of-repo file and asserts nothing is read or leaked (module + CLI).
- Observations addressed: `task_packet_unreadable` detail is now
  repo-relative (no absolute paths in error documents); out-of-range deep
  requests refuse (`excerpt_out_of_range`); the doc's fail-closed list now
  names every emitted code.

## Test + lint evidence (round 2; local, Python 3.11.9, ruff 0.13.0 = CI version)
- `python tools/test_repo_views.py` → 26 tests, OK (23 round-1 + 3 new
  regression tests).
- `python -m pytest tools/test_repo_views.py -q` → 26 passed.
- Unit C regression `python tools/test_subsystem_resolver.py` → 21 OK;
  Unit D regression `python tools/test_memory_graph.py` → 31 OK.
- `ruff check` on the three new files → All checks passed.
- `python tools/modularity_check.py --check` → selected 259 files; failures 0
  (4 pre-existing warnings in unrelated files).
- New module sizes (SLOC-class): repo_views ~300, repo_views_query ~250,
  test_repo_views ~330 — all far below the 600 warn line.
