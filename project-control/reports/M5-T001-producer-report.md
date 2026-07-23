# M5-T001 — Producer report (deterministic coverage-aware scenario foundation)

**Producer:** scenario-optimization-engineer (worker; NOT authorized to accept, gate, or run the
control CLI). **Status requested:** `awaiting_gate` (submit evidence for independent G1/G3/G4/G5).
**Nothing here is Published, Verified, or accepted.** Every scenario is draft/`needs_review`; no field
ever equals `verified`; the canonical R5 cap is SURFACED, never recomputed.

> Worktree note: this evidence was produced in the harness-assigned agent worktree
> `.claude/worktrees/agent-aaa1485a1271b2c31` (branch `worktree-agent-aaa1485a1271b2c31`), which the
> Write sandbox confines me to. Its base is `main` @ `0a61b7d` and contains all M4/M2 code inputs
> (rule_evaluation contract, r5 rule, response.py, fixtures). The two commits unique to
> `task/M5-T001-scenario-foundation` (`133ebe6` packet create + G0, `c773992` progress 10%) are
> ledger-only (`project-control/tasks/M5-T001.json` + progress log) and do not affect the code/tests
> this task produces. The orchestrator should integrate the commit(s) below onto
> `task/M5-T001-scenario-foundation`.

---

## 1. What shipped, by area (allowed_paths only)

**New deterministic service module — `services/api/app/scenario/`**
- `models.py` — `ConstraintCompleteness` enum with EXACTLY the six states
  `known|draft|missing|conflicting|unsupported|professional_review_required`; `ScenarioKind`
  (`preliminary|no_scenario|unsupported`); `DataCompleteness` (PRD §12 `complete|missing_noncritical|
  missing_critical`) + a deterministic most-severe helper (fails closed to `missing_critical`).
- `constants.py` — the mandatory cap label (proposal §5.4), the not-Verified disclaimer, the fixed
  missing-envelope constraint table, the §7 rule-coverage dependency matrix, integrity tolerance +
  method, and the narrowed coverage vocabulary. All human-reviewed constants; nothing computed.
- `builder.py` — `build_scenario(property_profile, rule_evaluation, *, assumptions=None)`, pure and
  deterministic, consuming both contracts READ-ONLY (never mutates inputs). Implements proposal §5
  precedence **malformed → conflict → professional-review → unsupported → preliminary**, surfaces the
  canonical `max_residential_floor_area_sq_ft` VERBATIM on a preliminary, and runs the
  verification-only far×lot_area integrity check that fails closed on disagreement.
- `contract.py` — `validate_scenario_document` / `ScenarioContractError` / `assert_scenario_not_verified`,
  loading the bundled schema via `importlib.resources` (mirrors `app.rules.response`); also fails
  closed on any NaN/Infinity (strict-JSON guard) and any `verified` coverage_status.
- `__init__.py` — public API surface.

**New additive contract — `packages/contracts/schemas/v1/scenario.schema.json`**
- References `coverage_status.schema.json` narrowed to exclude `verified` via the SAME `allOf` + subset
  enum pattern `rule_evaluation` uses (never redefines or edits `coverage_status.schema.json`).
- `additionalProperties:false` root with an optional fixture-only `_expected_failure` key.
- Runtime bundle copy `services/api/app/_contract_schemas/v1/scenario.schema.json` kept byte-identical
  (guarded by a dedicated test, since `sync_contract_schemas.py` SCHEMA_FILES is a forbidden edit
  target — exactly the rule_evaluation precedent).
- Generated TS `packages/contracts/generated/scenario.ts` via additive wiring in
  `packages/contracts/scripts/generate_ts_types.py` (independent `generate_scenario`/`check_scenario`/
  `write_scenario`; property_profile.ts and rule_evaluation.ts stay byte-identical) + generator unit
  tests `packages/contracts/scripts/tests/test_generate_scenario_ts.py`.
- Fixtures: `fixtures/valid/scenario/{preliminary_r5_cap,unsupported_family,no_scenario_conflict,
  no_scenario_professional_review}.json`; `fixtures/invalid/scenario/{coverage_status_verified,
  embedded_property_profile,missing_scenario_kind}.json` (the required `verified` + embedded-profile
  invalids present).

