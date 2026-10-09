# M4-T021 producer report - B4 wide-street 100-ft buffer/intersection engine

Producer: backend-engineer. Base: `d7c22f3e` ("D-060 captured"). Scope: exactly the 3
`allowed_paths` files:

- `services/api/app/connectors/wide_street_buffer_engine.py` (production module, now 754 lines
  after rework, was 632)
- `services/api/tests/connectors/test_wide_street_buffer_engine.py` (test suite, now 947 lines /
  40 tests after rework, was 662 lines / 29 tests)
- `project-control/reports/M4-T021-producer-report.md` (this file)

No accepted connector, rule file, or any other path was touched (`git status --short`/`git diff
--stat` re-verified after the rework commit shows only the 2 code files above as modified;
verified again below under S5).

**REWORK NOTICE (this section added on rework, both reviewed head `2231227a` gates recorded and
consolidated in `project-control/reports/M4-T021-rework-ruling.md`).** Sections 1-9 below are the
ORIGINAL submission, left largely intact for the record; corrections are layered in-place at the
specific claims the reviewers found false or incomplete, and a new **Section 10 - Rework record**
maps each of the three blocking findings (G3-F1, G3-F2, G4-F1) to its exact fix. Two claims in the
original text below were FALSE and are corrected in-place rather than silently rewritten: the
"quad_segs=8 matches shapely's implicit default" claim (item 2 below, and section 9's `quad_segs`
bullet), and the "carried through unmodified into the result" provenance claim (item 5 below) for
`source_retrieved_at`/`source_raw_digest`, which in the original submission never reached any
output field at all.

## 1. Contract item map (task packet items 1-6)

### Item 1 - typed inputs, read-only reuse, both CRS identities validated

- `AttestedWideSegment` (`wide_street_buffer_engine.py:301-329`) wraps the accepted M4-T020
  `SegmentPolyline` (imported, never re-implemented) plus an explicit, no-default `wkid` /
  `latest_wkid` pair the module independently re-validates - it never trusts the wrapper's claim
  merely because a `SegmentPolyline` object exists.
- `AttestedLotPolygon` (`wide_street_buffer_engine.py:332-352`) wraps the accepted
  `mappluto_geometry_arcgis.GeometryAssessment` (imported, never re-implemented) with the same
  independent CRS re-validation.
- `_require_crs` (`wide_street_buffer_engine.py:417-440`) is the single CRS gate used for BOTH
  sides; absence (`None`) or mismatch on either raises the typed `WrongCRSError` naming expected
  vs received (mirrors the accepted M4-T020 `_require_page_crs` / M2-T009
  `require_authoritative_crs` precedent).
- Both accepted connectors' own `EXPECTED_WKID` / `EXPECTED_LATEST_WKID` constants are imported
  and cross-checked equal at import time (`wide_street_buffer_engine.py:157-164`) - proving,
  rather than assuming, the research report's Part 2.3 "same CRS on both sides" finding.
- Reuse: `canonical_to_shapely` (lot geometry rebuild) and the M4-T020 `SegmentPolyline`/
  `GEOMETRY_OK` typed geometry are consumed by import; `analyze_lot_geometry` and
  `parse_segment_geometry_page` are used ONLY in the test suite's fixture builders (also
  read-only reuse, never duplicated parsing logic).

### Item 2 - buffer

- `BUFFER_FT = 100.0` with `BUFFER_FT_CITATION` quoting ZR 23-22 footnote 1 verbatim
  (`wide_street_buffer_engine.py:180-186`).
- `linework.buffer(BUFFER_FT, quad_segs=BUFFER_QUAD_SEGS)` - `BUFFER_QUAD_SEGS = 16`, pinned
  explicitly for determinism. **CORRECTED ON REWORK (G3-F2):** the original submission claimed
  `BUFFER_QUAD_SEGS = 8` "matches shapely's implicit default" - this was FALSE. The buffer call
  actually made here invokes `BaseGeometry.buffer` (a method call on a shapely geometry instance,
  e.g. `linework.buffer(...)`), whose real default is `quad_segs=16`
  (`inspect.signature(shapely.geometry.base.BaseGeometry.buffer)` -> `quad_segs=16`, verified live
  against installed shapely 2.0.7). The `8` the original submission checked belongs to a
  *different*, unused top-level function, `shapely.buffer()`
  (`inspect.signature(shapely.buffer)` -> `quad_segs=8`). Per the rework ruling, the module now
  pins **16** (matching the real default of the API actually called, with no source-derived reason
  to prefer a coarser value) and the in-code comment states the corrected fact plainly, including
  the verified distinction between the two APIs. Buffer only ever runs on the shapely geometry
  rebuilt from the CRS-validated inputs - never in degrees.

### Item 3 - intersection (boolean + sub-geometry/area, per-segment AND aggregate)

