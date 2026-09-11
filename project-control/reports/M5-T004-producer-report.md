# M5-T004 — Compare (Step 3) UI — Producer Report

**Status: DELIVERED (code + acceptance tests written; awaiting the independent gate).**
**Producer:** frontend-engineer (persistent-local-20). **Branch:** `task/M5-T004-compare-ui`.
**Base SHA:** `1c8945be` (packet tool-discipline commit; the `allowed_paths` fix `16d085c2`
un-blocked the earlier BLOCKED state — see §0). No credentials, no backend change, no Supabase,
no Geoclient. **I did NOT run the frontend test commands** (thin-client policy: `apps/web/node_modules`
is not installed on the owner PC, and "no local npm" is standing policy). Frontend green is
CI-/orchestrator-captured at gate time (same division of labor as M5-T003). **No green is claimed.**

---

## 0. Prior blocker, resolved

The first attempt was BLOCKED by a control-plane `allowed_paths` trailing-slash mismatch (new files
under directory patterns were un-writable). The orchestrator corrected the packet globs (commit
`16d085c2`, "fix allowed_paths globs so worker file-writes auto-approve"): the `lib` deliverables are
now the auto-approving `apps/web/src/lib/scenario-*` + `validate-scenario.ts` globs, and the compare
route/components globs use `**`. Every file below wrote through the broker without a hold.

---

## 1. What was delivered (all inside `allowed_paths`)

### Library (hardened client + contract + display vocab)
| Path | Purpose |
|---|---|
| `apps/web/src/lib/scenario-contract.ts` | Type-only re-export of the GENERATED `packages/contracts/generated/scenario.ts` vocabulary + a RUNTIME `validateScenarioDocument` (mirror of `validate-profile.ts`): every 200 body is checked against the documented key set and contract-locked enums, `verified` is rejected, failure is total (bounded problem list only). Two-way `MutuallyEqual` tsc proof locks the enum arrays to the generated unions. |
| `apps/web/src/lib/scenario-api.ts` | Hardened typed client `fetchScenario(bbl)`: EXACT `(HTTP status, body state)` pair matrix mirroring `scenario.py STATUS_STATE_MATRIX` **plus** the flag-off `(404, null)` → `feature_unavailable`; every 200 body runtime-validated BEFORE returning `{kind:"scenario"}`; bounded reflected text + allowlisted correlation id; `AbortController` + timeout (`aborted` / `client_timeout`); typed outcome union; `classifyScenario()` + `announcementForScenario()`. Offline by construction (`fetchImpl` injectable). |
| `apps/web/src/lib/scenario-display.ts` | Display-only vocab + safe readers: `SCENARIO_KIND_LABELS`, `CONSTRAINT_STATE_LABELS`, `COVERAGE_MATRIX_STATUS_LABELS`, `findConstraint`, `missingCoverageGaps`, and `baseDistrictCandidates` (preserved base-district share ranges, never collapsed) / `ruleConflict`. No legal or numeric computation. |

### Route + components
| Path | Purpose |
|---|---|
| `apps/web/src/app/property/compare/page.tsx` | Step-3 route: `Suspense` + `CompareEntry` reading `?bbl=`; `metadata.title`. Mirrors `property/confirm/page.tsx`. |
| `apps/web/src/components/compare/CompareScreen.tsx` | Client orchestrator: fetch + state machine + persistent `OutcomeAnnouncer` (aria-live) + deterministic focus-to-outcome-heading + Retry. Exports `CompareScreen({bbl, fetchImpl?})` and `CompareEntry()`. Mirrors `ConfirmScreen`. |
| `apps/web/src/components/compare/ScenarioResult.tsx` | Success renderer — the Step-3 blocks: coverage-status header, cap (block 1), practical-usable-range honesty disclosure (block 2), ranked card or no_scenario reason + preserved share ranges (block 3), coverage labels + gaps (blocks 5–6), opportunity + risk (block 7), one clear next action (block 8). |
| `apps/web/src/components/compare/ScenarioCard.tsx` | The single ranked card: cap **verbatim** + `cap_label` verbatim + draft/needs_review label + NAMED objective (`cap_provenance.output_name`) + constraint breakdown + `integrity_check` surfaced verbatim. |
| `apps/web/src/components/compare/CoverageMatrixSection.tsx` | Full coverage vocabulary as distinct TEXT labels (verified/conditional/professional_review_required/data_conflict/unsupported/not_applicable — plain text, NOT badges, so no `.status-verified` node → S7 honesty preserved) + every MISSING family listed as a gap with `governs` + blocks-envelope marker. |
| `apps/web/src/components/compare/ScenarioFailureStates.tsx` | First-class failure/`feature_unavailable` states (mirror `property/FailureState.tsx`): each with the allowlisted correlation id + Retry (recoverable only), nothing partially rendered, no raw stack/secret/invented scenario. |

