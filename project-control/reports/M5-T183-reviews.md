# M5-T183 reviews (every return kept unchanged)

- Two build rounds (backend-engineer, worktrees): round 1 builder commit 8276bb48 integrated as the cherry-pick dec38ebf; round 2 builder commit eca07305 integrated as bed48258 (3 files: the kernel, its test, the producer report; inside the 5 allowed paths; LF sha256 equal to the builder's return). The drawing kernel only (M5-T173 part A); not placed on any report page or website view.
- Independent pre-integration checks at each builder commit (return-M5-T183-precheck.json, -precheck-r2.json, session 2026-10-15a): scope, digests, ruff, the test file, tests/drawings/kit, modularity, lanes; whole api suite green (round 2: 9868 passed).
- G2 orchestrator self-check at 48d6587b (the branch head; the task's files unchanged since bed48258): the five files equal the builders' digests; the kernel imports only the standard library and the kit's own helpers; nothing outside the allowed paths changed in either round; lane coverage PASS; the two snapshot SVGs byte-identical between rounds; CI run 38703438698 at 48d6587b success.
- G1 data-contract-verifier at dec38ebf: PASS (one advisory for the wiring task); its skeptic: no REQUIRED finding to test.
- G3 code-reviewer at dec38ebf: PASS. G3 visual-quality-reviewer at dec38ebf: PASS with three advisories for M5-T173 (label size if scaled below about 0.89x; the bar-beside-the-building-diagram pairing composed on the scenario sheet; placement), each upheld as advisory by its skeptic. Both returns are kept below under the one G3 record.
- G4 qa-engineer at dec38ebf: PASS.
- G5 security-reviewer at dec38ebf: PASS with corrections F1-F3 (non-finite or huge coordinates, zero-area outline, no vertex cap); its skeptic judged them real but outside part A's reach; the orchestrator closed them in round 2 because the kernel's contract is to fail closed. G5 delta check (security-reviewer, session 2026-10-15b) at bed48258: PASS, F1-F3 closed, hostile probes reproduced, one advisory (a comment's wording).
- The advisories are carried to M5-T173 part B and M5-T174 (their packets will carry them); none changes a drawn value.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

I have everything needed. All review-relevant files are byte-identical at HEAD, the 28-test suite passes, I independently measured the SVG geometry, and I verified every value against the contract constants and the settled reading. Here is my G1 data-contract report.

---

# M5-T183 G1 data-contract review — area-illustration drawing kernel

**Reviewer role:** G1 data-contract verifier (data-contract-verifier). I am an AI agent; this is an independent, read-only AI review, not a human or professional review. I did not produce this work.

**Pinned identity:** `dec38ebf` (cherry-pick of builder `8276bb48`, parent `dc3a2276`) on `task/wave26-envelope-constraints` in `/root/project/w-wave20`. I confirmed the five review files are byte-identical between `dec38ebf` and current HEAD `69db15cf` (clean tree), so an in-place run is valid.

**VERDICT: PASS.**

## What I checked and reproduced (not taken from the producer)

- **Values come only from the document.** `_validate` reads `share`, `apartment/other/total_sqft`, `fitted` from the block and refuses unless `|apartment+other−total| ≤ 0.01` and `|apartment/total − share| ≤ 0.005`. I recomputed: placed `13300+5700=19000`, `13300/19000=0.70`; rear-yard `12025+6475=18500`, `12025/18500=0.65`. The footprint is `placement.outline[0]` (the 82×82 ring), scaled 82→196 pt. No value is hardcoded.
- **Percentage = `round(share*100)`.** Snapshots print `70%`/`65%`; test S4 proves `0.60→60%`. Not hardcoded (mutant M3 confirmed).
- **Drawn proportion = share within 0.5% — measured by me.** I re-parsed the snapshot geometry independently: shoelace area of the two placed zones gives apartment fraction **0.700000**; the rear-yard bar widths `189.80/292.00` give **0.650000**. Both exact.
- **Labels/caption byte-equal to tokens.** Hex-verified the em dash is U+2014 (`e2 80 94`) and no trailing period in the token `.py`, the `presentation-tokens.json` mirror, and both snapshots: "Apartment area" / "Other building area: core, circulation, walls and services" / "Illustrative area allocation—not a floor plan". The design contract line 43 explicitly settles that the owner's sentence full stops are not part of the text.
- **Exactly one stated percentage.** One `area_percentage` text; the only digit-bearing text content is the percentage (test S5 `numbers == [pct]`).
- **Measure + conversion match the contract constants.** Schema `$defs.area_measure` const `residential_floor_area`, `plate_conversion_statement` const (byte-equal to `_CONVERSION`), `illustrative_label` const `Illustrative`, `share` bounds 0.60–0.75 — all match; the kernel validates byte-equal and returns `Unavailable` on any mismatch (mutant-equivalent S8 `garbled`). The conversion statement is the G-14 disclosure carried on the drawing by contract. The displayed measure `Residential floor area` is a deterministic 1:1 humanisation of the single allowed enum (matches design-contract line 72); not a value from outside the document.
- **One caption; method elsewhere.** Exactly one caption drawn; `placement.method` is never read/drawn by the kernel (appendix-owned).
- **Fail-closed draws nothing mislabelled.** Fitted-without-outline → `Unavailable(not_placed)`; inconsistent split (apartment/total≠share) → `Unavailable(inconsistent)`; neither renders a `Drawing`, so no bar is ever mislabelled fitted.
- **No plan detail.** Only percentage, two zones/bar, footprint, one division, legend, measure, conversion, caption. No unit count, room, unit wall, stair or elevator.
- **Tests:** I ran `pytest tests/drawings/kit/test_area_allocation_drawing.py` with the lanes venv → **28 passed in 0.34s**.
- **Settled reading (step P8):** `placement-building-b.json` records share_low 0.60, ZFA 20,150, and the identical plate/conversion wording with the physical plate not checked. Nothing drawn contradicts it.

## 60% vs 65%/70% kept apart — YES, correctly

The kernel is data-driven: it prints `round(share*100)` of whatever the document carries and hardcodes no percentage (test S4 covers 0.60/0.65/0.70; mutant M3 proves it). The two snapshots show 70%/65% because they draw the two **synthetic** fixtures; the real report's **60%** is the engine's `share_low = 0.60` emitted upstream (`preliminary_apartment_estimate.py`; design contract line 70), and would be printed verbatim once wired (Part B, not this task). The engine's 60% and the synthetic 65%/70% are therefore not conflated.

## R087–R098 row-by-row (this part)

| Row | What the drawing does | Holds? |
|---|---|---|
| R087 | Two-zone illustration; "other" labelled "core, circulation, walls and services" (not "core and corridors") | Holds |
| R088 | Two zones replace the "nothing drawn" state | Holds |
| R089 | Zone labels byte-equal to the two tokens | Holds |
| R090 | Caption byte-equal to token (em dash, no period) | Holds |
| R091 | One stated % = `round(share*100)`, drawn proportion = share (±0.5%, measured) | Holds |
| R092 | Measure `residential_floor_area`; conversion statement carried; ZFA never equated to physical plate | Holds |
| R093 | No rooms/unit walls/counts/stair/elevator; one number only | Holds |
| R094 | Zones only when `fitted` + placed outline; else proportional bar | Holds |
| R095 | One short caption; method not drawn (appendix) | Holds |
| R096 | Website/PDF same-state | N/A — not wired this task (Part B/M5-T174) |
| R097 | Decision recorded in design contract + questionnaire | N/A to kernel — design contract carries R089/R090 wording (verified line 43); recording owned elsewhere |
| R098 | Rendered readability/consistency check | Partial here — labels 9.5 pt (≥8.5), hatch-not-colour, geometry verified; full rendered G3 is the visual-quality reviewer's remit |

## Findings

None REQUIRED. One **ADVISORY** observation (no correction needed): `_MEASURE_WORDS = "Residential floor area"` is a local humanisation of the enum const rather than a shared token; because the enum is a single-value const and the string matches the design contract, it is sound, but a future wiring task may prefer a shared token for the measure label.

## What I could not check

- Full-document R096/R098 (website+PDF same-state) — out of scope (Part B/M5-T174/M0-T195); correctly not asserted.
- Rendered-pixel readability is the visual-quality reviewer's G3 pass; I verified the measurable facts (9.5 pt, hatch distinction, geometry, byte-stable SVG) only.
- Whole api suite (9804 passed) — captured by the independent precheck at the builder commit; I reran only the dedicated test file.

END-OF-REPORT

## G1 (skeptic of the G1 review)

I have what I need. The G1 return marks **zero findings REQUIRED** (explicit: "None REQUIRED. One ADVISORY observation (no correction needed)"), so there is nothing REQUIRED to refute. I verified the single ADVISORY against the files.

SKEPTIC RETURN — M5-T183 G1 (pinned dec38ebf; files byte-identical at HEAD 86ae6cb for the kernel/packet/contract I read)

REQUIRED findings in the G1 return: NONE. The reviewer's verdict is PASS with no REQUIRED finding, so there is nothing in the REQUIRED class to uphold or refute.

The only finding of any class present:
- ADVISORY-1 (`_MEASURE_WORDS = "Residential floor area"` is a local humanisation of the enum const, not a shared token) — NOT REQUIRED, and correctly so. Evidence: `presentation_tokens.py` WORDING carries exactly three tokens (`area_zone_apartment`, `area_zone_other`, `area_illustration_caption`) — there is no measure-label token for the kernel to use verbatim, so no "must-use-token" rule is violated. The string matches contract R092 ("the proposed building's residential floor area", lines 72-74) and the schema enum `residential_floor_area` 1:1. Packet S2 lists only the two zone labels + caption as verbatim-token strings; the measure label is not a token-bound string. So this is a genuine optional observation, not a mis-graded REQUIRED defect. Its own wording ("a future wiring task may prefer a shared token") places any action in Part B / M5-T174, not this kernel task.

Scope confirmation (skeptic cross-check, so no REQUIRED defect was buried under a PASS):
- The review correctly scopes to Part A kernel-only. Items it declined to assert (R096 website+PDF same-state; full R098 rendered-pixel pass) are packet-exempt here (S7 and packet objective: "No report wiring, no website"; R096 is Part B + M5-T174 + M0-T195). Declining them is faithful to scope, not an evasion.
- DB-248 (apartment/total==share way rule) is owned by M5-T172; the kernel's `_validate` consistency refusal is defensive only (packet S3 NOTE, RISK 3). The review states this and does not claim DB-248 closed. Correct — no finding owed here.
- The real-report 60% vs synthetic 65%/70%: kernel prints `round(share*100)` data-driven (`_draw_bar`/`_draw_zones`); the 60% is upstream `share_low=0.60` (contract line 70). No conflation; no REQUIRED finding masked.
- Fail-closed paths (`_validate` + `_placed_ring`): missing/garbled block, non-finite or out-of-range share, apartment+other≠total, apartment/total≠share, fitted-without-outline all return `Unavailable` — matches S8 and the packet; the review's claims reproduce against source.

Conclusion: the G1 PASS carries no REQUIRED findings to challenge, and the lone ADVISORY is correctly non-required and, if ever actioned, belongs to the wiring task (Part B / M5-T174), not M5-T183. No REFUTED/UPHELD lines are owed because the review raised no REQUIRED finding. I surface no additional REQUIRED defect of my own within Part A scope. The G1 PASS stands.

END-OF-REPORT

## G3 (code-reviewer)

I have everything needed. All evidence reproduced. Here is my gate report.

---

# G3 Code Review — M5-T183 (area-illustration drawing kernel)

**Reviewer:** code-reviewer (AI agent, read-only, independent — I did not produce this). This is not a human or professional review.
**Reviewed identity:** `dec38ebf` (`task/wave26-envelope-constraints`). The worktree head moved to `69db15cf`, but `git diff dec38ebf HEAD` on all 5 task files is **empty** (byte-identical), so I ran ruff/pytest/modularity directly from the worktree. The read-only guard blocked `tar -x` to scratch, so I could not build a separate archive copy; byte-identity makes the worktree equivalent for execution.

## What I checked (reproduced)

- **Scope:** `git diff-tree dec38ebf` = exactly the 5 allowed paths; no forbidden path (fixtures, presentation_tokens, section/site_plan/adapter, report/, maps/, schemas, scenario/, apps/web/) touched.
- **Tests:** `pytest tests/drawings/kit/test_area_allocation_drawing.py` → **28 passed**.
- **Lint:** lanes-venv `ruff check` on both task files **and** whole `services/api` → All checks passed.
- **Modularity:** `tools/modularity_check.py --check` → failures 0; `area_allocation.py` (485 SLOC) absent from all 33 warnings.
- **Imports/layering:** imports only `.model`, `.presentation_tokens`, `.svg` — nothing from the engine (`scenario`/`rules`) or `drawings/report`/`drawings/maps`. Ruff confirms no unused import.
- **Signature/return (interface the wiring consumes):** `draw_area_allocation(allocation, *, placement=None, caption=True) -> Drawing | Unavailable` (lines 459-461) mirrors `section.draw_floor_stack`'s keyword-only `caption`/`-> Drawing | Unavailable` convention, including `caption=False` for the report frame. Stable and minimal.
- **Fixed values are source-backed, not guessed:** share range `_SHARE_MIN/_MAX = 0.60/0.75` (lines 57-58) equals `results.schema.json $defs.area_allocation.share` (minimum 0.6, maximum 0.75). `_LABEL`/`_MEASURE`/`_CONVERSION` (lines 48-54) equal the schema `illustrative_label`/`area_measure`/`plate_conversion_statement` consts byte-exact; printed only after the block is verified equal to them (`_validate`, lines 329-332) — no default stands for a fact.
- **Fail-closed:** every refusal in `_validate`/`_placed_ring` (not-Mapping, garbled label/measure/conversion, non-finite share, out-of-range share, total≤0, apartment+other≠total, apartment/total≠share, non-bool `fitted`, fitted-without-placed-outline) is correct and each is test-driven.
- **Determinism:** `num()` 2-dp, fixed attribute order, 100-iteration bisection + Sutherland-Hodgman clip; `test_s9` (reordered keys) and the 2 snapshots pin byte-stability.
- **Escaping:** all text routes through `svg.escape`; the caption's em-dash is legal and passes through; XML-illegal chars are refused.
- **Reference reading:** `placement-building-b.json` (real Building B, 0.60 share) is not contradicted — the kernel draws the two synthetic fixtures (0.70/0.65), reads `round(share*100)` from the block, and hardcodes no share.

## Test adequacy (my required check — each scenario vs the defect it guards)

Every S1-S9 test **fails on the defect it guards**: S1 switch (if the state branch were wrong, bar/zone roles flip → fail), S3 proportion (`data-apartment-fraction` is computed from the clipped polygon areas, so a wrong division x fails it; `test_s3_changing_only_the_share` is a genuine mutation guard: f(0.65)<f(0.70)), S4 (`60%`/`65%`/`70%` catches a hardcoded percentage), S5 `numbers == [pct]` (any extra drawn number fails), S7 (`sizes and all(...>=8.5)` guards the empty-vacuity trap; two distinct `patternTransform` prove hatch-not-colour), S8 (distinct refusals + plain-words). **The only vacuous test is the intentional, labeled seed `test_module_imports` (line 105)** — required by the repo's empty-suite rule, not a concern.

## Findings

1. **ADVISORY — label provenance empty.** `_text` builds `Label(text, "", role)` and passes `source=None` to `text_element` (lines 257-261), so no label carries a JSON pointer. `section.py` sets real `source=/floor_schedule/...` for data-derived labels, and `model.Label`/the report's C-4/C-5 provenance discipline expect pointers. The percentage/measure/conversion here are data-derived. **Correction for the M5-T173 wiring:** populate `source` (e.g. `/area_allocation/share`, `/area_allocation/conversion_statement`) when embedding, or confirm the report does not provenance-check embedded drawing labels. Not a defect in an unwired leaf kernel.
2. **ADVISORY — `_MEASURE_WORDS` hardcoded.** `"Residential floor area"` (line 49) is a display string, not a `WORDING` token (unlike the zone labels/caption). Low risk (derived from the byte-exact measure const); consider a token for consistency.
3. **ADVISORY — division geometry assumes a simple/convex-at-the-cut footprint.** `_draw_zones` (lines 436-453) derives the single division segment from `on_division` y-extent; exact for both (rectangular) fixtures, but a notched/non-convex placed outline could draw one segment spanning a notch. Out of scope here (both fixtures rectangular); flag for M5-T173 when real footprints are placed.

## What I could not check

- PNG rasterization / visual look — the visual-quality-reviewer's G3 remit (needs the Chromium rasteriser; I never start a server or Playwright).
- Per-requirement D-094 (R024, R087-R095, R098) attestation — the directive-compliance-verifier's pass. I confirmed the **drawing-behavior** requirements I can judge (R091 proportion ≤0.5%, R092/G-14 measure+conversion carried, R098 ≥8.5 pt) are met in code, tests and snapshots.

## Verdict

**PASS** (code share). Correctness, interface stability, imports/layering, determinism, escaping, error paths, modularity and ruff all reproduce clean; 28 tests pass and each scenario test is non-vacuous. The three findings are ADVISORY and none blocks acceptance; findings 1 and 3 are inputs the M5-T173 wiring should address.

END-OF-REPORT

## G3 (visual-quality-reviewer)

Greyscale confirms the two zones are unmistakable by hatch direction in print. My review is complete. Here is my gate report.

---

# M5-T183 — G3 visual review (area-allocation drawing kernel)

**Reviewer:** visual-quality-reviewer (AI agent, not a human/professional review). **Read-only.** Pinned SHA `dec38ebf` in `/root/project/w-wave20`. Scope of my share: the two snapshot SVGs.

**Verdict: PASS** (no REQUIRED findings; three ADVISORY notes for M5-T173 placement).

## What I did
- Extracted both snapshots at `dec38ebf` and rasterised them with the repo's own Chromium (`~/.cache/ms-playwright/chromium-1228`, file: URL, no server/port), at 3x, colour and greyscale. PNGs in `/tmp/claude-0/t183-review-g3-visual/` (`placed.png`, `rear_yard.png`, `placed_gray.png`).
- Cross-checked each drawn proportion against the source fixtures' `area_allocation`/`placement` blocks.
- Checked labels/caption against `presentation_tokens.py` and `ARCHITECT_PRESENTATION_CONTRACT.md`, and against owner rows D-094 R087–R098.

## Verification results (reproduced, not taken on trust)
- **Fitted state** `synthetic_placed_building_...area_allocation.svg`: fixture `share=0.70, fitted=true, placement.status=placed` (square outline 82×82). Drawn as two hatched zones inside a square footprint (196×196, aspect preserved) split by one vertical division; apartment width 137.20/196 = **0.700**. Matches R091/R094. ✓
- **Not-fitted state** `synthetic_rear_yard_..._area_allocation.svg`: fixture `share=0.65, fitted=false, placement.status=withheld`. Drawn as a single proportional bar; apartment 189.80/292 = **0.650**. Matches R091/R094. ✓ Both shares sit inside the 60–75% band (R087/R091).
- **Labels verbatim (R089):** "Apartment area" / "Other building area: core, circulation, walls and services" — exact match to the tokens and contract line 43/68; the remaining share is **not** called "core and corridors" (R087). ✓
- **Caption verbatim (R090):** "Illustrative area allocation—not a floor plan" with the em dash (U+2014) — confirmed in the rendered image. ✓
- **One explanation (R095):** the only *explanatory* caption is the one above. The "Residential floor area" measure line and the "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" line are **required on the drawing** by R092/R024 and contract line 72, not methodology — so they do not breach R095. ✓
- **Measure compatibility (R092):** the drawing names the same measure as the estimate (residential floor area) and carries the plate/zoning-floor-area disclosure; zoning FA is not presented as physical floor-plate. ✓
- **No floor-plan cues (R093):** only two zones, one division line, hatch, a legend and the caption — no rooms, walls, counts, stairs or elevators. The single vertical division is the neutral, non-layout choice. ✓
- **Colour + greyscale distinguishability:** the two zones share fill (#EEF4F7) and hatch colour (#182B3A) and are told apart by hatch **direction** only (−45° vs −135°). In the greyscale render (`placed_gray.png`) the perpendicular hatches remain unmistakable, and the 70/30 split reads in under a second. This is colourblind- and print-safe and satisfies "distinguishable in colour and in greyscale." ✓
- **Label size (contract line 82/258, R047):** every label is 9.5 pt. The drawing is authored at 1 user-unit = 1 pt, viewBox width 468 pt (= US-Letter content width; fits A4's ~516 pt content width at 1:1). At the designed 1:1 size, labels are ≥ 8.5 pt and hit the preferred 9.5 pt. ✓

## Findings

1. **ADVISORY — preserve final displayed size when T173 places it.** `...area_allocation.svg` whole drawing. The 8.5 pt floor and the hatch distinction are met *at 1:1* (468 pt wide). If M5-T173 scales the drawing below ~0.89× to sit beside the section/floor-stack, labels drop under 8.5 pt and the 0.5 pt hatch at 5 pt pitch can visually merge, weakening the two-zone read. *Correction:* place at ≥ its authored width, or re-derive hatch pitch/stroke and label pt at the reduced size so both stay legible. (Advisory, not REQUIRED: nothing is broken at the designed size.)

2. **ADVISORY — building diagram pairing is still owed (R094).** `rear_yard` bar renders **alone**; R094/contract line 111 require the bar "beside the building diagram." That pairing is correctly M5-T173's composition job, not this kernel's — flagging so T173 seats the bar next to the section/floor-stack, or R094 will not read true on the sheet.

3. **ADVISORY — flat type hierarchy for the headline share.** `area_percentage` ("70%/65% apartment area") renders at the same 9.5 pt as the fine-print conversion caveat, so the five-second anchor rests on the graphic proportion rather than the number. The contract does not mandate a larger stat inside a drawing, so this is optional; consider lightly emphasising the percentage (heavier weight within the drawing-label band) if T173 has room.

## What I could not check
- Behaviour at the **actual placed scale** on the scenario sheet (M5-T173 not yet built) — hence finding 1 is forward-looking.
- I reviewed the **committed snapshots as rendered**; I did not re-execute `draw_area_allocation` to regenerate them, and did not rerun the api suite (read-only; the pre-integration check records the whole api suite 9804 passed at the builder commit). Code-level re-derivation and byte-stability are the G4/precheck's remit.

**Nothing drawn contradicts** the settled reading in `docs/reference-cases/R6B/cases/placement-building-b.json` (the split is the fixtures' pre-computed share; this task draws it, it does not compute it).

END-OF-REPORT

## G3 (skeptic of the G3 visual review)

I have the evidence I need. All verified against the packet, the SVGs, tokens, and the contract.

Verdict summary: the G3-visual review contains ZERO findings marked REQUIRED — all three are ADVISORY and deferred to M5-T173. There is nothing to refute in the skeptic sense (no REQUIRED finding). I confirmed each advisory is correctly classified (genuinely out of this Part-A kernel's scope), and the PASS verdict holds.

Per-finding disposition (id, disposition, evidence):

F1 (ADVISORY, label size if T173 scales below ~0.89x): advisory classification UPHELD — correctly NOT required/in-scope. At the kernel's authored 1:1 size every `<text>` in both snapshots is `font-size="9.50"` (≥ 8.5 pt), viewBox 468 pt fits A4 content width (~516 pt) at 1:1. Packet S7 pins readability "at the printed size" and explicitly excludes the website+PDF same-state check (R096 → Part B / M5-T174 / M0-T195). Reduced-scale behavior is M5-T173's composition, so this is not a defect of the unwired kernel.

F2 (ADVISORY, R094 bar-beside-building-diagram pairing still owed): advisory classification UPHELD — correctly NOT required/in-scope. R094 (contract line "a simple proportional bar sits beside the building diagram") is satisfied by composition on the scenario sheet; the packet objective + S1 require the kernel to emit only "a proportional bar ... no zone drawn inside any outline," and forbidden_paths/objective bar report, section and website wiring ("No report or website embedding"). The rear_yard SVG correctly renders the bar alone. Pairing belongs to M5-T173 Part B, not here.

F3 (ADVISORY, flat 9.5 pt type hierarchy for the headline share): advisory classification UPHELD — correctly optional, NOT a defect. `area_percentage` is 9.5 pt, equal to other labels; neither the contract (print type scale R047/R048) nor any D-094 row mandates an enlarged stat inside a drawing. No contract/packet requirement is breached.

Independent cross-checks that would have forced a REQUIRED finding had they failed — all PASS, so none was wrongly downgraded:
- Proportions data-driven from share: placed 137.20/196 = 0.700 (share 0.70); rear_yard 189.80/292 = 0.650 (share 0.65). S3/S4 hold.
- Token strings byte-equal to presentation_tokens.py lines 106-108, including the U+2014 em dash and no trailing period (S2). Caption is the single explanatory caption (R090/R095).
- One stated percentage = round(share*100) → "70%"/"65%"; the contract's 60% is the upstream `share_low`, correctly out of this kernel (RISK 2 / S4) — not a token mismatch.
- No floor-plan cues: only two hatched zones, one division line, legend, caption; data-roles carry no rooms/walls/counts/stair/elevator (S5/R093).
- Zones distinguished by hatch direction (−45° vs −135°, shared fill #EEF4F7) not colour alone (S7); conversion statement present verbatim (S6/R024/R092).

Nothing in the review masks an in-scope defect. No REQUIRED finding exists to refute; the three advisories are correctly scoped to M5-T173/Part B. The reviewer's PASS is consistent with the files at dec38ebf.

Scope note: I verified the drawn artifacts, tokens, contract rows and packet; I did not re-execute the kernel or rerun pytest (read-only; byte-stability/determinism is G4/precheck's remit).

END-OF-REPORT

## G4 (qa-engineer)

I have everything needed. All six mutations each failed targeted tests and the source restored to 28/28; snapshots regenerate byte-identical; forbidden paths are clean in the task's own commit; modularity, ruff, layering, tokens and the design contract all check out. Here is my gate report.

---

# GATE REPORT — M5-T183 (G4, independent QA)

**Task:** M5-T183 — area-illustration drawing kernel, both states (`services/api/app/drawings/kit/area_allocation.py` + test + two snapshots).
**Gate:** G4 (QA / regression). **Reviewer:** qa-engineer, read-only. **I am an AI agent; this is not a human or professional review.**
**Reviewed identity:** `dec38ebf` on `task/wave26-envelope-constraints` in `/root/project/w-wave20` (cherry-pick of builder `8276bb48`; claim head `dc3a2276`). Worktree file confirmed byte-identical to `dec38ebf`.

## Verdict: PASS

All nine scenarios reproduce, all six required mutations are caught, snapshots regenerate byte-identical, and the task commit is byte-clean on every forbidden path. No REQUIRED findings.

## Required checks (archive copy of `dec38ebf`, lanes venv, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, from `services/api`)

| check | result | exit |
|---|---|---|
| `ruff check .` | All checks passed | 0 |
| task test file `test_area_allocation_drawing.py` | 28 passed | 0 |
| `flock heavy-run.lock pytest tests/drawings/kit` (once) | 465 passed in 23.04s | 0 |
| `UPDATE_DRAWING_SNAPSHOTS=1` regenerate → diff vs committed | both SVGs byte-identical | 0 |
| `modularity_check --check` (run in worktree, file byte-identical; archive has no .git) | failures 0; `area_allocation.py` not warned | 0 |

## Scenarios (how tested / result)

| id | how I tested | result |
|---|---|---|
| S1 state switch | roles of rear_yard (fitted=false→bar, no zone/division/footprint); placed (fitted=true+outline→zones, 1 division, no bar); fitted-no-outline (None/withheld)→Unavailable `not_placed` | PASS |
| S2 labels/caption verbatim | SVG text == WORDING tokens; em dash; no trailing period; exactly one caption | PASS |
| S3 share-driven proportion | bar & zone fraction == share ±0.5% at 0.60/0.65/0.70/0.75; fixtures 13300/19000=0.70, 12025/18500=0.65 == share; inconsistent total & share→`inconsistent` Unavailable | PASS |
| S4 one percentage | `round(share*100)` = 60/65/70%, not hardcoded | PASS |
| S5 no plan detail | only 6 texts; one number (the %); one `area_division` line; no rooms/walls/counts/cores | PASS |
| S6 measure+conversion | carries "Residential floor area" + exact conversion statement; "zoning floor area" absent from measure (ZFA not equated) | PASS |
| S7 readability | every `font-size` 9.5pt ≥ 8.5; both zones same fill `#EEF4F7`, two distinct hatch patterns (45°/135°) | PASS |
| S8 fail-closed | None/{}/NaN/0.50/0.80/garbled conversion/non-bool fitted → Unavailable; reasons carry no internal names | PASS |
| S9 determinism | repeat render + reordered-keys render byte-identical; snapshot byte-stable | PASS |

## My own mutation probes (archive copy; each applied, shown failing, restored → 28/28)

| # | mutation | first failing test | exit |
|---|---|---|---|
| 1 | draw zones when fitted is false (drop bar branch) | `test_s1_unfitted_draws_a_bar_no_zone` (+9) | 1 |
| 2 | percentage ≠ document share (+1) | `test_s4_percentage_is_round_share_times_100_not_hardcoded` | 1 |
| 3 | swap the two zone labels | `test_s2_labels_and_caption_are_the_tokens_verbatim` | 1 |
| 4 | add a second caption | `test_s2` (caption count) + `test_s5` | 1 |
| 5 | draw a bar when fitted + outline | `test_s1_fitted_with_outline_draws_zones_no_bar` | 1 |
| 6 | fitted-without-outline draws something | `test_s1_fitted_without_outline_is_unavailable_never_a_bar` | 1 |

Baseline and post-restore both 28 passed, exit 0. The harness genuinely pins each decisive behavior.

## Forbidden-path integrity

The **task commit `dec38ebf` itself touches only the 5 allowed paths** (`git show dec38ebf --name-only`). The `dc3a2276..dec38ebf` *range* shows `docs/reference-cases/` (9 files, 1-line additive seeds) moving — but that is the **disjoint peer commit `d0f15242` (M5-T184 contracting)**, not this task. The two shared synthetic fixtures (RISK 1), `presentation_tokens.py`, `section.py`, `__init__.py`, `results.schema.json` and every other packet-forbidden path are byte-identical across the range. Task identity is byte-stable; per the frozen-head convention the gate should be recorded against the task's own diff. No scope violation.

## Directive requirements reproduced (G4-testable; full verdict is the directive-compliance-verifier's, producer ≠ verifier)

R089 labels, R090 caption/em-dash/no-period, R091 one `round(share*100)` % (real-report 60% is upstream `share_low=0.60`, a documented responsibility split — not this kernel's to emit), R092/R024/G-14 measure+conversion carried and ZFA never equated, R093 no plan detail, R094 bar→zones switch, R095 one caption, R098 ≥8.5pt + hatch-not-colour — each reproduced against source and snapshot, and tied to a failing mutation. No drawn value contradicts the settled reading `placement-building-b.json` (60%): the kernel is data-driven and never draws the benchmark (it carries no `area_allocation` until M5-T172).

## What I could not check (not a defect)
- **Full api suite** — forbidden here; the pre-integration precheck ran it: 9804 passed at the builder commit (`return-M5-T183-precheck.json`).
- **PNG rasterisation / visual legibility** — the visual-quality-reviewer's G3; I verified font sizes, fills and hatch patterns from the SVG text only.
- **Website/PDF same-state (R096 document level)** — Part B / M5-T174 / M0-T195; correctly not asserted here.
- `modularity_check` in the archive copy fails on `git ls-files` (no `.git`); I ran it in the worktree on the byte-identical file instead (exit 0).

No REQUIRED or ADVISORY findings.

END-OF-REPORT

## G5 (security-reviewer)

All evidence gathered. The task test passed (28 passed, exit 0); precheck confirms ruff clean, whole api suite 9804 passed, modularity/lane/research checks green at the builder commit cherry-picked as `dec38ebf`. Composing the G5 report.

---

# G5 Security Gate Report — M5-T183 (area-allocation drawing kernel)

**Reviewer:** security-reviewer (independent, read-only). **I am an AI agent; this is not a human or professional security review.**
**Reviewed identity:** `dec38ebf` on `task/wave26-envelope-constraints` in `/root/project/w-wave20` (cherry-pick of builder `8276bb48`; 5 files). Content of all 5 files read directly; they match the precheck sha256s.
**Verdict: PASS with required corrections** (security posture clean; corrections F1–F3 are REQUIRED before the kernel is wired to any non-fixture document — M5-T173/T174).

## Scope confirmed
Diff touches exactly the 5 `allowed_paths` (kernel, test, 2 snapshot SVGs, producer report). No `forbidden_paths` touched: no fixture, `presentation_tokens.py`, `report/`, `maps/`, schema, or `apps/web/` edit. Not wired to report/website/benchmark. Reads only the two committed valid 1.5.0 fixtures.

## Security checks (my assigned share + standard G5 list)
1. **SVG/markup injection — PASS.** No document *string* is ever rendered. The kernel refuses (Unavailable) any block whose `label`/`measure`/`conversion_statement` differ from its own constants — confirmed by probe: markup in each → `Unavailable schema_invalid`. The only rendered text is module constants, presentation tokens, and the integer `round(share*100)`. Output helper `escape()` XML-escapes `& < > "` and raises on XML-illegal chars; attributes are always double-quoted. Confirmed `escape('<script>&"x')` → `&lt;script&gt;&amp;&quot;x`. Outline coords are coerced by `float()`; a non-numeric string raises `ValueError` (no injection). No document value reaches any attribute (all attribute values are numeric or constants).
2. **External resource / font / URL / XXE — PASS.** Valid output and both committed snapshots contain only the standard `http://www.w3.org/2000/svg` namespace and internal `url(#aa-hatch-*)` fragments. No `xlink`, `<image>`, `data:`/`file:`, `<!DOCTYPE>`/`<!ENTITY>`, external font or URL. `font-family` is a token name.
3. **Files / env / network — PASS (least privilege).** Imports only `math`, `collections.abc`, and local kit `.model/.presentation_tokens/.svg`. No `os`/`sys`/`open`/`subprocess`/`socket`/`urllib`/`requests`/`eval`/`exec`/`environ`. Pure function, no I/O.
4. **New dependency — PASS.** stdlib + local only.
5. **Secrets / log redaction — PASS.** No secrets in the diff (`token` = presentation tokens; `aws_` = `dr-aws_-a_bar` test names). No logging.
6. **Cross-tenant isolation / service-role secrecy / private storage / upload controls / SSRF / prompt-injection — N/A.** Pure deterministic drawing kernel: no DB, auth, tenancy, storage, uploads, network, or LLM. AI-boundary principle respected (deterministic code draws).

## Robustness findings from the mandated hostile-document probes
`share` and the area fields are well-guarded (non-finite / out-of-range / inconsistent → Unavailable — confirmed). The `placement.outline` coordinates feeding the fitted/zones geometry are **not** validated for finiteness, magnitude, or count:

- **F1 — MEDIUM, REQUIRED (fail-closed contract broken).** `area_allocation.py:203–207` (`_ring_points`) / `363–374` (`_placed_ring`) do not check coordinate finiteness. Probe: a `NaN` coordinate, and `±1e308` coords (which overflow to `inf`, then `inf*0=nan` in `place()` scaling, `:412–416`), both produce a **Drawing whose path `d` contains the literal token `nan`** — a malformed SVG — instead of `Unavailable`. No injection (`nan` sits inside a quoted, escaped attribute), but it contradicts the module's own "fail CLOSED … never a drawn guess" docstring. *Fix:* reject any non-finite outline coordinate in `_placed_ring` → `Unavailable`.
- **F2 — MEDIUM, REQUIRED (unhandled exceptions).** A degenerate zero-area outline (collinear points) raises an unhandled `ZeroDivisionError` at `:405` (`fraction = _poly_area(apartment_poly) / total`); an outline whose vertical clip yields an empty polygon raises `ValueError: not enough values to unpack` in `path_data`/`polyline_data` (`svg.py:89,96`). Probes `degen area0` and `±1e308` reproduce these. *Fix:* in `_draw_zones`/`_placed_ring`, require `_poly_area(ring) > 0` and non-empty clip results → `Unavailable` rather than raising.
- **F3 — MEDIUM, REQUIRED (enormous output / CPU).** No cap on outline vertex count. Probe: a 10^6-point outline produced a **42.6 MB SVG in ~103 s** (O(n) geometry × 100 bisection iterations). *Fix:* cap plausible footprint vertices (e.g. reject > a few thousand) → `Unavailable`.

**Severity context:** none of F1–F3 is reachable from the current wiring — this task reads only the two committed *valid* fixtures, and in the live pipeline `placement.outline` is produced server-side by the deterministic placement engine from real footprints (a handful of finite vertices), not from direct user input. None is an injection or disclosure vector. They are defense-in-depth that must be closed before this leaf ingests any non-fixture/less-trusted document (M5-T173/T174 Part B).

## What I verified / could not verify
- **Verified:** the full source of the 5 files; eight hostile-document probes (results above); valid-output and both committed snapshots carry no external/dangerous refs; task test green (`28 passed`, exit 0, lanes venv); scope clean; no secrets.
- **Relied on precheck (not re-run):** whole api suite 9804 passed, ruff clean, `modularity_check --check` (485 SLOC leaf, layering preserved, no giant functions), lane coverage, research-record check — all PASS at builder `8276bb48` = reviewed content. Modularity boundary is sound: single responsibility, imports only kit `model/presentation_tokens/svg`, no `drawings/report`/`maps` coupling.
- **Not in my remit:** per-requirement D-094 (R024, R087–R095, R098) verification — that is the `directive-compliance-verifier` pass; and visual/raster look — the G3 visual reviewer.

**Bottom line:** No security vulnerability in the scoped change (no injection, secret, SSRF, external fetch, tenancy, storage, upload, or dependency issue; least privilege and AI boundary respected). PASS, with F1–F3 as REQUIRED hardening corrections before the kernel is wired to live documents.

END-OF-REPORT

## G5 (skeptic of the G5 review)

All three findings reproduce; the kernel also satisfies every S8-named Unavailable case and both valid fixtures. I have enough to adjudicate.

SKEPTIC adjudication — M5-T183 @ dec38ebf (G5 REQUIRED findings F1–F3)

Framing: F1–F3 are all REAL, reproducible code defects (I reproduced each below). But every one concerns HOSTILE `placement.outline` COORDINATES, and the question that decides this gate is scope, not reality. The G5 reviewer itself writes "none of F1–F3 is reachable from the current wiring" and that they must be closed "before this leaf ingests any non-fixture/less-trusted document (M5-T173/T174 Part B)." That is a self-contradiction: a correction the reviewer scopes to a FUTURE wiring task cannot also be a blocking REQUIRED correction for THIS task. Part A is explicitly "the kernel only, not wired" (packet title/objective: "No report or website embedding"; reads only M5-T164's two committed VALID fixtures; path_notes: live `placement.outline` is produced server-side by the deterministic placement engine, never user/document input). The packet's fail-closed contract (S8 + the kernel docstring) enumerates exactly four Unavailable triggers — missing block, non-finite share, share outside 0.60–0.75, fitted-without-outline — and I verified all four plus both valid states behave correctly (missing/non-finite-share/out-of-range/fitted-no-placement/outline-absent/empty-outline → Unavailable; unfitted & fitted valid → Drawing, no `nan` token). Outline-coordinate sanitization is NOT in that contract. None of the cited D-094 rows requires it either: R089/R090 labels+caption, R091 one stated %, R092/R024 compatible measures / no silent equating, R093 no plan detail, R094 fitted-vs-bar state, R095 one caption, R098 readability check — all presentation, none input-robustness. The presentation contract governs page look, not geometry input validation.

Per-finding:

F1 (non-finite outline coords → literal `nan` token in SVG path `d`) — REFUTED as a REQUIRED M5-T183 correction. Real (reproduced: NaN coord AND 1e308 coord each DREW an SVG containing "nan"), but out of Part-A scope: unreachable from the two valid fixtures and from the deterministic engine; not among the packet's four named Unavailable triggers; no D-094 row demands it; reviewer itself defers it to wiring. Belongs to M5-T173/M5-T174 (Part B), as a WATCH/backlog item — not blocking.

F2 (degenerate zero-area outline → unhandled ZeroDivisionError at `_draw_zones` `fraction = _poly_area(...)/total`) — REFUTED as REQUIRED. Real (reproduced: collinear ring and 3-pt spike both raise ZeroDivisionError), same scope basis as F1. The `_placed_ring` structural guard (status/placed, Sequence, len>=3) is all the packet requires; positive-area / non-empty-clip hardening is a wiring-time (M5-T173/T174) concern. Defer, non-blocking.

F3 (no vertex-count cap → large SVG/CPU) — REFUTED as REQUIRED. Real mechanism confirmed (50k-vertex ring → DREW 2.1 MB in 3.6 s; linear, consistent with the reviewer's 10^6→42.6 MB/103 s). A DoS surface only once an untrusted document can set the outline — i.e. wiring (M5-T173/T174). Not reachable in Part A (fixtures carry a 5-point 82×82 ring; engine outputs a handful of finite vertices). Defer, non-blocking.

Net: M5-T183 meets its own acceptance contract (S8 fail-closed verified, valid fixtures render, no security/injection/secret/dependency issue — the reviewer's security posture is clean). F1–F3 are genuine hardening items that the reviewer's own scoping assigns to M5-T173/T174; they should be recorded (DISCOVERY_BACKLOG/WATCH or folded into the wiring packet) and must NOT block M5-T183. The G5 verdict should be a clean PASS for Part A with F1–F3 handed forward, not "PASS with required [blocking] corrections."

Reproduction (read-only, w-wave20, lanes venv): piped stdin probe importing `app.drawings.kit.area_allocation.draw_area_allocation` with `placement={"status":"placed","outline":[[...]]}` — F1a NaN→"DREW nan-token: True"; F1b 1e308→"DREW nan-token: True"; F2a/F2b→ZeroDivisionError; F3 50k→DREW 3.6s/2.1MB.

END-OF-REPORT

## G5 (security-reviewer, delta check of round 2)

G5 SECURITY DELTA REVIEW — M5-T183 round 2 (area-allocation drawing kernel)
Reviewer: security-reviewer (independent, READ-ONLY AI agent — not a human/professional review).
Pinned sha: bed48258 on task/wave26-envelope-constraints in /root/project/w-wave20 (cherry-pick of eca07305; round 1 = dec38ebf).

VERDICT: PASS (G5 delta).

Scope verification (both required empties CONFIRMED):
- git diff bed48258 48d6587b -- services/api/app/drawings/kit/area_allocation.py services/api/tests/drawings/kit/ -> EMPTY (nothing of the task changed after the pin).
- git diff dec38ebf bed48258 -- '*.svg' -> EMPTY (the two snapshots are byte-identical to round 1).
- bed48258 touches exactly 3 files, all in-scope: the kernel, its test, the producer report. (The larger dec38ebf..bed48258 name-only list is intervening merged work, not this commit.)

Hostile probes re-run in my scratch copy (lanes venv python; results reproduced, none raised, no nan/inf/<script> token anywhere):
1. label "<script>alert(1)</script>" -> Unavailable(schema_invalid) "The area allocation is incomplete." (label must equal "Illustrative"; and escape() would XML-escape it even if drawn). No script reaches SVG.
2. coord NaN / inf / -inf / 1e308 -> Unavailable(outline_invalid) "...point that is out of range." (F1 CLOSED).
3. coord == _COORD_MAX (1e9) -> Drawing, no bad tokens (boundary draws, no shoelace/scale overflow); coord just above 1e9 -> Unavailable (F1 boundary correct).
4. zero-area collinear ring -> Unavailable(outline_invalid) "...no area to show as two zones." (F2 CLOSED; the share division never sees total==0).
5. zero-width vertical spike -> Unavailable(outline_invalid) same reason (F2 CLOSED).
6. 1001 vertices -> Unavailable(outline_invalid) "...too many points to draw."; exactly 1000 -> Drawing (F3 CLOSED, boundary correct).
7. 10^6 points -> Unavailable(outline_invalid) rejected by the O(1) len(ring) check before any O(n) work (~2s wall is the Python list build, not the kernel).
8. non-number / nested-list / bool coord -> Unavailable (no crash); valid square -> Drawing, clean.

Findings:
F1 (non-finite / huge coords) — CLOSED. _placed_ring checks every vertex via _plausible_coord = _finite_number (int/float, not bool, math.isfinite) AND abs<=_COORD_MAX. path_data uses num()=f"{v:.2f}" which renders "nan"/"inf" for non-finite input, so the guard is the only thing preventing a malformed SVG token; probe confirms none leaks. REQUIRED-correction satisfied.
F2 (zero-area / empty clip) — CLOSED. After de-duplicating the closing vertex and requiring >=3 points, a ring with _poly_area<=0 returns Unavailable, so fraction=_poly_area(...)/total never divides by zero. I independently confirmed the svg-helper empty-clip ValueError (head,*rest=points on []) is unreachable for any positive-area, plausible-magnitude ring: bisection returns c in [minx,maxx] with minx<maxx, so keep_left always retains the leftmost vertex and keep_right the rightmost — each clip side has >=1 point. REQUIRED-correction satisfied.
F3 (vertex cap / DoS) — CLOSED. len(ring)>_MAX_OUTLINE_VERTICES refuses before building points or the 100-iteration bisection; only outline[0] is read (extra rings/holes never iterated). Worst-case bounded ~2e5 ops. REQUIRED-correction satisfied.
Cap constants — PASS. _MAX_OUTLINE_VERTICES=1000 and _COORD_MAX=1.0e9 are named module constants with a provenance comment; 1e9 ft covers EPSG:2263 NY state-plane (~1.1e6 ft) with large margin; 1000 vertices is generous for a footprint. Plausible.
Snapshots + valid path — PASS. SVG diff empty; test_matches_approved_snapshot (both committed fixtures) and the valid-square probe draw cleanly.
No new attack surface — PASS. Kernel adds only constants + two pure helpers; no new import (math already imported), no file/network/env/subprocess/dependency. Pure function; cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls, prompt-injection, log redaction are N/A at this leaf layer (no I/O, no auth, no LLM, no secrets; drawn text is fixed WORDING tokens + round(share*100)). Least privilege holds — inputs in, Drawing/Unavailable out.
Fail-closed is contract-safe — PASS. draw_area_allocation has no in-app consumer yet (exported + used only by its own tests), and Unavailable was already a documented return, so the new outline_invalid variant breaks nothing downstream.
Tests — PASS. 37/37 passed (flock, lanes venv, -p no:cacheprovider). Round-2 adds one test per input state (F1 parametrized nan/inf/-inf/1e308; F2 collinear; F2 spike; F3 over/at cap; plain-words reason; valid-still-draws). Each guard is load-bearing per my probes (remove F1 -> "nan" token; remove F2 -> ZeroDivisionError; remove F3 -> 1001 draws), matching the producer's mutation proofs; I confirmed by code reading + probe rather than mutating.
Reason strings — PASS. All refusals are plain words with reason_kind "outline_invalid"; the JSON-pointer "/placement/outline" lives in the traceability `source` field, not the user-facing reason. No field/record names, no secrets, no nan/inf in any reason.

ADVISORY A1 (non-blocking): the _COORD_MAX comment (lines 72-77) says a magnitude "at or above" the bound overflows the shoelace products; in fact exactly 1e9 is allowed (abs<=_COORD_MAX) and does not overflow (probe: 1e9 draws cleanly) — products reach ~1e18, sums ~1e21, far below float max. Behavior is correct and safe; only the comment's wording is imprecise. No change required.

D-093: this round adds fail-closed input validation only; it changes no feasibility fact, rule applicability, calculation input, result or certainty label, so revises no evidence record (consistent with the producer's read of NB-04: an outline area is a drawing measure, never a zoning figure — the kernel uses the outline only to draw proportions).

Limitations: I could not use a Write tool (none available) or shell file-writes (read-only guard); probes were fed to the lanes-venv Python via stdin against an archive of the pinned sha. I did not re-run tools/modularity_check.py; I confirmed by reading that the kernel is 527 lines (<600 warn line) and the change is a bounded addition within the kernel's existing responsibility (validate the outline before drawing) — no responsibility mixing, no giant function, no dumping ground.

END-OF-REPORT
