# M5-T147 PART C (first half) producer report — the results screen shows the contract-1.4.0 blocks

Producer: frontend-engineer (an AI agent). I am an AI agent.
Base (reset HEAD): `f804ab50e6e555d1679805e7b7549f2a838bea6c` ("M5-T146: G0 recorded again at the
corrected head (PASS)").
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a5ad298d55fa039ed`.

PART C, FIRST HALF only: the results panel reads the additive 1.4.0 blocks and shows them, tested
against the contract's own synthetic fixtures. NOT in this half (second half, after part E
regenerates the committed benchmark document): `apps/web/e2e/results.flag-on.spec.ts` and the tests
that read the committed benchmark document (`journey-215-16-northern.test.tsx`,
`lib/__tests__/results-api.test.ts`, `lib/__tests__/results-contract-checks.test.ts`). I did not
touch those, the contract, or any server file.

## What I built / changed, file by file

- `apps/web/src/lib/architect/three-answers.ts` (edited, additive): extended the reader Pick
  `ThreeAnswersResults` with the three 1.4.0 fields (`building_alternatives`, `coverage_by_portion`,
  `unit_estimate`); exported `conditionList` (one representation of a value_state's conditions, reused
  by the new view); added `hasBuildingAlternatives()` and `BUILDING_OPTIONS_BELOW_REASON`, and a
  building-option override in `answerView`: on a lot with worked alternatives the single building-option
  card shows a plain-words pointer to the list below instead of the document's machine reason (which
  names the `building_alternatives` contract field — never put on screen, §5a item 5; R556).
- `apps/web/src/lib/architect/first-building-options.ts` (NEW view model): `firstBuildingOptionsView`
  returns null for every document with none of the new blocks (so 1.0.0–1.3.0 render unchanged) and
  otherwise maps, read from the document: each alternative (label, floor-schedule rows, storey count,
  height, totals, the `way` conditions, what was not checked, its capacity estimate), coverage by
  portion (withheld = reason + gap-kind + resolved-by + ZR, NO number; available = ratios, 100 ft,
  portion areas, footprint), and the legal dwelling-unit limit (from `unit_estimate`, withheld or a
  value). Draft gate (`results.draft && !showDraftValues`) matches the existing cards. Formatters
  `sqft`/`feet`/`percent`/`twoDp` exported so tests read expectations through the same code.
- `apps/web/src/components/architect/answers/FirstBuildingOptions.tsx` (NEW component): renders the
  section — labelled alternatives (none preferred), floor schedule as a real `<table>` with
  `th scope`, the `Conditional` marker + per-line conditions, a "Not checked for this option" list,
  the preliminary capacity estimate under its owner label with the share/size shown as preliminary
  assumptions, the legal limit kept separate, coverage by portion (footprint only in the available
  branch). No colour-only status. Draft architect surface shows one not-reviewed line.
- `apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx` (edited): renders
  `<FirstBuildingOptions>` after the three answer cards when the view is non-null.
- `apps/web/src/components/architect/answers/three-answers.css` (edited): styles for the new section
  (table, estimate, coverage, legal limit); status never by colour alone.
- `apps/web/src/lib/results-contract-checks.ts` (edited, additive): accept `["1.3.0","1.4.0"]`
  (`SUPPORTED_RESULTS_CONTRACT_VERSIONS`) — kept the exported `RESULTS_CONTRACT_VERSION = "1.3.0"` so
  the committed-document test stays green; added shape checks for `building_alternatives` and
  `coverage_by_portion`, including the R556/R570 refusal: a withheld coverage carrying any number is
  rejected.
- Tests (NEW): `components/architect/answers/__tests__/first-building-options.test.tsx` (S1–S7 + older
  doc + draft gate); `lib/architect/__tests__/first-building-options.test.ts` (view model);
  `lib/__tests__/results-contract-checks-1-4-0.test.ts` (client check of the 1.4.0 blocks).
- Tests (edited): `components/architect/answers/__tests__/three-answers-panel.test.tsx` — the generic
  fixture loop computes the building-option card's expected text through the same override for the two
  1.4.0 fixtures (helpers `notAvailableFor` / `gapKindFor`). No committed-benchmark expectation changed.
- `project-control/reports/M5-T147-part-C.md` (this file, replacing the placeholder).

## Scenarios: input state, expected, test name

| Scenario | Input state | Expected (read from the document) | Test name |
|---|---|---|---|
| S1 | benchmark fixture, building B | labelled alternative + floor-schedule table (3 rows, 6,716.67 plan, 20,150 running total, 30 ft), list-driven; nothing feasible | `S1: shows building B as a labelled alternative with its floor schedule, from the list` |
| S2 | benchmark, building B estimate | "Preliminary capacity estimate", 17.27 to 21.59, share 0.60–0.75, size 700 sq ft as preliminary assumptions | `S2: shows the building's preliminary capacity estimate as editable preliminary assumptions` |
| S3 | benchmark, coverage withheld | reason (law by portion) shown, NO footprint figure, resolved-by shown | `S3: shows coverage by portion withheld with its reason and NO square-foot figure` |
| S3b | coverage-available fixture | footprint 8,000 sq ft, 100%, 80%, 100 ft shown | `S3b: when the document carries an available coverage, shows its figures` |
| S4 | benchmark, legal limit withheld | "Legal dwelling-unit limit" + "Not known — reason", no number, no value element, separate from estimate | `S4: shows the legal dwelling-unit limit withheld — no number, separate from the estimate` |
| S5 | benchmark (coverage withheld, building footprint available) | coverage block has no footprint and never the building's 6,716.67 figure | `S5: a withheld coverage result never falls back to a substitute value (R570)` |
| S6 | benchmark, building B | Conditional marker; not-checked list equals the document's; never "feasible" | `S6: shows what has not been checked and never calls an option feasible` |
| S7 | benchmark (1.4.0) | overall label "Preliminary zoning results" in the status strip | `S7: the overall results label stays 'Preliminary zoning results' on a 1.4.0 document` |
| (invariant) | 1.2.0 stable fixture | no first-building-options section | `an older document with none of the new blocks shows no first-building-options section` |
| (draft gate) | benchmark, architect surface | not-reviewed line, no numbers | `on a draft architect surface the options are hidden behind the not-reviewed gate` |

S8 (the e2e human-journey walkthrough) is the second half. S7's "web content tests pass against the
regenerated document" is also the second half (those tests read the committed benchmark document that
part E regenerates).

