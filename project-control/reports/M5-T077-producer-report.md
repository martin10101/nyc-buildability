# M5-T077 producer report - DB-051(a)-(e) geometry-threading hardening

Producer: backend-engineer (orchestrator-dispatched subagent; no controller checkpoint - the
packet's CHECKPOINT ENVELOPE input was ignored per the dispatch instruction, every other input
binding). Worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t077`, branch
`task/M5-T077-geometry-threading-hardening`, base b56f3d5b40171bcb6b760f97eb0eef574995f8ae.

ONE bounded change on the geometry-threading seam: the single null-segments contract + falsy-net,
taxonomy-detail, at-cap boundary, and non-scalar-bbl riders from the M5-T076 wave. Production edits
are the guard + docstring in `max_envelope_api.py` and a docstring in `lot_geometry_derivation.py`;
everything else is offline tests. `max_envelope.py` byte-untouched, route stays UNMOUNTED, no new
dependency.

## Files changed (== allowed_paths)

- `services/api/app/api/v1/max_envelope_api.py` - guard behavior + docstring (item b)
- `services/api/app/scenario/lot_geometry_derivation.py` - module docstring alignment only (no behavior)
- `services/api/tests/api/test_max_envelope_api.py` - tests for (a)(b)(c-route)(e)
- `services/api/tests/scenario/test_lot_geometry_derivation.py` - tests for (c-unit)(d)
- `project-control/reports/M5-T077-producer-report.md` - this report

## Per-AS evidence

### AS-1 (one null contract) [OBSERVED]
- Guard `_should_derive_lot_geometry` now returns True ONLY when `lot_line_segments` is ABSENT or
  an EMPTY LIST plus a usable scalar BBL: `max_envelope_api.py:176-178` (`supplied_empty =
  isinstance(segments, list) and not segments`; `None` and every other non-list value fall to
  `return False`). Docstring corrected at `max_envelope_api.py:167-174` - "ABSENT or an EMPTY LIST
  - nothing else"; explicitly states `null` is NOT treated as absent and stays on the 422 with no
  provider call.
- `null` refuses in all three states (no BBL; BBL + passing provider; BBL + failing provider),
  each 422 `validation_error` on `lot.lot_line_segments`, `resolutions == []` and `calls == []`:
  `test_null_segments_refuse_in_every_state_with_no_provider_call` at
  `tests/api/test_max_envelope_api.py:754`. The refusal is produced by `_build_lot_context`'s
  existing typed 422 (`proposal_checks_api.py:359-362`) because the guard leaves the `None` in
  place - verified: `_build_lot_context` refuses any non-list `lot_line_segments` and never reads
  `lot.bbl`.
- absent and `[]` still derive + fit: `test_absent_or_empty_segments_with_a_bbl_still_derive` at
  `tests/api/test_max_envelope_api.py:736` (the old `test_absent_or_null_..._still_derive` was
  rewritten per the orchestrator ruling: `null` dropped from the derive path).
- Both docstrings name only "ABSENT or an EMPTY LIST": `max_envelope_api.py:167` and
  `lot_geometry_derivation.py:15-19` ("`null` is NOT treated as absent"). No text claims null==absent.
- MUTATION (b) recorded below (re-admit None -> the null test reddens).

### AS-2 (falsy-malformed net) [OBSERVED]
- Malformed parametrize extended from the truthy set to `["abc", 42, {"id": "L-S"}, True, 0, "",
  {}, False, 0.0]`: `tests/api/test_max_envelope_api.py:700-708`. Each value -> 422 with no
  provider call, byte-identical with and without a BBL (asserted at `:719-728`).
- MUTATION (a) recorded below (`if lot.get(...)` weakening reddens all 5 falsy cases).

### AS-3 (taxonomy details) [OBSERVED]
- BBL_UNRESOLVABLE honest detail asserted at UNIT level (was pinned nowhere):
  `test_unresolvable_bbl_is_fail_closed_without_calling_provider` at
  `tests/scenario/test_lot_geometry_derivation.py:442` now asserts `derived.detail` is non-empty
  and names the unresolvable-BBL reason.
- Each derivation-failure class carries its reason into `placement.detail` at ROUTE level: the
  no_feature/multiple_features/invalid_geometry classes were already covered
  (`:571-588`); connector_fault now asserts it at `test_connector_fault_keeps_honest_gap`
  (`:591`, new asserts at `:604-609`) and bbl_unresolvable at
  `test_unresolvable_bbl_keeps_honest_gap_without_calling_provider` (`:613`, new asserts near
  `:625-628`). The append branch is `max_envelope_api.py:434-444`.
- MUTATION (c) recorded below (blanking the BBL_UNRESOLVABLE detail reddens the unit test).

### AS-4 (boundaries) [OBSERVED]
- At-cap boundary: a ring yielding EXACTLY `max_segments` segments derives all of them; `max_segments
  + 1` is `geometry_over_cap`: `test_ring_cutter_at_cap_boundary_derives_exactly_max_segments` at
  `tests/scenario/test_lot_geometry_derivation.py:423`. Cutter guard is `>` at
  `lot_geometry_derivation.py:183`.
- Non-scalar `lot.bbl` (`{"x": 1}` and `["1008350041"]`) -> 200 with the honest
  `lot_geometry_unsupported` gap, NO `derived_lot_geometry` block, provider never resolved or
  called (spy): `test_non_scalar_bbl_does_not_derive_and_never_calls_the_provider` at
  `tests/api/test_max_envelope_api.py:646-647`. `_build_lot_context` never reads `lot.bbl`, so no
  typed refusal - confirmed by the 200.
- MUTATION (d) recorded below (`>` -> `>=` reddens the at-cap assertion).

### AS-5 (scope + modularity) [OBSERVED]
- Exactly the allowed_paths changed (see `git status --short` below); no forbidden path touched.
- `max_envelope.py` byte-untouched: `git diff b56f3d5b -- services/api/app/scenario/max_envelope.py`
  empty; blob `f0abf88479d078d8ec7e88d4c2b1942fd69c040d` == HEAD blob == `git hash-object` of the
  worktree file.
- ruff clean; modularity exit 0 (failures 0); route stays unmounted (`test_route_is_unmounted_in_
  the_real_app` still passes); no new dependency (the null test's `MalformedResponseError` import
  is a local import of a symbol already used elsewhere in the file).

## Self-check runs (verbatim)

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t077\services\api`:
```
$ python -m ruff check .
All checks passed!

$ python -m pytest tests/scenario/test_lot_geometry_derivation.py tests/api/test_max_envelope_api.py -q
................................................................         [100%]
64 passed in 3.53s
```
Broader sweep (same cwd; G4 baseline was 1320):
```
$ python -m pytest tests/api tests/scenario -q
1329 passed in 44.86s
```
cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t077`:
```
$ python tools/modularity_check.py --check   ; EXIT=0
selected 484 files; failures 0; warnings 22
$ git diff b56f3d5b -- services/api/app/scenario/max_envelope.py
(empty - no diff)
$ git status --short
 M services/api/app/api/v1/max_envelope_api.py
 M services/api/app/scenario/lot_geometry_derivation.py
 M services/api/tests/api/test_max_envelope_api.py
 M services/api/tests/scenario/test_lot_geometry_derivation.py