- Per segment: `SegmentContribution.intersects` (boolean any-portion) + `.sub_geometry` +
  `.area_sq_ft` (`wide_street_buffer_engine.py:378-386`, populated at
  `wide_street_buffer_engine.py:578-588`).
- Aggregate: `WideStreetBufferResult.aggregate_intersects` / `.aggregate_sub_geometry` /
  `.aggregate_area_sq_ft` / `.aggregate_union_buffer`, computed via
  `unary_union(buffers)` BEFORE intersecting the lot (`wide_street_buffer_engine.py:591-593`) -
  the union-before-intersect design research Part 2.2 Step C/D requires.

### Item 4 - edge cases EC-1..6

- EC-1 (corner/multi-frontage): handled by construction - `unary_union` runs over every
  segment's buffer before the lot intersection; proven by
  `test_corner_lot_union_before_intersect_and_per_segment_visibility`.
- EC-2 (ambiguous/narrow segments excluded, honest under-claim): `EC2_UNDER_CLAIM_NOTICE`
  (`wide_street_buffer_engine.py:214-224`) is present on EVERY result (computed and empty alike);
  proven by `test_ec2_under_claim_notice_always_present`. Full tradeoff discussion in section 3
  below.
- EC-3 (always per-segment): every buffer/intersection is computed once per
  `AttestedWideSegment` - `SegmentContribution` never aggregates across segments before exposing
  its own result; the module never reads a street name.
- EC-4 (exact-tangency, no silent tolerance): `TANGENCY_NOTICE`
  (`wide_street_buffer_engine.py:203-212`) documents the open question; the module imports
  neither `BOUNDARY_TOLERANCE_FT` nor any other mappluto tolerance surface (proven structurally
  by the AST import-name scan in `test_module_never_reimplements_transport_or_reprojection`).
  Full empirical documentation in section 4 below.
- EC-5 (named-street override / alternate-width clause out of scope, no-default attestation):
  `Ec5AttestedPreconditions` is a frozen dataclass with every field required, no defaults -
  `compute_wide_street_buffer_intersection` takes it as a required keyword-only parameter with no
  default, so omission is a `TypeError` at the call site (proven by
  `test_missing_ec5_preconditions_is_a_construction_error` and
  `test_ec5_preconditions_dataclass_has_no_defaults`). **CORRECTED ON REWORK (G3-F1):** the
  original submission additionally claimed the module deliberately does NOT gate computation on
  the attested boolean values - the orchestrator ruled this reading did not satisfy the packet's
  named precedent (Section 10 below, RULING 1) and the module now DOES gate on the value: an
  unattested (`False` on either field) precondition now returns the typed
  `STATUS_PRECONDITIONS_NOT_ATTESTED` refusal, never `STATUS_COMPUTED`, mirroring the accepted
  `dcm_street_width_policy.classify_street_width_policy` -> `DECISION_UNRESOLVED` mechanism
  exactly. See section 10.
- EC-6 (empty segment set, typed honest result): `STATUS_NO_WIDE_SEGMENTS_PROVIDED` with
  `NO_WIDE_SEGMENTS_NOTICE` explicitly stating "NOT a computed False ... and NOT a computed True"
  (`wide_street_buffer_engine.py:190-198`, returned at `wide_street_buffer_engine.py:549-568`);
  proven by `test_empty_wide_segment_set_is_typed_never_a_default`.

### Item 5 - determinism + provenance

- `shapely.__version__` / `shapely.geos_version_string` are asserted against the accepted
  `mappluto_geometry_arcgis.PINNED_SHAPELY_VERSION` ("2.0.7") /
  `PINNED_GEOS_VERSION_STRING` ("3.11.4") at IMPORT TIME
  (`wide_street_buffer_engine.py:616-632`) - stricter than the mappluto module's own
  test-only-assertion precedent, per the packet's explicit "assert ... for determinism" wording;
  also re-captured on every result (`shapely_version`/`geos_version` fields) and re-asserted in
  the test suite (`test_shapely_and_geos_versions_are_pinned_for_determinism`).
- Provenance: `AttestedWideSegment.classification_basis` / `.source_retrieved_at` /
  `.source_raw_digest` and `AttestedLotPolygon.lot_identity` / `.source_retrieved_at` /
  `.source_raw_digest` are all required, no-default fields. **CORRECTED ON REWORK (G4-F1):** the
  original submission claimed ALL of these were "carried through unmodified into the result" -
  this was FALSE for `source_retrieved_at`/`source_raw_digest` specifically. Only
  `classification_basis` (-> `SegmentContribution.classification_basis`) and `lot_identity` (->
  `WideStreetBufferResult.lot_identity`) actually reached an output field in the original
  submission; `source_retrieved_at`/`source_raw_digest` from BOTH attested inputs were silently
  dropped between validation and result construction - no output dataclass carried them at all, so
  a result could not be traced back to the fetch that produced it. This is now fixed: threaded
  onto `SegmentContribution.segment_source_retrieved_at`/`.segment_source_raw_digest` (per
  segment) and `WideStreetBufferResult.lot_source_retrieved_at`/`.lot_source_raw_digest`
  (lot-level), populated in every branch (computed, EC-6 empty, and the new EC-5 refusal). See
  section 10. The 100-ft constant's citation (`BUFFER_FT_CITATION`) is present on every result.

