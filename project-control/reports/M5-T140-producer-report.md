# M5-T140 producer report

Producer: frontend-engineer (an AI agent). Worktree reset to the claim-seam head
`fa93d096778e620f9b8b8bc2d99137d69382a45a`. Part B of the R6B results connection: a results panel
on the website behind the default-off website switch `INTERNAL_RESULTS_UI_ENABLED`. No server file,
no package, no production switch. This report is evidence for the independent gates; it accepts
nothing.

## 1. Impact query — consumers of the six files

`python3 tools/code_graph/query.py --no-regen impact <path>` returned `STALE (stale fingerprint):
refusing to serve the cached graph` for all six paths (advisory tool; the graph was stale and
`--no-regen` refused it). I verified consumers directly in source with grep. Every consumer that
MUST change is inside the allowed paths; no forbidden/out-of-scope consumer must change.

| Changed file | Consumers (verified in source) | Needs a change? |
|---|---|---|
| workspace/types.ts | ArchitectShell.tsx (imports `dashboardHref` only), DashboardStatusStrip.tsx / dashboard-status.ts (use `DashboardTool` as a param/field type, no exhaustive map), DashboardEntry/Panels/Tools.tsx, floating-workspace-window.test.tsx | Only DashboardEntry/Panels/Tools (allowed) + floating-workspace-window.test.tsx (allowed, the tool-set test). `surveyReview/*` matches are that package's own `./types`, not workspace/types (false positives). |
| DashboardTools.tsx | DashboardEntry.tsx (allowed); tests parity-panel, dashboard-entry, dashboard-evidence, dashboard-proposal-flag, dashboard-unused-floor-area-flag (NOT allowed) | DashboardEntry only. The new `resultsUiEnabled?` prop is optional + false-absent and the new `case "results"` is additive, so no not-allowed test changed (verified: full suite green). |
| DashboardPanels.tsx | app/property/layout.tsx, DashboardEntry.tsx, dashboard-panels.test.tsx (NOT allowed) | DashboardEntry only. The opener is gated by the optional false-absent prop; no not-allowed test changed. |
| DashboardEntry.tsx | app/property/workspace/page.tsx (allowed), dashboard-entry.test.tsx (NOT allowed) | workspace/page.tsx only. New prop is optional + false-absent; dashboard-entry.test.tsx unchanged and green. |
| three-answers.ts | AnswerCard.tsx (allowed), ThreeAnswersPanel.tsx, ResultsStatusStrip.tsx, ScopeSummary.tsx (read-only; types only), three-answers-panel.test.tsx + three-answers.test.ts (allowed), journey-215-16-northern.test.tsx / scope-summary.test.tsx / building-option-notes.test.tsx / building-option-notes-view.test.ts (NOT allowed), results-fixtures.ts (type only) | AnswerCard.tsx + the two allowed tests only. The `gapKindLine` additions are additive (optional field, new testid element), so ThreeAnswersPanel and the three not-allowed card tests did NOT change and stay green. |
| AnswerCard.tsx | ThreeAnswersPanel.tsx | No ThreeAnswersPanel change (the gap-kind line is rendered inside the card; the panel passes the view through unchanged). |

## 2. The states, with the exact words the user sees and the pinning test id