## Expected vs what the code returned

Every expected value is READ from the loaded synthetic fixture through the module's own formatters
(no number retyped), matching the existing suite's discipline. The fixtures trace (M5-T146 part A) to
`docs/reference-cases/R6B/cases/step-p6-worked.json` rows `real-building-b` (3 storeys of 6,716.67;
20,150 total; 30 ft) and `real-estimate-b` (20,150 → 17.27 / 21.59 at share 0.60–0.75, size 700) and
the coverage-by-portion rows. The code returned exactly those rendered values; all scenario tests
pass (23 new tests). The legal dwelling-unit limit is withheld on the benchmark by the document's own
`unit_estimate` (`not_available`), so the panel shows it withheld (the step-p6 `real-unit-limit`
figure of 29 is intentionally NOT shown — it is not a substitute for the estimate, R688).

## Mutation proofs (one branch; mutate → red → restore; repo left clean)

- MUT1 — removed the withheld-coverage number-refusal loop in `results-contract-checks.ts`
  (`checkCoverageByPortion`). RED: `results-contract-checks-1-4-0.test.ts > R556/R570: refuses a
  withheld coverage result that carries a footprint figure` (1 failed | 5 passed). Restored; the
  guard text is back and all 16 contract tests pass. (This restore initially used `git checkout`,
  which reverted the whole file to base; I re-applied every edit and re-verified.)
