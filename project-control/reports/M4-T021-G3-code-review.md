# G3 Code Review Report — M4-T021 (B4 wide-street 100-ft buffer/intersection engine)

> Saved VERBATIM by the orchestrator from the code-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.
> Recorded as PASS per the gate-verdict semantics rule (the CLI supports PASS/FAIL/BLOCKED
> only); **F1 and F2 are BLOCKING for the next gate and for acceptance** until corrected,
> validated, and committed.

- Gate ID: G3
- Task ID: M4-T021
- Reviewer: code-reviewer (independent, read-only)
- Producer: backend-engineer (orchestrator-dispatched, unnamed spawn, base `d7c22f3e`, per D-060 deviation record in the task's progress_log)
- Reviewed head: `2231227a` (verified via `git rev-parse HEAD` at session start — matches pinned review head)
- Material producer commit: `cb277b8f`, integrated as `7dc56112` — verified **byte-identical** cherry-pick: `git diff cb277b8f 7dc56112 -- <3 allowed_paths files>` produced zero output.
- Result: **PASS with required corrections** (recorded as PASS; F1 and F2 below are BLOCKING for the next gate/acceptance per the project's PASS-with-corrections convention — precedent M1-T001/M1-T003/M1-T004/M4-T016/M4-T017)
- Clean environment/worktree used: primary checkout at pinned HEAD `2231227a` (no worktree switch needed; read-only, no writes made)

## Acceptance criteria reviewed

Task packet `project-control/tasks/M4-T021.json` contract items 1–6, scenarios S1–S5; pinned design source `project-control/reports/M4-T016-a2-geometry-mechanics-research.md` Part 2.2 (steps A–D), Part 2.3 (CRS/units), Part 2.4 (EC-1..6), Part 4.3 item 2 (B4 decomposition).

## Directive/requirement verification

Note: in the registry (`project-control/directives/*/requirements.json`), D-045-R002/R008/R009 and D-046-R001/R002 are each recorded `"producer": "orchestrator"`, `"independent_verifier": "directive-compliance-verifier"` — **not** `code-reviewer`. The formal PASS/FAIL verdict on these requirement IDs belongs to the directive-compliance-verifier's `verification.json`, not this G3 code gate. I give my code-level read below as supporting evidence only; it does not substitute for that independent verification.

| Requirement ID | Reviewed SHA | Code-level read (not the formal directive verdict) | Reproduced evidence |
|---|---|---|---|
| D-045-R002 | 2231227a | Supported — missing-input (EC-6) and error-path branches are typed and tested, never a manufactured number; module reproduces the ZR 23-22 footnote-1 citation verbatim | 29/29 local tests pass; `BUFFER_FT_CITATION` at wide_street_buffer_engine.py:178-183 |
| D-045-R008 | 2231227a | Supported — task is exactly the bounded B4 mechanic per Part 4.3 item 2; touches no rule file, no B3/B5/B6/B7 scope | `git diff` confirms exactly 3 files, none under `services/api/app/rules/**` |
| D-045-R009 | 2231227a | Supported — zero new dependencies, no compliance declaration, scope confined to allowed_paths | see "Scope/regression" below |
| D-046-R001 | 2231227a | Orchestrator-scope (dispatch-record evidence); not verifiable from source diff alone | task's own `path_notes`/progress_log assert sole-writer-at-dispatch; not independently confirmable by this reviewer's surface |
| D-046-R002 | 2231227a | Orchestrator-scope (disjointness of concurrent dispatch); not verifiable from source diff alone | same as above |

## Steps independently executed

1. `git rev-parse HEAD` → `2231227a...` (matches pinned head).
2. `git show --stat cb277b8f` and `git diff cb277b8f 7dc56112 -- <3 files>` → exactly the 3 allowed_paths files changed in the producer commit; cherry-pick is byte-identical (empty diff).
3. `git diff d7c22f3e 2231227a --stat -- <6 forbidden connector files + rules/** + pyproject.toml + requirements.in/.txt>` → empty (zero changes) across the *entire* base→head range, not just the producer commit.
4. `git show --stat 2231227a` → integration commit touches only `project-control/*` (evidence map, task json, state.json) — orchestrator territory, consistent with reviewer scope.
5. `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q` → `29 passed in 0.33s`.
6. `python -m pytest services/api/tests/connectors -q` → `781 passed in 4.30s`.
7. `cd services/api && python -m ruff check .` (then cd back) → `All checks passed!`.
8. `python tools/modularity_check.py --check` → `selected 405 files; failures 0; warnings 17` — neither new file appears in the warning list (verified against the printed list).
9. `grep -rn "wide_street_buffer_engine" services/api/app/rules` → no matches (module not wired into any rule file, as required).
10. `grep -n "shapely" services/api/pyproject.toml services/api/requirements.in services/api/requirements.txt` → pin is `shapely==2.0.7` in all three, unchanged, already-admitted (no new dependency).
11. Read `services/api/app/connectors/dcm_street_centerline_geometry.py` and `mappluto_geometry_arcgis.py` to check what CRS identity is actually carried on `SegmentPolyline`/`GeometryAssessment` (see A1 below).
12. Read `services/api/app/connectors/dcm_street_width_policy.py` (`AttestedPreconditions` / `_precondition_failures` / `classify_street_width_policy`) — the exact precedent the task packet names for EC-5 — to determine what "the D-052/M4-T019 AttestedPreconditions precedent" actually does (see F1).
13. `python -c "import inspect; from shapely.geometry.base import BaseGeometry; print(inspect.signature(BaseGeometry.buffer))"` → `quad_segs=16` (the method actually called by the module).
14. `python -c "import inspect, shapely; print(inspect.signature(shapely.buffer))"` → `quad_segs=8` (a *different*, unused, top-level function — the source of the producer's mistaken belief).
15. Empirically confirmed the two APIs diverge in effect: `LineString(...).buffer(100.0)` (16) vs `.buffer(100.0, quad_segs=8)` produces different vertex counts (67 vs 35) and different area on a short line (33365.48 vs 33214.45 sq ft) — quad_segs is not cosmetic.
16. Cross-checked the test suite's hand-derived expected values (10000 / 17500 / 40000 / tangency-area-0) against `test_line_probe_matches_the_hand_derived_expected_values`, which independently recomputes them via raw shapely calls, not via the module under test — confirms the suite is not deriving its own oracle from the code being tested.

## Expected versus actual

All numeric/behavioral claims in the producer report (§2 scenario table, §6 command outputs, §7 versions) were reproduced exactly: 29/29 and 781/781 test counts, ruff clean, modularity 0 failures/17 pre-existing warnings, shapely 2.0.7 / GEOS 3.11.4. No discrepancy found between claimed and actual test/tooling output.

Two claims in the report/module **do not match actual behavior**, detailed as F1/F2 below.

## Ruling on the 8 judged items

**1. CRS/input discipline.** PASS (with a documentation caveat, A1). `_require_crs` (wide_street_buffer_engine.py:417-440) requires exact `wkid == EXPECTED_WKID and latest_wkid == EXPECTED_LATEST_WKID`; `None`/mismatch on either side raises typed `WrongCRSError` (tested: `test_missing_lot_crs_is_typed_wrong_crs`, `test_mismatched_lot_crs_is_typed_wrong_crs`, `test_missing_segment_crs_is_typed_wrong_crs`, `test_mismatched_segment_crs_is_typed_wrong_crs`). The AST-scan test (`test_module_never_reimplements_transport_or_reprojection`, test file :591-644) asserts the **exact** set of imported modules (`assert imported_modules == {...}`) — not a substring/blacklist check — so *any* additional import (a reprojection library, `pyproj`, `shapely.affinity`, `importlib`, etc.) fails the test outright; this is non-vacuous and a real structural proof, mirroring the M4-T020 precedent. A violation this scan would miss: a hand-written reprojection formula using only already-imported names (no new import, no `0.3048`/`3.2808`/`to_crs` token) — a contrived, unrealistic case given the module's narrow surface, and not something I found evidence of.

**2. Buffer 100.0 ft planar / determinism assertions.** PASS for the 100.0 ft/planar/foot-CRS claim; import-time (`wide_street_buffer_engine.py:623-632`) and per-result determinism assertions are real and meaningful (verified equal to `mappluto_geometry_arcgis.PINNED_SHAPELY_VERSION`/`PINNED_GEOS_VERSION_STRING`, reproduced live). The `quad_segs` sub-claim is **wrong** — see F2.

**3. Both outputs (intersects + sub-geometry/area; per-segment + union aggregate) and union-before-intersect order.** PASS. Verified the code literally builds `buffers: list[BaseGeometry]` inside the per-segment loop (wide_street_buffer_engine.py:570-589), then only *after* the loop computes `union_buffer = unary_union(buffers)` (line 591) and intersects that union with the lot (lines 592-593) — union-before-intersect, not per-segment-sum. Confirmed numerically via S3 (10000 + 10000 − 2500 overlap = 17500, correct inclusion-exclusion for two perpendicular 50-ft bands over the fixture lot) and reproduced live.

**4. EC-4 (the trap).** PASS. `grep` over the module source shows the string `20.0`/`BOUNDARY_TOLERANCE_FT` appears **only** inside the `TANGENCY_NOTICE` documentation string (wide_street_buffer_engine.py:203-213), never as an imported name or an operative value; the buffer call (line 576) uses only `BUFFER_FT`. The AST-scan test also structurally asserts `"BOUNDARY_TOLERANCE_FT" not in imported_names`. The tangency characterization (intersects=True, zero-area LineString intersection at exact 100.0-ft) was reproduced two independent ways: the module's own test and a standalone shapely probe embedded directly in the suite (`test_line_probe_matches_the_hand_derived_expected_values`), both green. Consistent, non-vacuous, and the open legal question is documented, not resolved.

**5. EC-5 (the single most important ruling).** **Gap — does not satisfy the contract as written; blocking (F1).** The packet names a specific precedent ("the D-052/M4-T019 AttestedPreconditions precedent") for "so a caller cannot silently skip them." I read that precedent (`dcm_street_width_policy.py:337-364,384-402`): `AttestedPreconditions.exceptions_checked` (the *same* ZR named-street/alternate-width category) is not merely required to be present — when it is `False`, `classify_street_width_policy` returns `DECISION_UNRESOLVED`, refusing to issue any classification. That is a genuine value-gate, not just a presence-gate. `Ec5AttestedPreconditions` in this module requires the object's *presence* (TypeError on omission — real, tested) but never inspects the *value*: `test_ec5_preconditions_pass_through_unmodified_regardless_of_value` proves a caller can pass `(False, False, "not yet checked")` and still receive a full `STATUS_COMPUTED` result indistinguishable in shape from a properly-attested one. Nothing in the module's status/behavior differs based on the attestation truth, so a caller who has done zero legal verification and a caller who has done it correctly get the same-looking "computed" answer — this is exactly the "silently skip" failure mode the packet names. I weighed the producer's counter-argument (gating on `True` would make B4 permanently unusable today since the named-street override table doesn't exist yet, and the cited B5 dependency note in the research report is about a *different* decomposition item, not EC-5 — so the producer's own rationale partially misattributes its support) and find it a legitimate practical concern, but it does not resolve the divergence from the cited precedent's actual mechanism. **Ruling: this is a gap that must block** — either (a) gate on the attested values with a distinct typed refusal/state mirroring D-052's `UNRESOLVED` (my recommended fix), or (b) if a no-gate design is intentional, that must be an explicit owner/G6-ratified departure from the cited precedent recorded in the task or directive record, not a unilateral producer interpretation of ambiguous packet text. The producer's transparency here (an explicit, disclosed "open to reviewer disagreement" section) is commendable and is exactly the right process discipline — this finding rules on the substance, not the disclosure.

**6. EC-6 empty input / EC-2 under-claim / no re-classification / no rule-file touch.** PASS. EC-6: `len(wide_segments) == 0` returns `STATUS_NO_WIDE_SEGMENTS_PROVIDED` with every computed field `None`/empty (wide_street_buffer_engine.py:549-568), and the test explicitly asserts `aggregate_intersects is not True` and `is not False` — never coerced. EC-2: `EC2_UNDER_CLAIM_NOTICE` is present on every result unconditionally (verified in code and by `test_ec2_under_claim_notice_always_present`), and the producer report's §3 tradeoff section is substantive, not boilerplate. No rule file touched (`git diff -- services/api/app/rules` empty). No re-classification: the module never reads `Streetwidth`/disposition text (confirmed by `test_only_caller_supplied_segments_participate_never_reclassified`, which feeds a "narrow" (40 ft) labelled segment through unchanged and gets an identical geometric result).

**7. D-045-R009 preservation.** PASS. `git diff d7c22f3e 2231227a --stat` over the 6 forbidden connector files + `rules/**` + `pyproject.toml`/`requirements.in`/`requirements.txt` is empty across the *entire* base-to-head range (not just the single producer commit) — exactly 3 files changed anywhere in this task's history, matching allowed_paths exactly. Shapely pin unchanged in all three dependency files.

**8. General quality.** Fail-safe direction is consistently closed on ambiguous input (CRS/geometry/attestation all refuse rather than guess). Error taxonomy (`WideStreetBufferEngineError` base with `error_type`/`correlation_id`/`detail`/`to_payload()`) is structurally identical to the accepted `DCMConnectorError`/`MapPlutoGeometryConnectorError` precedents (verified by direct comparison). Module boundary/modularity: clean, single-responsibility new module; checker confirms 0 failures and neither new file in the warning list. Test-expectation independence: confirmed via the dedicated standalone-probe test — not derived by calling the code under test. `quad_segs=8`: the *choice* to pin explicitly is reasonable practice, but the *stated justification* is factually wrong — see F2. No multipolygon/holes lot fixture: disclosed honestly (§9 of the report); low risk today since `canonical_to_shapely` is reused generically and unmodified, but flagged as advisory (A3) since NYC corner/through lots with complex polygons are common and this is exactly the shape B7 will need.

## Evidence paths

- `services/api/app/connectors/wide_street_buffer_engine.py` (reviewed source)
- `services/api/tests/connectors/test_wide_street_buffer_engine.py` (reviewed tests)
- `project-control/reports/M4-T021-producer-report.md` (claims, treated as claims not evidence)
- `services/api/app/connectors/dcm_street_width_policy.py:100-436` (the cited EC-5 precedent, independently re-read)
- `services/api/app/connectors/dcm_street_centerline_geometry.py:290-350` (confirms `SegmentPolyline` carries no per-feature CRS field — basis for A1)
- `services/api/app/connectors/mappluto_geometry_arcgis.py:605-830` (confirms `GeometryAssessment.area_crs` is never cross-read by the engine — basis for A1)
- Git evidence: `cb277b8f`, `7dc56112`, `2231227a`, base `d7c22f3e`

## Scenario table (S1–S5), independently verified

| ID | Case | My verdict | Verification performed |
|---|---|---|---|
| S1 | wide_only_buffer_membership | PASS | Reproduced 4/4 tests live; manually re-derived the 10000 sq ft intersection area from the fixture geometry (straight-offset buffer edge at x=50, lot x∈[0,200]) — matches |
| S2 | crs_and_input_fail_closed | PASS | Reproduced 13/13 tests live; independently read the AST-scan assertion logic (exact-set equality, not substring) and confirmed it is non-vacuous; confirmed `Ec5AttestedPreconditions`/`AttestedWideSegment`/`AttestedLotPolygon` are true no-default dataclasses via direct field inspection |
| S3 | portions_split_corner_lot | PASS | Reproduced 2/2 tests live; independently re-derived 17500 via inclusion-exclusion (10000+10000−2500 overlap) — matches; confirmed union-before-intersect ordering by direct code read, not just trusting the test's assertion of the number |
| S4 | tangency_and_empty_honesty | PASS | Reproduced 4/4 tests live; confirmed `BOUNDARY_TOLERANCE_FT` absent from both `dir(engine)` and source via grep+AST; confirmed EC-6 never-coerced via explicit `is not True`/`is not False` assertions |
| S5 | scope_regression_determinism | PASS with correction (F2) | Reproduced 29/29 and 781/781 test counts, ruff clean, modularity 0 failures, shapely/GEOS pins, exactly-3-files scope — all live and matching; the determinism section's `quad_segs` claim is factually wrong (F2) |

## What I inspected vs. executed

**Executed (live, this session):** full connectors suite (781), engine-only suite (29), ruff on `services/api`, `modularity_check.py --check`, three `git diff`/`git show` scope-verification commands across the full base→head range, the byte-identical cherry-pick diff, three ad-hoc Python probes on `shapely.buffer` signatures/behavior (quad_segs default divergence), grep/AST-adjacent source scans for `BOUNDARY_TOLERANCE_FT`/quad_segs/error-class patterns.

**Inspected only (read, not separately re-executed beyond what pytest already covers):** the full 632-line module and 662-line test file end to end; `dcm_street_width_policy.py` (EC-5 precedent), `dcm_street_centerline_geometry.py` and `mappluto_geometry_arcgis.py` (CRS-carrier structure for A1); the pinned research report Parts 2.2–2.4 and 4.3; D-045/D-046 requirement JSON.

## Regression/security/provenance findings

No regression: pre-existing 752 connector tests remain green, no accepted file touched (verified across the full commit range, not just the head commit). No secrets/network I/O in the new module (confirmed by the exhaustive import allowlist test and by direct code read — no `requests`/`httpx`/socket usage). Provenance passthrough fields (`classification_basis`, `source_retrieved_at`, `source_raw_digest`, `lot_identity`, `buffer_ft_citation`) are all required, no-default fields, correctly carried into results.

## Defects

**F1 (blocking).** EC-5 `Ec5AttestedPreconditions` does not gate computation on the attested boolean values, diverging from the actual mechanism of the precedent the task packet names by name (`dcm_street_width_policy.AttestedPreconditions`, which *does* refuse/return `UNRESOLVED` when its analogous `exceptions_checked` attestation is `False`). Evidence: `wide_street_buffer_engine.py:443-469` (`_validate_ec5_preconditions` checks type/shape only) and `:543` (call site, no branch on value); `dcm_street_width_policy.py:337-364,384-402` (precedent's actual gate); test `test_ec5_preconditions_pass_through_unmodified_regardless_of_value` (test file :515-531) proves a `(False, False, ...)` attestation still yields `STATUS_COMPUTED`. Required rework: gate computation on the attested values with a distinct typed refusal/state (mirroring D-052's `UNRESOLVED`), OR obtain and record an explicit owner/G6-track ruling authorizing the no-gate design as an intentional departure from the named precedent, referenced from the module docstring.

**F2 (blocking).** The module's claim that `BUFFER_QUAD_SEGS = 8` "also" matches shapely's implicit default (wide_street_buffer_engine.py:185-187: `"# ... left to shapely's implicit default (also 8, but implicit is not documented)"`, restated in the producer report §9) is factually false for the API actually called. `linework.buffer(...)` invokes `shapely.geometry.base.BaseGeometry.buffer`, whose real default is `quad_segs=16` (reproduced live: `inspect.signature(BaseGeometry.buffer)` → `quad_segs=16`). The `quad_segs=8` default the producer likely checked belongs to the *different*, unused top-level `shapely.buffer()` function (`inspect.signature(shapely.buffer)` → `quad_segs=8`). This is a real, demonstrable divergence (reproduced: identical short `LineString(...).buffer(100.0)` calls with 16 vs. 8 quad_segs produce different vertex counts (67 vs 35) and different area (33365.48 vs 33214.45 sq ft on a 10-unit test line)) — not cosmetic. It has **zero impact on the 29 shipped tests** because every fixture segment extends far beyond the lot's y-range specifically to keep the rounded end-caps away from the area of interest (confirmed by direct inspection of the fixture coordinates), so the false claim does not corrupt any currently-tested numeric result. Required rework: correct the docstring/comment (and producer report §9) to state accurately that 8 is a deliberately-chosen value that *diverges* from the real default of 16, with the precision tradeoff disclosed honestly; consider matching the real default (16) absent a source-derived reason to prefer 8, since coarser resolution has no legal justification; add at least one end-cap-proximate test given the producer's own admission that this path is currently untested.

## Advisory findings

**A1.** The producer report's "independently re-validates" framing for CRS (§1 item 1) overstates what happens on the wrapper-object side: `SegmentPolyline` (`dcm_street_centerline_geometry.py:299-323`) carries no per-feature CRS field at all (CRS is a page-level property, validated once by `_require_page_crs` at parse time), and `GeometryAssessment.area_crs` (`mappluto_geometry_arcgis.py:611-636`) is never read or cross-checked by `wide_street_buffer_engine._require_crs`. The actual mechanism is: the module checks a caller-*declared* `wkid`/`latest_wkid` pair against a hardcoded expected constant — a real, typed, tested refusal on mismatch/absence, but not a derivation from the wrapped object's own embedded identity (because none exists at that granularity). Functionally sound and consistent with how CRS is scoped elsewhere in this connector family; recommend softening the report's wording rather than any code change.

**A2.** `WideStreetBufferResult.ec5_preconditions` currently has no consumer (B7 does not exist yet); the "carried through for downstream audit" guarantee is a forward promise, unverifiable today.

**A3.** No multipolygon/holes lot fixture, disclosed honestly by the producer. Low risk today (generic reuse of `canonical_to_shapely`), but NYC corner/through lots with complex geometry are common; recommend adding before B7 depends on this module for production-shaped lots.

**A4.** D-046-R001/R002 (parallel-dispatch disjointness) are outside what a code-only G3 review can verify; recommend the directive-compliance-verifier confirm dispatch-record evidence independently rather than relying on this report.

## Required rework

1. Fix F1: gate `Ec5AttestedPreconditions` on attested values (or obtain and record an explicit owner/G6 ruling ratifying the current no-gate design, referenced in-code).
2. Fix F2: correct the false "matches shapely's implicit default" claim in both the module and the producer report; state the real default (16) and the deliberate-divergence rationale honestly; add an end-cap-proximate test.
3. (Advisory, non-blocking) Consider A1–A3 before B7 consumes this module.

## Reviewer conclusion

The geometry engineering itself is solid and independently reproducible: CRS fail-closed discipline, the 100.0-ft planar buffer, union-before-intersect ordering, per-segment/aggregate portions exposure, EC-1/2/3/4/6 typed handling, determinism assertions, error taxonomy, scope discipline (exactly 3 files, zero new dependencies, byte-identical cherry-pick, no forbidden-file drift across the full base→head range), and test independence (hand-derived + standalone-probe cross-checked) all held up under live re-execution and independent re-derivation. Two concrete, narrow, correctable defects were found: F1 (a real divergence from the named EC-5 precedent's gating mechanism, on a legally-sensitive scope boundary) and F2 (a factual error about a library API default, reproducibly confirmed, currently inert against shipped tests but embedded as false documentation in permanent code). Neither requires redesign. **Verdict: PASS with required corrections** — record as PASS; F1 and F2 block the next gate/acceptance until corrected and re-verified.
