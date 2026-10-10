# M5-T149 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `db7824e70e0ca0fbd6e5fb4b61a57621a899fb8c` (branch `task/wave20-presentation-slice`, review copy `/root/project/rv-w6-b`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R256, R267, R526, R543, R544, R556, R570, R641, R700, R804, R805, R807, R809, R810, R811, R812, R813, R816, R817, R819, R820, R821, R822, R823, R824, R825, R826, R827, R828, R829, R830, R831, R832, R833, R856, R859, R869, R870, R871, R872, R873, R874, R875, R876, R877, R881, R882, R885, R886, R888, R890, R894, R895.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - NONE blocking. The four standing advisory NOTEs are non-blocking and need no rework for this gate: (a) the results-layout clipped-text helper skips any element bearing a clip-path (slightly broad; overflow:hidden clipping still caught); (b) AnswerCard's `conditionNames` prop is passed but no longer read (dead param); (c) the phone full-height CSS rule applies to all non-maximized floating windows, not Results-only (desktop-safe); (d) an unreachable path I found myself — lib/architect/three-answers.ts:308/373 still defines and wires BUILDING_OPTIONS_BELOW_REASON = "the building options are shown below", but on the benchmark the panel routes the building_option answer through BuildingOptionCard (scheduled area) whenever firstBuildingOptionsView is non-null, so the "shown below" text is not rendered (tests assert the benchmark never shows it) — latent/defensive, non-blocking. - NOT corrections but OWNER follow-ups owed (not this task's to fake): a real-person ten-second walkthrough (R817) and a real assistive-technology/screen-reader pass (R877); both are honestly disclosed as not performed.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-10 04:58 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T149 (directive D-090, 53 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is NOT a human or professional review. I produced none of this work. Every gate record, evidence map, producer report and the launch brief was treated as an unverified claim and re-derived from primary evidence (source code, tests, fixtures, git objects, the registry). READ-ONLY: I wrote no file, made no commit, ran no project_control write subcommand, reran no CI, and never touched ports 3000/3001/8000.

(1) HEAD VERIFIED
The frozen head db7824e70e0ca0fbd6e5fb4b61a57621a899fb8c is checked out clean (empty `git status`) in /root/project/w-wave20 on branch task/wave20-presentation-slice; `git rev-parse HEAD` == that sha. My own copy /root/project/rv-w6-b could not be moved to it (the read-only guard blocks `git checkout`), so I read the frozen head through git plumbing (`git archive db7824e70e0c | tar -x` into scratch, plus `git -C /root/project/w-wave20 show`/`git diff`). The directive validator and both registry digests were computed against the on-disk frozen head. Base of the branch: 0bb6acb293278d125e31c76da18e4ffe6e4b9ac1. Reviewed code head d745b635; the diff d745b635..db7824e7 touches ONLY 26 project-control files (no apps/packages/services/.github/tools/render.yaml), so the frozen head's product content is byte-identical to the reviewed head.

