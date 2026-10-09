# M5-T107 producer report — D-087 PKT-E: 3D scene assembler + UNMOUNTED scene route

Producer: backend-engineer (orchestrator-dispatched subagent), worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t107`, branch `task/M5-T107-scene-assembler`.
Claim seam / parent HEAD: `110894295ec97c1d7cb87deb3421a628b526b66b`.

## What was built

1. `services/api/app/scenario/scene_assembler.py` (NEW, 455 SLOC) — the pure, deterministic
   plan-section-2.1 scene assembler: `MassingModel.as_dict()` verbatim + a `context_buildings`
   layer under ONE declared vertical datum, with untrusted source text escaped, MultiPolygon
   holes disclosed, zero/unverified grounds disclosed, and string coordinates parsed to float.
2. `services/api/app/api/v1/scene_api.py` (NEW, 258 SLOC) — the UNMOUNTED, flag-gated
   `POST /api/v1/scene` route: bounded body, per-caller rate limit, off-event-loop cancellable
   job under a per-request deadline, connector called `interactive=True` with a wall-clock
   deadline, typed refusals, server correlation id.
3. `services/api/app/connectors/building_footprints_arcgis.py` (EDIT, 865→900 SLOC) — the
   pre-consumption riders DB-073 (a)-(d).
4. Tests: `tests/scenario/test_scene_assembler.py` (NEW), `tests/scenario/test_scene_api.py`
   (NEW), `tests/connectors/test_building_footprints_arcgis.py` (EDIT: DB-073 (e)-(g) + the
   updated deadline test).

`building_footprints_geometry.py` was NOT modified: the DB-073 fixes are localized hardening of
existing connector functions, and all new consumer logic lives in the new `scene_assembler.py`.

## Datum decision and its source (DB-058 (f), DB-053 (f); AS-1)

ONE ground datum, chosen knowingly and recorded in `scene.provenance.scene.ground_datum` and in
the `context_buildings.ground_datum` block (`GROUND_DATUM_DECISION`):

- **Chosen frame:** `local_scene_frame_relative_to_site_ground`. The massing model is a relative
  z=0 frame whose z=0 is the site ground; each context building is placed at
  `base_z_ft = GROUND_ELEVATION − site_ground_elevation_ft` (the connector's
  `relative_base_z_ft`), so the whole scene shares one local vertical frame. `base_z` is a
  RELATIVE offset, never an absolute NAVD88 elevation.
- **Source:** the NYC OTI building-footprint layer's `GROUND_ELEVATION`, as published
  (source field named in provenance). Vertical unit `us_survey_foot`, explicit.
- **Both official definitions disclosed, neither reconciled** (verbatim from M5-T101-G1): City
  dictionary = "lowest elevation at the building ground level, from LiDAR/photogrammetry"; FGDC =
  "interpolated bare-earth elevation at the building centroid (2010 LiDAR DTM)". **NAVD88 is
  attributed to the City dictionary only**; the FGDC states no datum.
- **Zero/unverified/missing grounds disclosed, never sea level:** per-building `ground_status` ∈
  {`grounded`, `ground_zero_unverified`, `ground_elevation_missing`, `site_ground_not_supplied`};
  when the ground or site ground is absent, `base_z_ft` is null (`base_z_grounded=false`), never 0.

## Per-AS evidence (all [OBSERVED] via the runs below)

- **AS-1 (payload):** `test_as1_payload_carries_massing_verbatim_plus_context_and_explicit_vertical_unit`
  (massing fields verbatim + `world_to_local`, `vertical_unit=us_survey_foot`, layers include
  `context_buildings`), `test_as1_one_declared_ground_datum_with_its_source_in_provenance`,
  `test_as1_golden_context_building_shape_is_pinned` (golden dict), `test_as1_string_coordinates_parse_to_float`
  + `test_as1_non_numeric_or_non_finite_coordinate_is_refused_typed` (DB-054 (o)),
  `test_as1_assembler_is_deterministic`.
- **AS-2 (honesty + disclosure):** `test_as2_proposed_and_generated_labels_follow_d083`,
  `test_as2_the_assemblers_own_labels_carry_no_barred_claim_word` (shared claim-word screen over
  every emitted label), `test_as2_per_level_nesting_and_party_wall_are_disclosed` (DB-054 l/n),
  `test_as2_multipolygon_courtyard_holes_are_disclosed_never_dropped` (DB-053 g),
  `test_as2_zero_and_unverified_grounds_are_disclosed_never_sea_level` (DB-058 f; parametrized).
- **AS-3 (untrusted text):** `test_as3_source_strings_are_declared_untrusted_and_escaped`
  (HTML entities + U+2028/9 stripped; raw string absent from the payload),
  `test_as3_escape_guard_is_load_bearing_in_process_mutation`,
  `test_as3_context_refusal_is_disclosed_and_bounded_never_dropped`,
  `test_as3_assembler_does_not_log_any_source_or_caller_text` (the assembler imports no logger).
- **AS-4 (route, unmounted):** `test_route_is_unmounted_in_the_real_app` (absent from routes AND
  OpenAPI), `test_flag_off_is_a_generic_404`, `test_413_oversized_body`, `test_422_*` (malformed,
  NaN, missing lot_ring, exactly-one-of, typed refusal named + bounded),
  `test_429_rate_limit_and_its_reddening_mutation`, `test_504_deadline_and_its_reddening_mutation`,
  `test_connector_is_called_interactive_with_a_deadline`,
  `test_correlation_id_is_server_generated_and_echoed`, `test_every_emitted_pair_is_in_the_matrix`.
- **AS-5 (connector riders DB-073 a-g):** `test_pkte_correlation_id_strips_line_and_paragraph_separators`
  (a), `test_pkte_correlation_id_is_length_bounded_at_the_source` (b),
  `test_pkte_deadline_checked_before_the_metadata_fetch` +
  `test_pkte_deadline_refuses_during_a_retry_sleep` (c),
  `test_pkte_tz_naive_deadline_is_a_typed_disallowed_request` (d),
  `test_pkte_connector_is_unwired_from_the_mounted_app_and_wired_only_to_the_scene_assembler` (e,
  replaces the grep-based not-wired test with an import-graph/AST walk from `app.main`),
  `test_pkte_deadline_is_checked_at_every_page_not_once` (f),
  `test_pkte_cumulative_bytes_ceiling_is_between_the_one_and_two_page_sums` (g).
- **AS-6 (scope):** zero new dependencies (`test_as6_module_imports_only_stdlib_and_app`;
  connector import-allowlist test still green); app/main.py untouched; connector's existing tests
  pass apart from the replaced not-wired test; modularity exit 0; exactly the allowed paths.

## DB-073 / DB-054 / related closure table

| Rider | Closure |
|---|---|
| DB-073 (a) U+2028/U+2029 not stripped from cid | `_CONTROL_CHAR_DELETE` now includes 0x2028/0x2029; cid safe at both log sites + for raw-render consumers |
| DB-073 (b) cid not length-bounded at log sites | `_safe_correlation_id` bounds to `_LOG_FIELD_MAX` at the source |
| DB-073 (c) deadline only at page top | `_check_deadline` added before the metadata fetch AND a deadline-aware retry-sleep wrapper `_Io._sleep_within_deadline`; the scene route passes `interactive=True` + a wall-clock deadline |
| DB-073 (d) tz-naive deadline → internal_error | `_validate_deadline` rejects a tz-naive deadline as `disallowed_request` before any I/O |
| DB-073 (e) grep not-wired test trips on wiring | replaced with an import-graph/AST walk from `app.main` (connector + scene_api unreachable; connector wired only to the assembler) |
| DB-073 (f) once-only deadline check survives | advancing-clock multi-page test trips the deadline on page 2 |
| DB-073 (g) per-page byte reset survives | cumulative-bytes ceiling test set between the one- and two-page sums |
| DB-054 (k) vertical unit explicit | `scene.vertical_unit` + per-building `vertical_unit` = `us_survey_foot` |
| DB-054 (l) per-level nesting vs lot | disclosed in `scene.disclosures[per_level_nesting_not_asserted]` |
| DB-054 (n) missing party-wall distinction | disclosed in `scene.disclosures[no_party_wall_distinction]` |
| DB-054 (o) string coords fail closed | `parse_ring` parses numeric strings to float; non-numeric/non-finite → typed `SceneAssemblyError` |
| DB-058 (a) untrusted source text | escaped for rendering (HTML entities + control/separator strip + bounded); declared; raw not emitted |
| DB-058 (f) datum conflict + zero ground | one declared datum; both definitions disclosed; zero/unverified/missing grounds disclosed, never sea level |
| DB-053 (f) one declared vertical datum | `GROUND_DATUM_DECISION` in provenance |
| DB-053 (g) MultiPolygon courtyard holes | every part + hole disclosed, never dropped; holes-policy disclosure |
| DB-061 (i) job + deadline + rate limit | route runs the assembly off the loop under `asyncio.wait_for` + per-caller rate limit; over-budget → typed 504 |

## Mutation table (every new guard has a reddening in-process mutation)

| Guard | Mutation that reddens | Test |
|---|---|---|
| U+2028/U+2029 strip | remove 0x2028/0x2029 from `_CONTROL_CHAR_DELETE` | `test_pkte_correlation_id_strips_line_and_paragraph_separators` |
| cid length bound | drop the `_LOG_FIELD_MAX` bound | `test_pkte_correlation_id_is_length_bounded_at_the_source` |
| deadline before metadata | remove the pre-metadata `_check_deadline` | `test_pkte_deadline_checked_before_the_metadata_fetch` |
| deadline during retry sleep | use plain `self.sleep` (no `_check_deadline`) | `test_pkte_deadline_refuses_during_a_retry_sleep` |
| tz-naive deadline refusal | remove `_validate_deadline` (→ internal_error) | `test_pkte_tz_naive_deadline_is_a_typed_disallowed_request` |
| deadline per-page (not once) | hoist the check before the loop | `test_pkte_deadline_is_checked_at_every_page_not_once` |
| cumulative-bytes ceiling | per-page reset of `decoded_bytes` | `test_pkte_cumulative_bytes_ceiling_is_between_the_one_and_two_page_sums` |
| untrusted-text strip | empty `_RENDER_UNSAFE_DELETE` (consuming namespace) | `test_as3_escape_guard_is_load_bearing_in_process_mutation` |
| per-caller rate limit | raise `SCENE_RATE_LIMIT_MAX` far above the count | `test_429_rate_limit_and_its_reddening_mutation` |
| per-request deadline | raise `SCENE_MAX_SECONDS` (same slow fetch → 200) | `test_504_deadline_and_its_reddening_mutation` |

## Commands (cwd noted; verbatim tails)

- cwd `services/api`: `python -m ruff check .` → [OBSERVED] my 6 files pass; 4 PRE-EXISTING
  E501s remain in seeded placeholder files for the parallel PKT-D/PKT-F packets
  (`export_api.py`, `export_service.py`, `dxf_import.py`, `dxf_import_api.py` — head line 1 is
  `"""Placeholder seeded at the M5-T109 contract seam..."""`), out of my scope. Ruff on exactly
  my six files: `All checks passed!`.
- cwd `services/api`: `python -m pytest tests/scenario tests/connectors -q` → `1813 passed in
  60.78s`.
- cwd `services/api`: `python -m pytest tests/api -q` → `700 passed in 70.16s` (nothing else broke).
- cwd repo root: `python tools/modularity_check.py --check` → `selected 497 files; failures 0;
  warnings 27`, exit 0. `scene_assembler.py` 455 SLOC and `scene_api.py` 258 SLOC are under the
  600 warn threshold; the connector is 900 SLOC (< 1000 hard).

## Cohesion note (modularity)

`building_footprints_arcgis.py` grew 865→900 SLOC (still < the 1000 hard cap; above the 750
justify signal, as it was before this packet). The +35 SLOC are localized hardening of EXISTING
functions (`_safe_correlation_id`, a new `_Io._sleep_within_deadline` retry-sleep wrapper,
`_validate_deadline`, and one pre-metadata `_check_deadline` call) — no new domain responsibility
was added to the connector. All new consumer logic (scene assembly, datum, escaping, coordinate
parsing) lives in the new focused module `scene_assembler.py`.

## Deviations

1. **Rate-limit "existing mechanism":** the packet said to "reuse the repo's existing rate-limit
   mechanism (see lot_geometry.py / properties.py)". Those routes only surface an UPSTREAM
   `rate_limited` state from the connectors' retry budget; there is NO route-level per-caller
   rate limiter in the repo. I implemented a minimal stdlib sliding-window per-caller limiter in
   `scene_api.py` (zero new dependencies), keyed by caller host. Recorded as DISCOVERY DB-1 below.
2. **Per-caller key without auth:** the route has no auth yet, so the rate-limit key is the caller
   host (best-effort, spoofable). Authn/tenancy arrive with PKT-H (mount); recorded as a
   disposition, matching the max_envelope route's auth posture.
3. **Cancellability:** `asyncio.wait_for` cancels the awaiting coroutine and returns a 504; the
   underlying `run_in_threadpool` OS thread cannot be force-killed, but the connector deadline
   (`interactive=True` + wall-clock deadline) and the massing model's internal bounds ensure the
   thread terminates promptly. This matches the accepted M5-T088 G5 fix (b) intent.

## DISCOVERIES (for the orchestrator to record in docs/DISCOVERY_BACKLOG.md)

- **DB-1 (rate-limit primitive):** the repo has no shared route-level per-caller rate-limit
  primitive; PKT-D/PKT-E/PKT-F (and PKT-H) each need one. This packet introduced a minimal
  stdlib sliding-window limiter inside `scene_api.py`. Consider extracting a shared route
  rate-limit helper (and a bounded/pruned store) before the mount packet, and choose the
  per-caller key at the auth seam. In-process state is unbounded in caller-host keys (pruned per
  key only) — bound the number of tracked keys before public exposure.
- **DB-2 (context param pre-validation):** invalid context query params (envelope/site_ground/
  page_size) are handled by the connector's fail-closed `disallowed_request` and surfaced as a
  DISCLOSED context refusal inside a 200 scene (the massing still builds). This is honest and
  matches the connector contract, but a UX packet may prefer a 422 for a caller-fault context
  query; recorded for the mount/UX packet.
- **DB-3 (GLB payload):** plan section 2.1 lists an OPTIONAL accompanying GLB via `write_glb`;
  not included in this packet (kept minimal, `app/cad` is out of scope). Route it to PKT-D/PKT-H.

---

## Round 2 (rework on top of integration head `8273c6881677d9ec83f1e03bc5c63af534180df7`)

Round 1 review: G1/G3/G4 PASS with advisories, G5 FAIL on F-1. The full failure surface was
inventoried and repaired as ONE bounded change across 5 files. The connector production module
(`building_footprints_arcgis.py`) and `building_footprints_geometry.py` were NOT touched this
round — the F-1 fix is entirely inside the assembler; the connector's own numeric inputs
(`_coord`/`_finite`, `_check_page_size`, `_validate_deadline`) already OverflowError-guard.

### Per-finding closure

- **G5 F-1 (BLOCKING) — huge-int coordinate → untyped 500.** `scene_assembler._coerce_coordinate`
  int/float branch now wraps `float(value)` in `try/except OverflowError → return None`, mirroring
  the connector's `_finite()`. A `10**400` coordinate now flows to the existing typed
  `unparseable_coordinate` refusal (422), not an untyped OverflowError (500). Other numeric inputs
  checked: the assembler's ONLY float() conversion is `_coerce_coordinate` (a huge numeric STRING
  already resolved to inf → refused via `math.isfinite`); heights/scalars are converted by the
  massing model (M5-T106 lane, now typed-refusing) and re-raised as `SceneAssemblyError` inside
  `build_scene_massing`'s try; site_ground/page_size/deadline are validated by the connector's
  already-guarded helpers. Tests: service + route + an in-process mutation; also a source-revert
  verification (below).
- **G5 F-2 = G3 A1 — incomplete escaping.** New `_escape_untrusted_mapping` escapes both KEYS and
  string VALUES; applied to `attributes_escaped` and each `gaps[]` record. `drift_signals` and
  `geometry_findings` are now `_escape_untrusted`-mapped in the layer/building. The
  `untrusted_source_text_escaped` disclosure, the module docstring, and the helper docstring are
  rewritten to be exactly true (enumerate keys, values, geom_source, last_status_type, gap fields
  incl. raw, drift_signals, geometry_findings). Fixed gap keys / official attribute keys escape to
  themselves (no consumer break).
- **G5 F-3 = G3 A2 — unbounded rate-limit state.** `_rate_limit_allows` now evicts a key when its
  pruned window is empty and bounds the tracked-key count via new `SCENE_RATE_LIMIT_MAX_KEYS`
  (4096): a new caller at the ceiling triggers `_evict_empty_keys` (sweep of expired keys) and, if
  the ceiling is still full of ACTIVE callers, is refused fail-closed. The shared limiter module
  stays a PKT-H note (DB-1, unchanged).
- **G5 F-4 — "cancelled" overstated.** Module docstring + `SCENE_MAX_SECONDS` docstring now state
  the truth: the awaited coroutine is cancelled and a 504 is returned with no partial scene to the
  client; the worker thread cannot be force-killed and runs to completion, its total work bounded
  by the connector deadline + interactive single-attempt + byte/vertex caps. Client 504 message
  reworded to not imply a thread kill.
- **G3 A4 — non-dict `context`.** DECISION: refuse it typed (422, field `context`) rather than
  silently treating it as no-context; an absent/null context remains honest no-context (200,
  not_requested). Rationale: silently swallowing a caller-fault masks the mistake and violates the
  "typed refusals" contract. Tested (str/list/int → 422; None → 200 not_requested).
- **G3 A5 — ground_status authority.** New layer disclosure `ground_status_is_authoritative` +
  paired test: a consumer must not read `base_z_grounded` alone; `ground_status` is authoritative
  (a zero/unverified ground yields a real base_z with base_z_grounded true but
  ground_status=`ground_zero_unverified`).
- **G4 adv 1 — vacuous AST test.** Added a traversal floor: `assert len(seen) > 1` and
  `assert "app.api.v1.proposal_validation" in seen` (a known main-reachable module the scene route
  also reuses), so the unreachability assertions cannot pass on an empty walk.
- **G4 adv 2 — route caplog.** New test: a refusal carrying a hostile caller string emits a log
  line containing ONLY `field=lot_ring[0]` + the server correlation id; the hostile string is in no
  record.
- **G4 adv 4 — 500 matrix pairs.** Two new tests exercise (500, internal_error): the assemble-stage
  `except Exception` (fake raising a RuntimeError; asserts no exception text leaks) and the
  serialization-unsafe branch (a NaN-bearing scene fails `allow_nan=False`).
- **G1 ADV-1 — height provenance.** New `HEIGHT_PROVENANCE` (imports the connector's
  `HEIGHT_UNIT_BASIS` [feet is inference, RQ-1] + `HEIGHT_REFERENCE` [HEIGHT_ROOF above ground, not
  sea level]) threaded onto the context layer, present even for not_requested. Tested.
- **OUT OF SCOPE, untouched:** shared limiter/proxy/auth (PKT-H); G1 ADV-2 (accepted connector
  wording, DB-073 (h)); G4 adv 3 (mounted include_in_schema, PKT-H); massing_model.py.

### Mutation table (reddening proof)

| Finding | Guard | Mutation | Result |
|---|---|---|---|
| F-1 | OverflowError guard in `_coerce_coordinate` | source-revert to bare `float(value)` | `test_422_huge_int_...` + `test_as1_huge_int_...` RED (OverflowError → 500); restored → green |
| F-1 | same | in-process: `sa._coerce_coordinate` → unguarded fn | `test_as1_overflow_guard_is_load_bearing...` asserts `OverflowError` leaks |
| F-2 | key escaping in `_escape_untrusted_mapping` | source-revert to values-only | `test_as3_hostile_attribute_key...` RED (raw key survives); restored → green |
| F-2 | key/gap/drift/findings escaping | in-process: `sa._escape_untrusted` → identity | `test_as3_escape_completeness_guard...` asserts raw `<k>`/`<r>`/`<d>` survive |
| F-3 | key ceiling + eviction | source-revert to pre-fix `_rate_limit_allows` | `test_rate_limit_evicts_expired_keys...` RED (4th caller admitted); restored → green |
| F-3 | key ceiling | in-process: raise `SCENE_RATE_LIMIT_MAX_KEYS` to 1000 | 4 active callers all admitted (embedded) |

### Commands (cwd, verbatim tails)

- `cd services/api && python -m ruff check .` → `All checks passed!`
- `cd services/api && python -m pytest tests/scenario tests/connectors -q` →
  `1842 passed in 71.47s` (was 1823; +19 tests).
- new/edited tests verbose → `14 passed in 4.40s` (all PASSED).
- source-revert reddening runs (F-1/F-2/F-3) → the named tests FAILED as expected, restored to
  green after re-applying each fix.
- `cd <repo root> && python tools/modularity_check.py --check` → `EXIT=0` (warnings only; the
  connector production file is unchanged this round, so no growth was added to it).

END-OF-REPORT
