# M5-T141 producer report

Producer: backend-engineer (AI agent). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-acfb7622865bafaf0`, reset to the claim head
`5cc65d654bcfdac4c60b721cf82136013a0030ee`.

Task: the browser-test harness (`apps/web/e2e/harness/fixture_api.py`) must serve the results route
from the recorded files BY PATH and import nothing from the server's test tree, so it starts where
only the installed server package `app` is on the Python path (GitHub's `web-e2e` job). Only the
three allowed paths changed.

## Step 1 - the red proof (before any edit)

CI's start condition was reproduced with a scratch folder OUTSIDE the repository holding only a
symlink `app -> <worktree>/services/api/app`; from `apps/web`, `PYTHONPATH` set to that folder
ALONE and the lanes venv first on PATH:

```
import sys; sys.path.insert(0,'e2e/harness'); import fixture_api; fixture_api.build_app()
-> Traceback (most recent call last):
     File ".../apps/web/e2e/harness/fixture_api.py", line 732, in build_app
       results_inputs_provider = harness_results_inputs_provider()
     File ".../apps/web/e2e/harness/fixture_api.py", line 642, in harness_results_inputs_provider
       from tests.contracts.test_evaluator_inputs import _benchmark_identity_address
   ModuleNotFoundError: No module named 'tests'
RED_EXIT=1
```

That is CI's exact failure: the harness dies at start because its results provider imported two
helpers from `tests.*`, absent when the server is installed as a package.

## Step 2 - the repair (inside the one harness file only)

`harness_results_inputs_provider` no longer imports from `tests`. It reproduces the canonical
recorded-Northern replay the server's own tests use (`tests/spatial/_northern_replay.py` and the
results-route test's `benchmark_provider`), reading the recorded pack
`services/api/tests/fixtures/benchmark_215_16_northern/` BY PATH and serving its bytes to the REAL
connectors' own fetch/parse code:

- lot geometry: `app.connectors.mappluto_geometry_arcgis.fetch_lot_geometry` over a pack transport
  that serves each recorded file by URL (from `MANIFEST.json`), with the replay's fixed clock
  `datetime(2026,9,30,6,20,UTC)`, `rng=Random(0)`, `correlation_id="b03-benchmark"`.
- street page: `app.connectors.dcm_street_centerline_geometry.parse_segment_geometry_page` over a
  `DcmTransport` built from the recorded DCM envelope-page bytes + its manifest `url`/`retrieved_at`.
- PLUTO body: `app.connectors.pluto_soda.fetch_by_bbl` over the same pack transport, same fixed
  clock / `correlation_id="b03-benchmark"` / `observation_event_id="b03-benchmark"`.
- site geometry: `app.spatial.site_geometry.{lot_outline_from_mappluto, street_data_from_pages,
  derive_site_geometry}` and `outline.prepare_outline`, exactly as `benchmark_provider` composes
  them. The DCM query envelope is DERIVED from the lot geometry by the production helper
  `app.spatial.site_geometry.street_envelope_for_lot(lot)` (not retyped); it equals the test
  tree's `DCM_ENVELOPE` `(1048638.63, 216160.44, 1049061.58, 216581.1)` (verified).
- confirmed address: read from the benchmark-lot fixture
  `packages/contracts/fixtures/valid/benchmark_lot/northern_blvd_215_16_queens_4073340070.json`
  field `identity.address` (the same file+field `_benchmark_identity_address` reads).
- `assemble_study_inputs` builds the profile from the replayed PLUTO and threads the geometry,
  prepared outline and address, exactly as `benchmark_provider`.

No response byte is hand-written and no recorded value is retyped; imports are stdlib / installed
packages / `app.*` only. Everything else of the harness is unchanged (the other providers, the two
per-process switches the results block sets, the CORS settings, and the rule that any other lot is
the route's fail-safe 503). The repair fit inside the one harness file; no module was added.

## Step 3 - the new server test (`services/api/tests/api/test_e2e_harness_results_inputs.py`)

Loads the harness by adding its folder to the Python path (as
`test_address_resolution_recorded_geoclient.py` does). Three checks:

- (a) THE GUARD: no Python file under `apps/web/e2e/harness` has a line that starts, after leading
  spaces, with `from tests` or `import tests` (regex `^(from|import)\s+tests(\.|\s|$)`; `tests` must
  be the whole top-level module, so `tests_helper` never matches). Plus a temp-directory MUTATION
  PROOF: unmutated copies report nothing, a copy with one appended `from tests` line is reported at
  exactly that line.
- (b) EQUALITY: for the recorded lot (BBL 4073340070) the harness provider's `StudyInputs` equal
  `benchmark_provider()`'s, compared field by field. ONE field is excluded and named:
  `property_profile.profile_version.generated_at`, a wall clock `build_property_profile` stamps from
  `datetime.now(UTC)`; neither provider fixes the profile clock, so it is the ONLY non-deterministic
  field between two builds (verified by diffing two `benchmark_provider()` builds). Everything else -
  the confirmed address, the derived B-03 site geometry, the prepared tax-map outline and the whole
  rest of the property profile - stays in the comparison, so a genuinely different harness input
  still fails. The address is also read independently from the fixture (never retyped).
- (c) ANOTHER LOT: three other BBLs each raise `StudyInputsUnavailableError` with
  `reason="not_served"` (the route's fail-safe 503), never a fabricated document.

The guard's IN-PLACE mutation proof (check e): one real `from tests.spatial._northern_replay import
replay_pluto` line was added to the harness; the committed guard test went RED (exit 1, reporting
`fixture_api.py:720`); the line was reverted exactly and the guard went GREEN again (exit 0); no
`MUTATION PROBE` remains in the harness.

## Step 4 - the green proof

- Green start (CI-like, `PYTHONPATH` = the scratch folder alone): `build_app()` prints `STARTED`,
  exit 0.
- Ports 3000/3001/8000 before: NOTHING LISTENING. The two results browser specs in the CI-like way
  (`PATH=venv/bin:$PATH PYTHONPATH=<scratch> CI=true npx playwright test e2e/results.flag-on.spec.ts
  e2e/results.spec.ts`, after one `npm ci` and one `npm run build`):

```
✓ [chromium] e2e/results.spec.ts flag off: no Results opener ... zero results requests (1.9s)
✓ [chromium-flag-on] e2e/results.flag-on.spec.ts M5-T140 results panel — flag-on journey over the
  real results route (5.1s)