### Confirm rewire (narrow edit)
| Path | Change |
|---|---|
| `apps/web/src/components/confirm/ConfirmScreen.tsx` | Replaced the "steps 3–4 arrive later" dead-end with a labelled primary link **`Compare preliminary scenario`** → `/property/compare?bbl={profile.identity.bbl}` (keyboard-reachable), keeping the secondary "Back to property lookup". No restructure; the Confirm tests are untouched. |

### Tests
| Path | Purpose |
|---|---|
| `apps/web/src/components/compare/__tests__/scenario-fixtures.ts` | Imports the COMMITTED M5-T003 fixtures (`preliminary_r5_cap`, `no_scenario_professional_review`, `no_scenario_conflict`) read-only; reuses `jsonResponse` from `@/test-support/fixtures`; adds `notFoundResponse()` (flag-off `404 {"detail":"Not Found"}`, no correlation id, no state), `stateResponse()`, and `stubFetch()`. |
| `apps/web/src/components/compare/__tests__/compare-screen.test.tsx` | vitest + RTL, AS-1..AS-8 (see §2) + `fetchScenario` unit coverage (client_timeout, aborted, validated-200). |

---

## 2. Acceptance-scenario coverage (AS-1..AS-8 → tests)
- **AS-1** preliminary cap: asserts the rendered `scenario-cap-value` **=== `formatValue(body.draft_zoning_floor_area_cap_sq_ft)`** (fixture cap `15000`) — the client transports, never recomputes; draft label + NAMED objective (`max_residential_floor_area_sq_ft`) + verbatim `cap_label` + constraint breakdown + integrity check all present.
- **AS-2** `no_scenario_professional_review`: reason + review-required label + **preserved share ranges** (`0.4/0.55/0.7` and `0.3/0.45/0.6`, districts R5/R6) rendered, **NO cap**, remains an informative result (`scenario-result` present, never an error). Second case: the `no_scenario_conflict` fixture also renders informatively.
- **AS-3** every coverage status renders as a distinct TEXT label; the preliminary fixture's **8** MISSING families are listed as gaps (count asserted `=== 8`), envelope-blocking families marked.
- **AS-4** contract safety: a malformed 200 body → `validation_failure` (only the correlation id, nothing partial); a `(418, "teapot")` pair outside the matrix → `unexpected_response` (state echoed, nothing rendered).
- **AS-5** flag-off `404` → benign `feature_unavailable` (no correlation id, no Retry); `source_unavailable`/`rate_limited`/`timeout`/`schema_drift` each render recoverable with the correlation id + Retry; a Retry recovers to a preliminary success; `client_timeout` proven at the client unit level.
- **AS-6** navigation: `ConfirmScreen` (rendered with a stubbed profile fetch) exposes `confirm-next-compare` → `/property/compare?bbl=1000010010`; the Compare next action preserves `?bbl=` in the confirmed-property link.
- **AS-7** offline/no-credentials: every test drives the screen through an INJECTED `fetchImpl` (or a stubbed global for the Confirm wiring) over the committed fixtures — no network, no Supabase, no Geoclient.
- **AS-8** accessibility: the persistent `compare-announcer` (`aria-live="polite"`) carries the single arrival announcement; focus moves to the `data-outcome-heading` on success AND on failure; headings are semantic; no material state by color alone (RTL assertions — `jest-axe` is not a project dependency and adding one is out of scope under the age gate).

