# GATE REPORT — G3 Independent Code Re-Review — M5-T002 (post D-022 correction)

> Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel
> (transport entity-decoding only). Reviewer ≠ producer. Supersedes the invalidated
> M5-T002-G3-code-review.md conclusions (prior identity 2fee786/31e652a, D-022-R016).

**Task:** M5-T002 scenario endpoint / scenario-contract validator
**Frozen code identity:** commit `69558cd53dc7bc9ebbe649aef318e65b1aa22d0`, tree `ee6dce0f29416e6637dd46382872a88a25578ce1`
**HEAD:** `7f9231edbd04aaf33e68b986dd643af4aa2ff916` (branch `task/M5-T002-scenario-endpoint`)
**Reviewer:** code-reviewer (independent; not the producer). Prior PASS at 2fee786/31e652a is invalidated per D-022-R016 and is NOT relied upon.

## (1) VERDICT: **PASS**

No blocking corrections. The D-022 correction faithfully closes all 8 owner-reproduced bypasses, is faithful to the canonical schema in both directions (enforces everything the schema states; invents nothing that would reject a legitimate canonical document), routes every 200-body validator failure to `validation_failure` before classification, preserves all prior assertions and the bounded-Problems / MutuallyEqual proofs, adds no dependencies, and touches exactly the 4 expected files. CI is 20/20 success at HEAD and the API suite is 144 passed.

## Identity pre-check (verified first, as instructed)
- `git diff 69558cd..HEAD --name-only` → only 4 files, all under `project-control/**` (`reports/M5-T002-evidence-map.json`, `reports/M5-T002.json`, `state.json`, `tasks/M5-T002.json`). Code identity is unchanged from the frozen SHA. PASS.
- `git rev-parse 69558cd^{tree}` = `ee6dce0f…` matches the contracted tree. PASS.
- `git diff 2d9eb74..69558cd --name-only` = exactly `apps/web/src/lib/__tests__/scenario-contract.test.ts`, `apps/web/src/lib/__tests__/scenario.test.ts`, `apps/web/src/lib/scenario-contract.ts`, `project-control/reports/M5-T002-producer-report.md` — the 4 expected files, no unrelated file touched. PASS.

## (2) Per-bypass trace table (traced line-by-line against `apps/web/src/lib/scenario-contract.ts` at 69558cd)

| # | Adversarial input | Rejecting function / line | Mechanism |
|---|---|---|---|
| 1 | `draft_zoning_floor_area_cap_sq_ft = -1` | `validateScenarioDocument` L522–533 | `isFiniteNumber(-1) && -1 > 0` is false, not null → problem added. (old code allowed any `typeof === "number"`) |
| 2 | `draft_zoning_floor_area_cap_sq_ft = 0` | `validateScenarioDocument` L522–533 | `0 > 0` false → rejected (schema `exclusiveMinimum: 0`) |
| 3 | `evaluated_input.bbl = "x"` | `checkEvaluatedInput` L292–294 | `BBL_PATTERN.test("x")` false → rejected (old code only required non-empty string) |
| 4 | `cap_provenance.rule_status = "verified"` | `checkCapProvenance` L418 → `checkEnum` L269–271 | not in `CAP_PROVENANCE_RULE_STATUSES` (old code only checked `typeof === "string"`) |
| 5 | `cap_provenance.citations = [null]` | `checkCapProvenance` L419–425 → `checkCitation` L374–376 | array items now iterated; `!isRecord(null)` → "must be a citation object" (old code only checked `Array.isArray`) |
| 6 | `assumptions = [null]` | `validateScenarioDocument` L539–545 → `checkAssumption` L351–353 | array items now iterated; `!isRecord(null)` → "must be an object" (old code only checked `Array.isArray`) |
| 7 | unexpected top-level property | `validateScenarioDocument` L490 → `checkKnownAndRequiredKeys` L251–255 | key not in `SCENARIO_REQUIRED_KEYS ∪ SCENARIO_OPTIONAL_KEYS` → "is not a documented property" (old code had NO root key check) |
| 8 | `embedded_property_profile.json` | `validateScenarioDocument` L490 → `checkKnownAndRequiredKeys` L251–255 | extra root key `property_profile` rejected; `_expected_failure` string is allowed (in optional keys, passes L491). Exactly the fixture's stated defect. |

Also independently confirmed the extra hardening tests pass: `+Infinity`/`NaN` cap rejected (L525 `isFiniteNumber`), and constraint `provenance = []` rejected (L342 `isRecord`, the former `typeof === "object"` array hole).

## Schema faithfulness (scenario.schema.json + common.schema.json `$defs`)
Enforces every schema constraint: root and all 7 nested `additionalProperties:false` + full `required` presence; BBL pattern `^[1-5][0-9]{5}[0-9]{4}$`; digest `^sha256:[0-9a-f]{64}$`; strictly-positive-or-null finite cap (`exclusiveMinimum:0`); `cap_provenance.rule_status` enum; full citation (incl. required-object `provenance`, optional `last_amended`), assumption, constraint, coverage-matrix-row, integrity-check shapes; provenance is `isRecord` (rejects arrays, faithful to JSON-Schema `"object"`); `Number.isFinite` on cap, constraint/assumption values, and `tolerance`. The fixture-only optional `_expected_failure` string is ALLOWED at root only (L147, L490–493) and correctly excluded from nested objects.

