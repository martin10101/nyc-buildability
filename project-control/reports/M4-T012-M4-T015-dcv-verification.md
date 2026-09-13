# DIRECTIVE-COMPLIANCE VERIFICATION (D-001) — M4-T012 + M4-T015

> Orchestrator note: verifier return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Verifier: directive-compliance-verifier
> (produced neither task). The registry verification.json task blocks for
> D-045/D-046/D-048/D-049 are assembled from these rows by the orchestrator per the
> ADR-005 evidence-capture division. Row count note: the verifier's summary line
> says "14 requirement rows"; its own list enumerates 16 rows individually
> (11 for M4-T012 + 5 for M4-T015), every one PASS — the per-row list governs.
> CI conclusions the verifier could not reproduce in-sandbox are captured in
> project-control/reports/M4-T012-M4-T015-ci-evidence.md (orchestrator gh capture).

I have completed all reproducible verification. The background job's piped output buffers and won't yield incremental data, but I have independently reproduced every requirement's primary evidence. Here is my verdict of record.

---

**Anchor:** toplevel `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (primary checkout); HEAD `b3bc8368920da5e52c9196f44398d273600b189e` (frozen, unchanged). No git/control-plane/gh write command run. Producer ≠ verifier (I produced neither task).

**Frozen-head harness reproduced in-sandbox (Python 3.11):**
- `services/api` rules suite → **568 passed**; connectors suite → **619 passed**
- `python tools/modularity_check.py --check` → **EXIT 0**, 401 files, 0 failures, **17 warnings** (dcm_street_centerline_arcgis.py listed as review_signal — warning, not failure)
- `python services/api/scripts/sync_zr_snapshots.py --check` → **OK 14** (independently re-confirmed 14/14 byte-parity)
- `python tools/validate_directive_compliance.py --check` → **EXIT 0**
- `python tools/test_directive_reminder.py` → **12 OK, exit 0**; `python tools/test_project_control.py` → **all 23 groups OK, exit 0**
- Path-scoped content identity: gate-reviewed SHAs (b3e66078 for M4-T012 gates; 8538c272/b3bc8368 for M4-T015) are ancestors of HEAD; `git diff` over the substantive paths (rulesets/snapshots/tests; connectors/tests/fixtures) between reviewed SHA and HEAD = **empty**. The code the gates reviewed IS the code at HEAD.

---

## M4-T012 | producer: rules-engineer | reqs: D-045-R001, D-045-R008, D-045-R009, D-048-R001, D-048-R002, D-049-R001..R006

**D-045-R001 | PASS**
- Four rulesets present at HEAD (`services/api/app/rules/rulesets/r1_r2_bare_pitched_height.rule.json`, `…suffix_variants_pitched_height…`, `…reference_plane_23421g…`, `…qrs_height…`), family `residential_height_setback_r1_r2`, all `status:"needs_review"`.
- I recomputed `sha256(verbatim_excerpt UTF-8)` for all 14 snapshots: **stored == recomputed for all 14** (the four M4-T012 ones: zr-11-25 `6843ad22…`, zr-23-421-r1-r2 `1bce8818…`, zr-23-421-g `52dd8aab…`, zr-23-424-r1-r2 `336ba2cb…`). Canonical `docs/research/zr-snapshots/v1/` == bundle `services/api/app/_zr_snapshots/v1/` **byte-identical 14/14**.
- Caps verbatim-traceable: zr-23-421-r1-r2 excerpt contains "maximum height above the base plane of **25 feet**" and "ridge line of **35 feet** above the base plane"; each ruleset parameter carries `citation_ref` + `content_digest_sha256` + `effective_from:2024-12-05`. `test_as1_bare_confident…` binds `{25.0, 35.0}`.

**D-045-R008 | PASS**
- Sloping-plane setback geometry (23-421 (a)–(f)) is a `documented_limitation` (exception `pitched_plane_setback_professional_review`) on every envelope rule, never a numeric output; `test_nc8_setback_geometry_never_a_numeric_output` enforces it. Engine/evaluator/schemas untouched — commits dd7c8b74/4f8b093f touch only rulesets/snapshots/tests/docs/reports (no `engine*`/`evaluator*`/`schemas`).

**D-045-R009 | PASS**
- All 5 status values `needs_review`; my banned-language grep over the four rulesets clean (only negated "NOT a Verified determination"/"never rendered as… requirement"). ZERO dependency-file touches across all material commits (no `requirements*.txt`/`pyproject.toml`/`package.json`). Owner-decision provenance never presented as express: `test_as1_bare_and_suffix_rules_cite_distinct_provenance` proves 11-25 is cited only by the suffix rule.

**D-048-R001 (express half) | PASS**
- `r1_r2_bare_pitched_height` applicability `in_set ["R1","R2"]` only, 25/35 cited to zr-23-421-r1-r2; snapshot express enumeration "R1 R2 R3A R3X…" confirms bare R1/R2 named. `test_nc1_bare_rule_scoped_to_bare_labels_only` proves no variant matches.

**D-048-R002 (superseded by D-049-R006) | PASS (as-superseded)**
- Supersession is real and owner-sourced: `D-049/source-001.md` line 54 ("modifies D-048-R001/R002 for the five named variants ONLY") and `D-049-R006` registry text. No manufactured number — the five variants receive the SAME 25/35 cited to the express snapshot via 11-25 owner-decision (not fabricated), bound by `test_as1_suffix_variant_confident…`.

**D-049-R001 | PASS**
- `r1_r2_suffix_variants` applicability `in_set ["R1-1","R1-2","R1-2A","R2A","R2X"]`; cites zr-11-25 (verbatim "All regulations applicable to a district designation… appended with a suffix, except as otherwise set forth in express provisions") + zr-23-421-r1-r2; exception `owner_decision_suffix_inheritance_not_express` marks OWNER DECISION D-049 2026-09-13; needs_review. Outputs {25.0,35.0} for all five variants (parametrized test).

**D-049-R002 | PASS**
- zr-23-21 structured table (verified): R2X standard FAR **1.00**; R2/R2A row **0.75** — source-accurate. Exception `r2x_far_row_is_floor_area_only` (documented_limitation) records FAR does not modify height; `test_as1_r2x_far_row_documented_as_floor_area_only` binds R2X→{25.0,35.0}, asserts the note present on R2X and absent on R2A.

**D-049-R003 | PASS**
- `r1_r2_reference_plane_23421g` applicability: `in_set ["R1-1","R1-2","R2"]` AND building_type AND `any[ all[area≥9500, width≥100], slope≥5 ]`; output `reference_plane_elevation_max_ft:5.0`. `test_nc2_letter_suffix_and_bare_r1_excluded_from_reference_plane` (R1-2A/R2A/R2X/R1 → NOT_APPLICABLE) and `test_nc2_no_letter_suffix_members_eligible` (R1-1/R1-2/R2 → CONDITIONAL 5.0) both pass; `test_nc8_trigger_boundary_values` proves 9500/100/5 off-by-one boundaries; `test_nc5_reference_plane_missing_any_single_geometry_input_fails_closed` → professional_review_required. Cited zr-23-421-g (`52dd8aab…`), excerpt contains "9,500 square feet", "100 feet", "five percent", "five feet above the base plane".

**D-049-R004 | PASS**
- 23-424 → dedicated `r1_r2_qrs_height` (qualifying_residential_site required + fail-closed; 12-10 never assumed; transit-route exclusion documented; same-family conflict surfaced, `test_nc7_*`, never silent precedence). 23-425 `large_site`, 23-426(a) `historic_district`, 23-443(b) `transportation_infrastructure_adjacent` flags each → professional_review_required (`test_nc3_*`). 119-212 + 113-523 folded into `special_district_present` with sections named in descriptions (producer decision 4, disclosed; G3 ruled satisfies R004). 23-413(a) noted; pitched envelope never a requirement.

**D-049-R005 | PASS**
- Owner-decision provenance + DRAFT-until-G6 on every rule; `docs/ARCHITECT_REVIEW_QUESTIONS.md` A1: "OWNER DECISION D-049 ISSUED 2026-09-13… PROFESSIONAL CONFIRMATION STILL SOUGHT AT G6" (issued + ask open). Source-capture states nothing is a Verified determination.

**D-049-R006 | PASS**
- Supersession mechanics honored (D-048-R001/R002 modified for the five variants only; D-048-R004 + other rows stand — per D-049 source/registry). BINDING capture-completeness proof internally consistent across three artifacts: zr-23-421-g `raw_pdf_sha256 b5777618fe…`, source-capture report ("Raw PDF sha256 b5777618…", "9,500-present check: PASS", "Reconciliation… MATCH"), and ARCHITECT_REVIEW_QUESTIONS ("sha256 b5777618…, 9,500 present, word-for-word MATCH"). No amendment files; validator --check exit 0.

---

## M4-T015 | producer: backend-engineer | reqs: D-045-R003, D-045-R008, D-045-R009, D-046-R001, D-046-R002

**D-045-R003 (connector build half) | PASS**
- Both modules present at HEAD: `services/api/app/connectors/dcm_street_centerline_arcgis.py` + `dcm_street_width_classifier.py`.
- Fail-closed rule verified in code: `WIDE_THRESHOLD_FT=75.0`; DISPOSITION_WIDE emitted ONLY for `clean_numeric_ge_75`, `range_both_endpoints_ge_75`, `gt_inequality_ge_75` (all true entailments of ≥75). Every other of the 24 `AMBIGUITY_CLASS_DISPOSITIONS` → `narrow_fail_closed` + typed class + review flag (approximations `~80`/`probably`, straddling `60-75`/`74-75.3`, `<=75` edge, hedged unknowns, prose, empty/None/non-string/negative).
- Connector targets `DCM_Street_Center_Line/FeatureServer/0` with `outSR=2263&f=json`; resultOffset/exceededTransferLimit paging with loop-safety; HTTP-200 ArcGIS error-object → typed `UpstreamError`; CRS validated (wkid 2263). No Geoclient/mappluto import (only posture comments). Mapped-street override keys only on `Feat_Type`/`Paper_ST`/`Record_ST`, never `Feat_status`.
- Fixtures: I recomputed sha256 for all **26 MANIFEST entries → 0 mismatches**; `synthetic:true` count = **exactly 1** (`provider_error_http200_synthetic.json`), 25 live; West 100 St fixture carries the two-segment 60/100 divergence.
- G1 live byte-verification: gate `M4-T015-G1` = PASS (reviewer data-contract-verifier, reviewed_sha b3bc8368); report documents WebFetch of 3 live fixtures + `dataLastEditDate` freshness match. Registry draft `dcm-street-centerline.json` non-final, connector-implemented, `self_declared_source_id` matches connector SOURCE_ID.

**D-045-R008 | PASS** — M4-T015 producer commit (8538c272) touched ZERO rules/`_zr_snapshots`/tests/rules paths; OQ-4 within-100-ft geometry explicitly deferred (registry + G1 report); no consumer wiring.

**D-045-R009 | PASS** — No rule touched (connector-only); ZERO dependency-file changes across material commits; registry `draft_status` non-final; OQ-1/OQ-3 left open, no compliance/legal judgment.

**D-046-R001 | PASS** — Both producers dispatched at 2026-09-13T06:49:18 (M4-T012 .269 / M4-T015 .649, same wave), isolated worktrees `wt-m4t012-r2` (base dbd07817) and `wt-m4t015` (base 2c127706), "Wave 2 slot 1/2 of 2" in both progress logs.

**D-046-R002 | PASS** — Producer material file sets **dd7c8b74 (17) ∩ 8538c272 (34) = 0 files**; M4-T012 producer touched no `connectors/` path, M4-T015 producer touched no `rules/rulesets`/`_zr_snapshots`/`tests/rules` path; orchestrator rework `4f8b093f ∩ 8538c272 = 0`. allowed_paths pairwise-disjoint by construction.

---

## UNVERIFIABLE / relied-upon (named explicitly; none gates a requirement row)

1. **CI conclusions** (dd7c8b74=FAILURE 6-ruff, 8538c272=SUCCESS, b3bc8368=report-only): `gh run list --commit` returned `[]` for both SHAs in my sandbox (the documented API-push/branch CI-trigger quirk). **Not independently reproduced.** Corroborated instead by: rules 568 / connectors 619 green at HEAD, modularity EXIT 0, the ruff fixes present in rework commit 4f8b093f (`test_r1_r2_height_setback.py`), and the G4 FAIL→PASS gate records. No lingering defect is observable at the frozen head.
2. **G1 live-network byte-verification** against the live DCM ArcGIS endpoint: I could not re-run WebFetch. Relied on the G1 gate report (primary control-plane record) plus my own reproduction of MANIFEST sha256 consistency and fixture provenance. All offline portions were fully reproduced.
3. **`tools/test_directive_compliance.py`**: every observed test printed `ok` (git-content-identity, empty-identity guard, LF/CRLF, multi-task verification, multiple-directives groups) but the suite exceeded my 550s timeout (Windows git-subprocess cost + concurrency contention) and did not print its final `OK`. **No failure observed; full completion not reproduced in-sandbox.** Corroborated by `validate_directive_compliance.py --check` EXIT 0 (the CI-wired integrity gate), `test_project_control.py` (23 groups OK), and `test_directive_reminder.py` (12 OK).

Intake note: for every cited directive (D-045, D-046, D-048, D-049) the `requirements.json` rows I checked faithfully reflect `source-001.md` (no amendment files exist; digests validated). No missing, weakened, combined, or invented requirement found among the cited rows; the D-048→D-049 supersession is explicit, symmetric, and owner-sourced.

**All 16 requirement rows: PASS on independently reproduced primary evidence. No VIOLATED row. The three caveats above are corroborating/harness items, each of which also has reproduced primary evidence behind the rows it touches.**

## VERDICT: PASS

VERIFICATION COMPLETE — with the three relied-upon items (CI conclusions, G1 live-fetch, and the slow `test_directive_compliance.py` completion) disclosed above as not-personally-reproduced-in-sandbox but corroborated; none is the sole evidence for any requirement row.
