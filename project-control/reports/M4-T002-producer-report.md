# M4-T002 — Producer report

Task: **M4-T002 Rules-engine integration with property-profile / spatial-analysis results.**
Producer: orchestrator (lead-only, owner directive 2026-07-21; no producer subagent dispatched).
Status requested: **`awaiting_gate`** — implementation complete; self-checks green; ready to freeze a
submit SHA and dispatch the independent gates (G3 code-review, G4 integration/regression, G5
security). Not accepted; no merge; no rule published/Verified.

## Submission summary

Wired the accepted-on-main **M4-T001** deterministic rules engine into the property-analysis flow at
the **service layer** (no new public endpoint, UI, or contract in this slice). A new module maps the
canonical **M2-T012** property profile (contract 1.4.0: `spatial_intersection`, `lot_geometry`) and
the **M2-T013** spatial-intersection substrate into evaluator inputs + a `spatial_context`, evaluates
the draft **R5 residential-FAR** family, and returns an honestly-draft, uncertainty-preserving,
never-Verified result. The module **maps**; it does not calculate (the evaluator calculates) and it
does not decide law.

## What was built (all additive; two new files)

### Integration module — `services/api/app/rules/integration.py` (new)
`evaluate_property(profile, *, registry=None) -> PropertyRuleEvaluation`. Pure and deterministic
(same profile → byte-identical result). Consumes the profile strictly **read-only** as a plain dict.

- **Derives `zoning_district` ONLY from a confident lot.** A base-zoning district is taken **only**
  when the spatial engine already classified the lot `single_district_confident` **and** the base
  pairs contain **exactly one** `interior_confident` district (the engine's own invariant, re-derived
  without collapsing anything). Any deviation → fail safe.
- **Derives `lot_area_sq_ft`** preferring the validated `lot_geometry.area_sq_ft` (M2-T009, EPSG:2263
  projected area), else the same MapPLUTO area carried on the confident base pair; absent → the
  evaluator's typed missing-critical path (no computed value).
- **Builds `spatial_context`** = `{lot_overall_class, professional_review_required, coverage_note}`
  and passes it to `evaluator.evaluate(...)`.
- **FAILS SAFE** (no evaluator call, no computed value) when `spatial_intersection` is absent, its
  class is missing, it is `data_conflict` (→ `data_conflict` coverage), or it is anything other than
  `single_district_confident` / routes to professional review (→ `professional_review_required`).
  Typed `fail_safe_reason` discriminators: `spatial_intersection_absent`, `spatial_context_incomplete`,
  `data_conflict`, `geometry_uncertain`, `inconsistent_confident_geometry`.
- **Preserves M2-T013 uncertainty verbatim** in `spatial_uncertainty`: `lot_overall_class`, the
  professional-review flag, `review_reasons`, per-base-district **share ranges**
  (`share_min`/`share_point`/`share_max`, never renormalized), and the ZTLDB `crosscheck` conflict —
  none collapsed into a definitive district.
- **Never Verified.** Coverage tops out at `conditional` (draft rule). Every result carries its
  `coverage_status`, the evaluated rule's `needs_review` lifecycle state, and a permanent
  `not_verified_disclaimer`. `assert_not_verified(payload)` fail-closes if a `verified` status ever
  appears at the top level, in any evaluator trace, or in the family-coverage block; `evaluate_property`
  calls it before returning and `PropertyRuleEvaluation.export()` re-checks it, so a downstream caller
  (scenario generator, UI, report) can never read a draft as final.
- **Provenance fail-closed.** Evaluator traces are taken through `RuleResult.export()`, which refuses
  to emit a material value whose citation lacks resolvable source provenance (PRD §19).
- **Coverage honesty.** A confident non-R5 district → visible `not_applicable` (the R5 rule's
  not-applicable trace is surfaced, never silence); the result also carries
  `registry.family_coverage("residential_far")`, and an unimplemented family reads `unsupported`.

