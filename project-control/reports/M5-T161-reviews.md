# M5-T161 reviews (every return kept unchanged)
- G3 code-reviewer at 5e3e8e68: PASS (two advisories, no action: the aggregate diff includes ledger and a peer report; a cross-reference comment to the vitest leg would help)
- G4 qa-engineer at 5e3e8e68: PASS (one advisory, no action: the zoning-lot wording is asserted as engine text; a future rewording updates this spec in lockstep); green 2 passed, its own two mutations fail

Both reviewers are AI agents; neither is a human or professional review.

## G3

<!-- saved unchanged by save_return.py from agent-acb2d2bbdf1518ebd.jsonl, entry 2026-10-11T09:09:37.996Z, sha256 3f54f3c56010b4986c1ee2cdf4673616fb7f29967b9c998d48cf41107762eed8 -->
# M5-T161 G3 (code-reviewer) gate report — VERDICT: PASS

I am an AI agent; this is an automated code review, not a human or professional engineering/legal review. Frozen head `5e3e8e68` in `/root/project/w-wave20`, task `project-control/tasks/M5-T161.json`. I did NOT run the browser e2e (reserved for the qa-engineer; ports 3000/3001/8000 held).

## What I checked (independently, from source — not the producer's conclusion)

1. Design matches M5-T157/DB-231. `services/api/.../result_way_bridge.py:409-442` `_density`: when the record is `NOT_IN_SPECIAL_DENSITY_AREA` and the statement is None OR True (agrees), it returns `EVIDENCE_NOT_IN_ONE` (the `says_in_one` disagreement branch is not taken). `result_ways.py:472-482` `_unit_standard_way` for `EVIDENCE_NOT_IN_ONE` returns `Conditional(conditions=(zoning_lot, area, k20))` with the generic `_zoning_lot_condition()` (`result_ways.py:117-134`, text "If this tax lot is the whole zoning lot…"). So from the FIRST press the standard limit is a Conditional ceiling with the zoning-lot condition; the special-density statement agrees and changes nothing, and the "as the user states" wording (only in the `USER_STATEMENT_NOT_IN_ONE` branch, `result_ways.py:487`) never appears because a usable record is present. Matches vitest "S4 (M5-T157)" (`journey-215-16-northern.test.tsx:116`).

2. Expected value is NOT hard-coded. Spec line 40 `UNIT_LIMIT_STANDARD = Number(rowValue("L6"))` reads reference row L6 (`docs/reference-cases/R6B/cases/real-lot.json` L6 expected.value = 29, `20150÷680=29.63→29`, ZR 23-52(b)). The `// 29` is a comment; the value tracks the reference case.

3. Locator uniquely targets the standard-residences row. The three unit-limit labels (`result_way_inputs.py:390-397`) ALL contain the substring "Legal dwelling-unit limit". BUT `_unit_qualifying_affordable_way`/`_unit_qualifying_senior_way` (`result_ways.py:561-607`) return `Withheld`, and `AnswerCard.tsx` renders shown/conditional rows as `data-testid="answer-value"` (lines 113-135) and withheld rows as `data-testid="answer-withheld-value"` (lines 137-152). So at every press only the standard (Conditional) limit is an `answer-value` carrying that substring; the two qualifying rows are `answer-withheld-value` and are excluded by `getByTestId("answer-value").filter({hasText:"Legal dwelling-unit limit"})` (spec 179-181, 235-237). The filter matches exactly one row.

4. A second matching row would FAIL, not pass. Playwright strict mode: `toBeVisible()`/`toContainText(string)`/`toHaveText(string)` throw a strict-mode violation when the locator resolves to >1 element. If a second `answer-value` ever carried "Legal dwelling-unit limit", spec line 182 `toBeVisible()` (and 183/184) would error → test fails. Uniqueness is enforced, not assumed.