## 3. e2e note (`npm --prefix apps/web run test:e2e`)
`apps/web/e2e/harness/fixture_api.py` (read-only; not in my `allowed_paths`) enables
`INTERNAL_RULE_EVAL_ENABLED`, **not** `INTERNAL_SCENARIO_ENABLED`, and maps no scenario BBLs, so a
Playwright e2e cannot drive the real scenario endpoint without extending that harness (a separate,
out-of-scope file). AS-7 is fully satisfied by the vitest/fixture path (the packet allows "and/or the
Playwright e2e"). **Recommend to the orchestrator:** accept the vitest offline proof for AS-7, or open
a follow-up to extend the harness with `INTERNAL_SCENARIO_ENABLED` + scenario BBL routing.

## 4. Verification honesty
- I did **not** run `npm --prefix apps/web run test` / `run typecheck` / `run test:e2e` — the owner PC
  has no `apps/web/node_modules` and "no local npm" is standing thin-client policy. **No green is
  claimed.** The gate should capture the three commands in CI (`web-e2e` job runs `npm ci` once).
- All rendered material values (cap, share ranges, coverage status, objective, integrity check) are
  transported VERBATIM from the validated endpoint body; the client never computes a legal value
  (`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`).
- Read-only templates (`api.ts`, `contract-matrix.ts`, `bounded.ts`, `validate-profile.ts`,
  `components/property/**`) were imported, never modified (forbidden_paths respected).

---

# REWORK ADDENDUM (gate wave at `84815a76`: G1 FAIL, G3 FAIL, G4 FAIL, DCV FAIL, G5 PASS-with-binding-spec)

**Reworked by:** a producer that did NOT author the original packet. **Base:** `0c810887` (control head
carrying the five gate reports). Sections 0–4 above describe the PRE-rework delivery and are left intact
as the historical record; everything below supersedes them where they conflict.

## R1. The core defect and what fixed it

The transport was never wrong — DCV traced 515 leaves and found **0 authored legal/numeric values**, and
the cap is byte-faithful. The defect was **silent projection at the render layer**: 19 schema-required
fields never reached the screen, and the two render branches were disjoint so neither ever showed the
whole document. The fix is composition, not new presentation: everything belonging to the DOCUMENT
rather than to one branch is now mounted once in `ScenarioResult` for every branch, converging on the
accepted sibling `components/rule-evaluation/RuleEvaluationResult.tsx` (read-only; not edited).

| Dropped field | Now rendered at |
|---|---|
| `contract_version` | `ScenarioProvenance.tsx` (`scenario-contract-version`) |
| `data_completeness` (top level) | `ScenarioResult.tsx` via the existing `completenessDisplay()`, in the `completeness-banner` treatment the property screen uses |
| `evaluated_input` (all 4 leaves) | `ScenarioProvenance.tsx` |
| `assumptions[]` (all 5 leaves) | `ScenarioAssumptions.tsx`, **with an explicit statement when empty** — every committed fixture carries zero assumptions, so that IS the shipped path |
| `cap_provenance.citations` (all leaves) | `ScenarioProvenance.tsx`, collapsed `<details>` mirroring `RuleEvaluationResult.tsx:107-150` |
| `constraints[].note` | `ScenarioConstraints.tsx` |
| `constraints[].provenance` | `ScenarioConstraints.tsx`, via the generic `provenanceLeaves()` walk |
| `integrity_check.tolerance` | `ScenarioConstraints.tsx` (`scenario-integrity-tolerance`) |
| `reasons` (dropped on preliminary) | `ScenarioReasons.tsx`, mounted on **both** branches |
| `constraints` + `integrity_check` (dropped on no_scenario/unsupported) | hoisted into `ScenarioResult.tsx` |
| `coverage_matrix` (silently filtered to `missing` rows) | full matrix + the gap list, `CoverageMatrixSection.tsx` |

`constraints[].provenance` is typed `unknown` by the contract, so it is rendered by a GENERIC leaf walk
rather than a hand-listed subset — a hand-listed subset is exactly what dropped `review_reasons`,
`coverage_note`, `lot_overall_class` and `pair_class`. Both the width and the strings of that walk are
bounded, and every bound it applies is DISCLOSED on screen.

## R2. Identity bound to the document (DCV CRITICAL-2 / G1-7)

`ScenarioResult.tsx` now heads the result with `document.evaluated_input.bbl` (null → "not stated", the
`RuleEvaluationResult.tsx:87` precedent) and renders an explicit IDENTITY MISMATCH block when the
document disagrees with the requested BBL — both values shown, nothing reconciled. The test fixtures and
props were corrected to agree (`FIXTURE_BBL = "1000477501"`, which is what all four committed fixtures
state), and the disagreement the old suite shipped silently is now its own asserted test case.

## R3. Conflict path wired (G1-6 / G3-7 / G4-3 / DCV-6)

`ruleConflict()` had zero consumers repo-wide while the UI printed "both values are shown, nothing was
resolved" twice and showed neither. `scenario-display.ts` adds `ruleConflicts(document)` (scans EVERY
constraint, not only `residential_far_cap`), and `NoScenarioBlock.tsx` renders the competing output
names, the competing rules with versions and effective dates, and the conflicting constraint VALUES.

