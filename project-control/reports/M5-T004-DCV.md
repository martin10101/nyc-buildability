# M5-T004 — Data-Contract Verification (DCV)

**Task:** M5-T004 — Compare (Step 3) UI
**Reviewed SHA:** `84815a7616a2519f499777cb52d283f1c26f1d4b` (rebase of producer output `a0bec4eb` onto `02379432`; diff byte-identical, 2353 insertions / 13 files)
**Reviewer role:** independent data-contract verifier (read-only; did not author the code)
**Reviewed at:** 2026-09-11
**Method:** static leaf-by-leaf tracing of all three committed M5-T003 fixtures against the traced render predicates, plus direct evaluation of the display formatter against adversarial numeric inputs. The project test suite was NOT run (`apps/web/node_modules` absent under the thin-client policy).

---

## VERDICT: FAIL

Numeric transport is clean. The failure is silent projection — the M5-T013 defect class, reproduced.

---

## Leaf classification

| Measure | Count |
|---|---|
| Total leaves traced (3 fixtures) | 515 |
| TRANSPORTED (reach the screen, value-preserving) | 191 |
| DROPPED (never reach the screen) | 324 |
| AUTHORED display values (distinct) | ~40 |
| **Authored LEGAL/NUMERIC values** | **0** |

Per fixture — `preliminary_r5_cap`: 188 leaves, 103 transported, 85 dropped. `no_scenario_professional_review`: 165 / 49 / 116. `no_scenario_conflict`: 162 / 39 / 123, including **0 of 96 constraint leaves**.

All 191 transported leaves are byte-faithful. The only numeric transform is en-US locale digit grouping, which changes no magnitude and no significant digit.

The single authored *material* value is non-numeric: the BBL identity (finding 2).

---

## Findings

### CRITICAL

**1. `cap_provenance.citations` is never rendered.**
`ScenarioCard.tsx:70-94` renders `rule_id`, `rule_version`, `rule_status`, `output_name`, `note` and stops. All 17 citation leaves — `snapshot_id`, `section`, `quote`, `last_amended`, plus the 13-leaf resolved source provenance including `request_url`, `retrieved_at`, `content_digest_sha256`, `raw_html_verified` — never reach the screen. The 15,000 sq ft cap is displayed as a material legal value with **no citation**, contradicting the contract's own rule at `scenario.schema.json:216`: *"a material value may never be surfaced without it, PRD section 19."*
*Fix:* render citations in a `<details>` disclosure mirroring `rule-eval-citations`.

**2. The displayed BBL is authored from the URL, not transported from the document.**
`ScenarioResult.tsx:167` renders `Step 3 — Preliminary comparison for BBL {bbl}`, where `bbl` is the prop threaded from `CompareEntry`'s `?bbl=` query parameter (`CompareScreen.tsx:153-159`). `document.evaluated_input.bbl` is never read — `evaluated_input` appears only in the validator, never in a compare component. **A document returned for a different BBL, or carrying `bbl: null`, would still be captioned with the requested BBL.** An authored identity binding on a legally sensitive screen.
*Fix:* display `document.evaluated_input.bbl` as the evaluated identity (`null` → explicit "not stated", per the `RuleEvaluationResult.tsx:87` precedent) and surface any mismatch rather than papering over it.

**3. Top-level `data_completeness` is dropped.**
Required field (schema line 12); value `missing_critical` in all three fixtures. The only `data_completeness` hit in the compare components is `ScenarioCard.tsx:112`, which is the *constraint-level* field. The document's most-severe completeness verdict never renders. Schema line 41 is explicit that a preliminary scenario is *"honestly missing_critical … even with the draft cap present the data is critically incomplete for a buildable envelope."* The screen instead shows only coverage `conditional`, glossed "Official source fact, not yet professionally reviewed" — **the reader sees the milder signal and never the critical one.**
*Fix:* render `completenessDisplay(document.data_completeness)` in the summary card beside the coverage label. Helper already exists at `lib/coverage.ts:79` and is used by `ConfirmScreen.tsx:180` and `PropertyLookup.tsx:99`.

**4. `evaluated_input` is dropped in full.**
All 4 required leaves: `bbl`, `profile_contract_version`, `rule_evaluation_contract_version`, `input_fingerprint`. The object exists (schema line 127) to pin which inputs produced the scenario without embedding the profile. The `input_fingerprint` (`sha256:c499fc3c…`) is the only way a consumer can confirm the scenario came from a specific input snapshot. It never renders.
*Fix:* as in `RuleEvaluationResult.tsx:84-95`.

### HIGH