(2) ROWS (each: this task's WEBSITE share; the row itself stays OPEN/pending in the registry for its other surfaces)

ROW D-090-R256 — PASS
 - The entered floor-to-floor height is read from the document and shown on the identity line (ThreeAnswersPanel.IdentityLine, IDENTITY_KEYS includes floor_to_floor_ft) and in the folded one-line inputs summary (ResultsForm.summarizeInputs), so no value is used in a calculation without being shown.
 - ResultsForm exposes the height as a labelled numeric input with unit, bound and Reset (confirmed in source + G3 CHECK 6), satisfying "visible, editable starting values / no hidden defaults" for the inputs this screen carries.
 - OPEN for later work: editing the apartment-size and efficiency-share assumptions on the screen (DB-213 a) — they are displayed but not yet editable here.

ROW D-090-R267 — PASS
 - The building-option card renders "Site fit not verified" plus the document's not_checked list (AnswerCard.BuildingOptionCard / FirstBuildingOptions), and conditional figures carry the plain-text "Conditional" marker (AnswerCard.ConditionalMarker), so nothing dependent on an unchecked item reads as confirmed.
 - result-status.ts has no "verified" code path (exhaustive settled/conditional/withheld); first-building-options.test.tsx S6 asserts the section never says feasible/complies/validated.
 - OPEN: the PDF/report surfaces carry this "never confirmed via disclaimer" rule further.

ROW D-090-R526 — PASS
 - The benchmark fixture's building_alternatives[0].not_checked includes the literal "Parking, loading and bicycle requirements" (packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json), and the card renders each not_checked item verbatim (first-building-options.test.tsx asserts items == buildingB.not_checked).
 - The website-typed parking line was removed (ruling V11(9)); G4 mutation 8 (re-adding it) was caught; no rendered text calls an option feasible (S6 negative assertion).
 - OPEN: capturing/resolving the actual parking/loading/bicycle provisions and the report counts section are later work (R517 chain).

ROW D-090-R543 — PASS
 - The estimate label is read from the document and branched on exactly ("Preliminary capacity estimate" vs "Not known") in lib/architect/first-building-options.ts (lines 243, 340) — the website never invents the label.
 - lib/architect/__tests__/first-building-options.test.ts and the component tests cover the shape/no-shape cases via the committed fixtures.
 - OPEN: the estimator that decides when an option "has floors and a shape" is server-side (M5-T145); this task only displays the document's label.

ROW D-090-R544 — PASS
 - On the benchmark the 29-unit legal dwelling-unit limit is shown withheld/conditional inside the floor-area-allowance answer, while the 17.27-21.59 apartment estimate sits only under the building option (scenario S5; confirmed in both review rounds and in the fixture values 17.27/20150/21.59).
 - Ruling V2 is enforced: the adapters only format/group (presented-results.ts, first-building-options.ts) and recompute nothing, so the legal ceiling and the estimate stay separate figures read from the document.
 - OPEN: the derivation that the estimate uses accommodated floor area (not the permitted maximum) is a server/estimator obligation verified elsewhere (R509/R392).

ROW D-090-R556 — PASS
 - lib/architect/three-answers.ts (lines ~426-446) renders a withheld DESIGNATED headline value as its reason (kind "withheld"), explicitly "never values[0] — R556"; the fallback to the first shown value happens only when the key is simply ABSENT in a legacy document, never when it is withheld.
 - G4 mutation 3 ("withheld -> value 999") was caught; ResultsPanel marks a result stale on input change rather than substituting an older value (stale guard, S10).
 - OPEN: the emit side (where withheld values originate) is covered by the wire-and-emit task; here only the website reader is in scope.

ROW D-090-R570 — PASS
 - AnswerCard.WithheldLine renders "Not known — <reason>" with NO numeric field (R556/R570 in-code), and metric-format never gives a "not_known" value a digit (G3 CHECK 3; three-answers-panel/results-panel tests S8/S11).
 - A text check (SNAKE_CASE / banned-words guards) finds no number for a withheld result on the screen.
 - OPEN: the document and the PDF export carry the same "stays withheld everywhere" obligation on their own surfaces.

ROW D-090-R641 — PASS
 - "Preliminary zoning results" is emitted server-side into status_strip[0] (services/api/app/scenario/three_answers/explanations.py:110) and is present in the benchmark fixture (line 519); the website's ResultsStatusStrip renders statusStripItems(results) from the document and types no label (ruling V2).
 - The owner's label therefore leads the status strip; nothing on the screen shows the old "Zoning maximum" wording (S3).
 - OPEN: the server emission of this label was done by prior/sibling work; this task only renders it.

ROW D-090-R700 — PASS
 - The estimate carries the APARTMENT_SIZE_BASIS_NOTE "on the HPD measurement basis" and the label "Preliminary capacity estimate"; ruling V11(11) ties the measurement-basis wording to results.schema.json by a test (G4 mutation 9 caught dropping it), so nothing presents the share range or apartment size as law/measured/validated.
 - No rendered copy calls these values a requirement or a measurement (SNAKE_CASE/banned-words guards; first-building-options.ts comments at lines 66, 87).
 - OPEN: editing the share range (0.60-0.75) and the 700 sq ft apartment size on the screen (DB-213 a).

ROW D-090-R804 — PASS
 - All 31 files in M5-T149's evidence-map files_changed are inside the packet's allowed_paths and none is in its forbidden_paths or the forbidden services/** , packages/** prefixes (verified programmatically against the packet); the globals.css and services/** changes on the shared branch belong to sibling tasks M5-T148/M5-T150, not M5-T149.
 - No calculation engine, rule file, security config, render.yaml or production switch is in M5-T149's set; the evidence map's what_did_not_change ("no rule/capture/reference/schema; no legal figure; no human verdict; no production switch") is consistent with the diff.
 - OPEN: nothing — scope/authority/security/holds are preserved for this task's share.

ROW D-090-R805 — PASS
 - After "Show results" the form folds to a one-line "Inputs used: … · Change inputs" summary and focus moves to the results heading (ResultsPanel formFolded + pendingHeadingFocus -> .ta-panel-title); identity + the three answers' headline values are in the first screen at 1440 and 390 px (scenario S12 browser test; delta visual/walkthrough PASS).
 - The full evidence stays available behind Details (ResultDetails) and in the right-column scope summary; nothing is hidden to shorten the screen (the removed content moved, it was not dropped — G4 CHECK 2/3).
 - OPEN: "the first REPORT page" half of this row is PDF work (contract steps 4-5).

ROW D-090-R807 — PASS (process obligation; evidenced by records + clean integration, not fully reproducible by me)
 - M5-T148's token/adapter files are byte-unchanged in the reviewed delta (G3 delta "M5-T148 … byte-unchanged"), so earlier fixes were preserved; the slice was built on the merged main line (base 0bb6acb2) and the producer report records reading the route wiring before editing.
 - The evidence map and producer report state the branch/task/directives were rechecked; I verified the preservation half directly (no regression to M5-T148 adapters) but the "rechecked before editing" step itself is a process attestation I can only confirm through the records.
 - OPEN: nothing specific to this task; this is a standing discipline each editing task must restate.

ROW D-090-R809 — PASS
 - The left column leads with identity, the context strip, then the three answers (ThreeAnswersPanel ta-left order, ruling V12), so the property and the three answers come first; no development status or source metadata appears in the main view (S11 SNAKE_CASE guard).
 - This is the V12 correction of the orchestrator's own V11(7), which had wrongly pushed conditions ahead of the answers.
 - OPEN: the report's page-one treatment is PDF work.

ROW D-090-R810 — PASS
 - Each answer renders as a concise row (label -> value+unit/unavailable -> one exception -> Details) in AnswerCard, and the open items are a separate "What needs resolving" list, not long prose in table cells (S4; openItemsView).
 - No long-prose-in-narrow-cell pattern exists on this screen.
 - OPEN: the PDF "pages 5-6 narrow cell" concern is PDF work.

ROW D-090-R811 — PASS
 - sharedConditionsView() keeps a condition with fan-out >= 2 in the shared list stated once, named "Condition N"; a fan-out-1 condition stays LOCAL and is shown in full with its result (three-answers.ts conditionIndex/sharedConditionsView; AnswerCard LocalConditions vs ConditionRefs), the V11(5) + local-exception fix.
 - G4 mutation 4 (hiding a one-result condition behind a name) was caught; the benchmark density statement stays attached in full to the 29-unit figure.
 - OPEN: shared-context-once is also a PDF obligation on that surface.

ROW D-090-R812 — PASS
 - The three answers are distinct cards (floor_area_allowance, permitted_envelope, building_option); the building option is explicitly the SCHEDULED area with "Site fit not verified" (AnswerCard.BuildingOptionCard, presented-results.ts ResultKind has no "achieved" member).
 - So allowance, envelope and the scheduled option are told apart and site-fit-unverified is stated explicitly.
 - OPEN: the PDF must tell the same three apart.

ROW D-090-R813 — PASS
 - The comparison shows the results that exist and marks a not-worked building "Not known" with its reason, never 0 and never an empty cell (BuildingOptionsComparison + first-building-options.ts COMPARISON_NOT_KNOWN at line 179; S7); no baseline number is repeated across options.
 - G4 mutation 5 (not-worked storeys -> "0") was caught.
 - OPEN: the PDF's eleven-option comparison page.

ROW D-090-R816 — PASS
 - The left-column reading order is identity -> context strip -> three answers -> building options + comparison -> what needs resolving -> shared conditions, with "how derived" (ScopeSummary/Details) available on demand — the contract's seven-question order (ruling V12; ThreeAnswersPanel).
 - The illustrative schedule is told apart from a fitted option (R895 wording), matching question 4.
 - OPEN: the report must follow the same seven questions (PDF work).

ROW D-090-R817 — PASS (task's share: the prohibition is honored and the basis is disclosed; the real-person test stays owed)
 - The ten-second target was exercised by an AI human-journey-reviewer on pictures, and the records DO say so plainly — evidence-map known_limits #4 "judged by AI reviewers on pictures, not by a real architect" and the R817 evidence entry "Open: the contract asks for a test with a real person" — so the row's prohibition ("never claimed from screenshots") is satisfied, with no false claim.
 - I confirm the brief's specific question: YES, it is stated that the ten-second target was judged by AI reviewers on pictures, not a real architect.
 - OPEN: the positive requirement — an actual ten-second walkthrough with a real person — was not performed in this environment and remains owed to the owner.

ROW D-090-R819 — PASS
 - Only components under components/architect and lib/architect changed; no app/ route or page file was added, so the existing single dashboard with its floating Results tool is kept and there is no new multi-page navigation or route change to see a map.
 - DashboardEntry has a single documented one-line wide-list addition (G3 CHECK 7), not a navigation rework.
 - OPEN: nothing for this task.

ROW D-090-R820 — PASS
 - three-answers.css sets `@container (min-width:1000px) .ta-layout { grid-template-columns: minmax(320px,44fr) 56fr }` — the three answers together in the left column with a >=320px floor near a 44:56 split, with details on the right (scenario S1 measured against the grid per ruling V10a).
 - Identity (search/confirmed-property header) stays with the answers; the active property/lot/scenario stay visible when the tool is open (S1).
 - OPEN: the property-search header itself is pre-existing dashboard chrome.

ROW D-090-R821 — PASS
 - statusStripItems() returns at most three visible items with the rest in `overflow`, and standing notices are grouped behind a "Notes (N)" count (ResultsStatusStrip); the "What needs resolving" list caps at three with "N more" (S3, S14).
 - A condition that changes one number stays attached to that number (local-exception rule).
 - OPEN: nothing for this task.

ROW D-090-R822 — PASS
 - Details open in place inside the answer's own ResultDetails region; the Results tool is a single floating surface and no stacked dialogs are introduced.
 - This matches "details in the existing tool surfaces, one at a time" (G3 CHECK 6).
 - OPEN: the comparison/map-enlargement/report-preview tool surfaces are exercised by other tasks.

ROW D-090-R823 — PASS
 - The comparison keeps one site and measurement basis (BuildingOptionsComparison uses the single document); changing an input marks the shown result stale (ResultsPanel `stale = … !sameInputs(values, askedWith)`, data-testid results-stale; S10).
 - A withheld/newer answer never leaves an older one shown (newest-wins, S10).
 - OPEN: export invalidation on input change is a PDF-slice obligation.

ROW D-090-R824 — PASS
 - This task introduced no display toggle coupled to a legal calculation input; it changed only results-presentation files, and the existing-building display preference and calc inputs were untouched (no such file in M5-T149's set).
 - Hiding a layer therefore cannot change whether the existing building counts in a calculation (no coupling added).
 - OPEN: nothing introduced; the standing preference lives outside this task.

ROW D-090-R825 — PASS
 - The results slice renders only behind its existing flag (e2e specs are *.flag-on.spec.ts) and activates no 3D or other held feature to match a mockup.
 - No held-feature switch is flipped by this task.
 - OPEN: nothing for this task.

ROW D-090-R826 — PASS
 - three-answers.css stacks to one column below 1000px and `@container (max-width:700px)` tightens panel padding to 16px; the phone window fills screen height via floating-workspace-window.css `@media (max-width:700px)` (S2, S12); identity, main answer and its exception stay first.
 - No material limitation is dropped on a narrow screen (the stacked content is the same, G4 CHECK 2/3).
 - OPEN: nothing for this task.

ROW D-090-R827 — PASS
 - The narrow comparison keeps row order/names/units with a sticky row-label column (`.bo-compare-rowhead { position: sticky }`, ruling V11(8)) inside a labelled role="region" scroll box; values/labels are not ellipsized and assumption inputs are labelled numbers with unit, >0 bound and Reset (G3 CHECK 6; S7).
 - Long addresses wrap (results-layout 200%-zoom / text-spacing checks).
 - OPEN: on-screen editing of the share/size assumptions (DB-213 a) — the one assumption input present (height) meets the rule.

ROW D-090-R828 — PASS
 - ResultDetails focuses the region on open (useEffect keyed on open) and Escape closes it and returns focus to the opener button (ResultDetails.tsx lines 27-34, 58-60); "Change inputs" returns focus into the form select (ResultsPanel) (S4).
 - Content stays in the DOM via `hidden` so focus is never stranded.
 - OPEN: modal focus-trap behavior of the floating window frame is pre-existing chrome.

ROW D-090-R829 — PASS
 - The offline reference's three stacked sheets are not copied as navigation; the existing floating window and single-column stack are used (no three-sheet layout in the diff).
 - OPEN: nothing for this task.

ROW D-090-R830 — PASS
 - AnswerCard renders each result in the exact order title -> headline(label + value+unit OR withheld state) -> at most one ExceptionTag -> ConditionalMarker -> Details; the qualifying fact (withheld reason, local condition) is never truncated and stays with the result, while supporting detail moves into Details.
 - The budgets are applied as defaults, not truncation (WithheldLine renders the full reason).
 - OPEN: the PDF applies the same per-result order.

ROW D-090-R831 — PASS
 - Developer wording is removed: the server reason no longer says "step-P6 method" (first_option_results.py, G4 mutation 1 caught restoring it) and the website drops "still owed"/"Not built yet"/"Not worked"/"internal preview" (three-answers.ts GAP_KIND_LINES; BANNED_WORDS test in three-answers-panel.test.tsx line 60).
 - A missing property fact carries only the short tag "Needs property information" (team work is never put on the architect).
 - OPEN: the server reasons it consumes are produced by M5-T150; this task verifies the rendered copy and the shared constants.

ROW D-090-R832 — PASS
 - No implementation id, merge status, route, contract version, task number or test outcome appears in the architect view; the SNAKE_CASE regex guard and banned-field-key list in three-answers-panel.test.tsx enforce it, and technical ids stay behind a "Technical details" surface (S11).
 - G3/G4 reproduced that machine field names (building_alternatives, buildings_not_worked) never reach the screen.
 - OPEN: the client PDF must keep the same discipline.

ROW D-090-R833 — PASS
 - The screen keeps the owner's R641 status set; the "Conditional" marker is compact plain text with colour secondary (AnswerCard.ConditionalMarker); result-status.ts has NO code path to "Verified" (so Verified is never a synonym for merged/arithmetic/link), and a withheld value is never relabelled conditional to be shown (WithheldLine stays "Not known").
 - Owner question C2 (the PDF's six labels on the screen) is left open and "Verified" is never shown (ruling V3).
 - OPEN: the PDF label mapping (R779-R799) and question C2.

ROW D-090-R856 — PASS
 - metric-format distinguishes exact 0 ("0 sq ft") from not_known (`value == null || !Number.isFinite`), and a document for another lot or a stale answer is not shown as current (resultIdentity + stale guard; S10, S15); the screen renders one document revision.
 - G4 mutations 2 and 6 confirmed the 0-vs-unavailable and another-lot guards have teeth.
 - OPEN: screen-and-export sharing one revision / stale-export prevention is a PDF-slice obligation.

ROW D-090-R859 — PASS
 - This task is the contract's step 3 (one complete website slice: real property -> three answers -> details -> one comparison -> real data states including partial), built after M5-T148's step-2 shared presentation (ruling V1 order; evidence map).
 - The reconcile-and-persist step (1) and shared presentation (2) are in place; this slice sits correctly at step 3.
 - OPEN: steps 4 (PDF slice), 5 (remaining sections/tools), 6-7 (bounded acceptance / deliver outputs) stay owed.

ROW D-090-R869 — PASS
 - UX-01: identity "Queens block 7334, lot 70" and the headline "20,150 sq ft Conditional" are in the first screen after Show results at 1440 and 390 px (e2e results-layout S12; delta visual/walkthrough PASS; results-panel.test.tsx / three-answers-panel.test.tsx).
 - Desktop and phone captures plus the (AI) walkthrough observations are recorded in M5-T149-G3G4.md delta round.
 - OPEN: the drawings and PDF (contract steps 4-5) carry UX-01 further.

ROW D-090-R870 — PASS
 - UX-02: allowance, envelope, the scheduled building option and the estimate are distinguishable; the 29-unit limit stays with the allowance and the 17.27-21.59 estimate with the building option (S5; first-building-options.test.tsx, three-answers-panel.test.tsx; populated + partial fixtures).
 - result-status.ts keeps estimates a separate kind (no "achieved").
 - OPEN: the drawings/PDF carry UX-02 further.

ROW D-090-R871 — PASS
 - UX-03: no withheld/unknown result is promoted to a number and no draft to verified — metric-format/WithheldLine add no digit, result-status has no verified path, and draft values are hidden behind "rules not professionally reviewed" unless showDraftValues (G4 mutations 3/9; state tests on the canonical fixtures).
 - OPEN: the PDF must pass the same state tests.

ROW D-090-R872 — PASS
 - UX-04: shared notices appear once (SharedConditions, sharedConditionsView) and are referenced by name elsewhere ("Applies: Condition N"); a material one-result exception stays visible in full with its result (S3, S14; disclosure inventory in the delta visual review).
 - OPEN: the PDF/drawing surfaces carry UX-04 further.

ROW D-090-R873 — PASS
 - UX-05: the screen and its comparison share one property/scenario/revision/basis (single document), a stale answer is marked (results-stale) and a document for another lot is not shown (AnotherLotCard; S10, S15; result-identity.test.ts).
 - G4 mutation 6 confirmed the cross-lot guard.
 - OPEN: cross-output identity against the drawings and PDF is later work (steps 4-5).

ROW D-090-R874 — PASS
 - UX-06: the comparison uses consistent units and one site basis with differences explicit, across at least two genuinely different buildings plus a not-worked (unresolved) case reading "Not known" never 0 (BuildingOptionsComparison; test-support/results-two-buildings.ts; S7).
 - COMPARISON_NOT_KNOWN enforces one wording per unavailable cell.
 - OPEN: the PDF's option comparison.

ROW D-090-R875 — PASS (reproduced via CI, not re-run locally — see section 6)
 - UX-07: no clipped text (outside labelled scroll regions), no sideways page scroll, no overlapping labels or covered controls at 320/390/768/1024/1440/1920 px — apps/web/e2e/results-layout.flag-on.spec.ts; the whole Playwright suite passed 167/167 at d745b635 and CI run 38023638114 is 21/21 success at that head.
 - The clip-path screen-reader-only exclusion in that spec is slightly broad (G3/G4 advisory NOTE) but real overflow:hidden clipping is still caught.
 - OPEN: the PDF page images carry UX-07 further.

ROW D-090-R876 — PASS (reproduced via CI — see section 6)
 - UX-08: long labels/addresses/large-small values and text expansion stay readable — results-layout.flag-on.spec.ts runs 200% zoom and the text-spacing check at 1280px; values wrap (G3 CHECK 8).
 - OPEN: PDF stress cases are later work.

ROW D-090-R877 — PASS (task's share: keyboard/focus/contrast implemented and tested; real assistive-technology check disclosed as not done)
 - Keyboard, focus-into-tool, Escape-return, accessible names (role="region" aria-label, labelled inputs), status words and token-based contrast are implemented (ResultDetails, ResultsForm; G3 CHECK 6) and the browser spec exercises focus-in/Escape-return; status is told by words not colour alone (AnswerCard).
 - The walkthrough reviewer states plainly "NO screen reader; a11y notes are from code + the README keyboard check, not assistive tech" — so the automated/keyboard portion is met and disclosed, but a real screen-reader/assistive-technology pass was not performed.
 - OPEN: an actual assistive-technology walkthrough remains owed (same human-test gap family as R817).

ROW D-090-R881 — PASS
 - UX-13: no development log, raw error, task id or schema jargon in ordinary content — "step-P6"/"still owed"/"internal preview" and the typed parking line are removed and guarded by the SNAKE_CASE regex + banned-words list across loading/empty/partial/error/normal states (S11, S14); the visual review's blocking "step-P6" item is fixed.
 - OPEN: the PDF must pass the same content review.

ROW D-090-R882 — PASS
 - UX-14: the scheduled area is shown with "Site fit not verified" before any caveat and nothing is called feasible/preferred/optimal/verified (FirstBuildingOptions/BuildingOptionCard; first-building-options.test.tsx S6 negative assertions; the benchmark fixture even states "none is preferred or a default").
 - A conditional gain (29 units) is tagged Conditional and an unavailable alternative reads "Not known", never a computed feasible outcome.
 - OPEN: the PDF comparison must meet UX-14.

ROW D-090-R885 — PASS
 - States covered on the screen: normal (synthetic_all_answers_available), the partial benchmark, no geometry (lot_conditions_unconfirmed), failed/stale fetch, another lot, and 10ft/16ft building-option states (S8-S10, S13, S15; results-panel.test.tsx).
 - Expected values come from the committed fixtures and the independent reference case, not the screen's own output.
 - OPEN: the contract's remaining states (an existing building's missing zoning floor area, add-on off/on, approval-dependent option, overlapping gains, short vs long report) need their own underlying results first.

ROW D-090-R886 — PASS
 - Correctness tests read independently-established values from the reference case real-lot.json (results.flag-on.spec.ts), not a second copy of the program's own output (G4 CHECK 2 verified the provenance).
 - This slice asserts semantics (no wholesale screenshot-baseline updates), so "never update every baseline to pass" is not at risk here.
 - OPEN: when image baselines are introduced (PDF pages) they must be visually reviewed before approval.

ROW D-090-R888 — PASS
 - Producer/reviewer separation held: five builders produced, and four independent reviewers (code-reviewer G3, qa-engineer G4, visual-quality-reviewer, human-journey-reviewer) — none the producer — reviewed both rounds, with the FAILs and fixes kept in M5-T149-G3G4.md; I am the fifth independent reviewer (directive-compliance-verifier).
 - No producer checklist is recorded as independent review; G2 is the producer self-check recorded by the orchestrator, not labelled independent.
 - OPEN: nothing for this task.

ROW D-090-R890 — PASS
 - Nothing is called perfect/fully verified/complete/production ready; the evidence map and review record list cosmetic known-limits (320px 3px headline clip, right-column whitespace, "Applies" weight) and the AI-only basis, saying what the evidence supports.
 - The producer report and gate records avoid completion/verification narratives.
 - OPEN: nothing for this task.

ROW D-090-R894 — PASS
 - The website comparison uses ONE wording per situation — COMPARISON_NOT_KNOWN = "Not known" for every unavailable cell, never 0, never an empty cell (first-building-options.ts line 177-184; BuildingOptionsComparison), with concise columns and no crowded headings (S7).
 - This applies the owner's "one wording" rule (originally raised for the PDF) to the website's comparison (ruling V11(3)).
 - OPEN: the eleven-option, three-column enumeration itself is the PDF's option pages (this website comparison covers the method's worked/not-worked buildings).

ROW D-090-R895 — PASS
 - The word "achieved" appears in NO rendered website source — only in code comments/the legacy presented-results key/tests (grep over components/architect + lib/architect); the building option reads "Building option: Site fit not verified" then "Scheduled area: 20,150 sq ft" BEFORE any caveat (FirstBuildingOptions.tsx:105-111; AnswerCard.BuildingOptionCard; presented-results.ts ResultKind has no "achieved").
 - first-building-options.test.tsx S6 asserts the section's lowercased text does not contain "achieved" or "unused", and throws if the fixture is vacuous; G4 mutation 4 ("Scheduled area" -> "Achieved") was caught. The web uses the sanctioned wording "Site fit not verified" (ruling V5) for the owner's "site fit unverified".
 - OPEN: the PDF side of R895 is PDF work.

(3) BINDING B1-B5
 - B1 PASS: `git diff 0bb6acb2..db7824e7` on requirements.json adds exactly 53 "+ \"M5-T149\"" task-id entries (one per bound row) and removes NO existing row's text/id/classification/binding/source_ref; the only new "text" bodies are the 8 source-080 rows R892-R899 (of which only R894/R895 bind here). No bound row's text changed.
 - B2 PASS: I recomputed both manifest digests at the frozen head — requirements_id_digest_sha256 = f31113ebdb80… (matches) and requirements_content_digest_sha256 = 59a3752d3d2c… via dr.sha256_text_artifact (matches); requirement_count 899 == 899 rows == 899 locked_requirement_ids.
 - B3 PASS: verification.json (schema directive_verification/v2) has exactly ONE M5-T149 task_verifications row; its requirements list is exactly the 53 cited ids (set-equal, no missing/extra), every state "pending", every per-row evidence [] and reviewed_sha null, the row-level verifier "" and reviewed_sha/reviewed_manifest_sha256 null, producer "frontend-engineer".
 - B4 PASS: reg.evaluate_task_refs(M5-T149 packet) returns ok=True, applicable_ids == cited_ids == the 53 expected, missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: the same evaluate_task_refs derives applicable from ALL active directives; the applicable set is exactly the 53 cited rows with nothing extra — no other active-directive requirement applies to this task uncited.
 - Gate records PASS: `python tools/validate_directive_compliance.py --check` exits 0 at the frozen head; G0 PASS (orchestrator, reviewed_sha 0ed7ae98), G2 PASS (orchestrator self_check), G3 PASS (code-reviewer), G4 PASS (qa-engineer) all with content_manifest_sha256 f024199223… at reviewed_sha 5bf6f729 — G2/G3/G4 at ONE content identity. The reviews were taken at d745b635 (product-identical to 5bf6f729 and to the frozen head); CI run 38023638114 is independently confirmed via gh as completed/success, 21/21 jobs, headSha d745b635, so gates sit on content for which CI was green. modularity_check --check exits 0 (only pre-existing services/tools warnings, none in the slice).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided: the git blob ids of apps/web, packages/contracts, services/api/app, .github, tools, render.yaml and this task's four reports (M5-T149-part-A/B/C.md, M5-T149-producer-report.md) are unchanged from the frozen head; the 53 rows' text and their M5-T149 binding are unchanged; and the only intervening commits touch solely project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the other wave-20 tasks (M5-T148, M5-T150) on this branch, or a main-line merge that changes none of those predicate files.
 - This condition currently holds: d745b635..db7824e7 (and 5bf6f729..db7824e7) touch only project-control files, and base..db7824e7 changes the 53 rows only by appending task_ids. If any predicate blob or any bound row's text/binding changes, this verdict must be re-derived.

(5) REQUIRED CORRECTIONS
 - NONE blocking. The four standing advisory NOTEs are non-blocking and need no rework for this gate: (a) the results-layout clipped-text helper skips any element bearing a clip-path (slightly broad; overflow:hidden clipping still caught); (b) AnswerCard's `conditionNames` prop is passed but no longer read (dead param); (c) the phone full-height CSS rule applies to all non-maximized floating windows, not Results-only (desktop-safe); (d) an unreachable path I found myself — lib/architect/three-answers.ts:308/373 still defines and wires BUILDING_OPTIONS_BELOW_REASON = "the building options are shown below", but on the benchmark the panel routes the building_option answer through BuildingOptionCard (scheduled area) whenever firstBuildingOptionsView is non-null, so the "shown below" text is not rendered (tests assert the benchmark never shows it) — latent/defensive, non-blocking.
 - NOT corrections but OWNER follow-ups owed (not this task's to fake): a real-person ten-second walkthrough (R817) and a real assistive-technology/screen-reader pass (R877); both are honestly disclosed as not performed.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I could not run the web unit/e2e suites myself: my copy /root/project/rv-w6-b has no node_modules, and the read-only guard blocks `npx`/any cache-writing command in the frozen worktree. I therefore relied on (i) CI run 38023638114 confirmed via gh as 21/21 success at the reviewed head d745b635 (product-identical to the frozen head), (ii) the orchestrator-reported 167/167 Playwright and 2615-test vitest at d745b635, and (iii) the G4 reviewer's reproduced one-at-a-time mutations. I independently read the test sources and confirmed the key assertions are substantive (they throw on a vacuous fixture and assert exact scheduled-area/"Site fit not verified"/absence-of-"achieved" etc.), but I did not re-execute them.
 - The real-person ten-second usability test (R817) and the real assistive-technology accessibility test (R877) were performed only by AI reviewers on pictures/code; I cannot verify a human/AT result that was not produced.
 - Process attestations in R807 ("rechecked branch/task/directives/wiring before editing") are verifiable by me only through the records and the clean integration (I directly confirmed the "preserve earlier fixes" half via M5-T148's byte-unchanged adapters).
 - I did not independently reproduce the server-side emission of the status-strip label, the apartment estimate, or the server reasons (M5-T150/prior tasks); this task only renders them, and that rendering I verified.
 - I am an AI agent; this is not a human or professional review.
END-OF-REPORT
```
