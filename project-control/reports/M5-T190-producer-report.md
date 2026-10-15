# M5-T190 producer report (backend-engineer)

Task: the report's document fingerprint is stable for the same document (backlog DB-282).
Claim head: `8d7cf91b1f754562b7383d54897d80031546c22e` (`task/wave28-placement-wiring`).

## The change

Two files, both in allowed_paths. No value, label, or text on any report page changes;
only the fingerprint is now reproducible across runs of the same document.

1. `services/api/app/drawings/report/run_identity.py`
   - `_FINGERPRINT_EXCLUDE` extended from `("results_id", "computed_at")` to
     `("results_id", "computed_at", "option_id", "study_id")`. These are the only four
     top-level fields the live results route mints fresh each run; the read-only check
     proved no real zoning value differs between runs.
   - Three in-file prose enumerations corrected to list all four excluded fields and say
     why (per-run metadata, not values): the module docstring, the comment above the
     tuple (S5), and the `document_fingerprint` docstring. All three are in this one
     allowed file; correcting the function docstring too keeps the file's own prose
     accurate (it previously named only two fields).

2. `services/api/tests/drawings/report/test_report_run_identity.py`
   - Module docstring updated to name the four excluded fields.
   - Three new tests added (one per input state) plus the imports they need
     (`TestClient`, `INTERNAL_RESULTS_ENABLED_ENV_VAR`, and the shared benchmark helpers
     `NORTHERN_BBL`, `_no_network`, `app_with`, `benchmark_provider` from
     `tests.api.test_results_read_api`, the same cross-test import that
     `test_results_read_law_examples.py` already uses).

Forbidden/out-of-scope note: `page_evidence.py`'s `_run_identity` docstring does NOT
enumerate the excluded fields (it says only "stable for the same document, changing with
any value"), so RISK 2 does not materialize and no forbidden file needs touching. No file
outside allowed_paths was changed.

## Input-state table (acceptance scenarios)

| id | input state | test | expected | result |
|----|-------------|------|----------|--------|
| S1 | two docs differ only in results_id, computed_at, option_id, study_id | `test_t190_s1_fingerprint_stable_across_all_four_run_fields` | equal fingerprint | PASS |
| S2 | one real value differs (answers floor_area_allowance value) | `test_s7_fingerprint_changes_when_any_value_changes` (pre-existing, unchanged) | different fingerprint | PASS |
| S3 | a document without option_id or study_id (older/synthetic) | `test_t190_s3_document_without_option_or_study_id_behaves_as_before` | unchanged behaviour (dropping the two ids does not move the hash) | PASS |
| S4 | the live results route run twice (benchmark_provider(with_zoning_lot=True, street_on=True), INTERNAL_RESULTS_ENABLED+LANE_A_ENABLED, body standard_residence) | `test_t190_s4_live_route_two_runs_share_a_fingerprint` | the two run ids differ per run yet the fingerprints are equal | PASS |
| S5 | module docstring + comment above the tuple | read (prose) | list the four excluded run fields and say why | PASS (prose corrected) |

Baseline confirmation (before the fix, at the claim head, via the TestClient twice):
the route minted different option_id/study_id/results_id each run and the fingerprints
differed (`c25301212bec` vs `89076e8eb7e1`) — the DB-282 defect reproduced.

## Mutation (red-proof)

Reverted `_FINGERPRINT_EXCLUDE` to the two-field tuple `("results_id", "computed_at")`
and ran S1, S3, S4 plus the pre-existing stability test:

```
FFF.   -> 3 failed, 1 passed
FAILED test_t190_s1_fingerprint_stable_across_all_four_run_fields  (c813b01a2619 != 943f149d20a2)
FAILED test_t190_s3_document_without_option_or_study_id_behaves_as_before  (a43b9aa2c61a != c813b01a2619)
FAILED test_t190_s4_live_route_two_runs_share_a_fingerprint  (15941496e95f != b87a293cb897)
MUTATION_EXIT=1
```

S1, S3 and S4 go red (the new tests pin the fix); the pre-existing
`test_s7_fingerprint_stable_excluding_run_id_and_timestamp` stays green because it only
tweaks results_id/computed_at, which the old tuple already excluded — confirming the old
test could not catch the option_id/study_id drift. The four-field tuple was then restored.

## Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)

| check | command | exit | counts |
|-------|---------|------|--------|
| ruff | `cd services/api && python -m ruff check .` | 0 | All checks passed! |
| run-identity file | `pytest tests/drawings/report/test_report_run_identity.py` | 0 | 11 passed, 1 warning (4.30s) |
| drawings/report folder (flock heavy-run.lock) | `pytest tests/drawings/report` | 0 | 225 passed, 1 warning (69.12s) |
| modularity | `python tools/modularity_check.py --check` | 0 | 812 files; failures 0; 33 warnings (none for the two edited files) |
| lane paths | `python3 scripts/lanes/check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS: 10812 files, each owned by one lane |
| whole api suite (flock heavy-run.lock) | `pytest` (from services/api) | 0 | 10084 passed, 8 skipped, 1 warning (492.51s) |

The 1 warning everywhere is the pre-existing Starlette `httpx`/`httpx2` TestClient
deprecation, unrelated to this change.

## What I could not check

- No preview/server/PDF print was run (out of scope and forbidden here); the report page
  renders the fingerprint via `page_evidence._run_identity`, exercised by the green
  `tests/drawings/report` folder run, so the rendered page is covered by test.
- Windows behaviour not exercised (no Windows here); CI covers it.