### Acceptance test pack — `services/api/tests/rules/test_rules_integration.py` (new, 23 tests)
Offline/deterministic. Spatial fixtures are built from the **real** `app.spatial` domain dataclasses
and serialized exactly as the accepted M2-T012 builder serializes them
(`LotIntersectionRecord.as_dict()` minus `coverage_audits`, plus `provenance_refs`) so no field name
can silently drift from production. The rule registry is the **real** one (real R5 rule + real ZR
23-21 source snapshot), so citation provenance genuinely resolves.

## Contracts / schema changed
**None.** No `packages/contracts/**`, no engine schema, no new public endpoint, no UI. Additive
service-layer module + tests only. The profile builder (`app/profile/**`) and the spatial engine
(`app/spatial/**`) are consumed read-only via imports; neither is modified.

## Acceptance scenarios RI-S1 … RI-S8 (evidence — `services/api/tests/rules/test_rules_integration.py`)

| Scenario | Evidence (test names) |
|---|---|
| RI-S1 confident path → R5 FAR result, conditional, full trace, resolvable citations | `test_ri_s1_confident_r5_carries_far_result_conditional_with_citations`, `_r5d_far_value`, `_lot_area_falls_back_to_spatial_pair_when_geometry_absent` (trace validated against the canonical evaluation-trace schema; outputs `far=1.5`, `floor_area=15000`) |
| RI-S2 uncertainty preserved, never collapsed; no district/value | `test_ri_s2_uncertain_geometry_fails_safe_no_value` (boundary_uncertain / sliver_ambiguous / split_lot_confident → PRR), `_data_conflict_is_typed_and_preserved` (→ data_conflict, crosscheck surfaced), `_invalid_geometry_review_fails_safe`; share ranges asserted intact |
| RI-S3 fail-safe on missing evidence | `test_ri_s3_absent_spatial_intersection_fails_safe`, `_present_section_missing_class_fails_safe`, `_confident_but_no_interior_pair_fails_safe` (no guessed assignment, no computed value) |
| RI-S4 honest draft status | `test_ri_s4_result_carries_coverage_needs_review_and_disclaimer`, `_fail_safe_result_also_honest` (coverage + `needs_review` + `rule_lifecycle_statuses==['needs_review']` + not-Verified disclaimer; no field equals `verified`) |
| RI-S5 determinism | `test_ri_s5_same_profile_byte_identical` (incl. a fresh registry load), `_fail_safe_is_deterministic` |
| RI-S6 coverage honesty | `test_ri_s6_confident_non_r5_district_is_visible_not_applicable`, `_unimplemented_family_is_visible_unsupported` |
| RI-S7 downstream safety (never Verified) | `test_ri_s7_no_verified_anywhere_in_any_outcome`, `_guard_rejects_a_verified_payload`, `_disclaimer_text_is_not_a_status` |
| RI-S8 regression + drift guard | `test_ri_s8_spatial_vocabulary_drift_guard`, `_only_canonical_coverage_statuses`, `_target_family_matches_r5_rule_family`; full API suite green (below) |

## Self-check evidence (local worktree; Python 3.11.9, shapely 2.0.7, pytest 8.4.2, jsonschema)

- `python -m pytest tests/rules/test_rules_integration.py -v` → **23 passed** (RI-S1..RI-S8).
- `python -m pytest -q` (full `services/api`) → **649 passed** (626 prior M4-T001 baseline + 23 new;
  **no regression**).
- `python -m ruff check app tests` (whole `services/api`) → **All checks passed**.
- No `packages/contracts` schema change → `validate_contracts.py` unaffected. Web (Node) jobs are
  untouched (no `apps/web/**`) and run on CI.

