# M5-T181 reviews (every return kept unchanged)

- Two build rounds. Round 1 (builder 689d4b0f, integrated 3edf9ae0): the lead band above the unchanged 44:56 grid. The orchestrator measured it on the real preview built from the branch at 1bec7065 (session-2026-10-14d/six-after-1bec7065/positions.txt) and read CI run 38651131040: the assumed conditions left the first screen, but the ceiling and estimate sat 21-49 px below the Results window's visible end at 768-1920 px, and the new spec's results requests exhausted the route's limit (the unedited results.flag-on.spec.ts:68 went red with 'Too many requests'). Round 2 (a fresh builder, 519f219f, integrated 965de3d5): the allowance beside the ceiling and estimate, the status strip after them, a smaller heading on phones; the spec rewritten to 2 results requests and to assert each value's bottom inside the window. Each round passed an independent read-only pre-integration check (ci-evidence-verifier: scope, digests, lint, typecheck, 591 vitest re-run).
- G2 orchestrator self-check at 965de3d5: 5 files, all inside the 5 allowed paths; LF sha256 equal to both builders' returns; lane coverage PASS. Measured on the real preview built from the branch at f78d302f (six-after-f78d302f/positions.txt): at 768, 1024, 1440 and 1920 px the allowance, the ceiling (top 531-550) and the estimate (565-584) lie inside the window (visible to 795); the assumed conditions start at 977 or lower (they started at 356 at 1440 before); at 390 and 320 the allowance is in the first screen and the ceiling's top is 848 and 963 (under 1.25 x 844). CI run 38655118526 at f78d302f: web-e2e 171 passed (both new first-screen tests and the unedited layout and journey specs); the api and exact-production-install jobs were red on the five review-register tests that belong to M5-T167 (fixed by its integration).
- G3 walkthrough (human-journey-reviewer) at 965de3d5: PASS, no required correction; advisories: on phones the ceiling is one short scroll away; only the allowance leads among the three answers; the status strip now follows the results.
- G3 visual (visual-quality-reviewer) at 965de3d5: PASS, no required correction; advisories: the status strip falls below the first screen; the unit wraps at 320 px (pre-existing); white space under the shorter allowance card; CI at the after head to be read by the orchestrator.
- G4 qa-engineer at 965de3d5: PASS, no required correction; S1-S8 reproduced (lint 0, typecheck 0, 591 passed; whole web suite 2703 of 2704, the one time-out in entry.test.tsx outside the task passes alone and in CI); forbidden paths byte-identical; probes caught; 2 results requests; advisories: the packet's S4 order text (corrected by the scope note), the 640 px switch, one helper that could pass vacuously (mitigated by the bottom assertions).
- The advisories are backlog DB-264 (for the later website task M5-T174); none changes a figure or a word.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (visual-quality-reviewer) - part 1

M5-T181 — G3 independent VISUAL review (visual-quality-reviewer, read-only). I am an AI agent; this is not a human or professional review. Reviewed head f78d302f (material commits 3edf9ae0 round 1 + 965de3d5 round 2) in /root/project/w-wave20.

VERDICT: PASS. The change does what the owner's outside reviewer asked ("the visible screen still gives substantial space to assumptions while results sit farther down") and does it cleanly at all six widths. No blocking defect. Four ADVISORY notes; none require a code change for this visual gate.