**Acceptance pack — `services/api/tests/scenario/`**
- `_support.py` (deterministic input builders), `test_scenario_foundation.py` (AS-1..AS-12 behavioral),
  `test_scenario_contract.py` (contract-layer: fixture validation, never-Verified, bundle byte-identity,
  canonical-coverage referencing, neighbouring contracts untouched).

**Only pre-existing file modified:** `packages/contracts/scripts/generate_ts_types.py` (additive
typegen wiring — within the "its generated typegen" allowance). No `app/profile/**`, `app/spatial/**`,
`app/rules/**`, `app/api/**`, `apps/web/**`, or any canonical contract schema was touched.

## 2. Self-check commands + actual outputs

Run from `services/api` unless noted; thin-client (Python only, no local npm).

```
$ python -m ruff check .
All checks passed!

$ python -m pytest tests/scenario -q
......................................................                   [100%]
54 passed in 0.38s

$ python -m pytest -q            # full API suite (regression / AS-12)
881 passed in 11.11s
```

Contract CI parity (run from repo root; CI uses `python3`, locally `python`):

```
$ python .github/scripts/validate_contracts.py
OK   packages\contracts\schemas\v1\scenario.schema.json (Scenario Foundation)
OK   packages\contracts\fixtures\valid\scenario\no_scenario_conflict.json (valid fixture passes scenario)
OK   packages\contracts\fixtures\valid\scenario\no_scenario_professional_review.json (valid fixture passes scenario)
OK   packages\contracts\fixtures\valid\scenario\preliminary_r5_cap.json (valid fixture passes scenario)
OK   packages\contracts\fixtures\valid\scenario\unsupported_family.json (valid fixture passes scenario)
OK   packages\contracts\fixtures\invalid\scenario\coverage_status_verified.json (invalid fixture correctly rejected: $.coverage_status: value 'verified' is not one of the allowed enum values [...])
OK   packages\contracts\fixtures\invalid\scenario\embedded_property_profile.json (invalid fixture correctly rejected: $: additional properties not allowed: ['property_profile'])
OK   packages\contracts\fixtures\invalid\scenario\missing_scenario_kind.json (invalid fixture correctly rejected: $: missing required property 'scenario_kind')
Checked 8 schema file(s); 0 failure(s).

$ python packages/contracts/scripts/generate_ts_types.py --check
OK: generated TypeScript types are up to date.
OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.
OK: generated rule_evaluation TypeScript types are up to date.
OK: generated scenario TypeScript types are up to date.

$ python services/api/scripts/sync_contract_schemas.py --check
OK: runtime-bundled contract schemas are byte-identical to the canonical source.

$ python -m pytest packages/contracts/scripts/tests -q
24 passed in 0.34s
```

Frontend `web` / `web-e2e` are NOT run locally (thin client) and are unaffected — zero `apps/web`
changes; `apps/web/src/lib/contract.ts` reported `unchanged` by the generator.

## 3. AS-1..AS-12 → proving test (file references)

All in `services/api/tests/scenario/test_scenario_foundation.py` unless noted.

| AS | Proof |
|----|-------|
| AS-1 confident R5 cap = canonical value | `test_as1_confident_r5_cap_surfaces_canonical_trace_value` asserts `draft_zoning_floor_area_cap_sq_ft == trace outputs.max_residential_floor_area_sq_ft`; `test_as1_value_comes_from_trace_not_recompute_even_without_far` proves the value is READ from the trace (surfaces with `max_residential_far` absent → recompute impossible). |
| AS-2 unsupported | `test_as2_unsupported_family_is_visible_stub_no_cap` (unsupported + not_applicable). |
| AS-3 missing constraint | `test_as3_missing_required_input_names_the_gap_and_infers_nothing`. |
| AS-4 spatial uncertainty | `test_as4_spatial_uncertainty_blocks_and_preserves_ranges` (share RANGES preserved on the district constraint, never collapsed). |
| AS-5 rule conflict | `test_as5_rule_conflict_blocks_and_surfaces_competing_rules`. |
| AS-6 malformed / non-finite | `test_as6_malformed_inputs_fail_closed_no_crash` (NaN/±inf/huge-int/wrong-type/non-positive on cap+lot_area; strict-JSON, no crash). |
| AS-7 integrity disagreement fail-closed | `test_as7_integrity_disagreement_fails_closed_and_surfaces_no_number` (asserts `data_conflict`, `integrity_check.agreed is False`, cap None, and neither canonical 15000 nor recompute 30000 surfaced). |
| AS-8 deterministic ordering | `test_as8_identical_input_yields_byte_identical_output` (insertion-order `json.dumps` equality across 4 kinds). |
| AS-9 never-Verified | `test_as9_no_scenario_is_ever_verified` (7 kinds; no `verified` coverage value; needs_review + disclaimer). |
| AS-10 provenance & completeness | `test_as10_provenance_and_completeness_preserved` (cap rule_id/version/status + citations verbatim; lot_area profile field + dataset resolved). |
| AS-11 explicit-assumption-only | `test_as11_variation_only_via_explicit_assumption_no_hidden_factor` (cap identical with/without assumption; only the `assumptions` array differs). |
| AS-12 regression | `test_as12_builder_never_mutates_its_inputs` + `test_as12_degenerate_empty_inputs_fail_closed_not_crash`; full suite 881 passed; `git status` shows zero changes to profile/spatial/rule-engine/canonical-contract paths. |