### Item 6 - zero new dependencies; accepted modules read-only; no rule-file edits

- No new import beyond the already-admitted `shapely` (2.0.7, already in `pyproject.toml`);
  `services/api/pyproject.toml` / `requirements.in` / `requirements.txt` are untouched (not in
  `git status`, and are `forbidden_paths`).
- `services/api/app/connectors/dcm_street_centerline_geometry.py`,
  `mappluto_geometry_arcgis.py`, `dcm_street_width_classifier.py`, `dcm_street_width_policy.py`,
  `dcm_street_centerline_arcgis.py`, `mappluto_lot_outline.py` are all consumed by import only -
  `git status --short` confirms none were modified.
- No file under `services/api/app/rules/**` was touched.

## 2. Acceptance scenarios S1-S5

| Scenario | Status | Evidence |
|---|---|---|
| S1 wide_only_buffer_membership | PASS | `test_segment_within_100ft_intersects_true_with_nonempty_area`, `test_segment_beyond_100ft_intersects_false_with_empty_portion`, `test_only_caller_supplied_segments_participate_never_reclassified`, `test_per_segment_identity_is_visible`, plus (rework, provenance) `test_segment_contribution_carries_source_provenance_passthrough`, `test_segment_contribution_carries_explicit_none_provenance_when_genuinely_unavailable`, `test_result_carries_lot_source_provenance_passthrough_when_computed`, plus (rework, G3-F2 end-cap) `test_end_cap_proximate_intersection_is_exclusively_from_the_rounded_cap`, `test_end_cap_proximate_intersection_is_sensitive_to_quad_segs_resolution` |
| S2 crs_and_input_fail_closed | PASS | `test_missing_lot_crs_is_typed_wrong_crs`, `test_mismatched_lot_crs_is_typed_wrong_crs`, `test_missing_segment_crs_is_typed_wrong_crs`, `test_mismatched_segment_crs_is_typed_wrong_crs`, `test_crs_gate_runs_before_geometry_is_ever_interpreted`, `test_invalid_lot_geometry_is_typed_invalid_geometry`, `test_invalid_segment_geometry_is_typed_invalid_geometry`, `test_ec5_preconditions_dataclass_has_no_defaults`, `test_attested_wide_segment_dataclass_has_no_defaults`, `test_attested_lot_polygon_dataclass_has_no_defaults`, `test_missing_ec5_preconditions_is_a_construction_error`, `test_malformed_ec5_preconditions_type_is_typed_error`, `test_malformed_ec5_preconditions_non_bool_field_is_typed_error`, plus `test_module_never_reimplements_transport_or_reprojection` (AST import-allowlist + forbidden-name scan proving no reprojection path exists); plus (rework, G3-F1 value gate) `test_ec5_affirmative_attestation_computes_normally`, `test_ec5_named_street_override_not_checked_is_typed_refusal`, `test_ec5_alternate_width_clause_not_checked_is_typed_refusal`, `test_ec5_both_unchecked_is_typed_refusal_naming_both_reasons`, `test_ec5_gate_refuses_even_with_an_empty_wide_segment_set` |
| S3 portions_split_corner_lot | PASS | `test_corner_lot_union_before_intersect_and_per_segment_visibility` (aggregate 17500 sq ft, strictly between per-segment 10000 and naive-sum 20000, strictly between 0 and lot area 40000), `test_non_wide_frontage_never_included_by_construction` |
| S4 tangency_and_empty_honesty | PASS | `test_exact_tangency_is_the_unmodified_geos_predicate_result`, `test_empty_wide_segment_set_is_typed_never_a_default`, `test_ec2_under_claim_notice_always_present`; plus (rework, provenance) `test_result_carries_lot_source_provenance_passthrough_when_empty_wide_segments`, `test_result_carries_lot_source_provenance_passthrough_when_preconditions_not_attested`. **REWORK NOTE:** `test_ec5_preconditions_pass_through_unmodified_regardless_of_value` (originally listed here) was RETIRED and replaced by the 5 EC-5 value-gate tests now listed under S2 above - it pinned the no-gate reading G3-F1/RULING 1 overturned. |
| S5 scope_regression_determinism | PASS | see section 6 below (verbatim command outputs) |

## 3. EC-2 honest under-claim tradeoff (required section)

