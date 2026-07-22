# M4-T002 — G4 (Integration & Regression) verbatim return, ROUND 2 (post-rebase re-gate)

_Verbatim independent qa-engineer return (transport decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

**VERDICT: PASS**

Independent, read-only re-validation on the M4-T003-corrected (hardened) evaluator after rebase. No regression; all RI-S1..S8 and C1-C3 preserved with unchanged meaning; the 5 new HARD tests are correct and (the 3 differentiating ones) regression-meaningful; strict-JSON, provenance-fail-closed, uncertainty-preserved, and never-Verified invariants all hold; registry.py/evaluator.py untouched (FH-1 deferred, FH-2 not naively guarded).

## Gate Report
- **Gate ID:** G4 (integration-and-regression QA), round 2 / post-rebase re-gate
- **Task ID:** M4-T002 (rules-engine ↔ property-analysis integration, service layer)
- **Reviewer:** qa-engineer (independent, read-only)
- **Producer:** orchestrator (lead-only, owner directive 2026-07-21)
- **Result:** PASS
- **Frozen SHA:** code == `ff33ad2`; worktree HEAD `82512e3` verified docs-only on top (`git diff --stat ff33ad2 82512e3` = only `project-control/reports/M4-RULES-FUTURE-HARDENING.md`). Python 3.11.9, pytest 8.4.2, ruff, jsonschema, shapely 2.0.7.

## Commands independently executed (from services/api)
```
$ python -m pytest tests/rules/test_rules_integration.py -q  =>  35 passed in 1.36s
$ python -m pytest -q            (full api suite)            =>  694 passed in 6.08s
$ python -m ruff check app tests                             =>  All checks passed!
```
Round-1 baseline was 649 at f25dbff/609efe9. The corrected main (M4-T003 hardened evaluator, +5 new HARD integration tests) now stands at 694 passed. No failures/errors/skips.

## Delta reviewed — `git diff b892975 ff33ad2 -- services/`
`integration.py` (+30/-7) and `test_rules_integration.py` (+86). Full task scope vs rebased main `git diff --stat f5ab631 ff33ad2 -- services/` = exactly two ADDED files; **registry.py and evaluator.py = 0-line diff** (inherited unchanged from corrected main). Three production changes: `_positive_number` requires `math.isfinite` + OverflowError guard (LOW-2); new `_as_list()` coerces malformed spatial containers to `[]` at `_base_pairs`/`_preserve_uncertainty`/`_input_provenance` (LOW-1); vestigial `verified_status_present` removed (INFO-4/G3-F2).

## RI-S1..S8 + C1-C3 coverage map (all PASS; meaning unchanged post-rebase)
| Item | Test name(s) | Verified meaning intact |
|---|---|---|
| RI-S1 confident R5 | `test_ri_s1_confident_r5_carries_far_result_conditional_with_citations` | coverage=**conditional** (≠verified), district=R5, outputs `{max_residential_far:1.5, max_residential_floor_area_sq_ft:15000.0}`, every citation carries `content_digest_sha256`, section 23-21, trace validates vs canonical schema |
| RI-S1 variants | `_r5d_far_value` (R5D→FAR 2.0/floor 10000), `_lot_area_falls_back_to_spatial_pair_when_geometry_absent` | intact |
| RI-S2 uncertainty preserved | `test_ri_s2_uncertain_geometry_fails_safe_no_value` [3 params], `_data_conflict_is_typed_and_preserved`, `_invalid_geometry_review_fails_safe` | share ranges **not renormalized**, review flags surfaced, crosscheck set_conflict flows through, district=None, evaluations=[] |
| RI-S3 fail-safe missing evidence | `_absent_spatial_intersection_fails_safe`, `_present_section_missing_class_fails_safe`, `_confident_but_no_interior_pair_fails_safe` | intact |
| RI-S4 honest draft | `_result_carries_coverage_needs_review_and_disclaimer`, `_fail_safe_result_also_honest` | intact |
| RI-S5 determinism | `_same_profile_byte_identical` (incl. fresh registry), `_fail_safe_is_deterministic` | intact |
| RI-S6 coverage honesty | `_confident_non_r5_district_is_visible_not_applicable`, `_unimplemented_family_is_visible_unsupported` | intact |
| RI-S7 never-Verified | `_no_verified_anywhere_in_any_outcome`, `_guard_rejects_a_verified_payload`, `_disclaimer_text_is_not_a_status` | intact |
| RI-S8 drift guard | `_spatial_vocabulary_drift_guard`, `_only_canonical_coverage_statuses`, `_target_family_matches_r5_rule_family` | four constants still pinned to real values |
| C1 overlay family filter | `test_c1_confident_base_with_commercial_overlay_pair` | district=R5, FAR 1.5, overlay excluded from base_district_candidates (==["R5"]) |
| C2 confident + missing lot_area | `test_c2_confident_district_but_missing_lot_area_no_value` | district=R5, lot_area None, fail_safe=False, coverage=PRR, `evaluations[0].outputs=={}`, completeness=missing_critical |
| C3 R5A/R5B | `test_c3_r5a_r5b_variants_far_1_5` [2 params] | FAR 1.5, conditional |
| G3-F1 review-flag clause | `test_f1_confident_class_but_professional_review_required_fails_safe` | fail_safe_reason=**geometry_uncertain** |
| gap1 / gap6 defensive | `_two_interior_pairs_fails_safe`, `_empty_pairs_fails_safe` | fail_safe_reason=**inconsistent_confident_geometry** |

Fail-safe discriminators unchanged. No scenario silently changed meaning after the rebase.

## New HARD tests — cover the follow-ups and are regression-meaningful
- **HARD-1 (LOW-1) — regression-meaningful.** Pre-hardening `for pair in (pairs or [])` with `pairs=999` → `for pair in 999` raises TypeError; `list(5)` likewise. "Must not raise" FAILs pre-hardening. Now: pairs→[] → `inconsistent_confident_geometry` fail-safe, containers coerced to [], strict-JSON on a fail-safe result succeeds.
- **HARD-2 (LOW-2) — regression-meaningful.** Pre-hardening `_positive_number(inf)`=True → inf enters evaluator → `max_residential_floor_area_sq_ft: inf`, conditional. Test asserts `lot_area_sq_ft is None` + PRR + `"inf" not in json.dumps` + strict-JSON → FAILs pre-hardening. District still confidently R5.
- **HARD-3 (INFO-4) — regression-meaningful.** Pre-removal the field made `hasattr` True and appeared in `as_dict()`/`export()` → assertions FAIL. Now absent everywhere.
- **HARD-2b / HARD-4** — companion/reinforcement pins (NaN/-1/0 already rejected; normal success already strict-JSON); honestly framed as pins, not overstated.

## Invariants independently confirmed
- **Strict-JSON:** `json.dumps(export, allow_nan=False)` asserted on a confident success AND on a fail-safe result. Holds.
- **Provenance fail-closed:** computed values reach the payload only via `RuleResult.export()`; RI-S1 asserts each citation's `content_digest_sha256` resolves. Intact (evaluator untouched).
- **Uncertainty-preserved:** share ranges not collapsed/renormalized and crosscheck conflict surfaced.
- **Never-Verified fail-closed:** no field equals `verified` anywhere; `assert_not_verified` rejects a planted verified payload at top-level and in a trace; disclaimer text is not a status.
- **FH-2 NOT naively fixed / FH-1 deferred:** `git diff f5ab631 ff33ad2 -- registry.py evaluator.py` = 0 lines. No family-wide overlap guard introduced; impossible-calendar-date remains deferred. Both recorded as future-hardening (docs-only) rather than fixed in this slice.

## Findings by severity
- CRITICAL / HIGH / MEDIUM: none. No RI/C regression (35 integration + 659 other = 694 pass).
- LOW/INFO (non-blocking, carried forward): LOW-1 and LOW-2 now remediated at the integration layer; FH-1 (impossible-calendar-date), FH-2 (rule_series overlap), and FH-3 (assert_not_verified evaluations guard) remain documented pre-endpoint-exposure prerequisites. INFO-3 (non-dict profile arg → AttributeError) remains an accepted in-process no-endpoint posture.

## Notes / limitations of this gate
Service-layer only; no endpoint/UI, so no human-walkthrough. Fixtures built from real `app.spatial` dataclasses serialized exactly as the M2-T012 builder, with the RI-S8 drift guard pinning the four duplicated constants to the real ones. Results are draft `needs_review` / non-Verified; G6 qualified-human legal approval remains the standing gate before any R5 result is Published/Verified.

**VERDICT: PASS**