| State | What the user sees (exact) | Test (file · name / testid) |
|---|---|---|
| switch off | PlannedView: "Results is not available in this version" + "No results model or calculation is connected…" ; no call | dashboard-results-flag.test.tsx "switch undefined/false"; results.spec.ts (browser) |
| switch on, before the ask | the form + one button "Show results"; no result; no call | results-panel.test.tsx "S2/S7/S9 … makes NO call on mount"; dashboard-results-flag.test.tsx "switch on" |
| loading | LoadingCard "Working out the results for this property…" (`results-loading`), button `aria-busy` | results-panel.test.tsx "S2 … loading state" |
| result shown, input changed since | "You changed an input. These results are for the earlier inputs. Press Show results to update." (`results-stale`) | results-panel.test.tsx "S19 … stale line" |
| success (200) | `three-answers-panel` renders + parking line (`results-parking`) | results-panel.test.tsx W-2; results.flag-on.spec.ts |
| 404 | NotConnectedCard "Results are not connected yet" + "The results service is not available on this server. No results were shown." (`results-unavailable`) | results-panel.test.tsx "S11 … 404 not connected" and "S11 … say exactly true words" |
| 422 validation_error | FailureNoticeCard "The request could not be understood" + server field message (`results-failure-notice`) | results-panel.test.tsx S11; results-api.test.ts W-1 |
| 429 rate_limited | "Too many requests" + "Try again shortly." + retry | results-panel.test.tsx S11; results-api.test.ts W-1 |
| 503 inputs_unavailable | "The results could not be loaded right now" + server message + recovery "Trying again is safe." + retry | results-panel.test.tsx S11 (+ "say exactly true words"); results-api.test.ts W-1 |
| 503 lot_conditions_unconfirmed | "The results are not available for this lot" + server reason + recovery "Trying again will give the same answer until that record can be read.", NO retry (never safe) | results-panel.test.tsx S11 (+ "say exactly true words"); results-api.test.ts W-1 |
| 500 internal_error / internal_contract_error | "Something went wrong" + "…Nothing was shown." (no stack/path) | results-panel.test.tsx S11; results-api.test.ts W-1 |
| network failure | "Could not reach the server" + retry | results-panel.test.tsx "S12 … network"; results-api.test.ts W-1 |
| bad document (200 fails website check) | "The results could not be loaded" + no partial document | results-panel.test.tsx "S12/S21 … fails the website's own check"; results-contract-checks.test.ts S21; results-api.test.ts W-1 |
| timeout / unexpected response (panel-rendered) | "The results took too long" / "Unexpected response from the server" | results-panel.test.tsx "F3 … timeout and unexpected-response notices" |
| large height accepted (no upper limit, R4/S9) | 500 ft sent; no field error | results-panel.test.tsx "S9/R4 a large height is accepted" |
| website check refuses a value settled by silence | available answer with no value_states; a shown value with no entry; a conditional with no conditions | results-contract-checks.test.ts "B1 / B2 / B3" |
| S4 withheld shows reason not number | "Not known — <reason>", no % | results-panel.test.tsx S4; three-answers.test.ts "S14 RED PROOF" |
| S5 gap-kind shown | "Not built yet: this part of the program is still owed." / "Missing information about this property." | three-answers.test.ts "gapKindLine …"; three-answers-panel.test.tsx "S5 …" |
| S6 conditional names assumption | the value + "If <assumption>" line | three-answers-panel.test.tsx / three-answers.test.ts "S14 conditional"; results.flag-on.spec.ts |
| S13 feasibility/estimate | parking line present; no option called feasible; unit_estimate not shown | results-panel.test.tsx S13 |
| S14 no internal words (WHOLE panel, form included, before and after a result) | no `this slice`/`Lane A`/`task A-12`/`not encoded`/`not_available`/`rule_not`/snake_case; nothing "maximum for this property" | results-panel.test.tsx S14 |
| S15/W-4 standing label once | panel adds no standing-review-label | results-panel.test.tsx W-4 |
| S18/W-6 keyboard + a11y | panel has accessible name "Development results"; Escape closes + returns focus | results-panel.test.tsx W-6; results.flag-on.spec.ts |
| S20 switch threading | absent/false → opener hidden, not-available view, no call; true → form | dashboard-results-flag.test.tsx |
| S22 newer request wins | older answer discarded; second answer only | results-panel.test.tsx S22 |

## 3. Every text the website writes (each plain and true — no internal name, no machine word, no task/PR number, never "professional review", never "unsupported")

Form (always): "Development results"; "Housing program"; options "Standard residence" / "Qualifying
affordable housing" / "Qualifying senior housing" (the server transform's own words,
`three_way_document.py _HOUSING_PROGRAM_DISPLAY`); "Floor-to-floor height (feet)"; helper "Leave
empty to use the program's starting height. The height used is shown with the results."; "I state
that this lot is not in a special density area."; helper "This is your statement about the lot, not
a recorded fact. It is sent only when you make it, and any result it produces is shown as
conditional on your statement."; button "Show results". Field message (refused height): "Enter a
height in feet greater than zero."