Expected vs actual: confident R5, lot area 10 000 sq ft → `max_residential_far=1.5`,
`max_residential_floor_area_sq_ft=15 000`, coverage `conditional` (**not** verified) — matches. R5D
5 000 → FAR 2.0, floor area 10 000 — matches. Every uncertainty class → `professional_review_required`
(or `data_conflict`) with `zoning_district=None` and `evaluations==[]` — matches.

## Source / API evidence
No external source calls. Consumes accepted internal substrates only: the M4-T001 evaluator
(`app.rules`), the M2-T012 canonical profile shape (contract 1.4.0), and the M2-T013 record shape
(`app.spatial.models.LotIntersectionRecord`). Field fidelity is enforced by building test fixtures
from the real spatial dataclasses and by the RI-S8 drift guard.

## Assumptions & defaults (disclosed)
- **`zoning_district` source = confident geometry, not PLUTO zonedist.** A lot-level district is only
  as trustworthy as its positional certainty; the integration therefore derives the district solely
  from a `single_district_confident` M2-T013 record and never from a bare PLUTO string. This is the
  fail-safe posture the hard rules require.
- **`lot_area_sq_ft` precedence:** validated `lot_geometry.area_sq_ft` → confident base pair's
  `lot_area_sq_ft` → none. A **documented limitation**: a zoning lot may differ from the tax-lot
  geometry; this is a draft-rule input, never a Verified boundary.
- **`site_class` is deliberately NOT derived.** Whether a lot is a "qualifying residential site" is a
  separate legal determination the R5 rule defers; leaving it absent makes the rule surface the
  higher-FAR alternative as a **conditional** exception rather than guessing.
- **Spatial vocabulary values are duplicated, not imported.** Importing `app.spatial` executes its
  `__init__`, which pulls in the shapely-dependent engine — an unnecessary heavy dependency for a pure
  data mapping. Four values (`base_zoning`, `single_district_confident`, `data_conflict`,
  `interior_confident`) are copied with a **drift-guard test** (RI-S8) that imports the real constants
  and asserts equality — the same technique `coverage.py` uses against the canonical contract.

## Known limitations
- Only the **R5 residential-FAR** family is evaluated (the only draft family on main). Adding another
  residential-FAR district rule to the registry needs **no change** here (it evaluates the whole
  `residential_far` family). Other families read `unsupported` honestly.
- Service-layer only: no endpoint/UI wiring in this slice (a published rules-evaluation **contract** +
  endpoint + UI are separate additive tasks, per the packet STOP conditions).

## Security / provenance impact
No auth, storage, upload, secret, external call, or dependency change. Read-only consumption of
in-process data. Provenance is **fail-closed** (evaluator `export()`); the never-Verified guard is
**fail-closed**. Input-provenance refs from the profile are surfaced for traceability; the output
provenance is the rule's own citations. No official-derived value is fabricated or up-labeled.

## New risks or dependencies
None. No new package. `app.rules` gains **no** runtime dependency on `app.spatial` (constants are
duplicated + drift-guarded), preserving engine/spatial layer separation.

## Recommended next tasks
1. A published, versioned **rules-evaluation contract** in `packages/contracts` (additive) once a
   cross-tier consumer (reviewer UI / report) needs the `PropertyRuleEvaluation` shape.
2. A property-analysis **endpoint + UI** surfacing this result with its coverage/needs-review/
   disclaimer (later milestone; forbidden in this slice).
3. Additional residential-FAR district rules (R1–R10) as reviewed drafts — zero integration change.
4. G6 qualified-human legal approval remains the standing gate before any R5 result is Published/Verified.

## Gate status
Required gates **G0 (PASS, recorded) / G2 (self-check, green above) / G3 (code) / G4 (integration) /
G5 (security)**. Submitting to the independent gates at the frozen submit SHA. Final acceptance stays
coupled to M4-T001's outstanding **G6** (human) — acceptable and safe: this slice ships only
`needs_review` / non-Verified draft results. Not accepted; no merge; no rule published/Verified.

## Exact report path
`project-control/reports/M4-T002-producer-report.md`
