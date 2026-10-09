# M5-T017 producer report — C1 unused draft zoning floor area (D-041:D-041-R001)

Producer: scenario-optimization-engineer
Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-ad7765d1e1dc63bb4`
Worktree branch: `worktree-agent-ad7765d1e1dc63bb4`
Base (packet) commit: `462c8ad1`
Directive binding: D-041 → D-041-R001 (only applicable requirement to M5-T017).

## Summary

Added the owner-approved gap-list C1 output server-side: a typed
`unused_draft_zoning_floor_area` section that rides on EVERY scenario document
(preliminary + every no-scenario / unsupported variant). It reports the draft
residential zoning-floor-area cap MINUS the existing built floor area, consuming
the canonical cap VERBATIM, with per-input provenance, precise-noun labeling, a
machine-readable ZR 12-10 assumption, an honest negative (over-built) remainder
routed to professional review, and typed not-computable states — never estimated,
never clamped, never hidden.

All C1 logic lives in a NEW focused module (`unused_floor_area.py`, the `derive.py`
separate-module precedent); `builder.py` received a bounded ~13-line wire-in in
its single `_assemble` choke point.

## What was built, per file

### NEW `services/api/app/scenario/unused_floor_area.py`
Pure deterministic `build_unused_floor_area_section(*, property_profile, cap_value,
cap_provenance) -> dict`. Consumes the profile READ-ONLY. Guards mirror `builder.py`
(`_finite_float` / `_positive_finite_float`, plus `_nonnegative_finite_float` so an
existing area of exactly 0 — e.g. a vacant lot — is usable). Resolves the bldgarea
fact's `provenance_ref` against the profile root `provenance[]` array with a local
copy of the `_profile_provenance_index` / `_lot_area_provenance` pattern (kept local
to avoid an import cycle with `builder.py`). Decision order:
1. no positive cap → `not_computable` / `no_draft_far_cap`;
2. cap present, no bldgarea fact or `value is None` → `not_computable` /
   `missing_existing_building_area`;
3. cap present, fact present but coverage_status not usable OR value not a finite
   non-negative number → `not_computable` / `existing_building_area_unusable`
   (coverage_status echoed verbatim);
4. otherwise `value = cap - existing_area` (unrounded): `< 0` → `over_built`
   (section PRR true + honest statement), else `computed` (an exact 0 is computed).

### `services/api/app/scenario/builder.py` (bounded wire-in only)
Added `from .unused_floor_area import build_unused_floor_area_section` and, in
`_assemble`, one call plus the section key on the document, and widened the root
`professional_review_required` to `professional_review_required or
unused_section["professional_review_required"]`. No C1 logic added to `builder.py`.

### `services/api/app/scenario/models.py`
Added `UnusedFloorAreaState` (`computed` / `over_built` / `not_computable`) and
`UnusedFloorAreaNotComputableReason` (`missing_existing_building_area` /
`existing_building_area_unusable` / `no_draft_far_cap`).

### `services/api/app/scenario/constants.py`
Added `UNUSED_FLOOR_AREA_LABEL` (precise-noun), `UNUSED_FLOOR_AREA_SCOPE_NOTE`,
`UNUSED_FLOOR_AREA_OVER_BUILT_STATEMENT`, `UNUSED_FLOOR_AREA_FORMULA`,
`USABLE_EXISTING_AREA_COVERAGE_STATUSES = {"conditional"}`, and
`zoning_lot_extent_assumption()` (fresh ZR 12-10 record each call). None of these
strings contain "maximum buildable area", "remaining development rights",
"remaining capacity", "verified", or "compliant".

### `services/api/app/scenario/__init__.py`
Additive facade exports: `UNUSED_FLOOR_AREA_LABEL`, `UnusedFloorAreaState`,
`UnusedFloorAreaNotComputableReason`, `build_unused_floor_area_section`.

### Contract — BOTH copies, byte-identical
`packages/contracts/schemas/v1/scenario.schema.json` AND
`services/api/app/_contract_schemas/v1/scenario.schema.json` gained the new REQUIRED
root key `unused_draft_zoning_floor_area` (`$ref` to a new fully-specified, closed
`$defs/unused_draft_zoning_floor_area`) plus a closed `$defs/unused_floor_area_inputs`.
The bundle was written by `cp` of the canonical bytes; verified byte-identical
(25992 bytes; `test_s6_both_schema_copies_are_byte_identical` +
`test_runtime_bundle_copy_is_byte_identical_to_canonical`).

### Tests
NEW `services/api/tests/scenario/test_unused_floor_area.py` (S1–S6 + direct
pure-function + determinism + no-mutation). Deliberate additive shape updates (no
assertion weakened) to `test_scenario_foundation.py` (section present on every
document), `test_scenario_contract.py` (required/closed schema + fixtures carry the
section), and `services/api/tests/api/test_scenario_api.py` (AS-1 computed 5000 sq ft
from F01 bldgarea 10000 vs cap 15000; AS-2 no-scenario carries no_draft_far_cap).

## Section field schema (exact)

`unused_draft_zoning_floor_area`:
- `state`: `"computed" | "over_built" | "not_computable"`
- `unused_draft_zoning_floor_area_sq_ft`: `number | null` (may be negative on
  over_built, exactly 0 on computed, null on not_computable; never NaN/Inf)
- `unit`: `"square_feet" | null`
- `label`: string (precise-noun constant)
- `scope_note`: string (geometry not assessed; tax lot treated as zoning lot)
- `formula`: `string | null`
- `professional_review_required`: boolean (SECTION-level; true on over_built)
- `over_built_statement`: `string | null`
- `not_computable_reason`: enum-or-null (the three typed reasons)
- `inputs`: `{ draft_zoning_floor_area_cap: {value_sq_ft, unit, provenance},
  existing_building_floor_area: {value_sq_ft, unit, coverage_status, provenance_ref,
  provenance} }` (closed)
- `assumptions`: array of `{key, assumption_type, value, unit, rationale}` — the ZR
  12-10 `zoning_lot_extent` record on computed/over_built; `[]` on not_computable.

## Design note — professional_review_required widening + downstream consumers checked

Root PRR is now `rule_evaluation_fail_safe_trigger OR section_over_built`. This
widens the meaning of the document root flag: previously the preliminary path always
emitted `False`; an over-built remainder now forces it `True`. Both triggers are
pinned by `test_root_prr_or_semantics_both_triggers`.

Downstream consumers of a SCENARIO document's root `professional_review_required` I
checked (grep over `services/api/app`):
- `services/api/app/api/v1/scenario.py` — the endpoint returns the scenario as a
  normal 200 regardless of PRR; it does NOT branch on the flag (only a docstring
  mention). No behavior change.
- `services/api/app/api/v1/evidence.py` — reads `rule_evaluation.get(
  "professional_review_required")` (the RULE-EVALUATION document), not the scenario
  document. Unaffected.
- `services/api/app/api/v1/scenario_analysis.py` — `FORBIDDEN_FACT_KEYS` includes
  `professional_review_required` to reject caller-supplied assumption keys that
  mirror document keys. My new key `unused_draft_zoning_floor_area` is not a caller
  input path: the section is computed server-side from profile + cap and never from
  caller assumptions, so there is no forgery surface and no change is needed there
  (and that file is out of this task's scope).

No test anywhere asserted a preliminary scenario's root PRR is `False` in a case my
change would flip; the only preliminary+bldgarea path in the suites (API AS-1, F01
bldgarea 10000 < cap 15000) is `computed` → PRR stays `False`.

## S1–S6 → test mapping (`services/api/tests/scenario/test_unused_floor_area.py`)

- S1 computed normal remainder → `test_s1_computed_normal_remainder` (value ==
  cap−bldgarea, label/scope/formula, per-input provenance resolved, ZR 12-10
  assumption, PRR False).
- S2 over-built honest negative → `test_s2_over_built_honest_negative` (value < 0,
  != abs, statement, section+root PRR True, provenance/assumption discipline).
- S3 zero boundary → `test_s3_zero_boundary_is_computed_not_over_built`.
- S4 missing/unusable → `test_s4a_missing_existing_area_fact_is_not_computable`,
  `test_s4b_unusable_existing_area_echoes_coverage_status`
  (`data_conflict`/`unsupported`), `test_s4b_present_but_nonnumeric_value_is_unusable`.
- S5 no draft FAR cap → `test_s5_no_cap_paths_are_no_draft_far_cap` (6 no-cap
  factories, bldgarea present to prove the reason is the absent cap),
  `test_s5_section_is_present_on_degenerate_empty_inputs`.
- S6 contract/JSON-safety/precise-noun →
  `test_s6_both_schema_copies_are_byte_identical`,
  `test_s6_new_key_is_required_and_fully_specified_and_closed`,
  `test_s6_every_state_survives_strict_and_utf8_json` (both
  `json.dumps(allow_nan=False)` and `.encode("utf-8")` for every state),
  `test_s6_no_forbidden_nouns_and_no_verified_compliant_language`,
  `test_s6_section_present_and_valid_on_every_state`.
- OR-semantics: `test_root_prr_or_semantics_both_triggers`.
- Direct pure function + verbatim cap + determinism + no-mutation:
  `test_direct_pure_function_*`, `test_section_is_deterministic`,
  `test_builder_does_not_mutate_profile_with_bldgarea`.

## Verification evidence (real output)

Commands run from the worktree root.

```
$ python -m pytest services/api/tests/scenario -q --no-header
..............................................................           [100%]
422 passed in 1.19s
```

```
$ python -m pytest services/api/tests/api -q --no-header
......................................                                   [100%]
398 passed in 13.17s
```

```
$ python tools/modularity_check.py --check   # (exit code captured separately)
selected 393 files; failures 0; warnings 16
# EXIT=0  (builder.py NOT among the warnings; unused_floor_area.py is a focused module)
```

Additional CI-parity checks:
```
$ python -m ruff check services/api/app/scenario services/api/tests/scenario services/api/tests/api/test_scenario_api.py
All checks passed!