5. No vacuous pass (the REQUIRED check). The value row lives inside the `ResultDetails` disclosure, which renders `<div … hidden={!open}>` closed by default (`ResultDetails.tsx:54-71`). The OLD check `expect(await dialog.innerText()).not.toContain("29 units")` passed vacuously because `innerText` omits hidden text, so it only proved the row was folded, not absent — the producer's explanation is correct. The NEW checks click `answer-details-button` (spec 178, 234) and assert `toBeVisible()` BEFORE the text/marker, so they cannot pass while the row is hidden or absent. I confirmed the allowance card's only child is a `SupplementRow` (no button; `ThreeAnswersPanel.tsx:86-91`), so `allowance.getByTestId("answer-details-button").first()` is the one, correct disclosure; sibling cards' buttons are outside the `allowance` section.

6. Full zoning-lot text in the row is sound. `three-answers.ts:313,399-407`: a condition on one result renders local (full text in the row); on two-plus results it renders by name. The generic zoning-lot condition is used only by `_unit_standard_way` (count=1 → local → full text), while area/k20 are shared ("Applies: Condition 1, Condition 2"). So spec 185/241 `toContainText("If this tax lot is the whole zoning lot")` on the row is correct for the browser route render (the harness carries no ACRIS zoning-lot index → generic condition), which is WHY it differs from the vitest leg (property-specific ACRIS condition, rendered shared). The marker assertion (184/240 `answer-conditional-marker`="Conditional") also guards "never settled" — a settled row has no marker and would fail.

7. Every other assertion unchanged. The diff is two hunks confined to the two special-density blocks (spec ~166-185 and ~216-244) and their comments; floor-area, envelope, building B, 14-ft, housing-program, keyboard-close, and the second (16-ft) test are untouched. Comments are plain and accurate.

8. Scope / allowed paths. The builder's MATERIAL commit `f2f76654` touches exactly the two allowed files (`apps/web/e2e/results.flag-on.spec.ts`, `project-control/reports/M5-T161-producer-report.md`). The wider `8cc9a3a0..5e3e8e68` diff also shows `project-control/reports/M5-T158-DCV.md` (disjoint peer commit `463f6f46f`) and `project-control/state.json` + `project-control/tasks/M5-T161.json` (orchestrator integration commit `5e3e8e68`, ledger authority). No product source changed. See A1.

9. Typing / locator stability / waits. Locators are stable test ids (no positional text). No new `waitForTimeout` or long custom timeouts that could hide failures. Typing follows CODING_RULES.md (standard Playwright locators/assertions; no `as`-casts introduced in the changed lines).

## Commands I ran (read-only, in the clean worktree at the frozen head)
- `node_modules/.bin/tsc --noEmit` (apps/web) → exit 0 (TYPECHECK PASS).
- `node_modules/.bin/eslint e2e/results.flag-on.spec.ts` (apps/web) → exit 0 (no errors/warnings on the changed file).
(Worktree HEAD == 5e3e8e68 and `git status apps/web` clean, so the in-place run equals a frozen-head export; node_modules reused — package.json/lock are forbidden paths and unchanged.)

## What I could NOT check (and why)
- The live browser e2e and the actual runtime record-decision (`gather_special_density_record` → NOT_IN for this Queens lot) and the disclosure-reset-on-re-render behaviour: out of my scope (qa-engineer runs the browser test; CI web-e2e on the integration head is the authoritative full-suite proof per D-090-R639). The engine logic, the existing passing re-render/reopen pattern (spec 214), and the producer's mutation outputs are consistent with the expected behaviour, but I did not execute them.
- Full-project `eslint .`: I linted the changed file only (clean) plus typecheck (clean); producer reports full lint passes with 2 pre-existing warnings in untouched files — CI is authoritative.

## Findings
- A1 (ADVISORY): the aggregate `8cc9a3a0..5e3e8e68` diff spans 5 paths; only the material builder commit is in task scope and it is confined to the two allowed files. The extra paths are a disjoint peer DCV report and orchestrator ledger files — expected, not a defect.
- A2 (ADVISORY): the browser spec (full zoning-lot text in the row) and the vitest S4 leg (by-name + panel body) assert the condition's text in different places by design, because they run against different fixtures. The producer documented this; both are correct. A one-line cross-reference in the spec comment would prevent future confusion. Non-blocking.

No REQUIRED findings. The change is a correct, non-vacuous, test-only repair that aligns the browser spec with the shipped M5-T157 behaviour.

VERDICT: PASS (two advisory, non-blocking notes).