Contract layer (`test_scenario_contract.py`): valid/invalid fixture validation, never-Verified,
by-reference identity (no embedded profile), bundle byte-identity, coverage referencing (never
redefines the canonical enum), and property_profile/rule_evaluation contracts untouched.

## 4. §5a hard-prohibition confirmations

- **No independent legal calc as the surfaced value** — the cap is read from `trace.outputs`
  (`_find_residential_far_trace` + surface); the only multiply is the VERIFICATION-ONLY integrity
  check that never replaces the value and fails closed (AS-1 no-far test + AS-7).
- **No inference of height/stories/setbacks/yards/parking/lot-coverage/efficiency/unit-count/
  gross-to-net/constructability** — all emitted `missing` with `value: null` (constants
  `MISSING_ENVELOPE_CONSTRAINTS`; AS-3 asserts they stay missing with no value).
- **No relabeling** — the cap always carries `DRAFT_CAP_LABEL` (proposal §5.4) verbatim (AS-1).
- **No hidden utilization/optimization defaults** — a preliminary equals the raw cap; assumptions are
  recorded verbatim and never applied to the value (AS-11).
- **Never `verified`** — narrowed schema enum + `assert_scenario_not_verified` on every document +
  AS-9 exhaustive check.
- **Fail closed** — malformed/conflict/professional-review/spatial/missing-input all yield
  `no_scenario`/`unsupported` with no cap and no crash (AS-2..AS-7, AS-12 degenerate).

## 5. Coverage-matrix note

Every scenario emits the §7 rule-coverage dependency matrix (`constants.COVERAGE_MATRIX`): only the
R5 residential-FAR row is `draft`; height, setbacks/yards, lot-coverage/open-space, street-wall, and
special-districts rows are `missing` and `blocks_buildable_envelope: true`; tower + gross-to-net rows
are `out_of_scope`. Top-level `data_completeness` is deterministically `missing_critical` even on a
preliminary — the honest signal that a floor-area cap is NOT a buildable envelope.

## 6. Assumptions / limitations / boundary

- Lot area + zoning district are consumed from the `rule_evaluation` canonical inputs; lot-area
  provenance is enriched by resolving `input_provenance.lot_area_sq_ft` refs into the profile's
  `provenance` array (source_id + dataset_version). A profile without those records still yields a
  valid scenario (provenance `resolved: []`).
- Added a bbl cross-check: a profile↔rule_evaluation `bbl` disagreement is treated as `data_conflict`
  (fail closed). This is an additive safety guard beyond the literal spec.
- **Acceptance boundary (unchanged):** M5-T001 may be built + independently reviewed now, but FINAL
  acceptance waits on its M4 dependencies clearing genuine G6 legal approval (M4-T001). G6 is NOT
  weakened; B-010 is not a blocker here.
- No endpoint added (service-layer only this slice); no UI/3D (holds active).

## 7. Frozen-SHA candidate

The final commit on the branch below is the proposed FROZEN SHA for the G1/G3/G4/G5 wave. (Recorded by
the orchestrator; see the returned commit hash.)