**5. The `no_scenario` / `unsupported` branch drops the entire `constraints` array AND the entire `integrity_check` object.**
`ScenarioResult.tsx:178-182` routes non-preliminary documents to `NoScenarioBlock`, which renders only `reasons` and the preserved share ranges. `constraints` and `integrity_check` render only inside `ScenarioCard`. Measured on `no_scenario_conflict`: **0 of 96 constraint leaves and 0 of 5 integrity leaves render.** Contradicts schema line 61 — *"Every candidate constraint … nothing silently absent."*
*Fix:* hoist the constraint breakdown and integrity block out of `ScenarioCard` so both branches render them.

**6. `ruleConflict()` is dead code, and the screen makes a claim its render path contradicts.**
`scenario-display.ts:126-153` extracts `competing_output_names` / `competing_rules`, documented *"Competing rules are surfaced verbatim; the platform never selects a winner."* No component calls it — only `findConstraint` and `baseDistrictCandidates` are imported (`ScenarioResult.tsx:5-6`). Meanwhile `CoverageMatrixSection.tsx:68` renders the `data_conflict` gloss *"Official sources disagree; **both values are shown, nothing was resolved**."* For `no_scenario_conflict` the two competing rules (`r5-residential-far` 0.1.0-draft vs `r5-residential-far-alt` 0.2.0-draft) are never shown. **The UI asserts both values are shown while showing neither.**
*Fix:* call `ruleConflict(findConstraint(document, "residential_far_cap"))` in `NoScenarioBlock` and render the competing rules, mirroring the share-range block.

### MEDIUM

**7. `coverage_matrix` is silently projected to `missing` rows only.** `scenario-display.ts:56-58` filters `rule_status_today === "missing"`; `CoverageMatrixSection.tsx:41,83` renders only those. The preliminary fixture's 11 rows become 8 — the `draft` R5 residential-FAR row and both `out_of_scope` rows (12 leaves) never render, with no disclosure of the total. Schema line 97: *"Emitted on every scenario in a fixed order."* The heading "Rule families still missing (8)" is honest about the filter but not about the omission. *Fix:* render the full matrix with status per row, or state the total alongside the filtered count.

**8. All 11 `constraints[].note` values are dropped.** `ScenarioCard.tsx:103-115` renders `key`, `value`, `unit`, state label and `data_completeness` — no `note`. Required (schema line 158); each carries the anti-inference warning, e.g. *"No rule family provides max height / story count; recorded as a gap. MUST NOT be inferred, defaulted, or estimated."* The file's own header comment at `ScenarioCard.tsx:19` claims *"each constraint value + state + note"* is rendered. It is not. *Fix:* render the note, and correct the comment.

**9. `integrity_check.tolerance` is dropped while `method` is shown.** `ScenarioCard.tsx:133` renders `method` = `abs(recomputed - canonical) <= tolerance * max(1, abs(canonical))`, referencing a `tolerance` (1e-06) that never appears. The displayed method is uninterpretable without it. Required (schema line 262).

**10. `reasons` is dropped on the preliminary branch.** Renders only in `NoScenarioBlock` (`ScenarioResult.tsx:49-53`); `ScenarioCard` never renders it. The preliminary fixture's single reason is load-bearing: *"Preliminary scenario: surfaced the canonical draft residential zoning-floor-area cap (ZR 23-21) from the rule_evaluation trace, verbatim. NOT a buildable envelope - see the coverage matrix for the rule families still MISSING."*

**11. Coverage glosses authored for the *profile* vocabulary are reused for *scenario* semantics.** `CoverageMatrixSection.tsx:60-71` renders all six glosses from `lib/coverage.ts:22-47` (an M2-T001 file, unmodified by this diff but newly applied to this vocabulary). `unsupported` is glossed "The platform detected a data problem and cannot support this value", whereas the scenario contract defines unsupported as "the district/rule family is not implemented" (schema line 35) — **a different meaning under the same word.**

### LOW

**12.** `contract_version` ("1.0.0") is never rendered. Required, schema line 9.
**13.** The unit "square feet" is asserted by the UI (`ScenarioCard.tsx:53`, `ScenarioResult.tsx:113`), not taken from the contract. Defensible — the field name is `draft_zoning_floor_area_cap_sq_ft` — but `constraints[]` carry an explicit `unit` field while the cap does not. Worth a comment rather than a change.
**14.** `scenario_kind` renders as a mapped label only; the raw enum value never appears, unlike `coverage_status` (verbatim at `ScenarioResult.tsx:170`) and `rule_status_today` (verbatim at `CoverageMatrixSection.tsx:88`). `scenario-display.ts:24` maps `unsupported` → "Not supported yet", dropping the contract word and adding a forward-looking "yet".
**15.** `scenario-display.ts:104` — `minorPortion: record?.minor_portion === true` resolves an absent or malformed value to `false`, rendering as the *absence* of the "(minor portion)" marker. An unknown rendered as a negative assertion. Low impact; still a default-fill.

