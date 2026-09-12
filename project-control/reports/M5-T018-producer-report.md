# M5-T018 producer report — C1 web contract mirror + Compare rendering (D-041:D-041-R001)

Producer: frontend-engineer
Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a850ed7092df8adde`
Worktree branch: `agent-a850ed7092df8adde` (detached work committed on the isolated worktree)
Base (packet) commit: `6919dab2` (contains the M5-T018 packet + the M5-T017 server material at 45f63efb: the section, the updated schema, and the four updated shared contract fixtures)
Final commit: `1b2495da`
Directive binding: D-041 → D-041-R001.

## Summary

M5-T017 added a REQUIRED root key `unused_draft_zoning_floor_area` to the closed
scenario contract and updated the four shared contract fixtures to carry it. The
hand-written web mirror validator `apps/web/src/lib/scenario-contract.ts` did not
know the key, so `checkNoUnknownKeys` rejected every fixture document at the top
level — turning every Compare test that renders a scenario into a
`validation_failure`, red on CI web-e2e at 08bf965b (run 34689359382). The
deployed UI would have rejected real updated API responses identically.

This task:
1. Taught the mirror validator the new REQUIRED section and its closed inner
   shape, mirror-faithful to the schema `$defs`.
2. Rendered the C1 line on the Compare screen as its own labeled line beneath the
   cap line, on every branch, with the three honest states.
3. Added S1–S4 tests (validator fidelity + the three render states) with local
   computed/over_built fixture variants derived from the shared preliminary
   fixture — the shared fixtures were NOT edited (forbidden; they are M5-T017's).

No file outside `allowed_paths` was touched. `packages/contracts/**` and
`services/api/**` (M5-T017, in flight) were read-only.

## What changed, per file

### `apps/web/src/lib/scenario-contract.ts` (validator — mirror update)
- Added `"unused_draft_zoning_floor_area"` to `SCENARIO_KEYS` (now a documented,
  required key; a document MISSING it fails because `checkUnusedFloorArea`
  rejects a non-object).
- Added the type alias `UnusedFloorAreaSection = Scenario["unused_draft_zoning_floor_area"]`
  and two runtime enum arrays with the same two-way `MutuallyEqual` tsc proof the
  file already uses for its other enums, so they can never silently diverge from
  the generated union:
  - `UNUSED_FLOOR_AREA_STATES` = computed / over_built / not_computable
  - `UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS` = missing_existing_building_area /
    existing_building_area_unusable / no_draft_far_cap
  - both added to `ScenarioEnumAssertions`.
- Added closed key sets: `UNUSED_FLOOR_AREA_KEYS`, `UNUSED_FLOOR_AREA_INPUTS_KEYS`,
  `UNUSED_FLOOR_AREA_CAP_INPUT_KEYS`, `UNUSED_FLOOR_AREA_EXISTING_INPUT_KEYS`.
- Added two local primitives (the shared checks module `scenario-contract-checks.ts`
  is out of scope): `checkNullableFiniteNumber` (number-or-null, rejects NaN/Inf)
  and `checkNullableObject` (schema `type:["object","null"]`, arrays excluded).
- Added `checkUnusedFloorAreaInputs` (closed inputs object + its two closed
  sub-objects) and `checkUnusedFloorArea` (the section), wired in after
  `checkIntegrityCheck`.
- Generalised `checkAssumptions` to take an `arrayPath` (the `$defs/assumption`
  shape appears both at the root and inside the section); the root call now passes
  `"assumptions"`. Emitted paths are byte-identical to before, so no existing
  assumptions test changes.

### `apps/web/src/components/compare/UnusedFloorAreaSection.tsx` (NEW focused component)
Renders `document.unused_draft_zoning_floor_area`. Mounted once by ScenarioResult
on every branch (the section rides every document). Free text it newly surfaces
(`label`, `scope_note`, `over_built_statement`) is length-capped/control-stripped
via `boundedText` at the point it is read (see the bounding note below). Renders
the three honest states (per state table below).

### `apps/web/src/components/compare/ScenarioResult.tsx` (wire-in)
Imports and mounts `<UnusedFloorAreaSection document={document} />` directly after
the branch-specific cap card / no-scenario block (i.e. beneath the cap line), and
before the other document-level blocks. One import + one element; no other change.

### `apps/web/src/components/compare/__tests__/scenario-fixtures.ts` (LOCAL variants)
Added `computedUnusedFloorAreaBody`, `overBuiltUnusedFloorAreaBody`,
`notComputableUnusedFloorAreaBody`, and a `zoningLotExtentAssumption` helper. The
computed/over_built remainder is DERIVED from the preliminary fixture's own draft
cap (15,000) minus a test-chosen existing area — never an invented official value.
The shared fixtures under `packages/contracts/` were not touched.

### `apps/web/src/components/compare/__tests__/unused-floor-area.test.tsx` (NEW)
S1 (validator fidelity + negatives), S2 (computed render), S3 (over_built honest
render + accessibility), S4 (all three not_computable reasons).

## Validator fidelity table (mirror vs schema `$defs`)

Schema source: `packages/contracts/schemas/v1/scenario.schema.json`
`$defs/unused_draft_zoning_floor_area` and `$defs/unused_floor_area_inputs`
(read-only). Generated type: `packages/contracts/generated/scenario.ts` lines 88–113.

| Schema field | Schema type | Validator check |
|---|---|---|
| (whole section) | object, `additionalProperties:false`, required on root | `checkUnusedFloorArea`: `isRecord` + `checkNoUnknownKeys(UNUSED_FLOOR_AREA_KEYS)`; missing/non-object → fail |
| `state` | enum computed/over_built/not_computable | `checkEnum(UNUSED_FLOOR_AREA_STATES)` |
| `unused_draft_zoning_floor_area_sq_ft` | number \| null (never NaN/Inf) | `checkNullableFiniteNumber` (negative accepted; NaN/Inf rejected) |
| `unit` | string \| null | `checkNullableString` |
| `label` | non_empty_string | `checkNonEmptyString` |
| `scope_note` | non_empty_string | `checkNonEmptyString` |
| `formula` | string \| null | `checkNullableString` |
| `professional_review_required` | boolean | `checkBoolean` |
| `over_built_statement` | string \| null | `checkNullableString` |
| `not_computable_reason` | enum \| null | inline enum-or-null against `UNUSED_FLOOR_AREA_NOT_COMPUTABLE_REASONS` |
| `inputs` | object, closed | `checkUnusedFloorAreaInputs` + `checkNoUnknownKeys(UNUSED_FLOOR_AREA_INPUTS_KEYS)` |
| `inputs.draft_zoning_floor_area_cap` | object closed {value_sq_ft, unit, provenance} | closed keys + `checkNullableFiniteNumber` / `checkNullableString` / `checkNullableObject` |
| `inputs.existing_building_floor_area` | object closed {value_sq_ft, unit, coverage_status, provenance_ref, provenance} | closed keys + finite-or-null / nullable-string ×3 / nullable-object |
| `assumptions` | array of `$defs/assumption` | `checkAssumptions(path)` (bounded array + closed record per element) |

Unknown keys fail at every object level (`checkNoUnknownKeys` at the section, the
inputs object, and each inputs sub-object). The pre-existing unknown-top-level-key
rejection is untouched (the section key was ADDED to `SCENARIO_KEYS`, nothing was
removed). Cross-field state coupling (null on not_computable, negative on
over_built) is intentionally NOT re-imposed here: JSON Schema declares `value` as
number-or-null on every state, so a mirror-faithful validator accepts that shape
and surfaces the server's honest state verbatim. In particular an over-built
NEGATIVE remainder is a VALID document — never rejected, never clamped.

## Render behavior per state (research 3.1/3.3, D-041-R001)

- **computed** — its own labeled line beneath the cap: the document's `label`
  verbatim (bounded), the exact value via `formatValue` + a "square feet" unit,
  a DRAFT-discipline label, and the document's `scope_note` directly beneath the
  number (3.1). The existing cap line is unchanged.
- **over_built** — the NEGATIVE remainder is shown exactly (`formatValue(-5000)`
  → "-5,000"); never clamped to zero, hidden, or restyled positive. The
  document's `over_built_statement` renders verbatim as its own explicit
  statement. A needs-professional-review notice renders as TEXT inside a
  `role="status"` region — exposed to assistive tech, not colour-only.
- **not_computable** — the standard "No supported estimate" treatment (3.3): no
  number, no invented zero, and the typed reason surfaced in plain language
  DERIVED from the document's enum (a fixed gloss per reason, the same technique
  coverage.ts uses for a coverage status; no number is invented).

Naming discipline: every human string is the document's own or a fixed gloss of a
typed enum; the D-041/research forbidden nouns and any approval/attestation
language are not introduced. Grep of the four changed files for the banned
phrases returns only (a) the validator's pre-existing `verified`-rejection code
and docstrings and (b) the S1 negative test that asserts `state:"verified"` is
REJECTED — no user-facing copy introduces them.

## S1–S5 → test mapping

`apps/web/src/components/compare/__tests__/unused-floor-area.test.tsx`:
- **S1 validator fidelity** — `describe("S1 …")`: accepts every valid state
  (shared not_computable + derived computed/over_built + all three reasons);
  FAILS missing section, unknown inner key, unknown nested-inputs key,
  out-of-enum state, out-of-enum reason, NaN value; ACCEPTS an honest negative
  over_built; still rejects an undocumented TOP-LEVEL key (no weakening).
- **S2 computed line** — `describe("S2 …")`: value derived from the fixture cap
  (asserted `=== 5000` then DOM literal `"5,000"` to catch a formatter
  regression), "square feet" unit, label verbatim (`=== section.label`),
  scope_note beneath (`=== section.scope_note`), DRAFT label, cap line unchanged
  (`scenario-cap-value === "15,000"`).
- **S3 over_built** — `describe("S3 …")`: value `=== -5000` and DOM `"-5,000"`
  (asserted NOT "5,000" and NOT "0"), `over_built_statement` verbatim, review
  notice `role="status"` carrying "professional review".
- **S4 not_computable** — `describe("S4 …")`: three cases (shared preliminary =
  missing_existing_building_area; shared professional-review = no_draft_far_cap;
  local variant = existing_building_area_unusable) — no value node, "No supported
  estimate", the plain-language reason, rest of scenario still renders.
- **S5 suites green, no weakening** — not a new test but the aggregate outcome:
  adding the key to the validator is what makes the previously-red fixture-
  consuming suites (compare-screen, compare-entry, and the fixture-acceptance
  cases in scenario-contract.test.ts) render `scenario-result` again. No existing
  assertion was deleted or loosened; the only edit to an existing suite path was
  additive (new fixtures + the new test file). The `checkAssumptions` signature
  change is path-preserving, so the existing assumptions assertions are unchanged.

## Bounding note (deliberate design decision)

`boundScenarioDocument` (`apps/web/src/lib/scenario-bounds.ts`) length-caps and
control-strips the server text it surfaces, but it spreads the new section
through unchanged via `{...document}` (it predates the section), and that file is
OUT of this task's scope (allowed_paths cover only `scenario-contract.ts` +
`components/compare/**`). Consistent with the module's own documented
"bounded where it is read" doctrine (scenario-bounds.ts lines 52–54, for the
weakly-typed provenance the display readers in scenario-display.ts walk), the
section's newly-surfaced free text (`label`, `scope_note`, `over_built_statement`)
is bounded HERE, at render, via `boundedText`. If a later task widens
`scenario-bounds.ts` to bound the section centrally, this render-time bound
remains a correct no-op backstop.

## Verification — thin client: local execution was IMPOSSIBLE

Per the packet and `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` there is no
`node_modules` and no local npm on this machine, so vitest/tsc/eslint could not
be run locally. CI (`web` = lint+typecheck+build, `web-e2e` = vitest+Playwright)
is the executable authority and runs after the orchestrator pushes. What I
verified by source reasoning instead:

- **Validator vs schema**: built the fidelity table above field-by-field against
  the schema `$defs` and the generated TS type (scenario.ts 88–113); confirmed
  every check matches the declared type and that unknown keys fail at each level.
- **The four shared fixtures pass**: read each fixture's `unused_draft_zoning_floor_area`
  block (preliminary = not_computable/missing_existing_building_area with cap
  15000; the three no-scenario/unsupported = not_computable/no_draft_far_cap with
  null cap) and traced each field through the new checks — all pass.
- **Red→green trace**: re-read compare-screen.test.tsx, compare-entry.test.tsx,
  and scenario-contract.test.ts at the base; the failure is the top-level
  unknown-key rejection of the section, and adding the key to `SCENARIO_KEYS` +
  the structural checks is exactly what restores `scenario-result`.
- **New tests vs component**: traced every S1–S4 assertion against the exact
  testids and text the component emits, and confirmed the constructed
  computed/over_built/not_computable bodies pass the new validator (so
  CompareScreen reaches the render path). NaN test calls `validateScenarioDocument`
  directly (not through `jsonResponse`), so the NaN is not serialized to null.
- **Modularity**: `python tools/modularity_check.py --check` → `selected 394
  files; failures 0; warnings 16` (scenario-contract.ts NOT among the warnings;
  the new component is a focused module). This is the one gate runnable on the
  thin client and it PASSES.

## Deviations / disclosures

- No files outside `allowed_paths` were edited. (M5-T017 disclosed a fixture +
  generated-TS scope expansion on ITS side; those files are read-only here and
  were consumed as-is.)
- One in-scope design decision recorded above: the section's free text is bounded
  at render (compare/**) rather than in the forbidden `scenario-bounds.ts`.
- No blockers. `git push` / `gh` / `project_control.py` not run (orchestrator
  authority). CI is the executable authority for the vitest/Playwright evidence.