States: loading "Working out the results for this property…"; 404 "Results are not connected yet" +
"The results service is not available on this server. No results were shown."; stale
"You changed an input. These results are for the earlier inputs. Press Show results to update.";
success parking line "Parking, loading and bicycle requirements are not yet checked for this option.
It is not shown as feasible." Failure titles/recovery: "The request could not be understood" /
"Check the form and try again."; "Too many requests" / "Try again shortly."; "The results could not
be loaded right now" / "Trying again is safe."; "The results are not available for this lot" /
"Trying again will give the same answer until that record can be read."; "Something went wrong" / "The app hit an unexpected problem while
loading the results. Nothing was shown."; "The results could not be loaded" (bad document);
"Could not reach the server"; "The results took too long"; "Unexpected response from the server";
shared "The property you entered is fine. Trying again is safe." / "This needs the platform team.
Trying again will likely give the same result until it is fixed." The server `message` reflected in
a body is plain English and length-capped (bounded.ts). The shared FailureNoticeCard chrome
("Try again", "Technical details (for support)") is unchanged; the support codes (correlation id,
HTTP status, rejection code, format problems) sit behind the closed disclosure, not in the prose.

Reader/card gap line (three-answers.ts, ONE place): "Missing information about this property." /
"Not built yet: this part of the program is still owed." Workspace: tool label "Results"; window
description "The development results for this property, each shown as settled, conditional or not
known."; opener button "Results"; region "Development results"; form region "Results inputs".

## 4. Could two things on this screen disagree? (the five pairs)

1. Form vs the shown result (R3): NO. When any raw form field differs from the inputs the shown
   result was asked with, the stale line stands above the result and the shown numbers do not change
   until the button is pressed (results-panel.test.tsx S19).
2. The form's program label vs the returned line (R3): NO. The option labels ARE the server
   transform's own words; the flag-on journey proves the returned housing-program line names the
   form's chosen label ("Standard residence was selected for this run as the housing program").