END-OF-REPORT

## G4

<!-- saved unchanged by save_return.py from agent-a1cda96d4c730cf9d.jsonl, entry 2026-10-11T09:13:26.386Z, sha256 9ba740d73268c73caf365d0e297c7c932d9ecce08780bc4bf429b7b195881744 -->
# G4 (qa-engineer) gate report — M5-T161

I am an AI agent. This is an independent automated QA gate, not a human or professional legal review.

**Task:** M5-T161 — CI repair: update the flag-on results browser spec to M5-T157's record-driven special-density behaviour (test-only).
**Frozen head:** 5e3e8e68817fe11c3d599c1ef57a61430fe0fe47 (task/wave23-density-zoning-lot, /root/project/w-wave20).
**Verdict: PASS.** No REQUIRED defects. One ADVISORY (non-blocking).

## What I checked (independently, from sources first)

**Expected result, worked from NB-05 + reference row L6 before reading the changed spec.** Lot 70 is Queens (MapPLUTO Borough QN, BoroCode 4) → outside the Manhattan Core (Manhattan CD 1–8, ZR 12-10 E2); SPDist1 null → outside the Special Downtown Brooklyn District → NOT in a special density area (ZR 12-10 E1), so the ZR 23-52(b) factor 680 applies. 20,150 (FAR 2.00 × lot area 10,075, row L1) ÷ 680 = 29.63 → fraction 0.63 < 0.75 → **29 units (row L6)**. The record decides, so from the FIRST press the standard legal dwelling-unit limit is a Conditional ceiling (never settled, never withheld) carrying the always-present zoning-lot condition; a user statement that agrees changes nothing and is never named (engine branch EVIDENCE_NOT_IN_ONE, not USER_STATEMENT_NOT_IN_ONE). This matches the shipped `result_ways._unit_standard_way` and the NB-05 revision-3 record (verdict "agrees").

**Provenance of expected values.** UNIT_LIMIT_STANDARD = Number(rowValue("L6")) read from docs/reference-cases/R6B/cases/real-lot.json (= 29), asserted as `${UNIT_LIMIT_STANDARD} units` — not a hard-coded 29, not a program run. FA_STANDARD/FA_QUALIFYING likewise from L1/L2. displayQuantity(29,"dwelling_units") → "29 units" (three-answers.ts:181). Confirmed.

**Vacuous-pass trap (old line 172).** ResultDetails.tsx renders the derivation region as `<div hidden={!open}>` (closed by default); the legal-limit value is an `answer-value` row inside it. `innerText` excludes hidden text, so the old `dialog.innerText().not.toContain("29 units")` passed because the row was FOLDED, not because 29 was absent. The new S1/S2 checks click `answer-details-button`, then `expect(legalLimitFirst).toBeVisible()` before the text assertions — cannot pass while hidden. Proven by mutation A below (the `.not` assertion fails on the opened, genuinely-visible row).

**Locator targeting (brief's specific ask).** `allowance.getByTestId("answer-value").filter({ hasText: "Legal dwelling-unit limit" })` matches exactly ONE row: `legal_unit_limit_standard` (label "Legal dwelling-unit limit, standard residences (new all-residential building): …"). The qualifying-affordable and qualifying-senior limits DO have labels containing "Legal dwelling-unit limit", but both are **withheld** → rendered as `answer-withheld-value`, not `answer-value` (AnswerCard.tsx:116 vs :143; confirmed in result_ways `_unit_qualifying_affordable_way`/`_unit_qualifying_senior_way` returning Withheld, and the committed fixture's `values` list carrying only the standard limit). So the filter targets the standard row and no other. A second matching `answer-value` row would resolve the locator to ≥2 elements and make `toBeVisible()`/`toHaveText()` throw a Playwright strict-mode violation → the test FAILS, never passes vacuously. The mutation-1 received-string showed a single clean row read, confirming one match empirically.

