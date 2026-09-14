# M4-T021 producer report - B4 wide-street 100-ft buffer/intersection engine

Producer: backend-engineer. Base: `d7c22f3e` ("D-060 captured"). Scope: exactly the 3
`allowed_paths` files:

- `services/api/app/connectors/wide_street_buffer_engine.py` (NEW production module, 632 lines)
- `services/api/tests/connectors/test_wide_street_buffer_engine.py` (NEW test suite, 662 lines,
  29 tests)
- `project-control/reports/M4-T021-producer-report.md` (this file)

No accepted connector, rule file, or any other path was touched (`git status --short` before
writing this report showed only the two files above as modified/untracked; verified again below
under S5).

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
- `linework.buffer(BUFFER_FT, quad_segs=BUFFER_QUAD_SEGS)` (`wide_street_buffer_engine.py:576`) -
  `BUFFER_QUAD_SEGS = 8` pinned explicitly rather than left to shapely's implicit default.
  Buffer only ever runs on the shapely geometry rebuilt from the CRS-validated inputs - never in
  degrees.

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
  `Ec5AttestedPreconditions` (`wide_street_buffer_engine.py:266-289`) is a frozen dataclass with
  every field required, no defaults - `compute_wide_street_buffer_intersection` takes it as a
  required keyword-only parameter with no default, so omission is a `TypeError` at the call site
  (proven by `test_missing_ec5_preconditions_is_a_construction_error` and
  `test_ec5_preconditions_dataclass_has_no_defaults`). The module does NOT gate computation on
  the attested boolean values (design decision explained in section 5).
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
- Provenance: `AttestedWideSegment.classification_basis` /
  `.source_retrieved_at` / `.source_raw_digest` and `AttestedLotPolygon.lot_identity` /
  `.source_retrieved_at` / `.source_raw_digest` are all required, no-default fields carried
  through unmodified into the result (`SegmentContribution.classification_basis`,
  `WideStreetBufferResult.lot_identity`). The 100-ft constant's citation
  (`BUFFER_FT_CITATION`) is present on every result.

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
| S1 wide_only_buffer_membership | PASS | `test_segment_within_100ft_intersects_true_with_nonempty_area`, `test_segment_beyond_100ft_intersects_false_with_empty_portion`, `test_only_caller_supplied_segments_participate_never_reclassified`, `test_per_segment_identity_is_visible` |
| S2 crs_and_input_fail_closed | PASS | `test_missing_lot_crs_is_typed_wrong_crs`, `test_mismatched_lot_crs_is_typed_wrong_crs`, `test_missing_segment_crs_is_typed_wrong_crs`, `test_mismatched_segment_crs_is_typed_wrong_crs`, `test_crs_gate_runs_before_geometry_is_ever_interpreted`, `test_invalid_lot_geometry_is_typed_invalid_geometry`, `test_invalid_segment_geometry_is_typed_invalid_geometry`, `test_ec5_preconditions_dataclass_has_no_defaults`, `test_attested_wide_segment_dataclass_has_no_defaults`, `test_attested_lot_polygon_dataclass_has_no_defaults`, `test_missing_ec5_preconditions_is_a_construction_error`, `test_malformed_ec5_preconditions_type_is_typed_error`, `test_malformed_ec5_preconditions_non_bool_field_is_typed_error`, plus `test_module_never_reimplements_transport_or_reprojection` (AST import-allowlist + forbidden-name scan proving no reprojection path exists) |
| S3 portions_split_corner_lot | PASS | `test_corner_lot_union_before_intersect_and_per_segment_visibility` (aggregate 17500 sq ft, strictly between per-segment 10000 and naive-sum 20000, strictly between 0 and lot area 40000), `test_non_wide_frontage_never_included_by_construction` |
| S4 tangency_and_empty_honesty | PASS | `test_exact_tangency_is_the_unmodified_geos_predicate_result`, `test_empty_wide_segment_set_is_typed_never_a_default`, `test_ec2_under_claim_notice_always_present`, `test_ec5_preconditions_pass_through_unmodified_regardless_of_value` |
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
line = LineString([(-100,-1000),(-100,1000)]).buffer(100.0, quad_segs=8)  # boundary lands at x=0.0 exactly
lot.intersects(line-buffer)          -> True   (boundary touch is not disjoint)
lot.intersection(line-buffer)        -> LineString, area 0.0   (measure-zero touch, geometrically exact)
```

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

## 5. EC-5 attestation design decision (not a defect - documented here)

The packet requires a typed, no-default `Ec5AttestedPreconditions` input so a caller "cannot
silently skip" the named-street-override / C5-3/C6-4/C6-6 alternate-width scope gap. This module
implements the no-default TYPE requirement (construction fails with `TypeError` on omission,
`MalformedAttestationError` on a wrong-shaped/wrong-typed value) but deliberately does NOT gate
`compute_wide_street_buffer_intersection`'s computation on the attested boolean VALUES (i.e. a
caller may construct `Ec5AttestedPreconditions(named_street_override_checked=False, ...)` and the
module still computes a result). Rationale, per the pinned research report Part 4.3 item 2's own
dependency note: "B4 can proceed today using the classifier's already-accepted conservative
disposition; B5 only changes which segments cross into `wide` at the margin" - i.e. B4 is
explicitly NOT blocked on B5/B6/B7. Gating computation on the EC-5 attestation would make this
module unusable until the (separately-scoped, not-yet-built) named-street-override table exists,
which the research report's own decomposition says should not happen. The attestation is still
carried through unmodified on every result (`WideStreetBufferResult.ec5_preconditions`) for
downstream audit, and its omission at the call site is a hard construction-time `TypeError` -
proven by `test_ec5_preconditions_pass_through_unmodified_regardless_of_value` (computes
successfully with both attestations False) and
`test_missing_ec5_preconditions_is_a_construction_error` (fails closed on omission). This
interpretation is disclosed here explicitly as a design choice open to reviewer disagreement, not
asserted as the only possible reading of the packet's EC-5 language.

## 6. Self-checks (verbatim command outputs)

Command 1: `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q`
(run from repo root, `services/api` on path via pytest config)

```
.............................                                            [100%]
29 passed in 0.29s
```

Command 2: `python -m pytest services/api/tests/connectors -q`

```
........................................................................ [  9%]
........................................................................ [ 18%]
........................................................................ [ 27%]
........................................................................ [ 36%]
........................................................................ [ 46%]
........................................................................ [ 55%]
........................................................................ [ 64%]
........................................................................ [ 73%]
........................................................................ [ 82%]
........................................................................ [ 92%]
.............................................................            [100%]
781 passed in 2.87s
```

(781 = the previously-accepted 752 + this task's 29 new tests; the pre-existing suite stayed
green with no modification to any accepted file.)

Command 3: `cd services/api && python -m ruff check .` (then `cd` back to repo root - Bash cwd
persists across calls)

```
All checks passed!
```

(First run surfaced 3 findings - two `I001` import-sort/format issues auto-fixed with
`ruff check --fix` on the two new files only, and one `B017` blind-exception assert in a test,
fixed by narrowing to `dataclasses.FrozenInstanceError`. Re-run above is clean.)

Command 4: `python tools/modularity_check.py --check` (run from repo root)

```
selected 405 files; failures 0; warnings 17
```

(0 failures; the 17 pre-existing warnings are all in other files - `dcm_street_centerline_arcgis.py`,
`scenario_analysis.py`, `breakeven.py`, several `tools/agent_supervisor/*` files, `types.ts`,
`context_benchmark.py` - none are the 2 files this task adds. Neither new file appears in the
warning list; both sit comfortably under the 600-line warning threshold at 632/662 raw lines
including docstrings, well under the 750-line justification and 1000-line hard thresholds.)

Command 5 (scope check): `git status --short` and `git diff --stat` at time of writing this
section, before the report commit:

```
 M services/api/app/connectors/wide_street_buffer_engine.py
 M services/api/tests/connectors/test_wide_street_buffer_engine.py
 .../app/connectors/wide_street_buffer_engine.py    | 633 +++++++++++++++++++-
 .../connectors/test_wide_street_buffer_engine.py   | 663 ++++++++++++++++++++-
 2 files changed, 1294 insertions(+), 2 deletions(-)
```

Exactly the 2 code files in `allowed_paths` are modified (both started as 1-line placeholders,
replaced in full); no accepted connector, rule file, pyproject/requirements file, or any other
path was touched. This report file itself is the 3rd `allowed_paths` file, added in the same
commit.

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

- The EC-5 "does not gate on attested values" design decision (section 5) is a defensible but
  not the ONLY possible reading of the packet text; flagged explicitly for reviewer judgment
  rather than asserted as settled.
- This module has no integration test against the LIVE accepted M4-T020/M2-T009 connectors' real
  fetch paths - it is deliberately fully offline per the packet's own instruction ("Keep test
  expectations literal/hand-derived... tests must be fully offline"). Live-data integration
  (wiring a real DCM+MapPLUTO query into this engine) is B7's job, not this task's.
  - the geometry-fixture ring-orientation convention (esri clockwise = exterior) and the
  DCM synthetic-page CRS/geometry shape were both independently confirmed via standalone
  `python` probes against the ACCEPTED connectors (not this module) before being relied on in
  test fixtures - recorded in sections 4 and 6 of this report as the verification trail.
- `quad_segs=8` (the buffer arc-approximation resolution) is pinned explicitly but its numeric
  choice (vs. a higher resolution) is not itself independently re-derived from an official
  source - it matches shapely/GEOS's own long-standing default, chosen for determinism
  continuity rather than any legal precision requirement (buffer boundaries away from a
  segment's endpoints are exact straight offsets regardless of `quad_segs`; only the rounded
  end-caps at each polyline terminus are approximated by this parameter, and no test in this
  suite currently exercises an end-cap-proximate scenario).
- No attempt was made to handle multi-polygon lots with holes in a dedicated test (the accepted
  `canonical_to_shapely` already supports `MultiPolygon`/holes generically and this module makes
  no assumption about polygon vs multipolygon - `lot_geometry.intersects`/`.intersection` are
  shapely operations that work identically on either - but a dedicated multipolygon-lot fixture
  was not built here; flagged as an untested-but-structurally-supported case).