---

## Non-findings — checked and cleared

- `formatValue` (`lib/format.ts:9-24`): no rounding, no truncation. Verified against 15000, 1e-6, 0.30000000000000004, 12345.678901234567, 1234567.891, 9007199254740992, 1e21, 15000.4999999 — all preserved exactly, commas only. `maximumFractionDigits: 20` defeats the default 3-digit rounding.
- `formatValue(null)` → `"—"`: absence renders as absence, not zero, not "N/A".
- No `toFixed`, no arithmetic on any contract number. The only `Math.` is `Math.round(outcome.timeoutMs / 1000)` at `ScenarioFailureStates.tsx:279`, on the client's own 12,000 ms constant — not contract data.
- Every `??` / `||` fallback is on client-owned options or server *error* text (`scenario-api.ts:217-218, 322`), never on a legal value.
- `scenario-api.ts:274` compares the RAW `state` before sanitizing — correct. Sanitizing first could launder a malformed state into a documented one.
- `validateScenarioDocument` is total: a failure returns only a bounded problem list, and `ScenarioValidationFailureState` renders nothing from the payload.

---

## Dropped fields — summary

**Never rendered under ANY code path (top-level required):** `contract_version`, `data_completeness`, `evaluated_input` (all 4 leaves), `assumptions`.

**Never rendered (required sub-fields):** `cap_provenance.citations` (all leaves), `constraints[].note` (11 per document), `constraints[].provenance` (all leaves, incl. per-constraint citations), `integrity_check.tolerance`.

**Branch-conditional whole-field drops:** `reasons` (dropped on preliminary), `constraints` (dropped on no_scenario/unsupported), `integrity_check` (dropped on no_scenario/unsupported).

**Silently projected:** `coverage_matrix` — only `rule_status_today === "missing"` rows render; `draft` and `out_of_scope` rows filtered out with no disclosure of the total.

**Total: 8 required fields never render at all; 3 more drop on one branch each; 1 silently filtered.**

---

## In-repo precedent for the fix

`apps/web/src/components/rule-evaluation/RuleEvaluationResult.tsx:70-135` is an **accepted sibling component that already renders `evaluated_input` and citations for the same document family.** This diff diverges from it. The rework should converge on that precedent rather than invent a new presentation.

---

## What was verified

**Contracts:** `packages/contracts/schemas/v1/scenario.schema.json` (full read, 284 lines), `coverage_status.schema.json`, and the three committed fixtures under `packages/contracts/fixtures/valid/scenario/`.
**Client libs:** `lib/scenario-contract.ts`, `scenario-api.ts`, `scenario-display.ts`, plus transitive `format.ts` and `coverage.ts`.
**Components:** `compare/CompareScreen.tsx`, `ScenarioResult.tsx`, `ScenarioCard.tsx`, `CoverageMatrixSection.tsx`, `ScenarioFailureStates.tsx`, `app/property/compare/page.tsx`, and the `ConfirmScreen.tsx` diff hunk.
**Precedent:** `components/rule-evaluation/RuleEvaluationResult.tsx:70-135`.

---

## Per-AS verdicts — ALL PASS

**Critical separation for the ledger: the acceptance scenarios all PASS. This FAIL is on the data-contract completeness bar, which no acceptance scenario covers.**

**AS-1 — PASS**, with one HIGH hole and one weak guard.
*Transport verified:* `ScenarioCard.tsx:32` reads `draft_zoning_floor_area_cap_sq_ft`, `:51` renders `formatValue(cap)`. Grepped `toFixed|Math.|parseFloat|Number(` across all compare components and scenario libs — the only `Math.` is `Math.round(timeoutMs/1000)` (`ScenarioFailureStates.tsx:279`) on the client's own 12,000 ms constant. 15,000 reaches the DOM as 15,000. Objective named from `cap_provenance.output_name` (`:75-77`) ✓, score breakdown ✓, draft label present ✓.
*The test assertion is TAUTOLOGICAL.* `compare-screen.test.tsx:43-45` asserts `capNode.textContent === formatValue(bodyCap)` — **the component and the test call the same `formatValue`.** Change `maximumFractionDigits: 20` to `2`, or add rounding, and **both sides move together and the test still passes.** It cannot detect the display-magnitude regression it exists to guard. `toBe(15000)` pins the fixture *input*, not the rendered *output*; and 15000 has no fractional part, so even a literal assertion would miss a rounding regression with this fixture. *Fix:* assert a literal (`toBe("15,000")`) and add one fractional-cap fixture case.
*HIGH hole:* the "always present" label is conditional — `ScenarioCard.tsx:55` gates on `document.needs_review`; schema says always-true (`:46`) but types it a bare boolean with no `const`, and the validator only type-checks it (`scenario-contract.ts:318-322`). `needs_review: false` passes validation and the DRAFT label **silently vanishes**; with `cap_label: null` (also nullable, `:336`) a bare "15,000 square feet" renders with no draft qualifier at all. Corroborates G1 finding 9.

