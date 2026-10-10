# M5-T154 producer report — the map data around the lot for the report

Producer: geospatial-engineer (an AI agent). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a82f93f94e70f0a81`.
Contract head reset to `f68c60267c983c756f314c2b03628279a1bfc63a` (confirmed, clean tree).
Directive: D-090 (R843, R936, R937); rulings Y2, Y4, Y5, Y7, Y11, Y12, Y13 followed.

## What was built (allowed paths only)

- **`services/api/app/connectors/mappluto_window_arcgis.py`** (new) — a sibling of the per-BBL
  MapPLUTO geometry connector (imported read-only, never changed). `fetch_window_lots(envelope,
  subject_bbl, ...)` returns every tax lot whose outline intersects an EPSG:2263 envelope, the
  subject lot carried separately on `result.subject` and EXCLUDED from `result.lots`, each
  neighbour once. Out-fields are `OBJECTID,BBL,Block,Lot,Address,Version` ONLY — never OwnerName
  or any personal field. Geometry is kept verbatim (no quantize/repair/re-orient). A wrong CRS,
  an ArcGIS error object, a paging fault or a malformed ring each RAISE a typed
  `MapPlutoWindowConnectorError` (no partial result). Field names/URL/CRS taken from the parent
  connector's constants and the live layer metadata (confirmed: Address=esriFieldTypeString,
  Version=esriFieldTypeString, BBL=esriFieldTypeDouble, maxRecordCount=2000, extent SR 102718/2263).

- **`services/api/app/contracts/map_context.py`** (extended) — `build_report_map_context(...)` builds
  the 1.1.0 document: `subject_lot` (the measurement-grade MapPLUTO outline, Y5), `zoning_districts`
  always `not_available` (the report context does not fetch zoning), `building_footprints` (reusing
  the accepted buildings layer), and the new `context_window`, `tax_lots` and `streets` members
  (ruling Y2). `parse_mapped_width_ft(text)` returns a number ONLY for one plain non-negative number
  ("60"->60, "100"->100); "60-75", "<=75", "", None -> null (D-052). Attributions placed verbatim;
  the source edit date rides on each layer's provenance (Y7). Geometry verbatim.

- **`packages/contracts/schemas/v1/map_context.schema.json`** + the bundled copy
  **`services/api/app/_contract_schemas/v1/map_context.schema.json`** (synced byte-identical) —
  additive 1.1.0: enum `["1.0.0","1.1.0"]`; three OPTIONAL members `context_window` (window_box),
  `tax_lots` (available/not_available), `streets` (available/not_available) with `$defs`
  window_box / tax_lots_available / tax_lot_entry / streets_available / street_entry / line. Only
  KNOWN_KEYWORDS used (`type` arrays for the number-or-null / string-or-null fields). Every 1.0.0
  document stays valid (existing fixtures pass).

- **`packages/contracts/fixtures/valid/map_context/synthetic_window_1_1_0.json`** (new valid) and
  **`.../invalid/map_context/street_mapped_width_not_a_number.json`** (new invalid: a streets entry
  whose `mapped_width_ft` is the string `"60"` instead of number-or-null).

- **`services/api/app/api/v1/report_context.py`** (new) — the provider `(bbl, correlation_id) ->
  1.1.0 document | None` and the FastAPI dependency `get_report_map_context_provider`. Live binding
  gated by `LIVE_SPATIAL_PROVIDER_ENABLED` (flag off -> None, zero connector calls). Never raises:
  a connector refusal makes THAT layer `not_available`; no subject outline gives None. Assembly
  takes injectable fetch functions (`ReportMapFetchers`). Windows from the subject lot's own bbox
  (0.01-ft precision): tax lots + footprints = bbox + 400 ft; streets = bbox + 1,000 ft.

- **`services/api/tests/fixtures/benchmark_215_16_northern_window/`** (new pack) — MANIFEST.json,
  README.md, `.gitattributes` (`* -text`) and the three recordings (see below).

- **`services/api/tests/spatial/_northern_window_replay.py`** (new) — offline replay helper (window
  pack + base pack fallback).

- Three test files (S1–S8 + two mutation proofs): `tests/connectors/test_mappluto_window_arcgis.py`,
  `tests/contracts/test_map_context_window.py`, `tests/api/test_report_context_provider.py`.

## Harness entry point (ruling Y4)

`app.api.v1.report_context.recorded_pack_provider(pack_dir, *, base_pack_dir=None, notes=None)
-> MapContextProvider` where `MapContextProvider = Callable[[str, str], dict | None]` i.e.
`(bbl, correlation_id) -> 1.1.0 document | None`. It binds the provider to a recorded window pack
folder, serving the recorded bytes through the real connectors' own fetch/parse code (no network),
usable with only the `app` package importable. The subject lot's per-BBL geometry and the layers'
service metadata come from the base pack the window pack extends
(`../benchmark_215_16_northern`, resolved on the filesystem). Verified: it returns a document
byte-equal to the direct build (S8).

## Recording (ruling Y11) — one-time keyless GET via the connectors; no key/account/email

Subject lot BBL 4073340070; windows from its EPSG:2263 bbox (1048788.63, 216310.44, 1048911.58,
216431.10). The three window data recordings in the new pack (the subject per-BBL geometry and each
layer's metadata are the base pack's already-recorded, byte-identical responses — verified at
capture, so this pack stores only the three window recordings and "no other network call" holds):

| File | URL (short) | bytes | sha256 (first 12) |
|---|---|---|---|
| mappluto_window_lots_4073340070_plus400ft.json | services5…/MAPPLUTO/FeatureServer/0/query?…geometry=1048388.63,215910.44,1049311.58,216831.10…outFields=OBJECTID,BBL,Block,Lot,Address,Version | 74668 | df19e5429806 |
| building_footprints_window_4073340070_plus400ft.json | services6…/BUILDING_view/FeatureServer/0/query?…geometry=1048388.63,215910.44,1049311.58,216831.10… | 158077 | cb153371ba78 |
| dcm_street_centerline_window_4073340070_plus1000ft.json | services5…/DCM_Street_Center_Line/FeatureServer/0/query?…geometry=1047788.63,215310.44,1049911.58,217431.10… | 34631 | 5c01484c55bf |

## Benchmark counts (verified by replay)

- Neighbouring tax lots: **200** (201 features in the window; the subject BBL 4073340070 excluded).
- Building footprints: **263** (one page).
- Street segments: **35** usable-geometry entries. Named streets with mapped widths include
  Northern Boulevard **100**, 215 Place **60**, 215 Street **60** (S7). Bell Boulevard carries a
  non-numeric "80-100" and ">90" -> mapped_width_ft null (width_text kept).
- S7 independent check: lot 1 (BBL 4073340001) shares a **99.9765 ft** boundary with the subject
  (within 0.01 ft of 99.98 ft).

## Checks (all via `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`)

- `services/api$ python -m ruff check .` — **exit 0** (All checks passed).
- `services/api$ python -m pytest -q -p no:cacheprovider tests/connectors/test_mappluto_window_arcgis.py
  tests/contracts/test_map_context_window.py tests/api/test_report_context_provider.py` — **20 passed, exit 0**.
- `services/api$ python -m pytest -q -p no:cacheprovider tests/connectors tests/contracts tests/api
  tests/spatial tests/drawings/maps` — **2 failed, 3543 passed, 4 skipped** (exit 1). The 2 failures
  are OUT-OF-SCOPE consumer assertions in `tests/contracts/test_map_context_contract.py` (NOT an
  allowed path) — see "Out-of-scope consumer update required" below.
- `python3 services/api/scripts/sync_contract_schemas.py --check` — **exit 0** (byte-identical).
- `python .github/scripts/validate_contracts.py` — **exit 0** (23 schemas, 0 failures; the new
  valid/invalid map_context fixtures pass/reject correctly).
- `python -m pytest -q .github/scripts/tests` — **24 passed, exit 0**.
- `python3 tools/modularity_check.py --check` — **exit 0** (0 failures; none of the new/grown files
  flagged; map_context.py 577 lines, mappluto_window_arcgis.py 718 lines, report_context.py 374 —
  all under the warn/justify thresholds by SLOC).
- `python3 scripts/lanes/check_lane_paths.py --coverage` — **exit 0** (LANE COVERAGE PASS, 9928
  files, each owned by exactly one lane).

## Mutation proofs (scratch copy outside the repository)

Ran in `/tmp/.../scratchpad/mutcopy` (a copy of services/api + packages/contracts):

1. **Owner-name field added to the request** (`OUT_FIELDS += "OwnerName"`): CAUGHT by
   `tests/connectors/test_mappluto_window_arcgis.py::test_request_never_asks_for_an_owner_name`
   (the out-field set and the byte-exact URL assertion fail).
2. **"60-75" parsed as 60** (parser switched from `fullmatch` to first-number `search`): CAUGHT by
   `tests/contracts/test_map_context_window.py::test_mapped_width_parser_only_parses_a_plain_number`.

Both named tests pass on the unmutated sources (part of the 20 green) and fail on the mutated copy.

## Out-of-scope consumer update required (STOP-and-report per the brief / Y12)

Extending the contract to 1.1.0 and adding the two required fixtures necessarily invalidates two
assertions in **`services/api/tests/contracts/test_map_context_contract.py`**, which is NOT in this
task's allowed paths. I did not edit it. The two exact edits the orchestrator must apply (or add the
file to scope):

1. `test_fixtures_present`: `assert len(VALID) == 4` -> `== 5`; and the INVALID name set must add
   `"street_mapped_width_not_a_number.json"`.
2. `test_document_kind_and_version_are_pinned`: `assert props["contract_version"]["enum"] ==
   ["1.0.0"]` -> `== ["1.0.0", "1.1.0"]`.

Every other assertion in that file still passes (the globbed valid/invalid fixture tests already
cover the new fixtures correctly, verified). No other out-of-scope file must change.

**Scope correction 1 (orchestrator, packet at 3ef5b09b4):** `test_map_context_contract.py` was
added to this task's allowed paths; the two named assertions above are now applied in this
worktree (valid count 4->5 + the new invalid name; version enum `["1.0.0","1.1.0"]`), nothing else
in that file changed, as a second commit on top of 962a21a2.

## Assumptions / limitations

- The subject outline from the window query is byte-identical (0.00 ft) to the base pack's per-BBL
  MapPLUTO outline, so sizing the windows from a per-BBL fetch and drawing that outline is faithful.
- The building-footprints layer metadata moved its edit date since the base pack (2026-09-27 ->
  2026-10-04); the queried field schema is IDENTICAL, so the base-pack metadata stays a faithful
  replay (the footprints layer's provenance edit date is the base pack's recorded value). Documented
  in the pack README.
- A tax lot or street with a malformed ring/path makes the WHOLE tax_lots/streets layer refuse
  (the connector raises; the provider demotes that one layer to not_available) — the rest of the
  map still draws. The benchmark window has none.
- No server was started; ports 3000/3001/8000 untouched (Y12). Nothing is labelled Verified (Y13).


---

RETURN AFTER SCOPE CORRECTION 1 (saved unchanged by the orchestrator):

Done, as an AI agent, in the same worktree on top of 962a21a2.

New commit: `c8361c760f878f1f6df41b536ca54d48e6a30eda` — parent `962a21a27afd28787e9914cb32c3b94aa7b9607e`. Tree clean.

Changes: `services/api/tests/contracts/test_map_context_contract.py` only — the two named consumer assertions (valid count 4→5 and the INVALID set gains `street_mapped_width_not_a_number.json`; version enum `["1.0.0","1.1.0"]`), docstring counts kept consistent, nothing else. Diff: +6 / −4 (10 lines) in that file; +5 lines in the producer report.

Suite (lanes venv, direct exit): `ruff check .` passed; `pytest tests/connectors tests/contracts tests/api tests/spatial tests/drawings/maps` → 3545 passed, 4 skipped, EXIT 0.

END-OF-REPORT


---

CORRECTIONS RETURN, after the review wave (saved unchanged by the orchestrator):

M5-T154 corrections done (AI agent), one commit on 9b72bb4c.

Commit: `b7c077a48c9cb22e2f574bbf9772ecba19755afc` — parent `9b72bb4c46cd73f9fdb242cd651b05a28b180b76`. Tree clean.

FIXES: (1) switch-off test now uses counting spies and asserts zero calls on every fetcher; (2) window-pack integrity tests added to tests/connectors/test_mappluto_window_arcgis.py (SHA-256 per recording, MANIFEST == on-disk, README + `* -text` .gitattributes present) — no new file, no STOP needed; (3) `_pack_url_map` refuses any MANIFEST entry escaping its pack folder (`_resolve_inside`), with a parametrized test (`../`, `sub/`, absolute).

MUTATION (scratch copy): removed the live-flag gate → the switch-off test FAILED (PYTEST_RC 1) → caught.

CHECKS (lanes venv, direct exit): ruff check . = 0; pytest tests/connectors tests/contracts tests/api tests/spatial = 0 (3474 passed); validate_contracts.py = 0 (0 failures); modularity_check --check = 0; check_lane_paths --coverage = 0 (9952 files).

END-OF-REPORT
