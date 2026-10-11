# M5-T161 (builder) producer report — flag-on results browser journey follows the record-driven special density

**Worktree:** `/root/project/nyc-buildability/.claude/worktrees/agent-a5f9a06132209271f`
**Contract head reset to:** `8cc9a3a06729369ab162002c705759777f77b7ea` (confirmed as HEAD before work)
**File changed (only):** `apps/web/e2e/results.flag-on.spec.ts` (+36 / −8). Report placeholder replaced by this file.
**Requested status:** awaiting_gate. The CI-red test is green; the real route behaves exactly as M5-T157 (DB-231) shipped; no product/fixture/harness/config/other-test file was touched.

## 1. What changed and why

M5-T157 (DB-231) made the city's record decide the special density area. For 215-16 Northern Boulevard
(BBL 4073340070, Queens) the record places the lot OUTSIDE both special density areas (ZR 12-10:
Manhattan Core = Manhattan CD 1–8; Special Downtown Brooklyn District; MapPLUTO lot 70 = Borough QN,
SPDist1 null). So the legal dwelling-unit limit for standard residences is now a CONDITIONAL ceiling
from the FIRST press — 20,150 ÷ 680 = 29.63 → 29 units (ZR 23-52(b), fraction < 0.75) — carrying the
always-present zoning-lot condition, never settled and never withheld. A user's special-density
statement agrees with the record and changes nothing; a statement never overrides the record. M5-T157
updated the unit-test leg of this journey (`journey-215-16-northern.test.tsx`, test "S4 (M5-T157)") but
not this browser spec, which still expected the pre-M5-T157 "withheld / only shows a number after the
statement / names the statement as the condition" behaviour. CI web-e2e failed on
`results.flag-on.spec.ts:216` (`toContainText("special density area")`) at every run since 05:48 UTC
2026-10-11. This task updates ONLY the special-density part of the spec to the shipped behaviour.

In the e2e harness the results route builds the profile from the recorded Northern PLUTO pack through
the real engine (`fixture_api.py` → `harness_results_inputs_provider`); it carries NO ACRIS zoning-lot
index, so `zoning_lot_condition(inp)` is None and the GENERIC `_zoning_lot_condition()` text applies:
"If this tax lot is the whole zoning lot: the city's special-density record is kept per tax lot, while
the dwelling-unit limit is set on the zoning lot (ZR 23-52), so a zoning lot made of more than one tax
lot could change this limit". (The committed `recorded_215_16_northern_journey.json` fixture that the
vitest leg loads carries the property-specific ACRIS condition instead — that fixture was produced WITH
a zoning-lot index; the browser route is not. I assert the generic text the route actually renders, not
the fixture's text. Confirmed empirically in the baseline run below.)

## 2. Why the old line-172 check passed (the vacuous-pass trap)