**CRITICAL #2 demonstrated live in the shipped test.** `compare-screen.test.tsx:27` sets `PRELIMINARY_BBL = "1000010100"` and renders `<CompareScreen bbl="1000010100">`, while **every one of the four committed fixtures carries `evaluated_input.bbl = "1000477501"`.** The AS-1 test therefore renders the heading "Step 3 — Preliminary comparison for BBL 1000010100" over a document stating it was built for BBL 1000477501 — and nothing detects it, because `ScenarioResult.tsx:167` renders the URL prop and never reads `document.evaluated_input.bbl`. **Separately: the AS-1 acceptance text itself names "fixture BBL 1000010100" while the committed fixture says 1000477501 — the acceptance criterion's premise is stale and needs correcting either way.**

**AS-2 — PASS.** Ranges genuinely not collapsed: `ScenarioResult.tsx:66-71` renders all three bounds separately per candidate — no midpoint, no single value, no bound substituted. Fixture carries R5 (0.4/0.55/0.7) and R6 (0.3/0.45/0.6); the test asserts all six plus both district labels (`:84-90`). `minor_portion: true` transports. Visible reason ✓, review-required label ✓ (`:42-46`), NO cap ✓, informative not error ✓. Sub-leaf drops inside this block (`pair_class: "boundary_uncertain"`, `review_reasons`, `lot_overall_class`, `coverage_note`) do not collapse a range, so AS-2 stands.

**AS-3 — PASS.** Status words are the contract's own vocabulary **verbatim**: `coverage.ts:50` returns `{value: status, …}` and `CoverageMatrixSection.tsx:65-67` renders the raw enum string, not a re-wording. All six render as distinct TEXT in plain `<code>` — deliberately not the badge component, so no `.status-verified` node exists and the S7 invariant holds. Fixture `coverage_matrix` has 11 rows, of which **8** are `rule_status_today: "missing"`; 8 render; the test asserts 8 (`:120-124`). No missing family dropped. (Finding 7 — the 1 `draft` and 2 `out_of_scope` rows filtered with no total disclosed — sits beyond AS-3's bar and is not failed here.)

**AS-5 — PASS, strongest area of the diff.** "Never an invented scenario" holds *structurally*, not merely by test: `CompareScreen.tsx:126-139` renders `ScenarioResult` only when `outcome.kind === "scenario"`, which `scenario-api.ts:285-298` returns only after `validateScenarioDocument` succeeds. `ScenarioFailureStates` reads no document field in all 355 lines — it touches only outcome-envelope fields. Flag-off → benign `feature_unavailable`, no correlation id, no Retry ✓. Four upstream states recoverable with allowlisted correlation id + Retry ✓. `scenario-api.ts:274` compares the **raw** state before sanitizing — correct, since sanitizing first could launder a malformed state into a documented one ✓.

**AS-6 — PASS.** `ConfirmScreen.tsx` → `href={/property/compare?bbl=${encodeURIComponent(profile.identity.bbl)}}`, `data-testid="confirm-next-compare"`, renders as `<a href>`, labelled "Compare preliminary scenario" — keyboard-reachable and labelled ✓. **The BBL survives navigation byte-identical**, verified end to end: `encodeURIComponent` is identity on a 10-digit string; `CompareEntry` (`CompareScreen.tsx:153`) reads `?bbl=` and passes it to `validateBblInput` (`lib/bbl.ts:36-71`), which only trims and returns `canonical: text` — no padding, no reformatting, no digit alteration. The return link preserves it too.

---

## Additional coverage gap

`packages/contracts/fixtures/valid/scenario/unsupported_family.json` is committed but **no test uses it** — the `scenario_kind: "unsupported"` render path (`NoScenarioBlock` heading "Not supported yet — no maximum can be stated") is never exercised. That path also drops `constraints` and `integrity_check` per finding 5.