1) HIERARCHY — share of the first screen held by results, before vs after (from positions.txt + the pictures):
- 1440 & 1920 (two-column, the reviewer's case): BEFORE, the Assumed-conditions list sat at top 356 and filled essentially the whole RIGHT HALF of the first screen (~50%, visible to 795), while the allowance headline was a sliver at 737 and the ceiling/estimate were below the fold. AFTER, the assumed conditions drop to top 977 (below the fold — 0% of the first screen) and the allowance BESIDE the legal ceiling and the apartment estimate fill the lower band (allowance 561, ceiling 539, estimate 573 — all in the first screen). The reviewer's exact complaint is resolved.
- 768 & 1024: BEFORE single-column, ceiling/estimate below the fold (1246/1218). AFTER they reach the first screen side by side (768: ceiling 550, estimate 584; 1024: 531/565). Assumptions below (4353/3754).
- 390 & 320 (phones): BEFORE the allowance headline was below the fold (797/946). AFTER it is in the first screen (605/696); the ceiling is one short scroll away (848/963, both < 1.25x the 844 height = 1055 — design choice b). The address heading steps down one TYPE TOKEN (--pt-type-section-title-size) so the long address wraps to two lines instead of three, pulling the allowance up. The status strip is removed from between the identity and the allowance. Round-1 (1bec7065) phone was byte-identical to BEFORE; round 2 is the real fix, so this is genuine new work, not a repeat.
Across all six widths the ceiling and estimate read as a pair under one heading, with the distinction line ("The ceiling is a conditional zoning limit; the estimate is an unvalidated apartment-yield range; neither is a demonstrated layout") directly beneath them. The assumed conditions no longer dominate any first screen.

2) UX-07 at 320/390/768/1024/1440/1920 — I SAW ALL SIX in pictures (six-after-f78d302f/first-<w>.png). No clipped text, no horizontal page scroll (overflow px = 0 at every width in positions.txt and the capture log), no overlapping labels, no obscured control, no awkward empty band from the move. The one wrap I see is the headline unit at 320 ("20,150 sq" / "ft Conditional"), which is pre-existing .ta-headline-unit CSS untouched by this task and present in the BEFORE capture too (finding 3). The side-by-side figures leave white space under the shorter allowance card on wide screens — normal align-items:start, reads fine (finding 4). CI at f78d302f I could NOT run (finding 1); the six-width coverage is fully established from the pictures, so my visual verdict does not depend on it.

3) CONSISTENCY with the contract furniture/tokens: the new CSS adds .ta-lead (block) and .ta-lead-figures (block, becoming a two-column grid at @container min-width:640px with gap var(--pt-space-24)), plus a .ta-identity-lot type step-down at @container max-width:480px and a .ta-layout margin-top var(--space-4). Every token resolves in globals.css; both the --pt-* and --space-* naming schemes already live in this file, so nothing new is invented. No colour literal and no number literal appears in any property value; 640/480/1000px are @container breakpoints (which cannot reference custom properties) and match the file's existing 1000px/700px breakpoints. container-type:inline-size is already on .workspace-window__content (workspace.css:53), so the queries resolve, and the detail grid keeps its 1000px switch (design choice d). The cards and the Conditional/Provisional chips are the existing styles, unchanged. No default-template appearance. Scope is clean: only the five allowed apps/web + report paths changed; no forbidden file (ApartmentFigures, ScopeSummary, AnswerCard, globals.css, presentation-tokens.json, FloatingWorkspaceWindow, the other e2e specs) was touched.

Judgement on the known design choices: (a) lead band above the unchanged 44:56 grid — good; keeps results-layout S1/S12 unedited while pulling results up, and serves the architect. (b) one short phone scroll for the ceiling — acceptable; the decisive allowance headline leads and the ceiling is within 1.25x. (c) shared window height unchanged — fine. (d) status strip moved after the results and figures side-by-side from 640px — serves the reviewer's point; my only caution is that the strip now falls below the first-screen fold at every width (finding 2), though the per-result chips and the "— rules not professionally reviewed" heading keep the qualification on the first screen, consistent with contract principle 1.

What I checked and could not check are listed in the structured fields. The orchestrator must confirm the f78d302f web-e2e job is green before accept (finding 1); that is the only open precondition, and it is an orchestrator/qa action, not a visual defect. On the visual requirements this task is a clear, well-scoped improvement.

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 2

# M5-T181 — G3 human-walkthrough review (Results window first screen)