```
(The 22 modularity warnings are all pre-existing `tools/agent_supervisor/*` review signals -
none of the four M5-T077 files appear; failures 0.)

Environment note: sandbox Python is 3.11.9 (repo/CI target is 3.12); the api CI job re-runs ruff +
pytest on the pushed head. No behavior in this change is version-sensitive.

## Mutation record (each applied to shipped source, run, reverted; final tree is shipped/green)

- MUTANT(a) - idiomatic weakening `if lot.get("lot_line_segments"): return False` replacing the
  membership+shape block in `_should_derive_lot_geometry`. Target
  `test_malformed_segments_refuse_identically_with_and_without_a_bbl`: **5 failed, 4 passed** - the
  5 FALSY params (`0`, `""`, `{}`, `False`, `0.0`) redden (`assert (200, None) == (422,
  'validation_error')`), the 4 truthy params stay green. RED as designed; reverted -> green.
- MUTANT(b) - re-admit `None` to the derivable set (`supplied_empty = segments is None or (...)`).
  Target `test_null_segments_refuse_in_every_state_with_no_provider_call`: **1 failed** at the "BBL
  + passing provider" state (`assert (200, None) == (422, 'validation_error')`). RED; reverted -> green.
- MUTANT(c) - blank the BBL_UNRESOLVABLE detail (`_fail(..., "")` at
  `lot_geometry_derivation.py:225-229`). Target
  `test_unresolvable_bbl_is_fail_closed_without_calling_provider`: **1 failed** at `assert
  derived.detail` (`AssertionError: assert ''`). RED; reverted -> green.
- MUTANT(d) - `>` -> `>=` at the cutter cap check (`lot_geometry_derivation.py:183`). Target
  `test_ring_cutter_at_cap_boundary_derives_exactly_max_segments`: **1 failed** at `assert reason
  is None` (`AssertionError: assert 'over_cap' is None`) - at-cap wrongly refused. RED; reverted -> green.

## Deviations
- CHECKPOINT ENVELOPE input ignored (no controller checkpoint in the subagent dispatch), per the
  dispatch instruction. All other inputs honored.
- The old `test_absent_or_null_segments_with_a_bbl_still_derive` was RENAMED to
  `test_absent_or_empty_segments_with_a_bbl_still_derive` and its `null` case removed (now covered
  by the dedicated null-refusal three-state test), per the orchestrator ruling for (b).
- `lot_geometry_derivation.py` had no false null==absent claim to correct (grep confirmed); the
  packet's "docstring alignment" output for that file was satisfied by ADDING a module-docstring
  paragraph (`:15-19`) that documents the route's eligibility contract and states `null` is not
  absent - accurate, additive, behavior-neutral.

## Discoveries (D-069; out-of-scope, not fixed here)
- None new. DB-051 (f)/(g) remain the mount-packet class as recorded in `docs/DISCOVERY_BACKLOG.md`
  row DB-051 (the web client sends no `lot.bbl` so derivation is client-unreachable; GEOMETRY_OVER_CAP
  has no consumer; no request-scoped upstream budget). This packet closed only (a)-(e); the route
  stays unmounted, so (f)/(g) are untouched by design.

END-OF-REPORT
