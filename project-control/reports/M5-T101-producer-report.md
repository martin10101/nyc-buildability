# M5-T101 producer report — D-087 PKT-C: building-footprint connector wiring-hardening (split first)

Producer: geospatial-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t101`, branch `task/M5-T101-footprint-wiring-hardening`,
based at claim seam `442b2dd2`. Directives: D-087-R001/R002/R003/R009, D-066-R001.

Files changed (all inside allowed_paths, one commit):
- `services/api/app/connectors/building_footprints_geometry.py` — NEW module (was the seeded placeholder): the extracted geometry helpers.
- `services/api/app/connectors/building_footprints_arcgis.py` — split (re-exports) + riders (a)(b)(c)(d)(f).
- `services/api/tests/connectors/test_building_footprints_arcgis.py` — 14 appended PKT-C tests (existing 117 unchanged).
- `docs/research/source-registry-drafts/building-footprints.json` — source_registry draft (was `[]`).
- `project-control/reports/M5-T101-producer-report.md` — this report.

No forbidden path touched: fixtures under `tests/fixtures/building_footprints/` are byte-frozen and untouched;
`app/resilience/` and `mappluto_geometry_arcgis.py` are read-only and untouched; no route / `main.py` / `apps/` /
`packages/` / requirements change; zero new dependencies (no `import re` — the AS-5 import allowlist forbids it, so
control-char stripping uses `str.translate`).

## Self-checks (verbatim tails)

- **[OBSERVED] cwd `services/api`: `python -m ruff check .`** → `All checks passed!`
- **[OBSERVED] cwd `services/api`: `python -m pytest tests/connectors/test_building_footprints_arcgis.py -q`**
  → `131 passed in 2.41s` (117 pre-existing + 14 new PKT-C).
- **[OBSERVED] cwd `services/api`: `python -m pytest tests/connectors/ -q --co`** → `1052 tests collected` (no
  import breakage in sibling connectors from the split/re-export).
- **[OBSERVED] cwd repo root: `python tools/modularity_check.py --check`** → `selected 490 files; failures 0;
  warnings 27`, `exit=0`. Connector `building_footprints_arcgis.py`: **865 SLOC / 47 symbols** (was 907 / 50) —
  below the 1000 hard cap; the two remaining warnings are report-only (symbol_ceiling 47>40, review_signal
  865>750). New `building_footprints_geometry.py`: **150 SLOC / 8 symbols** (below all thresholds).
  Symbol-ceiling justification: the connector is one cohesive responsibility (the OTI footprint fetch): an
  11-class fail-closed typed-error taxonomy + 4 result contracts + the request/parse/paging pipeline. The split
  already lowered it (50→47); the count is a signal, not a boundary violation.

## Split (step 1) — proven behaviour-preserving before the riders

Moved VERBATIM to `building_footprints_geometry.py`: `_ring`, `parse_footprint_geometry`,
`classify_query_relation` + the helpers they share (`_is_real`, `_finite`, `_safe_repr`, `_signed_area`,
`FootprintPart`, `COORD_ABS_MAX_FT`, `GEOMETRY_VALID/INVALID/REVIEW_REQUIRED`). The connector imports them back
(compatibility re-exports) so every name the tests import still resolves from the connector. The dependency is
one-way (connector → geometry); the geometry module imports NOTHING from the connector (acyclic) — pinned by
`test_pktc_geometry_split_is_reexported_and_acyclic` (asserts the re-exports are the same objects and greps the
geometry AST for any back-import). Proven on its own: after the geometry move (with the rider constants/classes
added but behaviour-affecting riders defaulting to no-op on existing inputs), the **117 pre-existing tests passed
unchanged** and the sha256-pinned fixture pack stayed byte-identical (no fixture file edited;
`test_fixture_pack_is_small_recorded_and_sha256_pinned` still green).

## Per-acceptance-scenario evidence

- **AS-1 (split, byte-identical):** see above. `test_pktc_geometry_split_is_reexported_and_acyclic`; 117 unchanged;
  fixtures untouched; modularity exit 0, connector 865 SLOC < 1000.
- **AS-2 (memory + time bounds):**
  - per-geometry vertex cap → typed `resource_exhausted` in `_parse_page` before retention
    (`test_pktc_geometry_vertex_cap_refuses_before_retention`).
  - cumulative decoded-bytes ceiling → typed `resource_exhausted` in `_collect_pages` before retention
    (`test_pktc_cumulative_bytes_ceiling_refuses_before_retention`).
  - optional caller wall-clock `deadline` checked before each page → typed `deadline_exceeded`; a future deadline
    does not refuse (`test_pktc_wall_clock_deadline_stops_paging_typed`).
  - `interactive=True` caps upstream attempts at `INTERACTIVE_MAX_ATTEMPTS` (fail fast) — declared in the
    `fetch_context_buildings` signature + docstring (`test_pktc_interactive_caps_max_attempts_fail_fast`).
- **AS-3 (log safety):**
  - **Declared choice:** a caller `correlation_id` is SANITIZED (CR/LF + C0/C1 control chars + DEL stripped via
    `_safe_correlation_id`) at entry — the single chokepoint feeding BOTH log sites (this connector AND the shared
    transport, which logs `io.cid`); a missing / non-string / emptied-after-strip id falls back to a
    server-generated `uuid4().hex`. (`test_pktc_safe_correlation_id_strips_control_and_falls_back`,
    `test_pktc_hostile_correlation_id_never_reaches_a_log_raw`.)
  - DB-066(a): the class-name log field strips CR/LF outright BEFORE the shared allowlist (whose `$` matches
    before a trailing newline) via `_CONTROL_CHAR_DELETE` in `_sanitized_bounded`
    (`test_pktc_trailing_newline_in_log_field_is_stripped_not_forged`,
    `test_pktc_class_name_trailing_newline_is_stripped_end_to_end`).
  - DB-066(c) probe: a BARE alphanumeric secret in an exception message never reaches the log (the branch logs a
    fixed message + class name only, never `str(exc)`); paired passthrough assertion shows the allowlist alone
    would NOT catch it, so message-omission is the guard (`test_pktc_short_alphanumeric_secret_in_message_never_logged`).
  - DB-066(d) probe: a TYPED refusal (upstream 500, disallowed_request) emits NO ERROR record
    (`test_pktc_typed_refusal_emits_no_error_record`).
- **AS-4 (datum + untrusted text, honest):** each record discloses BOTH ground-elevation definitions (City
  dictionary lowest-ground vs FGDC centroid-interpolated), keeps NAVD88 as published, reconciles NEITHER; a zero
  ground stays a real `0.0` flagged `ground_elevation_zero_unverified` (never None/default); the record declares
  `untrusted_text_fields = ("attributes", "geom_source", "last_status_type")` + a notice that consumers must
  escape on render (`test_pktc_datum_disclosure_and_untrusted_text_are_on_the_record`,
  `test_pktc_zero_ground_elevation_is_a_typed_unverified_value_not_a_default`). DB-058(f) was substantially
  implemented by M5-T089 (GROUND_DATUM_BASIS); PKT-C pins it with a test and adds the (a) untrusted-text
  declaration.
- **AS-5 (registry draft):** `docs/research/source-registry-drafts/building-footprints.json` mirrors the
  dcm/dtm draft shape (2 objects: ArcGIS primary + SODA secondary); primary `source_id ==
  "nyc-oti-building-footprints-arcgis"` (== connector SOURCE_ID); every field/unit/cadence statement cites the
  accepted research note `docs/research/building-footprints-source-2026-09.md` (M5-T087) or the live metadata;
  the height-unit inference (RQ-1) and the datum + definition conflict (RQ-2) are listed as open
  (`test_pktc_source_registry_draft_matches_connector_identity`).
- **AS-6 (scope):** zero new dependencies (`test_as5_module_imports_only_stdlib_shapely_and_app` still green,
  no `re`); connector unwired (`test_as5_connector_is_not_wired_to_any_route_or_module` green); no route /
  main.py / web / fixture change; exactly the 5 allowed paths.

## Mutation table (in-process, CONSUMING namespace `bf.*` mutated; each reddens its guard test)

Scratchpad harness `scratchpad/m5t101/mutations.py` (not committed). Every mutant was DETECTED.

| Guard | Mutation (bf.*) | Observed bad outcome (guard test reddens) |
|---|---|---|
| vertex cap | `MAX_GEOMETRY_VERTICES = 1e9` | fetch `status=ok` (no `resource_exhausted` refusal) |
| bytes ceiling | `MAX_TOTAL_DECODED_BYTES = 1e12` | fetch `status=ok` |
| wall-clock deadline | `_check_deadline` → no-op | past deadline no longer refuses (`status=ok`) |
| interactive fail-fast | `INTERACTIVE_MAX_ATTEMPTS = 3` | interactive path retries past the 500 (`status=ok`) |
| correlation-id sanitize | `_safe_correlation_id` → identity | raw `\n` reaches the log line (`newline_in_log=True`) |
| class-name control strip | `_CONTROL_CHAR_DELETE = {}` | `_sanitized_bounded("Foo\n") == "Foo\n"` (allowlist `$` passes it) |
| zero-ground typed value | `_ground_attr` → returns None | `ground_elevation_ft = None` (a zero would be nulled/defaulted) |

Structural probes (no in-process lever; the mutant is a code change, documented in the test docstrings):
DB-066(c) message-secret leak = logging `str(exc)`; DB-066(d) double-log = adding an ERROR log to the typed
refusal path. Both are pinned by positive probes (`secret not in line`; `_error_records == []`).

## Deviations

- Symbol ceiling stays a report-only WARNING (47 > 40) — justified above; the packet permits "cleared or
  justified". SLOC review_signal (865 > 750) is likewise report-only; the file is a single cohesive
  responsibility and now smaller than at claim.
- DB-058(f) needed only a pinning test + the (a) untrusted-text declaration — the datum disclosure itself already
  shipped in M5-T089 (GROUND_DATUM_BASIS). Recorded honestly, not re-implemented.

## DISCOVERIES (route to docs/DISCOVERY_BACKLOG.md at the seam; not fixed in-packet)

- **[OPEN] The not-wired test `test_as5_connector_is_not_wired_to_any_route_or_module` uses a crude substring
  grep for the literal `building_footprints_arcgis` across `app/**`.** A legitimate sibling helper module (the
  PKT-C geometry split) cannot even NAME the connector in a docstring/comment without tripping it (it tripped
  once during this task; worked around by not repeating the literal in the geometry module and leaving a comment
  explaining why). The wiring packets (PKT-E/PKT-H) that DO import the connector will make this test fail by
  design — the reviewer/orchestrator should replace the substring check with an import-graph / AST check that
  distinguishes "imported by an app module" from "the connector's own split helper", before wiring lands.

END-OF-REPORT
