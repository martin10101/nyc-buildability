# M5-T100 producer report — D-087 3D-2b: building-footprint connector riders (DB-058 e, h, l, m)

Producer: geospatial-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t100`, branch `task/M5-T100-footprint-riders`,
based at the claim-seam commit `2957e40d`.

Scope: exactly the three allowed paths.
- `services/api/app/connectors/building_footprints_arcgis.py` — DB-058(e) only (findable,
  non-leaky internal-error log). Every other behaviour and every recorded fixture is byte-identical.
- `services/api/tests/connectors/test_building_footprints_arcgis.py` — added tests only for
  DB-058 (e), (h), (l), (m). No existing test changed.
- `project-control/reports/M5-T100-producer-report.md` — this report.

No forbidden path touched: no fixture (`tests/fixtures/building_footprints/`), no
`app/resilience/`, no `mappluto_geometry_arcgis.py`, no route/main/requirements. `git status`
shows only the two code files modified (report added by the commit).

## Design decision for DB-058(e) — findable but non-leaky (records the G5-safe choice)

The catch-all `except Exception` now logs, at ERROR level, ONLY for the UNEXPECTED-exception
(genuine-bug) branch — a typed `BuildingFootprintConnectorError` reaching the catch-all is not
re-logged (it is already a typed, returned refusal; the transport already logs its retries at
warning level). The log line carries three fields:
`class=%s message=%s correlation_id=%s` with args
`_sanitized_bounded(type(exc).__name__)`, `_sanitized_bounded(_INTERNAL_ERROR_LOG_MESSAGE)`, `cid`.

Key safety property (objective: "prove no upstream body text can reach the log"):
`str(exc)` is NEVER rendered. The exception's *message* is the one place upstream body text can
travel into a genuine bug (e.g. `ValueError: invalid literal for int(): '<upstream text>'`, or a
short alphanumeric secret — verified that `sanitize_retry_after('AdminSecret123')` returns it
verbatim, so sanitizing `str(exc)` would NOT stop a leak). Therefore only the exception CLASS
name (a Python identifier for any real exception) and a FIXED connector constant are logged, and
both are passed through the shared transport sanitizer
(`app.resilience.transport.sanitize_retry_after`, read-only import) and length-bounded to 200 as
defense in depth. The RETURNED refusal is byte-identical to before: `error_type="internal_error"`,
`message="unexpected internal failure; no data is returned"`, `detail={"exception": <class name>}`
— the class-name-only refusal the M5-T089 G5 review named the safe choice, unchanged.

`app/resilience/transport.py` exposes exactly one sanitizer in `__all__`
(`sanitize_retry_after`); that is the "shared transport's sanitizer" reused here. It is an
allowlist passthrough (`^[A-Za-z0-9,: +\-]{1,64}$`) else `repr()`, which escapes control
characters so a newline in a hostile value cannot forge a second log line.

## Per-AS evidence

- AS-1 (findable, not leaky). `test_t100_internal_error_is_findable_and_logs_no_upstream_text`
  injects `RuntimeError('UPSTREAM_BODY {"secret":"AdminSecret123"}\nFORGED: fake second log
  line')` via a broken transport (raises on the metadata call). Asserts: refusal is
  `internal_error` with `detail == {"exception": "RuntimeError"}` (unchanged); exactly one ERROR
  record from the connector logger; the line contains `class=RuntimeError`, the sanitized fixed
  message, and `correlation_id=t-cid`; and the line contains none of `AdminSecret123`,
  `UPSTREAM_BODY`, `FORGED`, or a raw `\n`.
  `test_t100_internal_error_log_sanitizes_and_bounds_a_hostile_class_name` injects an exception
  whose class `__name__` is `"Bad\nFORGED " + "Z"*400`; asserts the logged line has no raw `\n`
  (sanitizer escaped it) and carries `...(truncated)` (length-bounded), never the full name.
  `test_t100_sanitized_bounded_neutralizes_control_chars_and_bounds_length` unit-tests the helper:
  allowlist passthrough (`"RuntimeError" -> "RuntimeError"`), control-char escape (no raw `\n`),
  and length bound (`"Z"*500` truncated with the marker).

- AS-2 (missing geometry end to end).
  `test_t100_missing_geometry_key_is_typed_null_geometry_end_to_end` builds a SYNTHETIC page from
  the recorded page-1 body with `del features[1]["geometry"]`, runs it through
  `fetch_context_buildings`, and asserts `status == "ok"`, all 3 records returned, and the subject
  record is `geometry_status == "invalid"`, `geometry_findings == ["null_geometry"]`, `parts == []`,
  `footprint_area_sq_ft is None`, `query_relation is None`, `original_geometry is None` — the record
  is never dropped and never an untyped error. (The M5-T089 suite proved `null_geometry` only as a
  direct `parse_footprint_geometry(None)` unit case; this is the end-to-end proof G3-A4 asked for.)

- AS-3 (CRS halves). `test_t100_crs_page_gate_requires_both_wkid_and_latest_wkid` (parametrized ×2)
  builds SYNTHETIC pages with `spatialReference` `{"wkid":102718,"latestWkid":9999}` and
  `{"wkid":3857,"latestWkid":2263}`; each is refused `wrong_crs` with `request_url == P1_URL`. This
  pins the two-part gate (wkid AND latestWkid), which the only recorded wrong-CRS fixture
  (both-wrong web-mercator) could not.

- AS-4 (zero year). `test_t100_zero_construction_year_nulls_the_value_not_only_the_gap` drives a
  SYNTHETIC `CONSTRUCTION_YEAR = 0` through `fetch_context_buildings` and asserts BOTH
  `construction_year is None` (the displaced value) AND the `("CONSTRUCTION_YEAR",
  "zero_not_available")` gap. (The M5-T089 suite asserted only the gap.)

- AS-5 (no drift + scope). All 110 pre-existing tests pass unchanged (117 total = 110 + 7 new).
  Recorded fixtures untouched (the fixture-integrity test `test_fixture_pack_is_...sha256_pinned`
  still passes). Zero new dependencies: the only new import is `sanitize_retry_after` from the
  already-imported `app.resilience.transport` (root `app`), so
  `test_as5_module_imports_only_stdlib_shapely_and_app` still passes; connector stays unwired
  (`test_as5_connector_is_not_wired_to_any_route_or_module` passes). No network in any test.

## Commands (verbatim results)

1. `cd services/api && python -m ruff check .`
   -> `All checks passed!`
2. `cd services/api && python -m pytest tests/connectors/test_building_footprints_arcgis.py -q`
   -> `117 passed in 1.41s` (110 existing unchanged + 7 added test items)
3. `python tools/modularity_check.py --check` (worktree root)
   -> `selected 488 files; failures 0; warnings 26`. The connector is a warning
   (`review_signal` + `symbol_ceiling`), never a CI failure.
   `--report --json` for the connector: `sloc 907`, `symbols 50` (was 891 SLOC / 49 symbols;
   +16 SLOC, +1 symbol). Well under the 1000 hard limit.

Local Python is 3.11 (`AppData\Local\Programs\Python\Python311`); CI is 3.12. Nothing here is
Python-version-sensitive (stdlib logging, a str allowlist/`repr`, a slice). No command was
[BLOCKED]; all three documented commands ran from the stated cwd.

Modularity cohesion justification (recorded per the review signal): the module keeps ONE
read-only responsibility — turn the official OTI BUILDING layer into typed `ContextBuilding`
records. The +16 SLOC is a single 4-line log-safety helper (`_sanitized_bounded`) plus two
constants, placed next to the existing `_safe_repr`, and a 9-line if/else expansion of the
existing catch-all to insert one error log. No new domain concern was added. The peer connector
`dcm_street_centerline_arcgis.py` is 902 SLOC and carries the same warning. The natural future
extraction if it grows (unchanged from the M5-T089 G3 note) is
`_ring`/`parse_footprint_geometry`/`classify_query_relation` behind a facade. No split is
warranted before wiring.

## Mutation table (RED = the target test fails = guard proven; in-process mutant, source never edited on disk)

Harness: read the real connector source, apply ONE in-memory text replacement, register the
mutated module under `app.connectors.building_footprints_arcgis` in `sys.modules` before pytest
collects the test file (so the test's by-value imports bind to the mutant), run the target test
in an isolated subprocess. Baseline (no mutation) = 117 passed.

| # | Mutation | AS / rider | Target test | Result |
|---|---|---|---|---|
| MU-A1a | log `str(exc)` instead of the sanitized fixed message | AS-1 / (e) — "logging the raw message reddens" | `..._is_findable_and_logs_no_upstream_text` | RED |
| MU-A1b | drop `_sanitized_bounded(...)` on the class name (log it raw) | AS-1 / (e) | `..._log_sanitizes_and_bounds_a_hostile_class_name` | RED |
| MU-A1c | `logger.error` -> `logger.debug` (defeat findability) | AS-1 / (e) | `..._is_findable_and_logs_no_upstream_text` | RED |
| MU-H | remove the `if esri is None:` null_geometry guard | AS-2 / (h) | `..._missing_geometry_key_is_typed_null_geometry_end_to_end` | RED |
| MY1a | CRS gate checks only `latestWkid` (drop the wkid half) | AS-3 / (l) — G4 survivor | `..._crs_page_gate...[spatial_reference1]` ({wkid:3857,latestWkid:2263}) | RED |
| MY1b | CRS gate checks only `wkid` (drop the latestWkid half) | AS-3 / (l) — G4 survivor | `..._crs_page_gate...[spatial_reference0]` ({wkid:102718,latestWkid:9999}) | RED |
| MY7 | drop `year = None` (keep the zero as a false "year 0") | AS-4 / (m) — G4 survivor | `..._zero_construction_year_nulls_the_value_not_only_the_gap` | RED |

The three G4 survivors (MY1a, MY1b, MY7) are now killed, and the DB-058(e) log is guarded by
three mutations (raw-message leak, dropped sanitizer/bound, dropped/downgraded log). MU-A1b uses a
crafted class name that is both control-char-bearing and over-long, so removing `_sanitized_bounded`
reddens both the no-raw-newline (sanitize) and the `...(truncated)` (bound) assertions.

## Deviations

- The internal-error log deliberately does NOT use `logger.exception(...)` (the literal G3-A1
  suggestion), because that renders the full traceback and message and would leak upstream text
  and stack paths. The packet's own wording (class + sanitized bounded message + cid, prove no
  upstream text) supersedes the raw suggestion; the M5-T089 G5 "class-name-only refusal is the
  safe choice" is preserved. Documented, not silent.
- The shared transport sanitizer is applied to the exception CLASS name and to the fixed constant;
  it is NOT applied to `str(exc)` because `str(exc)` is never logged (an allowlist-safe short secret
  would pass through the sanitizer verbatim). This is the load-bearing reason `str(exc)` is
  excluded rather than sanitized.

## DISCOVERIES (route to the orchestrator; not fixed in-packet)

- None new. DB-058 riders (a)-(d), (f), (g), (i)-(k) remain OPEN for the later footprint
  wiring / 3D-context packet exactly as recorded; this packet closes only (e), (h), (l), (m).
  Forward note carried from M5-T089 G5-A4 / DB-058(d): when the connector is wired, the caller
  must pass a server-generated `correlation_id` (or strip control characters) — this packet logs
  `cid` as given (consistent with the shared transport), and a hostile cid remains a wiring-layer
  concern, not addressed here.

END-OF-REPORT
