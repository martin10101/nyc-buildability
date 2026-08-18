# M0-T068 producer report — Unit E: bounded repository-intelligence views

Producer: orchestrator (single writer, wt-m0t064, branch
`task/M0-T068-repo-views`). Stacked on accepted Unit D (M0-T067, merged to
main 40b530f).

## What was built (allowed_paths only)

1. **`tools/repo_views.py`** — the five bounded view builders over the
   accepted layers (all read-only): `census_view` (every eligible file
   accounted, per-reason exclusion/failure groups, bounded enumeration),
   `changed_view` (deterministic change classification vs the prior cache
   generation; unsupported stated bases refuse — never a guessed diff),
   `neighborhood_view` and `card_view` (bounded edges, ACTUAL graph kinds,
   subsystem ONLY via the versioned Unit C resolver), `deep_view` (exact
   bounded excerpt with line provenance + CRLF-normalized digest). Plus the
   ONE `coverage_record` builder (D-013-R024: identity, fingerprints, census
   groups, versions + ontology stamp, source-manifest/export digests, exact
   query params and limits) and the SEPARATE `cache_state_non_identity`
   section for cache hit/miss/rebuild fields.
2. **`tools/repo_views_query.py`** — typed deterministic question retrieval
   (`about_file`, `about_task`, `about_requirement`, `who_imports`,
   `what_changed`) with machine-readable no-answers, ADVISORY labeled
   memory-store reads (absent/empty labeled, never fabricated — R051), and
   the bounded CLI (`census/changed/card/neighborhood/deep/ask/check`).
   `check` is a two-run byte-identity self-proof of the deterministic
   sections (the cache-relative changed view documented-excluded).
3. **`tools/test_repo_views.py`** — 23 tests: AS-1..AS-6 packs plus
   truncation markers, no-answers, fail-closed paths, a REAL Unit D
   promotion surfacing in retrieval, and the cold-vs-warm determinism proof
   (deterministic sections identical while `cache_result` flips miss→hit).
4. **`docs/REPO_VIEWS.md`** — the views contract: modes, coverage-record
   fields, truncation semantics, advisory memory reads, fail-closed codes,
   compiler-consumption boundary.

## Key design decisions

- **One coverage-record builder** for all views (R024 anti-drift; packet
  risk note) — every field group asserted by AS-2 on all five views.
- **Cache-state separation**: R024 requires cache hit/miss counts, but they
  differ cold vs warm; they live in a labeled non-identity section so the
  deterministic sections stay byte-identical (proven by AS-6 with an actual
  miss→hit flip).
- **The changed view never guesses a base**: it reports against the prior
  cache generation or confirms no-change against the current snapshot; any
  other stated base refuses (`unsupported_base_fingerprint`).
- **Views feed the ONE compiler** (R039/R042): structured bounded data only;
  no prompt assembly, no budget, nothing included because space allows.
- **Reuse of the B1 hardening**: deep-view paths validate through Unit D's
  `is_canonical_repo_path` (traversal/absolute refuse before any read).

## G3 round-1 rework (review FAIL → fixed)

Round-1 review found two blocking defects, both fixed in round 2 entirely
within allowed_paths: (1) R024 "files removed" gap — `change_set` counts now
ride in the labeled cache-state section, asserted per view; (2) `about_task`
task-id path traversal — the id must match the exact `M<n>-T<n>` ledger
pattern before any filesystem access (`invalid_task_id`), regression-tested
with the reviewer's out-of-repo probe. Observations addressed: repo-relative
error details, `excerpt_out_of_range` refusal, complete fail-closed code list
in the doc. Round-1 report: `M0-T068-review-FAIL-round1.md`.

## Self-check results (documented_test_commands, round 2)

- `python tools/test_repo_views.py` → **26 tests OK**.
- `python -m pytest tools/test_repo_views.py -q` → **26 passed**.
- `python tools/modularity_check.py --check` → **failures 0** (259 files).
- `ruff check` (0.13.0, CI-matching) on the three new files → clean.
- Regressions: Unit C 21/21 OK, Unit D 31/31 OK.

## Scope compliance

- Diff touches ONLY allowed_paths (new files + the packet's own reports).
- All consumed accepted modules (index, graph, ontology, memory store,
  context-pack io) are forbidden_paths and untouched (R082 included).
- No benchmarks, runbook, or status projection (Unit F boundary).

Evidence details: `M0-T068-coverage-evidence.md`; per-requirement map:
`M0-T068-evidence-map.json`.
