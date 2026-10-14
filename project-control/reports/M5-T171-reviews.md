# M5-T171 reviews (every return kept unchanged)

- G2 orchestrator self-check at the material commit 2f69ee16: 8 files, all inside the 9 allowed paths; LF sha256 equal to the builder's return; lane coverage PASS. The owner's preview was rebuilt from the branch at 97b2a492 (web files byte-identical to 2f69ee16) and the Results window and the report were photographed; then the new block itself at 320, 390, 768, 1024, 1440 and 1920 px (capture_block.mjs, pictures and notes on the build server): no horizontal overflow at any width; the block starts below the first screen at every width.
- G3 walkthrough (human-journey-reviewer): PASS, no required correction; advisories (the block below the first screen; the estimate not linked; the zoning-lot sentence is the document's full condition; the 29 appears twice on the screen).
- G3 visual (visual-quality-reviewer): PASS with one required correction (no picture showed the block). The orchestrator took the pictures; a delta review by a visual-quality-reviewer looked at all twelve and found the correction met: PASS.
- G4 qa-engineer: PASS, no required correction; three advisories.
- The advisories are backlog DB-261 (for the later website task M5-T174); none changes a figure or a word the packet fixes.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (visual-quality-reviewer) - part 1

G3 WALKTHROUGH GATE REPORT — M5-T171 (website page-1 parity: legal ceiling beside the apartment estimate)

I am an AI agent (human-journey-reviewer), independent and read-only. This is not a human or professional review. I drove no browser and touched no port; I read the branch only through git plumbing at the pinned commit and read the e2e result from CI.

VERDICT: PASS (no required corrections; advisories below).

IDENTITY / EVIDENCE BASE
- Pinned material commit 2f69ee162 on task/wave24-report-v3 (worktree /root/project/w-wave20). Pictures taken at 97b2a492; current remote head c1da69322. I verified the web/report/token files are BYTE-IDENTICAL between 2f69ee162 and c1da69322 (git diff --stat empty for apps/web, services/api/app/drawings, docs/design), so the CI run at the live head is valid evidence for the pinned work.
- CI run 38506304838 (head c1da6932): web (lint+typecheck+build) success; web-dependency-security success; web-e2e (vitest + Playwright, six-width) success. The six-width spec results-layout.flag-on.spec.ts asserts the block (testid apartment-figures) is visible, holds no clipped text, no overlapping ceiling/estimate cells, and adds no sideways scroll at 320/390/768/1024/1440/1920.

WHAT I CHECKED (reproduced from source, not the producer's conclusion)
- Ceiling value+label parity: website apartment-figures.ts legalCeiling reads legal_unit_limit_standard, formats via formatMeasure ("29"), labels via labelForWay. The report (unit_limit_text.legal_ceiling → readers.named_value → present_values, status_label = label_for_way(state) if state else PROVISIONAL) uses the identical mapping: conditional→Conditional, settled→Provisional, absent→Provisional, other→Pending verification. Answer iteration order is identical ((floor_area_allowance, permitted_envelope, building_option)). Benchmark → "Legal ceiling 29" / chip Conditional, matching report page-01.png. MATCH.
- Estimate parity: both read building_alternatives[0].capacity_estimate.whole_below_low/high → "17-22", chip Provisional. MATCH.
- Distinction line: token docs/design/presentation-tokens.json wording.ceiling_estimate_distinction == the contract's quoted line == the website literal CEILING_ESTIMATE_DISTINCTION; S1 reads the token from disk and compares char-for-char, and asserts the rendered line equals it. Placed as a <p> immediately under the ceiling/estimate pair (where the eye meets the two figures), as on page 1. MATCH + readable.
- Lot-area line: byte-equal composition "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" (× = U+00D7; S6 asserts no " x "); "alone" added when the ACRIS zoning-lot condition is detected by the same marker "register of recorded documents" the report uses (zoning_lot_item.zoning_lot_basis). Fallback "Residential FAR on the recorded lot area" matches page_decision_summary._floor_area_basis. MATCH.
- Zoning-lot concern: the document's own condition sentence, read not invented; it says "The documents themselves were not read." Understandable to an architect.
- Every state covered with one test each (verified in apartment-figures.test.tsx): A conditional→Conditional; J settled→Provisional (never "settled"); B withheld/work_owed→reason + "Pending verification", no digit; B2 withheld/missing→Unresolved; C no ceiling→"Legal ceiling not available", no chip; D ranged→Provisional; E "Not known"→not available; F no alternatives→not available; G unconfirmed→concern + "alone"; H no condition→no concern/no "alone"; I fallback line. Draft gate: flag off → only "Not available — the rules for this answer are not reviewed yet", figures hidden.
- Forbidden words: S2 scans the block over every committed fixture for buildable, achievable, can be built, feasible, compliant, optimal, preferred, verified, achieved, recommended — none present. The 29 is never settled (chip Conditional; label set has no "Settled").
- Own testids only (no answer-conditional-marker/answer-value/answer-headline-number); three-answers-panel.test.tsx adds the marker-discipline guard and the DB-214 N2 reconciliation (allowance card keeps "29 units"; block adds "Legal ceiling 29"/"Estimate 17-22"). three-answers.ts untouched.
- D-093: screen does not contradict settled readings. R6B step-p6-worked and NB-04 confirm recorded lot area 10,075 (administrative_record) drives floor area (2.00×10,075=20,150); GIS outline 10,387.99 is display-only and never enters a zoning calc; the apartment estimate is kept apart from the legal dwelling-unit ceiling — exactly how the block presents it.

FINDINGS
1. [ADVISORY — headline] Placement weakens the ten-second scan. The block renders AFTER the three tall answer cards (ThreeAnswersPanel.tsx: .ta-answers → <ApartmentFigures>). DOM reading-order parity with page 1 (answers → ceiling/estimate → uncertainties) is faithfully achieved, but on the website the ceiling/estimate distinction falls below the first screen on desktop AND phone, because the web cards are far taller than page 1's compact table rows. In desktop-results.png the first screen shows only identity + the floor-area allowance card; e2e S12 guarantees first-screen visibility only for the identity and the floor-area headline, NOT the parity block. So in ~10 s an architect sees the property and the main answer (floor-area allowance 20,150 Conditional) but must scroll past two more cards to reach the legal ceiling, the estimate and their difference. Builder decision (a) ("beside the headline" read as "a prominent block after the cards") is defensible for parity, but I would lift the block directly under the status strip / beside or immediately after the floor-area allowance card so the ceiling-vs-estimate distinction is in the first screen as it is on page 1.
2. [ADVISORY] The estimate is not linked. Contract page-1 kind 3 says the estimate links to its full calculation on the scenario sheet; report page 1 links "Estimate 17-22" to #estimate-<building>. The website shows plain "Estimate 17-22". The Results window has no scenario-sheet page, so this is reasonable, but consider linking to the building-options section. Not in the task objective or the brief's consistency list.
3. [ADVISORY] Zoning-lot concern wording differs from page 1's heading sentence. The website shows the document's FULL condition sentence ("…recorded on February 8, 2022 … together with lot 1 … The documents themselves were not read."); page 1's heading shows the short index-entry sentence ("the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70"). Same fact, R030-compliant (names the index entry, not the instrument), and the fuller text is arguably clearer. No contradiction.
4. [ADVISORY/observation] "29" appears twice on the website (allowance card "29 units" + block "Legal ceiling 29") vs once on page 1. Intentional (DB-214 N2 keeps the limit with the allowance; the block adds parity); both Conditional, so no contradiction — only mild redundancy.
5. [Context on builder decision (b) — judged CORRECT] The draft gate is right and consistent with D-090-R010 and the other answer cards; its wording byte-matches the panel's existing draft line. Note: every committed fixture is draft, so on the production architect surface (flag off) the block hides the figures today; they show on the flag-on preview (the screenshots). The report route shows the figures with the standing label and does not gate — a pre-existing website/PDF asymmetry, not introduced by this task.

WHAT I COULD NOT CHECK
- The rendered parity block in the orchestrator's pictures: NONE of the four Results-window screenshots (desktop-results, phone-results, desktop-report-preview, phone-report-preview) actually show the block — they capture the top (first answer card) and the bottom (shared conditions + embedded report), skipping the block in between. Its on-screen appearance is unverified by picture; it is corroborated by the passing six-width e2e (visible/unclipped/non-overlapping) and by the answer cards rendering real figures on the same showDraftValues surface. The embedded report page 1 shown in the preview matches page-01.png.
- The ten-second test with a real person: NOT RUN (it needs a person), per the brief.
- I ran no browser, no Playwright, and no server/port; full non-web CI jobs (api, context-pipeline, etc.) were still in progress but are outside this frontend task's scope — the three web jobs are green.

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 2

G3 VISUAL REVIEW — M5-T171 (website page-1 parity). Reviewer: visual-quality-reviewer (independent, read-only). I am an AI agent; this is not a human or professional review. Pinned commit 2f69ee162 on task/wave24-report-v3 (pictures at branch head 97b2a4922).

VERDICT: PASS with required corrections.

CI READ (run 38506304838, web-e2e job 115664895905, SUCCESS; never rerun): vitest "129 files / 2704 passed" incl. apartment-figures.test.tsx (41 tests); Playwright "169 passed (3.9m)". results-layout.flag-on.spec.ts (line 136:9), which the builder extended to assert the block is visible + no clipped text inside + cells never overlap, passed at ALL SIX widths: 320 (t157), 390 (t158), 768 (t159), 1024 (t160), 1440 (t161), 1920 (t162). S12 (t166/t167): identity + floor-area headline stay in the first screen at 1440x900 and 390x844. So UX-07 S3 for the new block is empirically green at all six widths.

WIDTHS SEEN: I saw ZERO widths of the new block in any picture (see Finding 1). All six-width verification is from CI only.

WHAT I CHECKED: the four changed web files at the pinned sha (ApartmentFigures.tsx, apartment-figures.ts, three-answers.css .af-*, ThreeAnswersPanel.tsx wiring, e2e diff); report page 1 (current page-01.png vs accepted session-2026-10-11e reference — byte-identical layout, only footer date differs); report composition source (page_decision_summary.py, unit_limit_text.py, zoning_lot_item.py, layout.py .label-chip/.ceiling-estimate CSS); design contract "Change 2026-10-11"; tokens wording group; grayscale conversion of desktop-results.png (pure-Python decoder — sandbox has no ImageMagick/PIL/matplotlib).

CONFIRMED CONSISTENT (parity holds): (a) Chip style — .af-chip is a neutral bordered pill (divider border, supporting text, page bg) matching the report's .label-chip; both chips identical, status told only by the WORD (Conditional/Provisional), zero colour coding → grayscale-safe by construction (the grayscale of the existing surface read perfectly: "20,150 sq ft Conditional" fully legible). (b) Distinction line — byte-identical literal vs tokens wording.ceiling_estimate_distinction (S1, CI green) and matches page 1. (c) Lot-area line — "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" (× = U+00D7; "alone" only while unconfirmed), composed exactly as page_decision_summary._floor_area_basis; visible identically on page-01.png. (d) Pairing — ceiling beside estimate (flex, wraps to one column on narrow), no overlap at six widths (CI). (e) Ceiling label — website labelForWay mirrors the report's status_label derivation (settled→Provisional, conditional→Conditional), so no divergence; the benchmark ceiling is Conditional, never settled. (f) No forbidden words (S2, CI green). (g) All tokens, no colour literals; mirrors report furniture — NOT a default-template look.

BUILDER DECISIONS — both judged correct: (a) block AFTER the three answer cards matches report page 1's order (answers summary → ceiling/estimate → uncertainties) and the "main answer leads" principle; e2e S12 confirms identity+headline keep the first screen. "Beside the headline" is honoured as prominence/order, not literal adjacency — acceptable, no change. (b) Draft gate (draft doc + flag off → only "Not available — the rules for this answer are not reviewed yet") is consistent with the answer cards and D-090-R010; correct, no change.

NUMBERED FINDINGS:

1. REQUIRED (evidence, not a code defect) — contract "Change 2026-10-11" Checks H1/R083/R098 require each changed website view rendered, captured and looked at. NONE of the four supplied pictures shows the parity block: desktop-results.png / phone-results.png are scrolled to the top, desktop/phone-report-preview.png to the bottom; the block renders in the un-captured middle of the Results window. I verified it from CSS + CI, not from a rendered image. Correction: orchestrator captures the rendered block (desktop + phone, scrolled to apartment-figures) and adds it to after-97b2a492/ so the G3 "looked at" record exists before acceptance. This is the only item that blocks a clean PASS.

2. ADVISORY (parity) — zoning-lot concern wording diverges. Website (ApartmentFigures via zoningLotConcern) shows the raw document condition: "If lot 70 alone is the zoning lot. The city's register of recorded documents lists a zoning lot description recorded on February 8, 2022 … The documents themselves were not read." Report page 1 (zoning_lot_item.page_one_zoning_lot_sentence) shows the compact "the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70" — different length AND date format (February 8, 2022 vs 2022-02-08). Same substance, no invented fact (D-093-ok), and the packet did NOT require byte-parity here (only the distinction and lot-area lines). Against D-094 R041/R057 "same caveats on website and PDF" this is a gap. Correction: decide whether the website reuses the compact page-1 sentence or the fuller wording is intentional; record it.

3. ADVISORY (parity) — the estimate on report page 1 links to its full calculation (blue "Estimate 17-22" → #estimate-…; contract page-1 item 3); the website EstimateCell renders "Estimate 17-22" as plain text, no link to the scenario/calculation (a "Scenarios" surface exists on the page). Correction: add the link or confirm the omission is intended.

4. COSMETIC — figure emphasis. Report page 1 renders "Legal ceiling 29"/"Estimate 17-22" at section size (bold/linked); website .af-figure is body size, weight 600 — quieter. Acceptable (keeps the main answer leading); optional to raise for closer parity.

5. COSMETIC — .af-distinction renders at body size/ink; report .distinction is compact/supporting-grey. Minor; website slightly more prominent. Acceptable.

WHAT I COULD NOT CHECK: the rendered parity block at any width (Finding 1) — hierarchy, chip readability and the six-width layout were verified from CSS + CI, not a picture; the grayscale test ran on the existing surface only (the block is colour-neutral by CSS). I did not run Playwright, start/stop servers, or touch ports 3000/3001/8000.

NET: code and CSS are sound, parity substance holds, CI is green at this content identity. Clear once Finding 1 (capture the block) is supplied; Findings 2-3 should be resolved or explicitly accepted by the owner before the full report is called complete.

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 3

G3 VISUAL DELTA — M5-T171 apartment-figures block. Reviewer: visual-quality-reviewer (independent, read-only, AI agent; not a human/professional review). Branch head 97b2a4922, web files byte-identical to pinned 2f69ee162. I LOOKED at all 12 pictures + block-notes.txt and compared to report page-01.png (session-2026-10-11e/after-68d417fe). Wrote nothing; never touched ports 3000/3001/8000.

VERDICT: PASS.

REQUIRED CORRECTION MET. The prior G3 Finding 1 (no picture showed the apartment-figures block, so the contract Checks H1/R083/R098 "rendered and looked at" record was missing) is now satisfied: block-{320,390,768,1024,1440,1920}.png (block alone) and block-in-window-{same widths}.png (Results scrolled to the block) render the new block at all six widths. I inspected each.

PARITY of the four required texts — all equal report page 1 (clearest at block-768/1024 and block-in-window-1024):
- Figures: "Legal ceiling 29", "Estimate 17-22" = page 1.
- Chips: "Conditional" (ceiling), "Provisional" (estimate) — neutral bordered pills, status carried by the WORD only, no colour fill; readable without colour at every width. = page 1.
- Distinction line: "The ceiling is a conditional zoning limit; the estimate is an unvalidated apartment-yield range; neither is a demonstrated layout." = page 1, sitting directly under the pair at every width.
- Lot-area line: "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" (× = U+00D7) = page 1.

No clipped text (layout), no overlap, no obscured control in any of the 12. block-notes reports horizontal page overflow 0 px at all six widths; no horizontal scrollbar visible. The block is a bordered card between the "Building option" card and the "Building options" card (block-in-window-768/1024/1440/1920).

FINDINGS:
1. ADVISORY — block below the first screen at every width. block-notes: block top 1583/1380/1179/1151/1296/1296 px at 320/390/768/1024/1440/1920; first screen ends 844 (320/390) or 900. A scroll is always needed to reach it. ADVISORY because it matches the already-accepted order (answers → ceiling/estimate → uncertainties, = report page 1) and the "main answer leads" rule (prior G3 accepted this; e2e S12 keeps identity+floor-area headline on the first screen). No change.
2. ADVISORY — ceiling/estimate side-by-side vs stacked varies with card width, not monotonic with viewport: STACKED at 320 (card 223 px, chip wraps under the figure) and 390 (293 px); SIDE BY SIDE at 768 (639 px) and 1024 (895 px); STACKED again at 1440/1920 (card 417 px — the panel is the LEFT column of a two-column desktop Results layout, evidence/provenance list on the right; block-in-window-1440/1920). ADVISORY because the pair still reads as a pair (ceiling then estimate, distinction line beneath) at every width; flex-wrap is a sound responsive outcome. No change.
3. ADVISORY (capture artifact, not a layout defect) — block-320.png crops the heading's first line ("The legal ceiling and…") and shows faint bleed from elements above/below. The full heading renders: block-notes text and block-390/768/1024/1440/1920 show "The legal ceiling and the apartment estimate" complete; block-in-window-320 shows it at the scroll top. Crop framing only.

CARRIED-OVER (outside this delta, unchanged, for the record): prior ADVISORY Finding 2 — the website zoning-lot paragraph is the fuller "February 8, 2022" wording vs page 1's compact "2022-02-08" (visible block-768/1024); prior ADVISORY Finding 3 — EstimateCell "Estimate 17-22" is plain text with no link to the calculation. Both are open owner-decision parity items, not part of this required correction; the brief scoped parity to figures/chips/distinction/lot-area, all of which match.

WHAT I COULD NOT CHECK: I did not run Playwright or any browser, start/stop servers, or touch ports. Six-width non-overlap/no-clip was CI-green at this content identity in the prior G3; here I confirm it visually from the 12 static pictures. Hover/link behaviour and a programmatic grayscale pass were not run — the chips carry no colour fill by inspection, so word-only status is colour-safe by construction.

END-OF-REPORT

## G4 (qa-engineer)

# M5-T171 G4 QA gate report — website page-1 parity

**Reviewer:** qa-engineer (independent). **I am an AI agent; this is not a human or professional review.** Read-only: I wrote nothing in any repository; all copies/probes live in `/tmp/claude-0/t171-g4/`.
**Pinned commit reviewed:** `2f69ee162` (task/wave24-report-v3, `/root/project/w-wave20`). **Verdict: PASS** (3 ADVISORY notes, 0 required corrections).

## What I verified independently
- **Diff scope / no package:** the pinned commit changes exactly its 8 allowed-path files (apartment-figures.ts, ApartmentFigures.tsx, ThreeAnswersPanel.tsx, three-answers.css, two tests, the e2e spec, producer report). No package.json/package-lock.json change. `git diff --name-only 2f69ee162~1 2f69ee162` confirms.
- **Forbidden paths byte-identical to claim head 654ea3fad:** `git diff 654ea3fad 2f69ee162 --` over all 8 forbidden paths (three-answers.ts, globals.css, presentation-tokens.json, results.flag-on.spec.ts, journey-215-16-northern.test.tsx, results-contract-checks*×3) = empty, exit 0.
- **Parity re-derived against the report (not trusted from the producer):** read `page_decision_summary.py`, `readers.py`, `unit_limit_text.py`, `labels.py`, `formatting.py`, `zoning_lot_item.py` at the pinned head and compared each to apartment-figures.ts. formatMeasure/formatIntCommas/formatRatio, labelForWay/labelForWithheld, the contradicted_record recorded-area regex, the ACRIS marker, and `_floor_area_basis` composition all match the report for the realistic value shapes. ANSWER_KEYS == report ANSWER_NAMES.
- **Distinction literal == token:** apartment-figures.ts CEILING_ESTIMATE_DISTINCTION equals `wording.ceiling_estimate_distinction` in presentation-tokens.json, character-for-character.
- **Benchmark fixture values** (packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json): FAR 2.0, legal_unit_limit_standard 29 way=conditional, estimate 17–22, recorded lot area 10,075, ACRIS marker present, draft=true — faithfully reflected by the block; nothing recalculated in TSX. Consistent with NB-04 (uses recorded area, not the GIS outline), NB-05 (ceiling stays Conditional) and NB-01 (lot unconfirmed). Report page-01.png shows the same 29/17-22/distinction.

## Checks run (archive copy, node_modules symlinked from /root/project/w-wave20)
- `npm run lint` → exit 0 (0 errors; 2 pre-existing warnings in unrelated files).
- `npm run typecheck` → exit 0.
- `npx vitest run src/components/architect/answers src/lib/architect` → **32 files / 591 tests passed**, exit 0.
- `npx vitest run` (whole web unit suite, one run) → 2701/2704 passed. The 3 failures are in two OUT-OF-SCOPE files (workspace.test.tsx, parcel-study-records.test.tsx; untouched by T171) with ~14 s durations; **run in isolation they pass (15/15)** — a sandbox concurrency/timeout artifact, not a defect.
- **CI (read-only via gh, never rerun):** run 38506304838 at head `c1da6932`. `apps/web` is byte-identical between 2f69ee162 and c1da6932 (empty diff), so the result validates T171's web files. `web (lint+typecheck+build)` = SUCCESS; `web-e2e (vitest + Playwright, incl. the six-width results-layout.flag-on.spec.ts)` = SUCCESS; web-dependency-security, modularity, contracts = SUCCESS. Only an unrelated supervisor job was still running.

## My own mutation/behaviour probes (in the scratch copy; reverted clean)
1. Distinction literal `layout.`→`layoutX.` → S1 **2 failed** (literal + rendered). ✓
2. Conditional label → PROVISIONAL → S4 state A **failed** ("expected 'Provisional' to be 'Conditional'"). ✓
3. Strip legal_unit_limit_standard value+state from benchmark → block renders "Legal ceiling not available", no chip, **did not throw**. ✓
4. Give the block's ceiling chip the testid `answer-conditional-marker` → three-answers-panel whole-panel discipline test **failed** at line 332 ("expected true to be false"). ✓

## Scenario results
| Scenario | How tested | Result | Exit |
|---|---|---|---|
| S1 distinction byte-equal | archive literal==token; S1 unit tests; mutation 1 | PASS | 0 |
| S2 no forbidden word | S2 parameterised over all fixtures; block text read | PASS | 0 |
| S3 six widths no clip/overlap/scroll (UX-07) | CI web-e2e SUCCESS (spec asserts visible+no-clip+no-overlap at 320/390/768/1024/1440/1920); builder ran none | PASS | n/a (CI) |
| S4 29 Conditional, withheld shows reason | S4 A/J/B/B2/C unit tests; mutation 2; fixture way=conditional | PASS | 0 |
| S5 lint/typecheck/touched tests; e2e from CI | lint/typecheck exit 0; targeted vitest 591 pass; e2e from CI | PASS | 0 |
| S6 lot-area line byte-equal (U+00D7) | S6 unit test; code byte-matches report `_floor_area_basis`; "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" | PASS | 0 |
| S7 every fixture renders/degrades; panel green | S7 parameterised; probe 3; full unit suite green in CI; three-answers-panel green | PASS | 0 |
| S8 forbidden suites green UNEDITED; own testids | forbidden paths byte-identical to claim head; CI web+web-e2e green; mutation 4; own-testid unit test | PASS | 0 |

## Builder decisions judged
- **(a) Block after the three answer cards:** correct. Report page 1's order is answers → ceiling/estimate block → uncertainties; the website mirrors it, keeping the identity and floor-area headline on the first screen. "Beside the headline" is reasonably read as a prominent top-level block. No change required. (In the two provided viewport captures the block is below the fold; CI e2e proves it visible at all six widths.)
- **(b) Draft gate:** correct and consistent with the answer cards (D-090-R010/ADR-007) — an unreviewed figure never reaches an architect-surface; `showDraftValues` reveals it. Note (no action) the pre-existing asymmetry that the PDF page 1 prints the draft figures with the standing label while the website hides them behind the flag; not introduced by T171.

## Findings (all ADVISORY — none blocks acceptance)
1. **ADVISORY — zoning-lot concern wording differs from report page 1.** The website block shows the document's RAW condition sentence: "If lot 70 alone is the zoning lot. The city's register of recorded documents lists a zoning lot description recorded on February 8, 2022 that is filed on this lot together with lot 1 on the same block, so the zoning lot may include lot 1. The documents themselves were not read." Report page 1's page-1 named-furniture sentence is the PARSED index-entry form "the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70" (`page_one_zoning_lot_sentence`). Same facts, not byte-identical. The packet objective specified `zoning_lot_basis` (raw), only S1/S6 require byte-equality, and R030 is satisfied (names the register's index entry; states the instrument was not read — consistent with NB-01). If strict textual parity is wanted, reuse `page_one_zoning_lot_sentence`. Low priority.
2. **ADVISORY — the 29 appears twice on the website** (allowance card "29 units" per DB-214 N2 + the block "Legal ceiling 29") vs once on report page 1. This is the packet's documented additive design (three-answers.ts read-only); optionally confirm the allowance-card assumption line isn't duplicated verbatim in the block in a distracting way.
3. **ADVISORY (shared with the accepted report, not a T171 regression)** — both the website and report `legal_ceiling` logic would label a hypothetical "settled" ceiling "Provisional" (never occurs in real data; the ceiling is conditional). Mirrors the accepted report side.

## What I could not check
- A direct screenshot of the block itself — both provided captures (desktop-results.png, phone-results.png) show only the viewport top; the block is below the fold. Mitigated by CI web-e2e (visibility/no-clip/no-overlap at all six widths) and the unit DOM assertions.
- The full per-directive (D-094 R035/R041/R051/R057/R071/R078/R081/R083) re-derivation is the directive-compliance-verifier's gate; I verified the parity-bearing ones (R041/R057 structure+figures, R071/R078 distinction+ceiling-beside-estimate, R081 lot-area line) via parity.

**VERDICT: PASS.** The website Results block shows the same answer as report page 1 — byte-identical distinction and lot-area lines, identical figures/labels/caveats read from the document, own testids, degrades safely, forbidden suites byte-identical and green in CI, diff within allowed paths, no package added; all S1–S8 satisfied and four mutation probes bite.

END-OF-REPORT