**Scenario → assertion coverage (each fails if broken):**
- S1 (first press, no statement): opens disclosure; `toBeVisible` + `toContainText("29 units")` + `answer-conditional-marker` = "Conditional" + `toContainText("If this tax lot is the whole zoning lot")` (lines 178–185). Proven breakable by mutations A & B.
- S2 (after the agreeing statement, fresh press): same four assertions on `legalLimitAfter` (238–241) + `expect(dialog).not.toContainText("as the user states")` (244) — proves the limit is unchanged and the statement is never named. The negative guard uses dialog textContent (catches hidden text), so it is not evadable by folding.
- S3 (never settled/feasible/maximum): existing guards kept unchanged — options.innerText `not.toMatch(/feasible|complies|legally correct/i)` (168), dialog.innerText `not.toContain("maximum for this property")` (188); the limit is only ever asserted Conditional.
- S4 (rest of journey unchanged): `git diff 8cc9a3a0..5e3e8e68` shows only two hunks in the spec, both in the special-density blocks (+36/−8). 14-ft height, housing-program drift loop, keyboard close all untouched.
- S5 (mutation proof both directions, then green): reproduced below.

**Scope / modularity.** Producer material change is only the two allowed_paths files (apps/web/e2e/results.flag-on.spec.ts, project-control/reports/M5-T161-producer-report.md). No forbidden path (apps/web/src/, services/, harness, config) touched. Test-only change, no handwritten production source → modularity boundary answers / modularity_check N/A. (The range also contains ledger files state.json, tasks/M5-T161.json and a disjoint peer report M5-T158-DCV.md — orchestrator/control-plane commits, outside the producer's scope, as the brief noted "others may commit there".)

## Reproduction — browser runs (git archive of 5e3e8e68 under my scratch, never the checkout)

Export spec LF-sha256 = 5c1bcc52…baa5e8 == `git show 5e3e8e68:…spec` (verified; and re-verified == frozen after each restore). `npx npm@11.18.0 ci` exit 0; `npm run build` exit 0; chromium-1228 cached (playwright 1.61.1). Command: `PATH=lanes-venv:$PATH PYTHONPATH=<export>/services/api CI=true npx playwright test e2e/results.flag-on.spec.ts`.

| Run | Direct exit | Result |
|---|---|---|
| Green (unmutated) | PLAYWRIGHT_EXIT=0 | 2 passed (18.8s) |
| Mutation A: first-press → `.not.toContainText("29 units")` (accept a withheld/no-number limit) | 1 | 1 failed @ line 183, 1 passed — product shows "…29 units Conditional If this tax lot is the whole zoning lot…Applies: Condition 1, Condition 2" |
| Mutation B: expect "whole **tax** lot" instead of "whole **zoning** lot" | 1 | 1 failed @ line 185, 1 passed — product renders "whole zoning lot" |

Both mutations restored; spec sha256 back to 5c1bcc52…baa5e8 each time. Mutation A independently proves the first-press 29 is real and visible (the pre-M5-T157 "withheld/no number" expectation genuinely fails against the shipped route) and the zoning-lot condition text is the generic one the real route emits; mutation B proves the wording assertion is non-vacuous.

**Port rule:** `ss -ltn | grep -E ':(3000|3001|8000)\b'` printed nothing before AND after every run (green, A, B). I started/stopped nothing on those ports; Playwright's own webServers bound and released them within each run.

## Findings
1. **ADVISORY** — spec line 185/241: the zoning-lot condition is asserted by the hard-coded wording prefix "If this tax lot is the whole zoning lot" (engine text, not a reference-case value). This is an appropriate UI-text contract and the brief endorses this exact phrase, but any future rewording of `_zoning_lot_condition()` will require updating this e2e (and its golden siblings) in lockstep. Not blocking.

## What I could not check
- I did NOT run the whole browser suite or the api suite (out of scope per the brief). D-090-R639's full-suite proof is the CI web-e2e job on the integration head — that remains the orchestrator's required evidence; my local run covers only results.flag-on.spec.ts.
- Directive-requirement completeness (D-090 R255/R520/R584/R639, D-093-R051, D-094 R034/R035) is the independent directive-compliance-verifier's pass, not this G4 gate; I confirmed only the test-adequacy and D-093 expected-result derivation relevant to QA.
- I did not re-fetch live MapPLUTO/ZR; I relied on the committed snapshots and the NB-05 record (revision 3, data-contract-verifier "agrees") whose digests were verified upstream.

END-OF-REPORT