$ python -m pytest packages/contracts/scripts/tests -q --no-header
.............................                                            [100%]
29 passed in 0.40s
```

## Deviations / disclosures (IMPORTANT — scope expansion beyond listed allowed_paths)

Making the new key `required` in the CLOSED contract (as the packet mandates in
point 6 and acceptance S6: "new required key fully specified, closed") has two
unavoidable consequences on committed artifacts that were NOT in the packet's
`allowed_paths` list and are NOT in `forbidden_paths`. I edited them because there is
no way to satisfy "required key" + "no pre-existing test assertion weakened"
without doing so; the readonly-agent guard permits it for a roster producer. Both
are direct, mechanical consequences of the required-key contract change:

1. `packages/contracts/fixtures/valid/scenario/*.json` (4 files) — the 4 valid
   fixtures are validated by `test_valid_fixture_validates`; a new required key makes
   them invalid unless they carry it. I regenerated ONLY the new section into each
   via `build_unused_floor_area_section` using each fixture's own cap/cap_provenance
   and the minimal `_support` profile (no bldgarea), so every fixture's section is
   `not_computable` (preliminary → `missing_existing_building_area`; the 3 no-cap →
   `no_draft_far_cap`). Root `professional_review_required` was NOT changed on any
   fixture (section adds no PRR in these states). Re-dump was byte-clean (verified
   `json.dumps(indent=2, ensure_ascii=False)+"\n"` round-trips the originals).
2. `packages/contracts/generated/scenario.ts` — the committed generated TS type is
   drift-guarded by `test_committed_scenario_is_byte_identical_to_fresh_generation`.
   I regenerated it with `python packages/contracts/scripts/generate_ts_types.py`
   (26 insertions, scenario.ts only). The generator also rewrote
   `property_profile.ts` / `rule_evaluation.ts` / `survey_evidence.ts` with
   byte-identical content (LF/CRLF phantom only); I restored those three so the diff
   contains scenario.ts alone.

Please ratify this scope expansion when recording the gate, or advise if the fixture
+ generated-TS updates should instead be a sibling task. Everything else is inside
the packet's `allowed_paths`.

No other deviations. No blockers. `git push` / `gh` / `project_control.py` not run
(orchestrator authority).