3. A withheld value vs any number elsewhere (R9 + the reader's guard): NO. The website's own check
   refuses a document where a withheld key is also a shown value (S21), and the reader's
   headline-withheld branch never falls back to another value (red/green in three-answers.test.ts).
4. The kind-of-gap words vs the reason beside them (R6): NO. Both come from the SAME value_states /
   answer `gap_kind` entry; the words live in one place (GAP_KIND_LINES); an absent/null/unknown kind
   shows no line.
5. The status strip vs the conditional values (R5): STATED, not solved here. The strip is shown
   byte-exact as the document has it (its first item "Zoning maximum" is the server's words,
   ResultsStatusStrip is read-only). Whether that label sits beside conditional values is a server
   question on record (DB-199(d)), owed before the switch is turned on anywhere, NOT this task's. No
   line the website writes calls a value the property's maximum, a confirmed maximum, or feasible
   (results-panel.test.tsx S14).

## 5. Red proof (before/at the edit it belongs to)

- S21 / R9 refusal (results-contract-checks.ts). With the refusal branch neutralised
  (`if (false && way === "withheld" …)`), `vitest run results-contract-checks.test.ts -t "S21"`
  went RED: `AssertionError: expected true to be false` at `expect(result.ok).toBe(false)` — the bad
  document (a withheld key also present as a shown value) was accepted. Restoring the branch →
  green. Output kept in the scratchpad.
- The reader's headline-withheld red/green (three-answers.test.ts "S14 RED PROOF … R556") is the
  pre-existing proof; my gap-kind change did not disturb it (it stays green).
- Large-height acceptance (ResultsPanel `parseHeight`, R4/S9, third commit). Adding an upper limit
  (`value > 100` refused) made results-panel.test.tsx "a large height is accepted" go RED
  (`expect(calls[0].floor_to_floor_ft).toBe(500)` failed — 500 was refused); reverting → green.
  Done in place and reverted exactly (JS module resolution makes a true out-of-repo copy run
  impractical).

## 6. Mutation proofs (each: mutate production in place → run the pinned test → RED → revert exactly)

All seven were caught (the pinned test failed); each file was restored and re-verified green.

- panel calls the server on mount → results-panel.test.tsx "makes NO call on mount": RED (1 failed).
- client sends a height the user did not enter → "the body carries only what the user chose": RED.
- client omits an entered height → "the body carries only what the user chose": RED.
- statement sent when not made → "the body carries only what the user chose": RED.
- check accepts a number for a withheld key → results-contract-checks.test.ts "S21": RED (the §5 proof).
- reader shows no kind line → three-answers.test.ts "names the two kinds": RED.
- stale-inputs line never shows → results-panel.test.tsx "stale line": RED.
- an older answer replaces a newer one → results-panel.test.tsx "newer request wins": RED.

## 7. Tests on optional/possibly-zero values (presence checks, never truthiness)

- ResultsPanel `parseHeight`: presence `trimmed === ""`; validity `!Number.isFinite(value) || value <= 0`
  (so "0" is a REFUSED value, not "no height"). `buildRequest`: `if (height.kind === "present")`,
  `if (values.densityStatement === true)`. State guards: `askedWith !== null`, `outcome !== null`,
  `outcome?.kind === "success"`.
- three-answers.ts `gapKindLine`: `gapKind != null` (gap_kind is a string enum or null/undefined,
  never ""/0). AnswerCard: `entry.gapKindLine !== null`, `view.gapKindLine !== null`.
- results-contract-checks.ts: `states !== undefined && states !== null`;
  `answer.gap_kind !== undefined && answer.gap_kind !== null`; numbers via `isJsonNumber`.
- Pinning tests: results-panel.test.tsx "S7/S9 … empty height and unmade statement are omitted"
  (`floor_to_floor_ft`/`special_density_statement` assert `toBeUndefined`), "S9/R4 zero/non-number
  refused"; three-answers.test.ts "gapKindLine … absent/null/unknown → null";
  results-contract-checks.test.ts "withheld entry missing its gap_kind".

## 8. What is NOT changed

No server file (no route/engine/request-reader/config/contract/schema/fixture under services/api or
packages). No production switch (`INTERNAL_RESULTS_ENABLED` and `INTERNAL_RESULTS_UI_ENABLED` stay
off by default; the latter is set only on the e2e :3001 server; the harness sets the server flags for
its own process only). No report page, PDF, apartment-count estimator, option comparison, drawing/3D.
No change to package.json/package-lock.json, globals.css, render.yaml, .github, tools, .claude, the
rule tables. ResultsStatusStrip.tsx and ScopeSummary.tsx not touched (read-only). ArchitectEntry.tsx,
ArchitectShell.tsx, property/page.tsx, compare/page.tsx, confirm/page.tsx not touched. The blocks
addon_gains / best_combination / floor_stack / geometry / unit_estimate / existing_building /
rule_versions are not rendered (ThreeAnswersPanel reads only the Pick), so none appears without its
conditions and no engine internal word reaches the screen (DB-196(c), DB-199(e), DB-202(f)).

## 9. Checks (direct exit codes and counts)

- a. `apps/web` `npx --yes npm@11.18.0 ci --no-audit --no-fund` — EXIT 0 (added 314 packages).
- b. `npm run lint` — EXIT 0 (0 errors; 2 pre-existing warnings in files not touched here).
- c. `npm run typecheck` — EXIT 0.
- d. `npm run test` — EXIT 0; 116 files, 2484 passed (was 2434 at the claim head; +50 new tests).
- e. `npm run build` — EXIT 0.
- f. `CI=true npm run test:e2e` (lanes venv first on PATH, `PYTHONPATH=<worktree>/services/api`) —
  EXIT 0; 155 passed (8.1m). Includes results.spec.ts (flag-off) and results.flag-on.spec.ts
  (LAW journey, real POST 200 from :8000). First full run surfaced one failure (the harness
  study-inputs provider lacked the geometry/outline the engine chain needs → 503); fixed by giving
  the harness a recorded-Northern results provider; re-ran full suite green.
- g. `services/api` `pytest -q -p no:cacheprovider tests/api tests/journey` (lanes venv) — EXIT 0;
  1133 passed, 1 warning (re-run after the harness change; unchanged).
- h. `python3 tools/modularity_check.py --check` — EXIT 0 (no new/edited file over threshold; a
  non-blocking `symbol_ceiling` WARN on three-answers.ts — "a signal, not a verdict"). New-module
  raw line counts: results-api.ts 268, results-contract-checks.ts 251, results-ui-flag.ts 27,
  ResultsPanel.tsx 283, ResultsForm.tsx 138, results-panel.css 52 (all < 400); three-answers.ts 627
  raw / AnswerCard.tsx 301 (both well under the 600 counted-line warning; the modularity counter put
  three-answers.ts at 384 counted lines at the claim base).
- i. red proof + mutation proofs — see §5, §6 (all RED when expected; all reverted and green).
- j. `git status --porcelain` — 25 modified files, all placeholders seeded at the contract head,
  all inside the allowed paths; plus this report = 26 allowed paths. No untracked or out-of-scope
  file. `git diff --name-status fa93d0967 HEAD` is captured at commit time and shows only the 26
  allowed paths.

## 10. Rulings / doubts

- Ruling R2 vs disabling the button: the brief implies the user can issue a newer request while one
  is in flight ("A newer request aborts an older one"). I therefore kept the "Show results" button
  pressable during loading (it carries `aria-busy`) and relied on the newer-wins guard, rather than
  disabling it (which would make the R22 scenario unreachable). Flagging this as a deliberate
  reading of R2, not a departure.
- Ruling R6 on a whole not-available answer: R6 says a withheld value AND a whole not-available
  answer that carries a gap_kind both say their kind. The journey fixture's `building_option` is
  not-available with gap_kind `work_owed`, so its card now also shows the kind line. The packet
  table's "reason only, no number" for building_option is preserved (the kind line is plain words,
  not a number). I updated the two allowed card tests accordingly; no not-allowed card test changed.