This module's ONLY input for street width is what the caller already decided via the accepted
M4-T015 classifier / M4-T019 policy chain: a segment reaches this module only if it was already
resolved to `effective_disposition == "wide"`. Every DCM segment the classifier left in one of
its ambiguity classes (`range_straddles_cutoff`, `approximate_or_hedged_value_ambiguous`,
`width_irregular`, and the other ~20 documented classes) never reaches this module at all - it is
not passed in `wide_segments`, and this module has no way to know it was ever excluded.

Consequence: a real-world lot that sits within 100 ft of a street whose DCM `Streetwidth` reading
was genuinely a wide street (>=75 ft) but recorded in a messy/ambiguous form will be scored by
this module's result as `intersects=False` (or simply never contribute to the aggregate) for that
segment - NOT because the geometry says "not within 100 ft," but because the segment was never
offered as a candidate. This is conservative/fail-closed (consistent with the project's posture
throughout M4-T015/M4-T019/D-052), and it is an HONEST under-claim, not a defect: the module never
claims a portion is outside 100 ft of a wide street when it actually computed that answer - it
simply was never asked about the excluded segment.

Every `WideStreetBufferResult` (computed AND empty) carries `EC2_UNDER_CLAIM_NOTICE` verbatim so a
downstream consumer (eventually B7's rule wiring) cannot silently forget this scope boundary. This
mirrors the M4-T013 report's own tradeoff-section discipline the packet asked to be repeated here.

## 4. EC-4 open tolerance question (required section, documented not resolved)

Empirically verified (standalone shapely probe, run BEFORE writing any test assertion, output
recorded verbatim below) with shapely 2.0.7 / GEOS 3.11.4:

```
lot = Polygon([(0,0),(0,200),(200,200),(200,0),(0,0)])   # area 40000.0
line = LineString([(-100,-1000),(-100,1000)]).buffer(100.0, quad_segs=16)  # boundary lands at x=0.0 exactly
lot.intersects(line-buffer)          -> True   (boundary touch is not disjoint)
lot.intersection(line-buffer)        -> LineString, area 0.0   (measure-zero touch, geometrically exact)
```

(REWORK NOTE: re-verified with `quad_segs=16` - the corrected pinned value - on rework; identical
result to the original `quad_segs=8` probe, because this fixture's endpoints are far from the lot
(long y-range) so only the buffer's straight sides are exercised here, never the rounded end caps
the `quad_segs` correction actually affects. See section 10, F2, for the fixture that does exercise
the end-cap path.)

So at EXACT 100.0-ft tangency, this module's unmodified GEOS predicate returns `intersects=True`
with a zero-area (`LineString`) intersection - i.e. the ZR footnote-1 "within 100 feet" boolean
test currently reads TRUE at exact tangency, contributing ZERO measurable area to any future
apportionment. This is GEOS's literal, deterministic behavior for a straight-buffer boundary
coinciding exactly with a straight lot edge (both this and the 40000/10000/17500 sq-ft figures
used across the test suite were independently confirmed in the standalone probe before any test
assertion was written - not derived by calling the module under test).

`mappluto_geometry_arcgis.BOUNDARY_TOLERANCE_FT` (20.0 ft) is NEVER imported or referenced by this
module - it is the MapPLUTO source's own +/-20-ft POSITIONAL/SURVEY-ACCURACY disclosure, not a
legal buffer-boundary allowance, and reusing it here would silently invent a legal tolerance no
official source states. Whether the ZR intends any tolerance at exact 100-ft tangency (e.g.
whether "within 100 feet" should read as `<= 100` producing a zero-area technical TRUE, as this
module currently computes, or whether some other convention applies) is an OPEN, UNRESOLVED legal
question left explicitly to G6 qualified-reviewer review - this module documents the fact
(`TANGENCY_NOTICE`, carried on every result) and does not resolve it.

## 5. EC-5 attestation design decision (SUPERSEDED ON REWORK - see section 10 RULING 1)

**This section is preserved verbatim from the original submission for the record. It describes
the design as it shipped in the ORIGINAL submission - the no-gate reading. The orchestrator ruled
this reading did not satisfy the packet's contract (G3-F1, RULING 1 in
`project-control/reports/M4-T021-rework-ruling.md`), and the module has been reworked to GATE on
the attested values instead. See section 10 below for the corrected design and its evidence.**