2 passed (17.5s)   PLAYWRIGHT_EXIT=0
```

The flag-on spec drives the REAL cross-origin POST to the results route on :8000 served by the
repaired harness. Ports 3000/3001/8000 after: NOTHING LISTENING (CI=true, so no reused servers were
left running).

## Checks (direct exit codes)

- a. `python -m ruff check .` (from services/api): exit 0 ("All checks passed!").
- b. `python -m pytest -q -p no:cacheprovider tests/api tests/journey` (from services/api):
  exit 0, 1139 passed (1133 at the claim base + 6 new).
- c. red proof: exit 1 (`No module named 'tests'`); green start: exit 0 (`STARTED`).
- d. the two results specs CI-like: exit 0, 2 passed; ports free before and after.
- e. guard mutation proof: guard RED with the injected line (exit 1), GREEN after exact revert
  (exit 0).
- f. `python3 tools/modularity_check.py --check`: exit 0 (only pre-existing warnings, none for the
  changed files). `python3 scripts/lanes/check_lane_paths.py --coverage`: exit 0 ("LANE COVERAGE
  PASS: 9579 file(s)").
- g. `git status --porcelain` + `git diff --name-status <base> HEAD`: only the three allowed paths.

## What is NOT changed

No file under `apps/web/src`; no browser spec; no Playwright configuration; no server application
file (`services/api/app/**`); no existing test or fixture; no CI file; no dependency file. Only the
one harness file, the one new server test file, and this report.