Enforces NOTHING extra: cross-checked against all 4 committed valid fixtures — `preliminary_r5_cap.json` traced fully to `ok:true`; `no_scenario_conflict.json`, `no_scenario_professional_review.json`, `unsupported_family.json` each use only the 16 root keys, null cap/`cap_provenance` (early-return at L407), and object (non-array) provenance — none trip any new check. All 3 invalid fixtures fail (`embedded_property_profile.json` → `property_profile`; `coverage_status_verified.json` → `coverage_status` enum; `missing_scenario_kind.json` → required-key + enum).

MutuallyEqual proofs correct: generated `packages/contracts/generated/scenario.ts` has `rule_status: "discovered" | "extracted_draft" | "needs_review" | "published"` and `rule_status_today: "draft" | "missing" | "out_of_scope"`, matching `CAP_PROVENANCE_RULE_STATUSES` and `COVERAGE_MATRIX_RULE_STATUSES` exactly; the two new `ScenarioEnumAssertions` tuple slots (L116–117) are sound; `contracts-typegen` byte-identical drift CI is green.

## fetchScenario boundary (`apps/web/src/lib/scenario.ts`)
The 200 path (L332–344) routes every validator failure to `validation_failure` BEFORE constructing `kind:"scenario"`; the only site that builds `ScenarioOutcomeDoc` (L343) is gated on `validation.ok`. New tests (scenario.test.ts L159–195) assert `kind === "validation_failure"` and the specific problem path for cap=-1 (`draft_zoning_floor_area_cap_sq_ft`), null citation (`cap_provenance.citations[0]`), and the embedded-profile body (`property_profile`). Each body carries no `state`, so `(200,null)` is a documented pair and reaches validation. Directive item 8 (malformed nested data can never reach ScenarioResult) holds.

## Regression safety
- `ok:true` path still admits every valid fixture (preliminary traced fully; sweep asserts all 4).
- `git diff 2d9eb74..69558cd` on both test files is purely additive — the original `describe("validateScenarioDocument")` assertions are unchanged; no assertion weakened or deleted.
- Bounded Problems intact (`MAX_REPORTED_PROBLEMS=20`, sentinel at 21; test asserts ≤21).
- No new dependencies (no `package.json` in the diff); `web-dependency-security` CI green.
- `scenario-contract.ts` = 555 SLOC (< 600 warn); `modularity` CI green.

## (3) Numbered findings

1. **INFORMATIONAL (no action)** — `scenario-contract.ts` L193: an existing inline digest regex was extracted to the named constant `DIGEST_SHA256_PATTERN`, and `isConstraintValue` was renamed to `isContractScalar` (L230). Both are functionally motivated by the fix (grouping the new `BBL_PATTERN` constant; `isContractScalar` now also serves `checkAssumption` and its behavior changed to reject non-finite numbers), so neither is gratuitous cosmetic churn. This satisfies D-022-R013 (no cosmetic cleanup / broad refactoring beyond the fix); noted only for completeness. No change requested.

No BLOCKING or MAJOR findings.

## (4) Commands run + last lines
- `git diff 69558cd..HEAD --name-only` → 4 `project-control/**` files only.
- `git rev-parse 69558cd^{tree}` → `ee6dce0f29416e6637dd46382872a88a25578ce1`.
- `git diff 2d9eb74..69558cd --name-only` → the 4 expected files.
- `git show 69558cd:packages/contracts/generated/scenario.ts | grep rule_status` → `rule_status: "discovered" | "extracted_draft" | "needs_review" | "published";` and `rule_status_today: "draft" | "missing" | "out_of_scope";`.
- `gh api repos/martin10101/nyc-buildability/commits/7f9231e…/check-runs` → **20 contexts, all `completed success`** (incl. `web (lint + typecheck + build)`, `web-e2e (vitest + Playwright…)`, `contracts-typegen`, `contracts`, `modularity`, `api (ruff + pytest)`).
- `cd services/api && python -m pytest tests/api -q` → last line: `144 passed in 3.87s`.

## (5) What I could not / did not verify
- I did not execute the vitest or Playwright suites locally (npm/node forbidden for this reviewer). Evidence relied upon: the `web` and `web-e2e` CI contexts are `success` at HEAD `7f9231e` (the clean-checkout execution of the new vitest suites + typecheck + build + Playwright). All validator behavior above was verified by hand-tracing the source against the committed fixtures, which independently corroborates those green contexts.
- CI conclusions were read from the GitHub check-runs API for the exact HEAD SHA; I did not re-trigger CI (read-only).

Relevant absolute paths:
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/scenario-contract.ts`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/scenario.ts`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/__tests__/scenario-contract.test.ts`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/__tests__/scenario.test.ts`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/packages/contracts/schemas/v1/scenario.schema.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/packages/contracts/schemas/v1/common.schema.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/packages/contracts/fixtures/invalid/scenario/embedded_property_profile.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/project-control/directives/D-022-scenario-contract-validator-correction/source-001.md`

**FINAL VERDICT: PASS** (no blocking corrections).