- MUT2 — neutralized the building-option override in `three-answers.ts`
  (`pointsToAlternatives = false && …`). RED: 6 panel tests over the two 1.4.0 fixtures, including
  `shows no internal code, value key or source id …` (the machine field `building_alternatives` then
  leaks through the single-option card's raw reason). Reverted with an Edit; panel test green (77/77).

## Checks, one at a time, with direct exit codes (this Linux dev server; never the owner's PC)

- `npx --yes npm@11.18.0 ci --no-audit --no-fund` → exit 0 (once per worktree; lockfile only, no
  package added).
- `npm run lint` → exit 0 (0 errors; 2 pre-existing warnings in files I did not touch:
  `lot-site-setup.test.tsx`, `study-vocabulary.test.ts`).
- `npm run typecheck` → exit 0.
- `npx vitest run src/components/architect/answers src/lib/architect src/lib/__tests__` → exit 0;
  **Test Files 50 passed (50); Tests 1131 passed (1131)** (includes my 23 new tests and the
  committed-document tests, which stay green because 1.3.0 is still accepted and the committed doc is
  unchanged).
- `python tools/modularity_check.py --check` → exit 0 (no new flag on any file I wrote/changed).
- Did NOT run the api suite (CI's), nor Playwright e2e (second half).

Frozen baseline recorded before editing: lint 0, typecheck 0, and exactly 2 vitest failures
(`three-answers-panel.test.tsx > … shows no internal code …` for the two 1.4.0 fixtures), caused by
part A's `building_option` reason naming `building_alternatives`; my part C closes that.

## What the NEXT parts must know

- New exports in `lib/architect/three-answers.ts`: `hasBuildingAlternatives(results)`,
  `BUILDING_OPTIONS_BELOW_REASON`, and `conditionList` (now exported).
- New module `lib/architect/first-building-options.ts`: `firstBuildingOptionsView(results,
  showDraftValues)` and formatters `sqft`/`feet`/`percent`/`twoDp`; view types `CapacityView`,
  `CoverageView`, `LegalLimitView`, `BuildingAlternativeView`, `FloorRowView`,
  `FirstBuildingOptionsView`; `LEGAL_UNIT_LIMIT_LABEL`.
- New component `components/architect/answers/FirstBuildingOptions.tsx` with testids:
  `first-building-options`, `first-building-options-draft-hidden`, `building-alternative`(+`-label`,
  `-summary`, `-withheld`, `-not-checked`, `-not-checked-item`), `floor-schedule`(+`-row`),
  `option-conditional`(+`-marker`), `option-condition`, `capacity-estimate`(+`-label`, `-range`,
  `-wholes`, `-assumptions`, `-share`, `-size`, `-not-known`), `legal-unit-limit`(+`-label`,
  `-value`, `-not-known`), `coverage-by-portion`(+`-label`, `-reason`, `-gap-kind`, `-resolved`),
  `coverage-footprint` (available branch only), `option-rule-sections`.
- `results-contract-checks.ts` now accepts contract 1.4.0; `RESULTS_CONTRACT_VERSION` stays "1.3.0"
  and `SUPPORTED_RESULTS_CONTRACT_VERSIONS = ["1.3.0","1.4.0"]`.
- SECOND HALF: the e2e `results.flag-on.spec.ts` and the committed-document tests
  (`journey-215-16-northern.test.tsx`, `results-api.test.ts`, `results-contract-checks.test.ts`)
  update once part E regenerates `recorded_215_16_northern_journey.json` to 1.4.0 — then the
  journey/e2e assert the 1.4.0 blocks and that test's `RESULTS_CONTRACT_VERSION` pin can read 1.4.0
  (the accept-both change already supports it).

## STOP / doubt

- The brief (line 19) asks the "unchanged screen" proof on "an existing 1.3.0 fixture"; the ONLY 1.3.0
  fixture is the committed benchmark, which part E regenerates to 1.4.0, so I proved the invariant with
  a stable 1.2.0 synthetic fixture instead (and a view-model test covering every fixture without the
  blocks). The 1.3.0-specific proof belongs to the second half. No scope widened, no expected value or
  tolerance changed.
- DB-213(a): the share/size are shown as preliminary assumptions but NOT yet editable on screen
  (ruling W7; the input path is not wired end to end) — recorded, work owed.

END-OF-REPORT

## Second half — the website against the REGENERATED document

Base (reset HEAD): `455caec46895298a772505cdf34325d7fd758d96` (first half cherry-picked as `b6540dc67`,
plus the server wiring and the regenerated benchmark document at contract 1.4.0).

### What the regenerated document changed, and what I did
- Each listed building gained an OPTIONAL `fit_note`; the `label` became a short name. The screen now
  reads `fit_note` (view `BuildingAlternativeView.fitNote`) and shows it beside the building as plain
  text (`FirstBuildingOptions.tsx`, testid `building-alternative-fit-note`). Point 2 met.
- The older blocks changed meaning: `unit_estimate` and `floor_stack` now say "given in
  building_alternatives" (a pointer, and the text names the contract field); the older coverage answer
  (`max_lot_coverage` value state) carries the SAME reason as `coverage_by_portion`. My first half
  rendered a "Legal dwelling-unit limit" block FROM `unit_estimate`; against the regenerated document
  that mislabelled a pointer AND leaked the machine field name `building_alternatives` onto the panel
  (it reddened the whole-panel snake_case guards in `results-panel.test.tsx` and
  `three-answers-panel.test.tsx`). Fix: I removed the legal-limit-from-`unit_estimate` rendering
  entirely (`first-building-options.ts` + `FirstBuildingOptions.tsx`). Point 3 handled — see below.
- Ruling W7: corrected `first-building-options.ts` (the comment that called the share/size "editable")
  and the on-screen heading (`Preliminary assumptions you can change:` → `Preliminary assumptions used
  (not editable here):`). No user-visible text now says they can be changed here.

### What the panel does with each older block (point 3 — no contradiction)
- `building_option` (answer): not_available; the card shows a plain pointer "Not available — the
  worked building options are shown below" (first-half override), never the document's machine reason.
- `unit_estimate`: NOT rendered by the panel (it is a pointer to the list). The legal dwelling-unit
  limit itself is a withheld value_state (`legal_unit_limit_standard`) of the floor-area-allowance
  answer, shown by that answer card as "Not known — …" with no number — proven by
  journey-215-16-northern.test.tsx S4.
- `floor_stack`: never rendered by this panel (it was not in the reader before and is not now); no
  contradiction with the shown floor schedule.
- older `max_lot_coverage` value state: shown by the envelope card as withheld with its reason; it
  agrees with the withheld `coverage_by_portion` block (same reason), so no contradiction.

### Tests updated to follow the regenerated document (committed-document leg)
- journey-215-16-northern.test.tsx: contract assertion 1.3.0 → 1.4.0; added S1/S2/S6 (building B,
  floor schedule, conditions, not-checked, estimate), fit_note, S3 (coverage withheld, no figure),
  S4 (legal limit withheld on the allowance card, no number), and the building-option pointer guard.
- three-answers-panel.test.tsx: the S5 journey test now reads the withheld-gap split from the
  document (coverage + rear yard are missing_information, setback work_owed) and asserts the single
  building option carries no gap-kind line and still reads "Not available".
- three-answers.test.ts: the building_option gapKindLine test rewritten for the override (points to
  the list, no gap line).
- first-building-options.test.ts/.tsx: dropped the legal-limit assertions; added fit_note mapping;
  S4 now asserts the section does NOT restate the legal limit.
- results-contract-checks.test.ts: comment + the committed-document test follow 1.4.0 (version
  acceptance already included 1.4.0 from the first half).

### Checks (THIS Linux machine; direct exit codes)
- `npm run lint` → 0 (0 errors; 2 pre-existing warnings in files I did not touch).
- `npm run typecheck` → 0.
- `npx vitest run src/components/architect src/lib` → 0; **Test Files 103 passed (103); Tests 2206
  passed (2206)** (frozen baseline before edits was 5 failed across 4 files; all closed).
- `python tools/modularity_check.py --check` → 0.
- `npm run build` → 0 (needed so `next start` serves the e2e servers).
- e2e, lanes venv first on PATH + `PYTHONPATH=<worktree>/services/api`,
  `npx playwright test e2e/results.flag-on.spec.ts` → 0 (1 passed). See STOP below for why the new
  section is NOT asserted in the browser test.

### Mutation proof (point 2)
In `FirstBuildingOptions.tsx` I guarded the fit_note render with `false && …`; vitest then reddened
`journey-215-16-northern.test.tsx > … shows fit_note beside the building as plain text` ("Unable to
find [data-testid=building-alternative-fit-note]"); 17 passed | 1 failed. Reverted with an Edit; the
suite is green again.

### STOP (server-side, outside this task's files)
The LIVE results route cannot show the first-building-option section in the browser on this lot. I
ran the real engine through the e2e harness (`e2e/harness/fixture_api.py`, which imports THIS
worktree's `app` — verified `three_way_document.__file__` is in this worktree and `_apply_first_option`
is present) and POSTed BBL 4073340070 with three request bodies — default,
`floor_to_floor_ft=14`, and with the special-density statement. ALL returned **contract 1.3.0 with
`building_alternatives` absent and `coverage_by_portion` absent**, even though the floor-area answer
carries the `contradicted_record` condition. So the server-side `_apply_first_option` gate in
`services/api/app/scenario/three_answers/three_way_document.py` does not emit the 1.4.0 blocks for the
harness document, whereas the REGENERATED committed document (produced by part E) IS 1.4.0 and carries
them — the live engine output and the regenerated fixture disagree for this lot. `services/api` is a
forbidden path and the harness may not be changed, so I did NOT assert the new section in
`e2e/results.flag-on.spec.ts`; I left a NOTE there and kept the existing journey green (exit 0). The
new section's screen behaviour is fully proven by the vitest leg against the regenerated committed
document. The orchestrator should confirm whether the live read route is expected to emit the 1.4.0
blocks for this lot (a part B / part E consistency question) before relying on the browser leg.

END-OF-SECOND-HALF