Old line 172: `expect(await dialog.innerText()).not.toContain("29 units")`.
The legal-dwelling-unit-limit value is a ROW (`data-testid="answer-value"`) INSIDE the allowance card's
`ResultDetails` disclosure (`ResultDetails.tsx` renders `<div ... hidden={!open}>`; closed by default).
`innerText` returns only RENDERED (visible) text, so a row inside a closed/`hidden` region is excluded.
At the first press the route DOES return "29 units" in the DOM (proven below), but it sits in the closed
disclosure, so `innerText` omitted it and `not.toContain("29 units")` passed VACUOUSLY — it was testing
"the row is folded", not "the number is absent". (Line 215's `toContainText` uses `textContent`, which
includes hidden text, so it kept passing; only line 216's wording expectation reddened CI.) The new S1
check opens the disclosure and asserts the row `toBeVisible()` first, so it cannot pass while hidden —
proven by mutation A failing on the now-visible row.

## 3. Scenario → assertion table

| ID | Behaviour | How the spec now checks it |
|----|-----------|----------------------------|
| S1 | First press (no statement): standard legal unit limit is a Conditional 29 with the zoning-lot condition; the check cannot pass while the row is hidden | Open the allowance `answer-details-button`; locate the `answer-value` row filtered by "Legal dwelling-unit limit"; assert `toBeVisible()`, `toContainText("29 units")` (29 = `UNIT_LIMIT_STANDARD` from reference row L6, never hard-coded), `answer-conditional-marker` = "Conditional", and `toContainText("If this tax lot is the whole zoning lot")` |
| S2 | After the special-density statement + fresh press: same 29, Conditional, zoning-lot condition; the statement is never named | Fresh-press step kept; reopen the disclosure; same four assertions on `legalLimitAfter`; `expect(dialog).not.toContainText("as the user states")` (textContent catches it even while folded) |
| S3 | 29 never settled; nothing called the property's maximum / feasible / compliant | Unchanged existing guards kept: `options.innerText not.toMatch(/feasible|complies|legally correct/i)` (line 168), `dialog.innerText not.toContain("maximum for this property")` (line 175); the limit is only ever asserted as `Conditional` |
| S4 | 14 ft floor height, housing-program names, keyboard close, every other assertion | Untouched — only the two special-density blocks and their comments changed (diff: +36/−8, two hunks) |
| S5 | Mutation proof both directions, then green | See §5; plus the final restored run is green locally; CI web-e2e is the integration-head proof |

## 4. Commands (direct exit codes)

| Command (cwd) | Exit | Result |
|---|---|---|
| `npx npm@11.18.0 ci --no-audit --no-fund` (apps/web) | 0 | deps installed |
| `npm run build` (apps/web) | 0 | Next build OK |
| `npm run lint` (apps/web) | 0 | 0 errors; 2 pre-existing warnings in untouched files (lot-site-setup.test.tsx, study-vocabulary.test.ts) |
| `npm run typecheck` (apps/web) | 0 | `tsc --noEmit` clean |
| baseline (UNMODIFIED) `npx playwright test e2e/results.flag-on.spec.ts --project=chromium-flag-on` | 1 | 1 failed @ line 216 (`special density area`), 1 passed — reproduces the CI red |
| modified `npx playwright test …` | 0 | 2 passed |
| mutation A `npx playwright test …` | 1 | 1 failed @ line 184, 1 passed |
| mutation B `npx playwright test …` | 1 | 1 failed @ line 246, 1 passed |
| final restored `npx playwright test …` | 0 | 2 passed |

Browser runs used `PATH=/root/project/lanes-runtime/venv/bin:…` (lanes venv first; it imports `app` +
uvicorn 0.51.0) and `PYTHONPATH=<worktree>/services/api`, `CI=true`. Ports 3000/3001/8000 were confirmed
free before every run and free again after every run (`ss -ltn | grep …` printed nothing each time);
nothing of mine was left listening and nothing in the owner's preview range was killed or restarted.

## 5. Mutation outputs (S5)

Mutation A — restore the old first-press expectation, read the NEW way (row opened), assert NO number:
`await expect(legalLimitFirst).not.toContainText(`${UNIT_LIMIT_STANDARD} units`);` → FAILED at line 184:
```
Error: expect(locator).not.toContainText(expected) failed
Expected substring: not "29 units"
Received string: "Legal dwelling-unit limit, standard residences (new all-residential building):
20,150 ÷ 680 = 29.63 … 29 units ConditionalIf this tax lot is the whole zoning lot: the city's
special-density record is kept per tax lot, while the dwelling-unit limit is set on the zoning lot
(ZR 23-52)…Applies: Condition 1, Condition 2"
```
(Proves S1's positive is real and the row is genuinely visible, not vacuously passing.) Restored.

Mutation B — require the pre-M5-T157 phrase again after the statement:
`await expect(allowance).toContainText("special density area");` → FAILED at line 246:
```
Error: expect(locator).toContainText(expected) failed
Expected substring: "special density area"
Received string: "Floor-area allowance…Legal dwelling-unit limit, standard residences … 29 units
ConditionalIf this tax lot is the whole zoning lot: the city's special-density record is kept per
tax lot… (ZR 23-52)…"  (note "Hide details" present → the disclosure was open)
```
(The card says "special-density record", never "special density area"; reproduces the original CI
failure and justifies removing that assertion.) Restored; the final run is green (2 passed, exit 0).

## 6. Research & verification (D-093)

Read `.claude/rules/research-and-verification.md`, `docs/RESEARCH_AND_VERIFICATION.md` and the affected
record `docs/research/evidence-records/NB-05-special-density-area.json` (revision 3, verdict "agrees"
by an independent data-contract-verifier). Opened the primary sources it cites, not this brief's
summary: ZR 12-10 (special density areas = Manhattan Core + Special Downtown Brooklyn District; Manhattan
Core = CD 1–8), ZR 23-52 (factor 680; fractions ≥ 0.75 count as one unit; no factor in special density
areas / for qualifying senior housing), and MapPLUTO 26v2 lot 70 (Borough QN, SPDist1 null). These
independently establish the NOT-IN conclusion and 20,150 ÷ 680 = 29.63 → 29, matching the real route's
output byte-for-byte in the baseline run. Unresolved inputs are kept unresolved in the output: the
limit stays CONDITIONAL on the zoning lot (always-present condition) and the lot-area/other conditions
(shown as "Applies: Condition 1, Condition 2"); the spec never asserts it as settled or as the
property's maximum.

## 7. What I could not check / limitations

- I did NOT run the whole browser suite or the api suite (out of scope per the brief). CI web-e2e on the
  integration head is the required full-suite proof; my local run covers only `results.flag-on.spec.ts`.
- OQ-5 (NB-05): the exact PLUTO "DB" token spelling for the Special Downtown Brooklyn District is not in
  the repo; it does not affect this Queens lot (SPDist1 null) and is correctly kept open upstream. No
  professional/legal verification (ADR-007): the 29 is a Conditional ceiling, not a confirmed
  entitlement; I changed no product behaviour and promoted nothing to "verified".
- This spec is byte-identical to CI's web-e2e invocation except I passed `--project=chromium-flag-on`
  explicitly (the config's testMatch already routes `*.flag-on.spec.ts` to that project only; the
  second project ignores this file, so behaviour is identical). The harness, config and Next build are
  untouched.

END-OF-REPORT