The packet requires a typed, no-default `Ec5AttestedPreconditions` input so a caller "cannot
silently skip" the named-street-override / C5-3/C6-4/C6-6 alternate-width scope gap. The original
submission implemented the no-default TYPE requirement (construction fails with `TypeError` on
omission, `MalformedAttestationError` on a wrong-shaped/wrong-typed value) but deliberately did NOT
gate `compute_wide_street_buffer_intersection`'s computation on the attested boolean VALUES (i.e. a
caller could construct `Ec5AttestedPreconditions(named_street_override_checked=False, ...)` and the
module still computed a result). Rationale, per the pinned research report Part 4.3 item 2's own
dependency note: "B4 can proceed today using the classifier's already-accepted conservative
disposition; B5 only changes which segments cross into `wide` at the margin" - i.e. B4 is
explicitly NOT blocked on B5/B6/B7. This disclosed judgment call was exactly what triggered the
reviewer disagreement (G3 read the packet's NAMED precedent's actual mechanism and found it a
genuine value-gate; G4 read the packet's prose and judged non-omission sufficient) that the
orchestrator's rework ruling resolved in G3's favor - see section 10. The producer's disclosure
of this as an open judgment call (rather than silently picking one reading) was specifically
called out as good process discipline by both the ruling and the G3 report; only the substance of
the reading was overturned, not the disclosure practice.

## 6. Self-checks (verbatim command outputs)

**Original-submission outputs (29/781 tests, 632/662 lines) are superseded below by the rework
re-run (40/792 tests, 754/947 lines) - see section 10 for the full rework self-check record,
which is the authoritative, current evidence.** Original outputs are left below for the historical
record only.

Command 1 (ORIGINAL): `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q`

```
.............................                                            [100%]
29 passed in 0.29s
```

Command 2 (ORIGINAL): `python -m pytest services/api/tests/connectors -q`

```
781 passed in 2.87s
```

(781 = the previously-accepted 752 + this task's original 29 new tests.)

Command 3 (ORIGINAL): `cd services/api && python -m ruff check .`

```
All checks passed!
```

Command 4 (ORIGINAL): `python tools/modularity_check.py --check`

```
selected 405 files; failures 0; warnings 17
```

(0 failures; neither new file appeared in the warning list at the original 632/662 line count.
REWORK NOTE: after the rework's required additions, `wide_street_buffer_engine.py` (754 lines)
now DOES appear in the warning list - see section 10's self-check re-run for the exact line and
the honest disclosure.)

Command 5 (ORIGINAL scope check): `git diff --stat` at the original submission:

```
 .../app/connectors/wide_street_buffer_engine.py    | 633 +++++++++++++++++++-
 .../connectors/test_wide_street_buffer_engine.py   | 663 ++++++++++++++++++++-
 2 files changed, 1294 insertions(+), 2 deletions(-)
```

Exactly the 2 code files in `allowed_paths` were modified (both started as 1-line placeholders,
replaced in full); no accepted connector, rule file, pyproject/requirements file, or any other
path was touched. This report file itself is the 3rd `allowed_paths` file.

## 7. Determinism/environment evidence

```
shapely 2.0.7
geos_version_string 3.11.4
```

Matches `services/api/pyproject.toml`'s `shapely==2.0.7` pin (comment at pyproject.toml:27-30:
"The test suite asserts shapely.__version__ and shapely.geos_version_string") and the accepted
`mappluto_geometry_arcgis.PINNED_SHAPELY_VERSION` / `PINNED_GEOS_VERSION_STRING` constants
exactly.

## 8. Directive requirement evidence

- **D-045-R002** (A2 geometry-dependent mechanics; each mechanic ships with the data inputs it
  needs; unavailable input stays an honest "no supported estimate," never a manufactured number):
  satisfied structurally - `AttestedWideSegment`/`AttestedLotPolygon` require their own CRS
  identity (no manufactured geometry), EC-6 returns the typed
  `STATUS_NO_WIDE_SEGMENTS_PROVIDED` rather than a default True/False, and every typed error
  (`WrongCRSError`/`InvalidGeometryError`/`MalformedAttestationError`) refuses rather than
  computing. This module reproduces the documented ZR example (footnote-1 verbatim quote,
  `BUFFER_FT_CITATION`) and the missing-input branch is exercised by 7+ tests in section 2's S2
  row.
- **D-045-R008** (sequencing - one reviewed family/mechanic at a time under normal G0-G7 gates,
  never a monolithic task): this task is exactly the bounded B4 mechanic the research report's
  Part 4.3 decomposition names, citing `D-045:D-045-R002/R008/R009` as instructed; it does not
  touch B3 (accepted M4-T020), B5/B6 (not-yet-built), or B7 (rule wiring, explicitly out of
  scope and not attempted here - no file under `services/api/app/rules/**` is touched).
- **D-045-R009** (preservation/scope limit - no compliance declarations, dependency policy §G
  unaffected since zero new dependencies, expansion hold/PR #241/D-043 posture unaffected):
  this task adds zero new dependencies (verified: `pyproject.toml`/`requirements.in`/
  `requirements.txt` untouched), makes no legal compliance declaration (every result is a
  geometry FACT feeding a rule that remains DRAFT/needs-review until G6 - stated explicitly in
  the module docstring's closing paragraph), and does not touch any file outside its 3
  `allowed_paths`.
- **D-046-R001/R002** (parallel production scale-up; disjointness mandatory): this task's
  `allowed_paths` (2 new files + this report) are disjoint by construction from every other
  in-flight D-045 task's `allowed_paths` (all forbidden paths list every accepted connector this
  task reads, and this task writes to none of them) - satisfied as the sole writing producer on
  this scope per the task's own `path_notes`.

## 9. Limitations and honest disclosure

**REWORK UPDATE:** the two bullets below marked SUPERSEDED described defects that the rework
(section 10) fixed; they are kept for the historical record with a correction note rather than
deleted.

- SUPERSEDED ON REWORK: ~~The EC-5 "does not gate on attested values" design decision (section 5)
  is a defensible but not the ONLY possible reading of the packet text.~~ The orchestrator ruled
  this reading incorrect (RULING 1); the module now gates on the attested values. See section 10.
- This module has no integration test against the LIVE accepted M4-T020/M2-T009 connectors' real
  fetch paths - it is deliberately fully offline per the packet's own instruction ("Keep test
  expectations literal/hand-derived... tests must be fully offline"). Live-data integration
  (wiring a real DCM+MapPLUTO query into this engine) is B7's job, not this task's.
  - the geometry-fixture ring-orientation convention (esri clockwise = exterior) and the
  DCM synthetic-page CRS/geometry shape were both independently confirmed via standalone
  `python` probes against the ACCEPTED connectors (not this module) before being relied on in
  test fixtures - recorded in sections 4 and 6 of this report as the verification trail.
- SUPERSEDED ON REWORK: ~~`quad_segs=8` matches shapely/GEOS's own long-standing default~~ - this
  was FALSE (G3-F2); the real default of the API actually called is 16, and the constant is now
  pinned to 16. An end-cap-proximate test now exists
  (`test_end_cap_proximate_intersection_is_exclusively_from_the_rounded_cap`,
  `test_end_cap_proximate_intersection_is_sensitive_to_quad_segs_resolution`) exercising exactly
  the rounded-cap path the original suite left completely untested. See section 10.
- No attempt was made to handle multi-polygon lots with holes in a dedicated test (the accepted
  `canonical_to_shapely` already supports `MultiPolygon`/holes generically and this module makes
  no assumption about polygon vs multipolygon - `lot_geometry.intersects`/`.intersection` are
  shapely operations that work identically on either - but a dedicated multipolygon-lot fixture
  was not built here; flagged as an untested-but-structurally-supported case; carried forward from
  the original submission as G3 A3 / G4 NB-1, both reviewers judged this non-blocking).
- NEW (rework, honest disclosure): the rework's required additions (the EC-5 value gate, its 5
  tests; the provenance passthrough fields, their 5 tests; the end-cap fixture, its 2 tests; and
  the corrected documentation) grew `wide_street_buffer_engine.py` from 632 to 754 lines, crossing
  `tools/modularity_check.py`'s advisory warning threshold (`review_signal` - "above the warning
  threshold; consider the module boundary before growing it further"). This is a WARNING, not a
  FAILURE (`--check` still exits 0; `failures 0` both before and after) and every added line was
  required by one of the three blocking findings, not discretionary growth - disclosed here per
  CLAUDE.md's modularity discipline rather than left silent. No module split was attempted for
  this rework given the corrections are all within this single module's existing responsibility
  (typed inputs/CRS/buffer/intersection/provenance for one geometry computation); a future
  contributor extending this module further should weigh that warning before adding more.

## 10. Rework record (all 3 findings, G3-F1 / G3-F2 / G4-F1)

Ruling: `project-control/reports/M4-T021-rework-ruling.md`. Both original gate reports:
`project-control/reports/M4-T021-G3-code-review.md`, `project-control/reports/M4-T021-G4-test-adequacy.md`.

### F1 (G3-F1, blocking) - EC-5 must GATE on attested values

**Before:** `_validate_ec5_preconditions` checked only type/shape (presence); the attested boolean
VALUES were never inspected anywhere in `compute_wide_street_buffer_intersection` - a caller
passing `(False, False, "not yet checked")` received a full `STATUS_COMPUTED` result
indistinguishable in shape from a properly-attested one.

**After:**
- New helper `_ec5_precondition_failures` (`wide_street_buffer_engine.py:523-543`) mirrors
  `dcm_street_width_policy._precondition_failures` exactly: returns a tuple of human-readable
  reasons, empty only when both `named_street_override_checked` and
  `alternate_width_clause_checked` are `True`.
- New status constant `STATUS_PRECONDITIONS_NOT_ATTESTED = "preconditions_not_attested"`
  (`wide_street_buffer_engine.py:220`), in `__all__`.
- New result field `WideStreetBufferResult.ec5_not_attested_notice: str | None`
  (`wide_street_buffer_engine.py:465`, populated only on this status).
- The gate itself (`wide_street_buffer_engine.py:628-661`) runs AFTER the lot's CRS/geometry
  validation (so lot-level facts including provenance are known) but BEFORE the EC-6 empty check
  and BEFORE any segment is touched - when `ec5_failures` is non-empty, the function returns
  `STATUS_PRECONDITIONS_NOT_ATTESTED` immediately with `segment_contributions=()` and every
  `aggregate_*` field `None`, `ec5_preconditions` still carried through unmodified for audit.
  Affirmative attestation (both `True`) proceeds exactly as before - unchanged code path,
  unchanged existing-test behavior.
- Docstring (module-level EC-5 paragraph and the function's "Order of operations" paragraph)
  corrected to describe the gate.

**Proof (tests, all new):**
`test_ec5_affirmative_attestation_computes_normally` (both `True` -> `STATUS_COMPUTED`, unchanged
behavior), `test_ec5_named_street_override_not_checked_is_typed_refusal` (`(False, True)` ->
refusal naming only that field), `test_ec5_alternate_width_clause_not_checked_is_typed_refusal`
(`(True, False)` -> refusal naming only that field),
`test_ec5_both_unchecked_is_typed_refusal_naming_both_reasons` (`(False, False)` -> refusal naming
BOTH reasons), `test_ec5_gate_refuses_even_with_an_empty_wide_segment_set` (proves gate ordering:
EC-5 refusal wins over EC-6 empty-set status when both apply). Replaces the retired
`test_ec5_preconditions_pass_through_unmodified_regardless_of_value`, which pinned the overturned
no-gate reading.

### F2 (G3-F2, blocking) - quad_segs factual correction + end-cap test

**Before:** `BUFFER_QUAD_SEGS = 8` with a comment claiming it "also" matches shapely's implicit
default - FALSE for the API actually called (`BaseGeometry.buffer`, default 16; the `8` belongs to
the different, unused top-level `shapely.buffer()`). Verified live in this rework:
`inspect.signature(shapely.geometry.base.BaseGeometry.buffer)` -> `quad_segs=16`;
`inspect.signature(shapely.buffer)` -> `quad_segs=8`. Zero fixtures exercised the rounded end-cap
path (every fixture kept segment endpoints far from the lot via long y-ranges).

**After:**
- `BUFFER_QUAD_SEGS = 16` (`wide_street_buffer_engine.py:213`), comment corrected
  (`wide_street_buffer_engine.py:199-212`) to state plainly that it is set explicitly for
  determinism and matches the real default of the method actually called, with the verified
  distinction from the different top-level function's default of 8.
- Module docstring (BUFFER paragraph, `wide_street_buffer_engine.py:36-44`) corrected to match.
- New end-cap-proximate fixture (`test_wide_street_buffer_engine.py`, section preceding S2):
  a short segment whose near endpoint sits at `(248.0, -64.0)`, exactly 80.0 ft from the lot's SE
  corner `(200, 0)` (a hand-verified 48-64-80 right triangle: `48**2 + 64**2 == 80**2`), extending
  away from the lot toward `(900.0, -424.0)` so the buffer's STRAIGHT sides never reach the lot
  (independently confirmed with a flat-cap probe: `cap_style="flat"` -> `intersects=False`,
  `area=0.0`) - every bit of the intersection is therefore attributable exclusively to the rounded
  end cap.
- Expected values are HAND-DERIVED via an independent, standalone shapely computation (never via
  the module under test), mirroring this suite's own pre-existing, already-reviewed methodology
  (`test_line_probe_matches_the_hand_derived_expected_values`): with `quad_segs=16`, area =
  `382.9260890749891` sq ft; with the former (incorrect) `quad_segs=8`, area =
  `373.6219486597519` sq ft - a genuine, non-cosmetic ~9.3 sq ft difference on identical geometry,
  proving this fixture actually exercises the quad_segs-sensitive code path (computed live in this
  rework via `python -c` probes, recorded above).
- `test_line_probe_matches_the_hand_derived_expected_values` updated to call
  `.buffer(100.0, quad_segs=BUFFER_QUAD_SEGS)` (was hardcoded `quad_segs=8`) for parity with the
  corrected pinned constant; its docstring now explains why none of ITS THREE existing fixture
  values actually change between 8 and 16 (all three deliberately keep segment endpoints far from
  the lot).

**Expected-value changes caused by the 8->16 switch:** NONE of the pre-existing S1-S4 fixture
values changed (`10000.0`, `0.0` empty, `17500.0`, `40000.0`, tangency `0.0`) - independently
re-verified live: every pre-existing fixture's segment endpoints are far outside the lot's
y-range (`-1000`/`1000`), so only the buffer's straight sides are ever exercised, and those are
exact regardless of `quad_segs`. Only the NEW end-cap fixture's values are quad_segs-sensitive, and
those are the two literal values above, hand-derived independently as described.

**Proof (tests, both new):**
`test_end_cap_proximate_intersection_is_exclusively_from_the_rounded_cap` (pins the module's own
computed result against the independently-derived `382.9260890749891` sq ft, plus the flat-cap
proof that the straight sides alone never touch),
`test_end_cap_proximate_intersection_is_sensitive_to_quad_segs_resolution` (standalone,
independent-of-the-module confirmation that 8 vs 16 genuinely diverge on this exact geometry).

### F1 (G4-F1, blocking) - provenance passthrough onto outputs

**Before:** `source_retrieved_at`/`source_raw_digest` were required no-default fields on BOTH
`AttestedWideSegment` and `AttestedLotPolygon` but reached NO output dataclass - silently dropped
between validation and result construction. No test could have caught this (no assertable output
surface existed).

**After (remedy (a), per the ruling - threaded through, not disclosed away):**
- `SegmentContribution` gains `segment_source_retrieved_at: str | None` /
  `segment_source_raw_digest: str | None` (`wide_street_buffer_engine.py:410-411`), populated from
  the originating `AttestedWideSegment` inside the per-segment loop
  (`wide_street_buffer_engine.py:698-709`, the `SegmentContribution(...)` construction site).
- `WideStreetBufferResult` gains `lot_source_retrieved_at: str | None` /
  `lot_source_raw_digest: str | None` (`wide_street_buffer_engine.py:461-462`), populated from the
  `AttestedLotPolygon` in ALL THREE branches: `STATUS_COMPUTED`
  (`wide_street_buffer_engine.py:714` construction), `STATUS_NO_WIDE_SEGMENTS_PROVIDED`
  (`wide_street_buffer_engine.py:664` construction), and the new
  `STATUS_PRECONDITIONS_NOT_ATTESTED` (`wide_street_buffer_engine.py:640` construction) - a
  refusal result still carries the lot's provenance since the lot was validated before either gate.
- Dataclass docstrings updated to describe the new fields and their per-branch guarantees.

**Proof (tests, 5 new):**
`test_segment_contribution_carries_source_provenance_passthrough` (exact passthrough, compared
against the INPUT fixture's own field - not re-derived, not tautological),
`test_segment_contribution_carries_explicit_none_provenance_when_genuinely_unavailable` (explicit
`None` is preserved, not coerced), `test_result_carries_lot_source_provenance_passthrough_when_computed`,
`test_result_carries_lot_source_provenance_passthrough_when_empty_wide_segments`,
`test_result_carries_lot_source_provenance_passthrough_when_preconditions_not_attested` (all three
branches independently proven).

### Rework self-checks (verbatim, current/authoritative - run from repo root unless noted)

Command 1: `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q`

```
........................................                                 [100%]
40 passed in 1.00s
```

(40 = 29 original - 1 retired (`test_ec5_preconditions_pass_through_unmodified_regardless_of_value`)
+ 12 new (5 EC-5 gate tests + 5 provenance tests + 2 end-cap tests) = 40. Exact reconciliation:
`grep -c '^def test_' services/api/tests/connectors/test_wide_street_buffer_engine.py` -> `40`,
matching both the pytest collection count and this arithmetic exactly.)

Command 2: `python -m pytest services/api/tests/connectors -q`

```
792 passed in 5.59s
```

(792 = the previously-accepted 752 + this task's current 40 tests; the pre-existing suite stayed
green with no modification to any accepted file - confirmed by `git status`/`git diff --stat`
below showing exactly the 2 allowed-path code files touched.)

Command 3: `cd services/api && python -m ruff check .` (then `cd` back to repo root - Bash cwd
persists across calls)

```
All checks passed!
```

Command 4: `python tools/modularity_check.py --check` (run from repo root)

```
selected 405 files; failures 0; warnings 18
  warn review_signal: services/api/app/connectors/wide_street_buffer_engine.py - above the warning threshold; consider the module boundary before growing it further
```

(0 failures - PASS. One NEW warning vs. the original submission's 17: `wide_street_buffer_engine.py`
now crosses the advisory review-signal line-count threshold at 754 lines (was 632, comfortably
under). This is a warning, not a failure, and is disclosed honestly in section 9 above - every
added line was required by one of the three blocking findings.)

Command 5 (scope check): `git status --short` / `git diff --stat` against the rework base
(`f8ada299`, the pinned contract head):

```
 M services/api/app/connectors/wide_street_buffer_engine.py
 M services/api/tests/connectors/test_wide_street_buffer_engine.py
 .../app/connectors/wide_street_buffer_engine.py    | 190 ++++++++++---
 .../connectors/test_wide_street_buffer_engine.py   | 305 ++++++++++++++++++++-
 2 files changed, 451 insertions(+), 44 deletions(-)
```

Exactly the 2 `allowed_paths` code files are modified; this report is the 3rd, committed in the
same commit. No accepted connector, rule file, or any other path touched.