- Second commit (orchestrator corrections, on top of 06650cfe): made three sentences true — the
  404 card now reads "The results service is not available on this server. No results were shown."
  (a request WAS made; "this build" was inner language); the 503 inputs_unavailable recovery is now
  just "Trying again is safe." (the website does not know the cause and makes no "yet" promise); the
  503 lot_conditions_unconfirmed recovery is now "Trying again will give the same answer until that
  record can be read." (true by the route's `_lot_conditions_unconfirmed_503` contract; stays
  not-retryable). The flag-on journey now also selects each of the two other programs and asserts
  the returned housing-program line names the label read from the form's selected option (not
  retyped). A unit test ("say exactly true words") pins the three corrected sentences. Nothing else
  changed.
- Third commit (reviews: G3 passed with notes, G4 failed on one missing test), on top of a650956d:
  (A, G4-F1 blocking) added results-panel.test.tsx "a large height is accepted" (500 ft sent, no
  field error) with its red proof above. (B, G3-F1) tightened results-contract-checks.ts to refuse a
  value settled by silence — an available answer with values but no value_states map; a shown value
  with no value_states entry; a conditional with an empty conditions list — with B1/B2/B3 tests;
  verified NO valid contract-1.3.0 fixture under packages/contracts/fixtures/valid/results/ is
  refused (only the 1.3.0 journey fixture is subject to these rules and it passes; the pre-1.3.0
  fixtures are already refused by the existing contract_version check). (C, G4-F3) added the
  timeout and unexpected-response panel-render test. (D, G4-F4) the S14 text guard now runs over the
  WHOLE panel (form region included), before a result and after one. No form text tripped it.
- No ruling was impossible to build as written; nothing was chosen differently.
- The code-graph impact query was unusable (stale cache, `--no-regen`); I verified every consumer in
  source instead (§1). The harness imports the canonical recorded-Northern replay helpers from
  `tests.*` inside the provider function (the journey/results suites' own fixtures) so the e2e runs
  fully offline through the real engine; this couples the e2e harness to the test tree, which I note
  for the reviewer.

END-OF-REPORT