I am an AI agent (human-journey-reviewer), read-only, following /human-walkthrough. I did not produce this task and did not drive a browser or run Playwright (ports 3000/3001/8000 are the owner's). I walked the journey from the orchestrator's BEFORE/AFTER pictures at six widths, the positions.txt files, report page-01.png, the diff at 965de3d5, the packet M5-T181.json, the producer report, and the e2e/vitest specs. Reviewed head 965de3d5 (after-pictures head f78d302f differs only in control records).

Verdict: PASS. No required corrections; three advisory notes.

## 1. The ten-second first-screen read
Desktop 768/1024/1440/1920: the first screen now shows, without scrolling, the property (215-16 NORTHERN BOULEVARD, Queens; block 7334, lot 70), the main answer (Floor-area allowance 20,150 sq ft, Conditional), the legal ceiling (29, Conditional) beside the apartment estimate (17-22, Provisional), and the difference between them (the distinction line). positions.txt f78d302f: allowance, ceiling and estimate all "first screen" at all four widths; the assumed-conditions top moved from 356 (BEFORE, first screen at 1440/1920) to 977 (below). This directly answers the reviewer's point — "substantial space to assumptions while results sit farther down" — at 1440 and 1920 (where it was literally true), and brings the ceiling/estimate onto the first screen at 768/1024 too (they were at 1218-1246 BEFORE).

Phones 320/390: the allowance headline now leads the first screen (BEFORE it was cut at the bottom — the status strip sat between identity and allowance; the round-2 strip move + heading step-down pulled it up). The legal ceiling/estimate are one short scroll below the fold (ceiling top 963 at 320, 848 at 390; both < 1.25x844=1055). Assumed conditions far below (8757/6818). (Finding F1.)

Where it answers the reviewer: FULLY at 768, 1024, 1440, 1920 (allowance+ceiling+estimate on the first screen, assumptions below); PARTIALLY at 320, 390 (allowance leads, ceiling one short scroll).

## 2. Conditions stay attached
The ceiling/estimate block is the unchanged, forbidden ApartmentFigures component. On the after-1440/after-768 pictures every qualifier stays on its number: the Conditional chip on the allowance and on "Legal ceiling 29"; Provisional on "Estimate 17-22"; the distinction line; the lot-area basis ("10,075 sq ft recorded lot area x FAR 2.0, tax lot 70 alone"); and the zoning-lot concern ("If lot 70 alone is the zoning lot..."). Nothing material was removed. The assumed-conditions list keeps all 13 rows open (R119, demote-not-cap; the forbidden journey test still pins 13), moved below the results band — reachable by scroll, not hidden. "What needs resolving" (SharedConditions) stays in the detail-grid left column. The one status strip moved to after the results (F3).

## 3. Order vs report page 1
page-01.png order: results -> site graphic -> ceiling beside estimate -> uncertainties. Website after: identity -> allowance beside ceiling/estimate -> status strip -> (permitted envelope, building option, what-needs-resolving, assumed conditions). The high-level order — results, then the ceiling/estimate, then the uncertainties — matches. Two minor/intended divergences: only the allowance leads among the three answers (F2); and the status strip trails the results rather than preceding them (F3).

## 4. Plain words / labels
Placement-only change; no visible wording changed (diff is JSX moves + CSS + comments). Forbidden-word grep over the two changed files: none. The 29 keeps Conditional and is never shown settled (after pictures confirm). presentation-tokens.json, ApartmentFigures, AnswerCard and three-answers.ts untouched.

## Non-regression spot-check
The forbidden results-layout.flag-on.spec.ts S1 measures three-answers-left's width (still the 44fr column) and S12 queries identity+allowance at the dialog level (getByTestId on the dialog, not within three-answers-left). Moving them into the lead band keeps both in viewport — structurally no regression. The 44:56 grid ids and columns are preserved in the diff. The composition vitest (S4) now pins the lead order identity -> allowance -> apartment-figures -> status strip and that apartment-figures precedes three-answers-scope.

## The real-person check is NOT run
The ten-second / one-minute reader check with a real human (contract R062) is not performed — it requires a person. I am an AI agent; this is a structured walkthrough from evidence, not a human or professional review.

## Findings
F1 (ADVISORY) — Phones 320/390: the legal ceiling and estimate sit below the first-screen fold (one short scroll; positions ceiling top 963/848 < 1055). Accepted by packet S3, but it leaves the owner's "ceiling and estimate appear together" goal unmet on phones. Correction: carry the results-scoped-window-height open question forward (do not change the shared FloatingWorkspaceWindow here) so the ceiling/estimate can reach the first screen on phones.

F2 (ADVISORY) — The lead shows only the floor-area allowance among the three answers; the permitted-envelope ("Up to 55 ft") and scheduled-building ("3 storeys") answers that page 1 leads with in large type are demoted below the ceiling/estimate. Intended by the packet and defensible; note for owner awareness or a later parity pass (M5-T174).

F3 (ADVISORY) — The status strip moved from above the allowance to after the results band (round-2 deviation from the packet objective's stated order). Acceptable and consistent with page-1 "result first, context after"; on desktop it may now fall below the fold. The per-number chips and distinction line carry the material qualification on the first screen regardless.

## Checked
Six-width BEFORE (30762409) vs AFTER (f78d302f) pictures and positions.txt (plus round-1 1bec7065); report page-01.png; the net diff at 965de3d5 of ThreeAnswersPanel.tsx, three-answers.css, the composition test and the new e2e spec; packet scenarios S1-S8; producer report; forbidden results-layout S1/S12 (structural non-regression); forbidden-word grep.

## Not checked
I ran no browser/Playwright and no CI/gh or git write (read-only). Per-width CI pass/fail is corroborated by the orchestrator's real-preview positions.txt at f78d302f and must be confirmed by the orchestrator reading CI at the head; the api / exact-production-install jobs are known-red on unrelated review-register tests (M5-T167's fix) and must not count against M5-T181. The internal ceiling-vs-estimate layout is ApartmentFigures' (M5-T171) domain, out of scope. The real-person reader check (R062) is not run.

END-OF-REPORT

## G4 (qa-engineer)

# M5-T181 — G4 QA gate report (independent, read-only)

I am an AI agent (qa-engineer), not a human or professional reviewer. I did not produce this task. Reviewed at the pinned commit `965de3d5` (branch head `f78d302f`, which differs only in control records). Worktree source `/root/project/w-wave20`; all runs in a `git archive` copy under my scratch folder with `apps/web/node_modules` symlinked. Verdict: **PASS** (ADVISORY findings only; none block acceptance).

## What the task had to do
R151 (owner's outside reviewer, verbatim): "The visible screen still gives substantial space to assumptions while results sit farther down." The Results window's first screen must lead with the results (floor-area allowance, then legal ceiling beside apartment estimate), assumptions below — a placement/reading-order change only, no figure/label/certainty/wording change.

## Scope and provenance (probes 4, 7)
Both material commits (`3edf9ae0`, `965de3d5`) touch ONLY the 5 allowed paths (ThreeAnswersPanel.tsx, three-answers.css, three-answers-panel.test.tsx, results-first-screen.flag-on.spec.ts, producer report). No package.json/package-lock change. All 15 forbidden paths are byte-identical between claim head `658e51fb` and `965de3d5` (`git diff` = 0 lines each), including ApartmentFigures.tsx, ScopeSummary.tsx, AnswerCard.tsx, apartment-figures.ts, three-answers.ts, presentation-tokens.json and the four M5-T167 e2e/harness files. The extra files in the `658e51fb..965de3d5` range (CODING_RULES, PROGRAM_KNOWLEDGE, M5-T167 json/gate, state.json) come from intervening non-T181 commits, not from T181's material commits. No forbidden word (buildable/achievable/can be built) in either changed source file. CSS uses design tokens only (--pt-space-24, --pt-type-section-title-*, --space-4), no colour/number literals; the detail grid's @container(min-width:1000px) 44:56 switch is unchanged.

## Scenario results (scenario | how tested | result | exit)
| S | How tested | Result | Exit |
|---|---|---|---|
| S1 | CI web-e2e `results-first-screen...:173` + positions.txt (ceiling/estimate tops 550/584@768, 531/565@1024, 539/573@1440/1920, all <=795 fold) | PASS | CI job success |
| S2 | CI S2 block (width>=1440: figures.y+h<=scope.y, resultsPrecedeAssumptions) + vitest S4 DOM order + positions (scope 977 > ceiling 539 @1440) | PASS | CI/vitest 0 |
| S3 | CI `...:237` + positions (allowance 605/696 first screen @390/320; ceiling 848/963 < 1.25x844=1055) | PASS | CI success |
| S4 | local `npx vitest run src/components/architect/answers src/lib/architect` | PASS (591/591) | 0 |
| S5 | forbidden files byte-identical; vitest token/X5 tests in the 591; forbidden-word grep clean | PASS | 0 |
| S6 | CI: results-layout.flag-on.spec.ts all widths + S12@1440 & @390 + results.flag-on.spec.ts:68 all green UNEDITED; 13-row suites byte-identical+green | PASS | CI success |
| S7 | folded into both CI sweeps (overflow<=1, clippedText==[]) | PASS | CI success |
| S8 | local lint exit 0 (0 err, 2 pre-existing warnings), typecheck exit 0, focused vitest 591 exit 0; CI web job success | PASS | 0 |

## My own probes
1. Moved ApartmentFigures out of the lead back into the left column: ran S4 -> FAIL "Unable to find [apartment-figures]" at `within(lead).getByTestId`, exit 1; file restored byte-identical (sha c76263770c4...). Reading the e2e: the new spec's S1 would also fail (ceiling/estimate drop below the ~795 fold -> boxBottom > visible bottom), and S2 would fail (apartment-figures in the left column after the cards sits below the right-column scope, so `figures.y+h <= scope.y` is false). So the move is guarded by S4 and by the e2e.
2. Moved ScopeSummary above the allowance (out of the right column): ran S4 -> FAIL "Unable to find [three-answers-scope]" at `within(right).getByTestId`, exit 1; restored byte-identical.
3. S2 at 1440x900: the spec asserts `resultsPrecedeAssumptions` (DOM: apartment-figures precedes three-answers-scope) AND `figures.y+figures.height <= scope.y+0.5`. If the assumed-conditions list started above the ceiling (scope.y < figures' bottom, where the ceiling lives inside apartment-figures), the vertical assertion is false and S2 fails. It genuinely catches the R151 ordering defect.
4. Forbidden byte identity: confirmed (above).
5. Vacuous-pass: boxBottom throws on a missing element (fails, not skips); resultsPrecedeAssumptions returns false -> expect(true) fails; toBeInViewport fails on 0 elements. Core assertions cannot pass vacuously. One soft spot (parityCellsOverlap returns false when a cell is absent) — Finding 3, mitigated.
6. Results requests: exactly 2 tests, each calling `openResults` once; the POST trigger (`results-show` click) occurs only inside openResults; the resize loops re-measure without refetching. 2 <= 3. CI proof: round-1's rate-limit red (results.flag-on.spec.ts:68 "Too many requests") is now green.
7. Allowed-path-only + no package: confirmed (above).

## CI at head f78d302f (run 38655118526)
web (lint+typecheck+build) SUCCESS; web-e2e (vitest+Playwright) SUCCESS — both new-spec tests and the unedited results-layout (all widths, S1, S12@1440 & @390) and results.flag-on.spec.ts:68 pass. api and exact-production-install FAIL on exactly 5 tests, all in test_zoning_rule_review_register*.py about three_way_document.py (an M5-T167 file T181 never touches) — not T181's defect (Finding 4).

## R151 effect (before -> after, positions.txt)
At 1440/1920 the assumed-conditions top moved from 356 (top of first screen — the defect) to 977 (below the 795 fold); ceiling rose from 1382 to 539 (first screen). The results now lead; the assumptions follow. Six before/after captures are DISTINCT at every width (different sha256), so they are genuine evidence of the change (addresses the identical-image concern).

## Judgement of the known design choices
(a) Lead above the unchanged 44:56 grid so results-layout S1/S12 stay unedited — serves the reviewer's point and avoids colliding with M5-T167; positions show the scope demoted below the fold at desktop, better than the risk note feared. (b) Phone one-short-scroll for the ceiling (848/963 < 1055) with the allowance headline in the first screen — acceptable within the shared 690px window. (c) Shared window height unchanged — correct (no shared-component edit). (d) Strip-after-results and 2-up-from-640px — both sanctioned by the round-2 brief; serve the architect. I would only reconcile the stale packet S4 text (Finding 1).

## Verdict
PASS. All 8 scenarios pass (CI + local + measured positions), all 7 probes confirm, scope is clean, forbidden files untouched, no package, no fact/label/wording change, and R151 is demonstrably resolved. Findings 1-5 are ADVISORY and do not block acceptance; Findings 4-5 are unrelated-CI / flaky and not counted against M5-T181.

END-OF-REPORT