## R4. Validator depth (G4-2, G5-1/3, G1-9)

`scenario-contract.ts` + the new `scenario-contract-checks.ts` (modularity split; the public import
surface is unchanged by a compatibility re-export):
`checkCapProvenance` type-checks all six fields and **requires `cap_provenance !== null` whenever the cap
is non-null**; `citations` element shapes are checked; `assumptions[].value`/`.unit` are checked;
`constraints[].value` and `assumptions[].value` are pinned to the schema's scalar union (closing the
object-into-the-DOM path); unknown keys are rejected at every object level; `needs_review` is pinned to
`true`. All 37+ problem messages remain static literals — no byte of a rejected body can reach the DOM.

## R5. G5 bounding spec (implemented as written)

`MAX_DOCUMENT_ARRAY_LENGTH = 64`, one shared constant, **REJECT** for every document array (exactly 64
accepted, 65 rejected); free text **TRUNCATES** at the existing `MAX_REFLECTED_TEXT_LENGTH` with the
existing `TRUNCATION_MARKER` (new `scenario-bounds.ts`); identifiers truncate at `MAX_TOKEN_LENGTH` via
`boundedToken`; a 256 KiB `Content-Length` check runs before `.json()`. **No dependency added.**
Material values (the cap, every number, `constraints[].value`, `evaluated_input.bbl`) are deliberately
NOT transformed — the file documents each exclusion and why.

## R6. Also delivered

`.status-label` and `.section-subtitle` defined in `globals.css` (the caution now outweighs the number it
qualifies, by weight + a left rule, never by color alone); `app/property/error.tsx` route error boundary
(digest only, never `error.message`); `e2e/harness/fixture_api.py` enables `INTERNAL_SCENARIO_ENABLED`;
`e2e/compare-journey.spec.ts` adds five browser journeys — the first anywhere in the repo that reach
`/property/compare`.

## R7. Verification honesty (unchanged policy)

`apps/web/node_modules` is still absent; **the three documented test commands were NOT run and no green
is claimed.** What WAS executed offline, and is reproducible: `tools/modularity_check.py --check`
(377 files, 0 failures, 16 warnings — the G4 baseline, none of them these files), a full strict-mode
TypeScript program over the scenario lib layer (zero diagnostics; that layer has no external imports),
and a transpile-and-run harness exercising the validator, the bounding pass and the display readers
against the four committed fixtures plus adversarial bodies (31 assertions, 0 failures). That harness is
the producer's own scratch tooling, NOT the project suite — CI remains the only authority.
