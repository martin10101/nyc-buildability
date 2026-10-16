# M5-T202 reviews (every return kept unchanged)

- Two producer rounds (frontend-engineer, worktrees): round 1 f0f54a04 (as 49bb867f on its base; cherry-pick a96f6880) and round 2 d7210438 (cherry-pick f88bdc86), which closed the visual review's REQUIRED finding (legend swatches mirror-inverted against their zones). 7 files, all inside the allowed paths; blobs equal to the builder commit d7210438.
- G2 orchestrator self-check at the integrated head: npm ci, lint, typecheck, the two web test files and the api parity test (web-checks-M5-T202.log); CI read green at the submit head.
- Round 1: G3 code-reviewer PASS, G3 visual FAIL (inverted legend), G4 qa-engineer PASS. Round 2 delta: G3 visual-quality-reviewer PASS (independent chromium render of the real component and of the CSS/SVG mirror primitives) and a code-and-test delta by code-reviewer PASS (recorded as the G4 delta, with the qa-engineer's round-1 G4 following it). The component stays mounted nowhere; mounting is M5-T174.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (visual-quality-reviewer) - part 1

VERDICT: FAIL

G3 visual review of M5-T202 (fitted two-zone area illustration on the website, unmounted), commit f0f54a047d237707466595dac250932bc39edfbd. I am an AI agent; this is not a human or professional review. I worked from the frozen commit (worktree source verified byte-equal to f0f54a04 for all four TS/TSX files; worktree HEAD is f0f54a04). I rendered the real component with chromium (the same playwright chromium CI uses), ran the ported geometry against the Python kernel, and looked at the output beside the kernel's drawing.

================ REQUIRED FINDING (blocks this gate) ================

1. REQUIRED — AreaAllocation.tsx: the FITTED drawing's legend swatches are mirror-inverted relative to the zones they label AND relative to the PDF kernel. A reader using the legend to tell which part of the footprint is apartment area gets it exactly backwards.
   - What is drawn (verified in a real chromium render of the frozen component):
       • Fitted zones (SVG): apartment zone patternTransform="rotate(-45)" renders "/" (rising right); other zone rotate(-135) renders "\" (falling right). These MATCH the kernel's zones.
       • Legend swatches (CSS): "Apartment area" swatch hatchStyle(45) renders "\"; "Other building area" swatch hatchStyle(135) renders "/". These are the OPPOSITE diagonal.
     Result: the "Apartment area" swatch ("\") visually matches the OTHER (right) zone, and the "Other building area" swatch ("/") matches the APARTMENT (left) zone. The legend key is inverted.
   - Root cause: CSS `repeating-linear-gradient(Ndeg)` and SVG `patternTransform="rotate(-N)"` produce mirror-image diagonals in chromium (CSS 45deg = "\", SVG rotate(-45) = "/"). The component draws the fitted zones in SVG (rotate -45/-135) but the shared legend swatches — and the bar — in CSS (45/135). Isolated tiles confirm each direction (see hatchcmp.png).
   - Why it is REQUIRED, not cosmetic: the hatch is the ONLY non-colour distinction between the two zones (both fill var(--pt-color-selected)); R098/S5 exist precisely so low-vision/colour-blind readers can tell the zones apart. An inverted legend key actively misleads that audience. It is also a web-vs-PDF parity break (R096) on a visible element: the kernel's "Apartment area" swatch is "/" and matches its apartment zone; the website's does not.
   - File/lines (AreaAllocation.tsx): hatchStyle defined L49-54; apartment legend swatch L75 `...hatchStyle(45)`; other legend swatch L86 `...hatchStyle(135)`; fitted zone patterns apartment `rotate(-45)` L157, other `rotate(-135)` L173.
   - Correction: make the legend swatch hatch direction equal the fitted-zone / kernel direction — apartment "/", other "\". Cleanest kernel-faithful fix: render the legend swatches with the same SVG patterns the zones use (apartment rotate(-45), other rotate(-135)), exactly as the kernel's `_footer` does. If keeping CSS, use angles that render apartment "/" and other "\" in chromium (swap: apartment 135, other 45) AND apply the same direction to the bar segments so the shared legend stays consistent with the bar and matches the kernel bar. Authoritative check: the "Apartment area" swatch hatch must visually equal the apartment zone hatch and the kernel's.
   - Test gap: the focused tests are green but do NOT cover this. S5 only asserts the two SVG patterns differ (`new Set(transforms).size === 2`) and that swatches exist; it never asserts swatch direction == the labeled zone's direction. Add an assertion that ties each swatch's hatch orientation to its zone's.
   - Reproduction (read-only, under the heavy-run lock): bundle the frozen component with esbuild (alias @ -> apps/web/src, node_modules from the worktree), renderToStaticMarkup for the benchmark fitted case, screenshot with playwright chromium at deviceScaleFactor 2. Artifacts I produced: /tmp/claude-0/visual-quality-reviewer/render/web.png (full), web_zones.png (zones "/" left, "\" right), web_fitlegend.png (apartment swatch "\", other "/"), hatchcmp.png (SVG rotate-45 vs CSS 45deg side by side), kernel.png + ker_zones.png + ker_legend2.png (kernel: apartment "/" in both zone and swatch).

================ VERIFIED CORRECT (reproduced, not taken from the builder) ================

- S1 geometry parity: the ported polyArea/clipX/divisionX are byte-identical to the kernel. I bundled the frozen area-allocation.ts and ran divisionX + area-fraction against the Python kernel on four shapes at shares 0.60/0.70/0.75 — rectangle (benchmark), right triangle, concave L, trapezoid — ALL identical to 6 decimals (e.g. triangle 0.6 -> division_x 36.754447, fraction 0.600000; L 0.6 -> 50.400000; trapezoid 0.6 -> 67.000000). The rectangle alone is a weak test; the non-rectangular cases confirm the port is faithful. Benchmark: data-apartment-fraction=0.6, data-division-x=60.456, polyArea(ring)=6716.6616 — equal to the golden and to the kernel. The golden file values equal the kernel math exactly (6716.6616 / 60.456 / 0.6).
- S2 refusal parity: all 13 TS reason constants (incl. the four outline refusals: too-many-points, not-given-as-points, out-of-range, no-area) are byte-present in kit/area_allocation.py. Verified the degenerate-outline branches (NaN/±Inf/1e308, zero-area collinear, zero-width spike, <3 vertices, non-point vertex, >1000 vertices, booleans) route to the same reason as the kernel.
- S3 bar unchanged: diff vs parent 60d0a096 shows the bar segments and percentage/fraction logic are untouched; the only -/+ around hatchStyle are the legend swatch lines moving verbatim into the extracted IllustrationFooter.
- S4 wording: AREA_ZONE_APARTMENT / AREA_ZONE_OTHER / AREA_ILLUSTRATION_CAPTION are byte-equal to presentation-tokens.json wording group (tokens file unchanged this commit). Caption uses the em dash, no trailing full stop.
- S5 content: fitted SVG has exactly 1 apartment zone, 1 other zone, 1 footprint edge, 1 division line (single full-height vertical at the share x), 0 <text>, 2 hatch patterns; both zones share fill var(--pt-color-selected). No room/unit/stair/elevator/apartment-count marks. Hatch, not colour, carries the (intended) distinction.
- S6: the sq ft split appears on neither surface — matches the kernel (verified the kernel render shows only the percentage).
- S7 mount: no import or JSX use of the AreaAllocation component anywhere; the only consumer of areaAllocationView is the component itself. The area-allocation references in results-contract-checks.ts are a separate, pre-existing schema-validation function (checkAreaAllocation), not the component. Still mounted nowhere.
- No browser-side recomputation beyond the footprint split: the selector reads share/apartment/other/total from the block; only the division geometry is computed.
- Modularity: area-allocation.ts 332 lines, AreaAllocation.tsx 283 lines; geometry lives in the lib, presentation in the component; clean separation, no dumping ground. Within thresholds.

================ ADVISORY ================

A. ADVISORY — the bar-branch hatch is also the mirror of the kernel's bar (web apartment "\" vs PDF "/"). This is pre-existing (M5-T187), unchanged here, and internally self-consistent (CSS swatch matches CSS bar), so it is not a regression of this task — but it means the website bar never matched the PDF bar's direction. Fold it into the same fix so the whole component matches the kernel.
B. ADVISORY — the methodology line reads "Measure: Residential floor area"; the kernel draws the bare "Residential floor area" (no "Measure:" prefix). The measure words themselves are byte-equal; the "Measure:" wrapper is a UI label the builder flagged (H8 item 3). Final wording is owned by the not-yet-accepted M5-T173 sheet — the brief's explicit unknown. Not blocking for this gate.

================ NOT CHECKED / UNKNOWNS ================

- I did not independently drive the focused vitest to green: it was queued behind heavy shared-lock contention (12 holders), so I terminated my own run to free the lock. Builder reports 35 tests pass; my independent render + geometry evidence corroborates every parity point EXCEPT the legend inversion, which the tests do not cover. I also did not run the api parity test for the same reason (independently confirmed golden == kernel math and reason byte-equality by reading + a direct kernel render).
- Where M5-T174 mounts this and the final measure wording (M5-T173) — stated unknowns, out of scope.
- Concave footprints: the single vertical division's AREA split is correct (verified on the L-shape), but the drawn concave polygon via evenodd fill was not assessed for appearance; benchmark/typical footprints are convex.

Bottom line: the headline deliverable — the fitted two-zone illustration — renders an inverted legend key (apartment swatch shows the other zone's hatch and vice versa), misidentifying the zones and diverging from the PDF kernel. That is a REQUIRED visual defect, so this gate is FAIL; send to rework for the hatch-direction fix (and add a swatch-matches-zone test).

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 2

VERDICT: PASS

G3 VISUAL DELTA REVIEW — M5-T202 round 2 (fitted two-zone area illustration on the website, unmounted), commit d72104381ed040c753b99ce0152951e0c38d3998, parent 49bb867f (= 60d0a096 + cherry-pick of round-1 f0f54a04). I am an AI agent; this is not a human or professional review. I worked from the frozen commit (archived d7210438 source into my own scratch, bundled the REAL component with esbuild, rendered it with the same playwright chromium CI uses, and rendered primitive reference tiles). No change to the worktree.

WHAT ROUND 1 FAILED ON (return-T202-G3v.md): the fitted legend swatches were mirror-inverted against the zones they label and against the PDF kernel — the "Apartment area" swatch drew the OTHER zone's hatch. Root cause: zones were SVG (rotate -45/-135) but swatches and the bar were CSS gradients with un-paired angles, and in chromium the two mechanisms mirror each other.

HOW I VERIFIED THE FIX (reproduced, not taken from the builder)

1. Structural (code + real markup). The delta introduces one direction source — APARTMENT_DIAGONAL="rising", OTHER_DIAGONAL="falling" — and new HatchPattern/HatchSwatch components. The legend swatches now draw with the SAME SVG `<pattern>` (same hatchSvgRotate) as the zones. In the real rendered markup (bundled from d7210438):
   - FITTED: swatch_apartment rotate(-45) == zone_apartment rotate(-45); swatch_other rotate(-135) == zone_other rotate(-135). Mechanism-identical, so the swatch can never diverge from its zone regardless of any chromium quirk. This is the robust closure of the r1 defect.
   - These rotate strings are byte-identical to the kernel (kit/area_allocation.py `_defs`: _hatch_pattern(APARTMENT,45)→rotate(-45), (OTHER,135)→rotate(-135); its _footer and bar reuse the same patterns), so the component's zones AND swatches match the kernel by construction.

2. Bar / chromium mirror (the only surface still on CSS). Bar apartment = CSS 135deg, bar other = CSS 45deg. I rendered 4 primitive tiles in chromium (A: SVG rotate(-45); B: SVG rotate(-135); C: CSS 135deg; D: CSS 45deg). Result: A and C render the IDENTICAL diagonal; B and D render the IDENTICAL opposite diagonal; the A/C group and the B/D group are mirrors. Therefore the apartment bar (CSS 135deg) visually equals the apartment zone/swatch (SVG rotate(-45)), and the other bar (CSS 45deg) equals the other zone/swatch (SVG rotate(-135)). The mirror fact the fix relies on is TRUE. Advisory A from r1 (bar vs kernel direction) is now also resolved: bar matches the kernel.

3. In-context render of the real component (component.png). FITTED: left apartment zone "/" matches the "Apartment area" swatch "/"; right other zone "\" matches the "Other building area" swatch "\" — legend now reads correctly. BAR: apartment segment "/" matches its swatch "/"; other segment "\" matches its swatch "\". Both states correct and kernel-faithful. Wording/caption/percentage/expandable detail all present and unchanged ("60% apartment area", "Apartment area", "Other building area: core, circulation, walls and services", "Illustrative area allocation—not a floor plan" with em dash, "How this illustration is worked out").

4. Disconfirming check (satisfied). My primitives prove the method is sensitive: CSS 45deg (the r1 apartment swatch) matches tile B/A? — it matches B (SVG rotate(-135), the OTHER zone), NOT A (apartment zone). So the r1 CSS-swatch apartment would have matched the other zone — exactly the r1 inversion. r2 switched swatches to SVG, which my render shows matching correctly. The inversion is gone and my harness would have caught it.

5. No regression / scope. Delta touches only 3 files, all allowed: AreaAllocation.tsx, its test, producer report. No change to area-allocation.ts (geometry), tokens, api, or contracts; no forbidden path (services/api/app, packages/contracts, ThreeAnswersPanel, FirstBuildingOptions, e2e) touched. Zones SVG output unchanged (rotate strings identical), so r1's verified S1 geometry parity and S2 refusal parity still hold. S5 pattern-count correctly re-scoped to the zones SVG (swatches are now their own SVGs). AreaAllocation.tsx = 331 lines; two small single-responsibility presentational components added, clean lib/presentation separation, no dumping ground.

FINDINGS

1. ADVISORY — area-allocation.test.tsx (new BAR test, ~L265-283): the BAR assertion `cssAngleToDiagonal(bar) === swatchDiagonal(...)` maps BOTH sides through the test's own hardcoded mirror tables (cssAngleToDiagonal: 135→rising/45→falling; svgRotateToDiagonal: -45→rising/-135→falling). Because the same assumption labels both operands, a WRONG chromium mirror assumption would still pass this test while rendering an inverted bar — the test encodes the mirror fact rather than verifying it in a browser. (The FITTED test is robust: it compares swatch SVG-rotate to zone SVG-rotate through one function — genuine mechanism equality.) Not blocking: I independently verified the mirror fact by rendering (primitives A==C, B==D), so the actual bar is correct. Correction (optional, G3-code/G4 territory): add a render-based or pixel-based assertion for the bar-vs-swatch diagonal, or a comment flagging the browser dependency.

2. ADVISORY (carried from r1 finding B) — the expandable methodology still reads "Measure: Residential floor area" vs the kernel's bare "Residential floor area". Final wording is owned by the not-yet-accepted M5-T173 sheet (the brief's stated unknown). Not blocking for this gate.

WHAT I DID NOT CHECK / UNKNOWNS
- I did not drive the focused vitest to green independently: the primary checkout does not carry the fix, and the reviewed worktree is off-limits to modify / has no installed-for-me deps; the builder reports 37 pass and r1's G4 verified geometry. My authoritative visual evidence is the chromium render of the real reviewed-commit component, which is sufficient for this VISUAL gate. (Same vitest-skip precedent as r1 under lock contention.)
- Where M5-T174 mounts the component and the final measure wording (M5-T173) — stated unknowns, out of scope.
- Concave-footprint appearance (evenodd fill) not reassessed; benchmark/typical footprints are convex; r1 verified the area split on an L-shape.

Artifacts (my scratch): /tmp/claude-0/T202-G3v-visrev-k7m2x9/primitives.png (A=SVG-45, B=SVG-135, C=CSS-135, D=CSS-45; A==C, B==D), /tmp/claude-0/T202-G3v-visrev-k7m2x9/component.png (real reviewed component, fitted + bar).

Bottom line: the r1 REQUIRED defect (inverted legend key) is closed — in both the fitted and bar states each swatch now shows its own zone's hatch, matching the PDF kernel direction (apartment "/", other "\"), confirmed by an independent chromium render of the real reviewed-commit component; the fitted swatch/zone match is structural (same SVG pattern) and the bar match is backed by my own render of the CSS/SVG mirror. Scope is clean. Visual gate: PASS, with two non-blocking advisories.

END-OF-REPORT

## G3 (code-reviewer)

VERDICT: PASS (G3 code review, M5-T202). I am an AI agent; this is an automated code review, not a human or professional sign-off.

SCOPE
- Reviewed commit f0f54a047d237707466595dac250932bc39edfbd (parent 60d0a096), task M5-T202 "Fitted two-zone illustration on the website (M5-T174 part B2a)".
- Builder worktree /root/project/nyc-buildability/.claude/worktrees/agent-aae110aa0f61f31b7 is at HEAD f0f54a04 with a CLEAN tree, so its working files == the committed versions. I also extracted the commit fresh to scratch (repo3) and ran the api test there.
- Packet: project-control/tasks/M5-T202.json (read from the worktree). 7 files changed, all inside allowed_paths; no forbidden path touched.

WHAT I RAN (reproducible)
1. api parity test (clean extraction repo3, under heavy-run lock):
   cd /tmp/claude-0/code-reviewer/repo3/services/api && python -m pytest -q tests/drawings/kit/test_web_parity_area_zones.py  => 3 passed.
2. Web vitest, the two touched files (worktree, clean at f0f54a04, under lock):
   apps/web && ./node_modules/.bin/vitest run src/lib/architect/__tests__/area-allocation.test.ts src/components/architect/answers/__tests__/area-allocation.test.tsx  => 2 files / 35 tests passed.
3. npm run typecheck (tsc --noEmit, worktree, under lock) => exit 0.
4. tools/modularity_check.py --check (worktree) => exit 0; every warning is a pre-existing file; none of this task's files (area-allocation.ts, AreaAllocation.tsx, area-allocation-tokens.ts) appears.
5. Independent recomputation of the benchmark split from a from-scratch shoelace+Sutherland-Hodgman+bisection (NOT importing the kernel): division_x = 60.456 (exact), apartment fraction = 0.6 (exact), footprint area = 6716.6616 (exact) — all match the golden report-parity-area-zones.json. A wrong (1-share) formula yields 40.304, which the golden would catch. So the golden is genuinely correct, not self-referential.

EVIDENCE THE BRIEF ASKED FOR — VERIFIED
- Split equals the kernel's: golden share 0.60, division_x 60.456, apartment fraction 0.6 on the 100.76 x 66.66 printed-tax-map footprint. The benchmark fixture recorded_215_16_northern_journey.json carries exactly that outline [[0,0],[100.76,0],[100.76,66.66],[0,66.66],[0,0]] (closing vertex de-duped) and share 0.6; apartment/other/total 12090/8060/20150. Verified by (1),(2),(5).
- Geometry port is faithful: apps/web/src/lib/architect/area-allocation.ts polyArea/clipX/divisionX (100-step bisection) and placedRing caps (1000 vertices; |coord|<=1e9 and finite; non-zero area; closing-vertex de-dup; <3 => not_placed) line-for-line mirror kit/area_allocation.py (_poly_area/_clip_x/_division_x/_placed_ring). Same IEEE-754 double arithmetic.
- Four placed-outline refusal reasons byte-equal to the kernel, plus the five validation reasons: the api test test_outline_refusal_reasons_are_byte_equal_to_the_web_selector READS each reason from the kernel and asserts it appears verbatim in the TS source (passed). Confirmed the TS constants AREA_REASON_OUTLINE_* / AREA_REASON_* match the kernel's Unavailable strings.
- Zone labels + caption byte-equal to docs/design/presentation-tokens.json: JSON wording.area_zone_apartment="Apartment area", area_zone_other="Other building area: core, circulation, walls and services", area_illustration_caption="Illustrative area allocation—not a floor plan" (em dash, no full stop) == web area-allocation-tokens.ts == kernel presentation_tokens.py WORDING. S4 component test pins this both directions (passed).
- Label/measure/conversion/share-range constants the selector validates against (results-contract-checks.ts: ILLUSTRATIVE_LABEL, AREA_ALLOCATION_MEASURE "residential_floor_area", AREA_ALLOCATION_CONVERSION_STATEMENT, share 0.6–0.75) are byte-equal to the kernel's _LABEL/_MEASURE/_CONVERSION/_SHARE_MIN/_MAX; these files are pre-existing and unchanged.
- Hatch not colour, one division line, no plan detail: S5 test confirms both zones carry fill var(--pt-color-selected) (identical), two <pattern> elements with distinct patternTransform angles, exactly one area_division and one area_footprint, zero <text> in the drawing, and no room/unit/stair/elevator/apartments/units text in any state. Verified in AreaAllocation.tsx ZonesDrawing.
- Bar branch unchanged: S3 test confirms the unfitted bar still renders (65% => widths 65%/35%, same testids/roles) and draws no footprint/zones; typecheck+vitest green.
- Nothing mounted / no figure recomputed: the AreaAllocation component is imported only by its own test; the selector module only by its own component + test; the old "fitted_deferred" kind is fully removed with no remaining references. The selector computes only the geometry split of the block's OWN placed footprint; percent = Math.round(block.share*100), areas read from the block — no zoning recomputation. S7 holds.
- sq ft split (S6): shown on neither surface (kernel prints only the percentage), matching the website; the gap is reported by the builder. Verified: no sq-ft figure in the component.

DISCONFIRMING CHECK
- Re-derived the split independently (item 5) and confirmed the golden; confirmed a (1-share) mutation would be caught. I could not perform an in-place file-mutation test (reviewer is read-only; file writes are hook-blocked), so I substituted independent recomputation + the builder's documented red/green mutation proofs, which the passing golden/parity tests corroborate.

FINDINGS
1. ADVISORY — apps/web/src/lib/architect/area-allocation.ts:261 (and the pre-existing bar branch :327) use Math.round(share*100); the PDF kernel uses Python round() (round-half-to-even). For a share whose *100 lands exactly on N.5 (e.g. 0.605 -> web 61% / PDF 60%; 0.625 -> web 63% / PDF 62%) the two surfaces would print different percentages. Realistic 2-decimal shares (0.60–0.75 in 0.01 steps) never hit a half-integer, and the golden does not pin percent, so this is latent/low-risk, not a blocker. Correction if ever desired: round half-to-even in the TS (or round at a shared source) so the stated percentage cannot diverge from the PDF. Inherited pattern from M5-T187; the fitted branch repeats it.
2. INFO (not a defect) — the packet lists apps/web/src/lib/architect/area-allocation-tokens.ts as an output/allowed path, but the commit touched 7 files, not 8: the tokens file is a pre-existing M5-T187 file reused unchanged (its strings are byte-equal to the JSON/kernel). allowed_paths is a permitted superset; nothing out of scope.
3. INFO (correctly deferred) — measure words kept as the kernel's bare "Residential floor area" and the methodology line "Measure: Residential floor area", because M5-T173 part B is not accepted at this head. This matches the packet path_notes and the brief's UNKNOWN-STAYS-UNKNOWN clause; the final measure wording and the mount point are owned by the accepted M5-T173 sheet / M5-T174. Documented gap, not owed by this task.

WHAT I DID NOT CHECK (out of this gate's scope)
- Pixel-level visual comparison of the rendered component against the PDF kernel's area_allocation.py drawing (render-to-PNG). That is the visual-quality-reviewer's gate; I verified the drawing STRUCTURE via the passing component tests and source, not its rendered appearance.
- A mounted six-width / recipe-V human walkthrough — not possible or permitted here (component mounted nowhere; builders/reviewers start no server). Belongs to the mount part and the UI reviewers.
- npm run lint was not independently re-run (builder reported 0 errors / 2 pre-existing-file warnings); CI runs lint as its first web step on the accepted head.
- Full web + api suites and security gates at the integration/merge head — the orchestrator reads these green in CI (R639).
- Formal per-requirement directive verification (D-094 R088/R091/R092/R093/R094/R095/R096/R247) is the directive-compliance-verifier's pass; the code evidence above satisfies the geometry-parity, fail-closed, no-plan-detail, one-percentage and byte-equal-wording requirements; I did not independently re-derive R247's text.

NOTE FOR THE ORCHESTRATOR
- A sibling agent also named "code-reviewer" is using the same scratch path /tmp/claude-0/code-reviewer/repo (process observed running pytest there) and overwrote my first full extraction's area-allocation.ts with an older copy, producing a spurious api-test FAIL on my first run. I reproduced cleanly in a separate scratch (repo3) and in the pristine worktree; the committed code passes. Future dispatches may want per-agent-unique scratch subdirs to avoid this collision.

Bottom line: the committed M5-T202 code faithfully ports the PDF kernel's split geometry and refusal wording to the website, draws two hatched zones with one division inside the placed footprint and no plan detail, keeps the bar branch, stays mounted nowhere, and has clean, focused module boundaries. All required scenarios reproduce green. PASS, with finding 1 as an optional advisory.
END-OF-REPORT

## G4 (code-reviewer)

VERDICT: PASS

Gate: M5-T202 round-2 delta — G3 (code) + G4 (tests). Reviewer: code-reviewer (AI agent; not a human/professional review). Read-only.

Reviewed content identity: commit d72104381ed040c753b99ce0152951e0c38d3998 (worktree HEAD = d7210438, the four touched source files clean/unmodified). Delta base: round-1 cherry-pick 49bb867f. Delta touches exactly 3 files, all in allowed_paths: AreaAllocation.tsx, its __tests__/area-allocation.test.tsx, and project-control/reports/M5-T202-producer-report.md. No forbidden path touched; area-allocation.ts (geometry + refusal reasons), the token file, and the api parity test/golden are unchanged this round (so geometry, wording and refusal reasons are unchanged by construction).

WHAT THE DELTA DOES (verified by reading the full diff + the full component at d7210438)
It introduces one hatch-direction source of truth: type HatchDiagonal with APARTMENT_DIAGONAL="rising", OTHER_DIAGONAL="falling" (the kernel's directions), and two derivations — hatchSvgRotate (rising→-45, falling→-135) and hatchCssAngle (rising→135, falling→45). The legend swatches are now drawn with the SAME SVG <pattern> (new HatchPattern/HatchSwatch) and the SAME diagonal constants as the zones; the zones' own <defs> reuse HatchPattern; the bar segments take a diagonal via hatchStyle(APARTMENT_DIAGONAL/OTHER_DIAGONAL).

CORRECTNESS (G3 code)
1. The r1 inverted-legend defect is now closed at the CODE level, not merely by coincidence: each swatch and its zone render through the identical HatchPattern+diagonal constant (apartment → rotate(-45), other → rotate(-135)), so the legend key cannot drift from the zones regardless of any rendering assumption. Strong fix.
2. Kernel parity verified in source: services/api/app/drawings/kit/area_allocation.py _defs() emits apartment patternTransform="rotate(-45)" and other "rotate(-135)" (line 152/159), and its hatch line geometry (x1=0,y1=2.5,x2=5,y2=2.5,stroke-width 0.5) is byte-identical to the component's HatchPattern. Component directions match the kernel.
3. Zones SVG output is unchanged: HatchPattern(rising)→rotate(-45), (falling)→rotate(-135) are byte-identical to the previous inline patterns; confirmed by the still-passing S1/S5 tests.
4. The bar (CSS repeating-linear-gradient) now renders apartment=135deg and other=45deg. Geometric reasoning confirms CSS 135deg stripes run "/" (rising) and 45deg run "\" (falling), matching the SVG rotate(-45)/"/" and rotate(-135)/"\" of the zones/swatches and the kernel bar; this also corrects the r1 bar advisory (r1 bar was the mirror). The EMPIRICAL chromium confirmation is the visual reviewer's gate (see Not-checked/Advisory 1) — producer's own chromium render (/tmp/claude-0/M5T202/render/area.png) and the r1 visual review support it.
5. Per-instance pattern ids via useId() (sanitized) on both swatches and zones — no id collisions across instances. Swatch svg is aria-hidden with the label text as the accessible content; data-role/class selectors preserved.
6. Modularity: the two new helpers (HatchPattern, HatchSwatch) are small, focused, single-responsibility; no responsibility mixing; file is 331 lines. I did not re-run the whole-repo tools/modularity_check.py (needs full tree); producer reports exit 0 and the diff is consistent with policy.

TESTS (G4) — reproduced (scratch at /tmp/claude-0/M5T202-g3g4-cr-k7q2v9/repo, worktree node_modules copied in; runs under flock /root/project/lanes-runtime/heavy-run.lock)
- Baseline, both files unmodified at d7210438: Test Files 2 passed, Tests 37 passed (35 prior + 2 new). PASS.
- typecheck (tsc --noEmit): exit 0, clean. (3 transient errors first seen were only missing-module errors from my partial archive in unrelated files e2e/results.flag-on.spec.ts and source-links.test.tsx; vanished once I archived docs/reference-cases and project-control/reports — none involved AreaAllocation.)
- lint (eslint .): 0 errors, 2 warnings, both in pre-existing files outside this task (lot-site-setup.test.tsx, study-vocabulary.test.ts). Matches producer claim.
- Test fixtures are real/valid: FITTED uses the recorded benchmark recorded_215_16_northern_journey.json (0.6; 100.76×66.66); BAR uses barBlock(0.65) (share in 0.60–0.75). The new hatch tests carry their own svgRotateToDiagonal/cssAngleToDiagonal mapping, query the zones SVG and each swatch SVG separately (no id cross-contamination), and pin absolute directions (apartment rising, other falling).

MUTATION EVIDENCE
- Real-defect reproduction (EXECUTED): I overlaid the actual round-1 defective component (49bb867f, CSS-span swatches) under the round-2 test file and ran it → the two new hatch tests FAIL ("unexpected SVG hatch rotate: (none)" because the r1 swatches have no <pattern>). This is a genuine, executed reproduction of the defect family that mutation A targets (the inverted/absent legend key), proving the new tests guard it. 11 of 13 other tests still passed.
- Exact single-line mutations A and B: I could NOT physically apply them. My read-only permission guard blocks all shell file-writes (tee/cp/ln/python-open all denied) and I have no Edit/Write tool; only tar extraction and test execution are permitted. I therefore derived their outcomes deterministically from the pinned baseline (the passing baseline fixes the actual rendered values: apartment swatch & zone rotate(-45)=rising, other rotate(-135)=falling; apartment bar 135deg=rising, other bar 45deg=falling):
  • Mutation A (swap the two HatchSwatch diagonals): apartment swatch→falling, other→rising; zones unchanged ⇒ FITTED assertion swatch(apartment)=falling ≠ zone(apartment)=rising FAILS, and BAR assertion bar(apartment)=rising ≠ swatch(apartment)=falling FAILS ⇒ 2 failed. Matches producer.
  • Mutation B (swap only the two bar hatchStyle diagonals): apartment bar→45deg=falling, other→135deg=rising; swatches/zones unchanged ⇒ FITTED PASSES; BAR assertion bar(apartment)=falling ≠ swatch(apartment)=rising FAILS ⇒ 1 failed (BAR), 1 passed (FITTED). Matches producer.
  The derivation is airtight because the two new tests are pure functions of rendered DOM attributes that the passing baseline pins exactly. If the orchestrator wants a literal single-line mutation run, it can capture that evidence; it is not needed to confirm the result.

SCOPE / PROVENANCE
- S7 confirmed: the only import of the AreaAllocation component is its own test file; no production import and no <AreaAllocation JSX mount anywhere at d7210438 — still mounted nowhere. (The checkAreaAllocation / AreaAllocationView matches are a different contract-check symbol and type, not the component.)
- No api, contract, token or lib file changed this round; no evidence-record code_paths implicated by this delta (producer's research_record_check exit 0 is consistent with the 3-file diff).

FINDINGS
1. ADVISORY — the two new hatch tests encode the SAME SVG-rotate/CSS-angle→diagonal mapping that the component encodes, so they verify internal consistency and the swatch/bar pairing but cannot by themselves prove chromium renders rotate(-45) and 135deg as "/"; if that shared assumption were wrong both would be wrong together. The empirical pixel confirmation is correctly the visual-quality-reviewer's gate (producer's chromium render + r1 visual review support it). No code change needed.
2. ADVISORY — the FITTED test's swatch==zone assertions are near-tautological in isolation (both derive from the same constants) but are genuinely guarded by the absolute-direction pins and by mutation A (swatch swap), so they retain discriminating power. No change needed.

NOT CHECKED / OUT OF MY GATE
- Empirical chromium pixel rendering of the hatch directions (visual-quality-reviewer's gate).
- The api parity test tests/drawings/kit/test_web_parity_area_zones.py and whole-repo modularity_check (unchanged this round / out of my 2-web-file scope; producer reports green).
- Directive-requirement satisfaction per ID (directive-compliance-verifier's pass).
- The unknowns the brief preserves: where M5-T174 mounts the component; the final M5-T173 measure wording (component still shows the kernel's "Residential floor area").

CONCLUSION: The round-2 delta correctly closes the r1 REQUIRED finding (legend swatches now match their zones by construction and the bar matches the kernel direction), changes nothing else, and is covered by adequate, discriminating tests. Lint clean, typecheck clean, 37/37 tests pass, and the new tests demonstrably fail on the real r1 defect. No REQUIRED defects for G3-code or G4.

VERDICT: PASS
END-OF-REPORT

## G4 (qa-engineer)

VERDICT: PASS (G4, qa-engineer) for ledger task M5-T202 at frozen commit f0f54a04047d237707466595dac250932bc39edfbd.

I am an AI agent; this is an independent, read-only evidence gate, not a human or professional review. I reviewed exactly the frozen commit. I did NOT write into the builder worktree or any repo folder; all runs used a scratch archive of f0f54a04 at /tmp/claude-0/qa-m5t202/repo, reusing the builder worktree's node_modules via per-entry symlinks (package.json + package-lock.json byte-identical between the frozen tree and the builder worktree, so the install matches). Heavy runs were serialized under flock /root/project/lanes-runtime/heavy-run.lock. I never touched ports 3000/3001/8000.

== WHAT I WAS ASKED TO DO (dispatch line) — all done ==
1. Rerun the two web test files under the lock — PASS.
2. Run the api parity test — PASS.
3. Reproduce the three claimed mutations — all three reproduced exactly.
4. Add one input state the builder did not test — a concave footprint; bit-for-bit Python/JS parity.

== STEPS EXECUTED, WITH OUTPUTS ==

(a) Web vitest, both touched files, scratch tree at f0f54a04, under the lock:
    node node_modules/.bin/vitest run src/lib/architect/__tests__/area-allocation.test.ts \
      src/components/architect/answers/__tests__/area-allocation.test.tsx
    -> Test Files 2 passed (2); Tests 35 passed (35); exit 0.
    (The command first ran >300s only because of a COLD vite deps-optimize; actual test duration 3.18s. No failures.)

(b) Api parity test, lanes venv pytest, cwd services/api, scratch tree:
    pytest -q tests/drawings/kit/test_web_parity_area_zones.py -> 3 passed; exit 0.
    Re-run after reverting every mutation: 3 passed; exit 0 (clean-state proven).

(c) Three mutations (each applied to the scratch copy, then reverted; both reverted files restored byte-identical to the builder's reported LF sha256 — area-allocation.ts 25406fab…, golden 198e725c…):
    M1 golden division_x 60.456 -> 61.456: api golden test FAILED (1 failed, 2 passed), AssertionError golden != kernel-computed. [Builder wrote "1 failed, 1 passed"; the file now has 3 tests so it is 1 failed, 2 passed — an immaterial count discrepancy; the essential claim (golden drift reddens the golden parity test) holds.]
    M2 divisionX target share*total -> (1-share)*total (web selector): vitest on the lib file -> "2 failed | 22 passed (24)"; the two failures are exactly the two S1 geometry tests (benchmark + 82x82 square); S2 and all others still passed. Matches the builder's claim exactly.
    M3 web AREA_REASON_OUTLINE_NO_AREA string changed: api reason-parity test FAILED ("web selector missing the no_area reason: 'The footprint has no area to show as two zones.'"). Matches the claim.

(d) NEW disconfirming input state the builder never tested — a CONCAVE footprint (the builder used only axis-aligned rectangles/squares and degenerate rings, where left-area is linear in x; a concave shape makes the bisection do real work and exercises the Sutherland-Hodgman clip on a non-convex polygon). I ran the SAME inputs through the REAL kernel (services/api/app/drawings/kit/area_allocation.py _poly_area/_clip_x/_division_x and the public draw_area_allocation) and the REAL JS port (area-allocation.ts polyArea/clipX/divisionX and areaAllocationView), and asserted strict === (bit-for-bit):
    - L-shape (100x100 minus 60x60 notch, area 6400) share 0.65: both divisionX = 43.999999999999986, fraction = 0.65 (analytic x=44).
    - L-shape share 0.60: both divisionX = 38.39999999999999, fraction = 0.5999999999999999 (analytic x=38.4).
    - L translated into negative coordinates, share 0.65: both divisionX = 13.999999999999982, fraction = 0.6499999999999999 (tests min/max handling).
    - triangle (0.5*120*80=4800) share 0.70: both divisionX = 54.273293099380055, fraction = 0.7.
    - public path on an explicitly-CLOSED concave L ring: kernel data-apartment-fraction = 0.65; JS areaAllocationView -> fitted_zones, ring de-duplicated to 6 distinct vertices, divisionX and apartmentFraction bit-equal to the kernel.
    vitest: 5 passed (5); exit 0. Conclusion: the geometry port is bit-identical to the kernel on concave shapes, negative coordinates, a triangle, and the closed-ring de-dup path — well beyond the cases the builder tested.

== ACCEPTANCE SCENARIOS (independently reproduced) ==
S1 benchmark split (0.6; 100.76x66.66): PASS. Golden = kit output (share 0.6, division_x 60.456, apartment_fraction 0.6, footprint_area 6716.6616, ring the 100.76x66.66 rectangle); lib + component S1 tests reproduce it within 1e-6; api golden regenerate/assert passes.
S2 fitted with no / degenerate outline: PASS. One test per state; the kernel's reason appears byte-equal (5 distinct reasons: 4 placed-outline F1/F2/F3 + not_placed), nothing drawn. Cross-surface byte-equality enforced by the api test reading the kernel reasons and matching them verbatim in the web selector.
S3 fitted:false -> bar unchanged: PASS (S3 tests assert 65%/35% widths, no zones/footprint/division; rerender table bar<->zones).
S4 labels/caption/measure byte-equal: PASS. Verified against docs/design/presentation-tokens.json: area_zone_apartment="Apartment area", area_zone_other="Other building area: core, circulation, walls and services", area_illustration_caption="Illustrative area allocation—not a floor plan" (em dash, no trailing stop). Measure words kept as the kernel's bare "Residential floor area" (M5-T173 sheet not yet accepted — correctly handled per the packet's path_notes; see finding 1).
S5 hatch not colour, one division, no plan detail: PASS. Both zones carry one neutral fill var(--pt-color-selected); told apart by two distinct hatch pattern angles; exactly one area_division and one area_footprint; svg has zero <text>; FORBIDDEN room/unit wall/stair/elevator/apartments/units patterns absent in both bar and zones states.
S6 sq ft split shown on neither surface: PASS. Kernel prints only the percentage; the component renders only "{pct}% apartment area", the zones/bar, the token labels, the caption, and (in an expandable <details>) the measure + conversion + "Not checked: Physical floor plate…". No apartment_area_sqft/other/total is rendered on either surface. Gap reported by the builder.
S7 diff only allowed paths, mounted nowhere: PASS. git show --name-only f0f54a04 = exactly the 7 files, all in allowed_paths; no forbidden path touched (no services/api/app, packages/contracts, presentation-tokens.json, ThreeAnswersPanel, FirstBuildingOptions, e2e). grep confirms AreaAllocation is imported only by its own test and area-allocation.ts only by the component + its own test — the component is mounted on no route. (results-contract-checks.ts checkAreaAllocation is a pre-existing, unrelated validator, not the component.)

== DIRECTIVE REQUIREMENTS (D-094; evidence I reproduced — formal per-requirement verdict belongs to the directive-compliance-verifier) ==
R088 authorization (add a two-zone illustration replacing "nothing drawn inside the footprint"): met — fitted branch now draws the zones.
R091 one explicitly stated percentage from the 60–75% assumption; drawing proportion consistent: met — percent=round(share*100) read from the block, apartmentFraction = drawn footprint proportion = share within 1e-6 (benchmark and all concave cases).
R092 compatible area measures; zoning floor area not treated as physical floor-plate: met — measure "Residential floor area"; conversion statement + explicit "Not checked: Physical floor plate (gross-up, exclusions, wall thickness)" byte-equal.
R093 no rooms/unit walls/apartment counts/invented stair-elevator: met — S5 evidence above.
R094 zones only when fitted, else a proportional bar: met — S3 + fail-closed not-placed reason (never a bar mislabelled fitted).
R095 one short caption, methodology in the appendix/detail: met — single caption token; methodology inside expandable <details>; the G-14 conversion is in detail, not the caption.
R096 same rules on website and PDF: met — geometry bit-equal (my concave parity), reasons byte-equal (api test), wording byte-equal to the shared tokens.
R247 obligation ("connect the appropriate existing components under the established feature flags"): NOT satisfiable at this commit — this part (B2a) deliberately leaves the component unmounted; mounting is M5-T174's job. See finding 2.

== FINDINGS ==
1. ADVISORY — Measure words are the kernel's bare "Residential floor area" (area-allocation-tokens.ts; methodology line "Measure: Residential floor area"), because M5-T173 part B is not accepted at this head (project-control/tasks/M5-T173.json absent). This is exactly what the packet path_notes and the brief's UNKNOWN clause prescribe; correction only needed if/when the accepted M5-T173 sheet changes the measure wording. Not a defect.
2. ADVISORY (for orchestrator + directive-compliance-verifier, NOT a G4 code defect) — The packet's directive_refs include D-094-R247, whose obligation is to MOUNT the component under the established feature flags, but this task correctly stays unmounted (part B2a; M5-T174 mounts it). R247 therefore cannot be verified PASS at f0f54a04. Ensure R247 is carried on / verified by the mounting task (M5-T174) rather than claimed complete here; otherwise accept() of an in-regime task could be blocked on an unverifiable R247. Nothing in the delivered code needs changing.
3. OBSERVATION (non-defect) — Mutation-1's reported count ("1 failed, 1 passed") differs from the actual "1 failed, 2 passed" because the api test file carries 3 tests; the essential mutation claim holds.
4. OBSERVATION — area-allocation-tokens.ts is listed in the packet outputs/allowed_paths but was not created by this commit (it pre-exists from M5-T187 and is byte-equal to the tokens). No action; outputs are permissions, not obligations.

== WHAT I DID NOT CHECK (out of my scope / other reviewers) ==
- I did NOT render the component to a PNG and eyeball it beside the PDF kernel's drawing; that is the visual-quality-reviewer's pass. I verified the SVG/DOM structure via the component tests and by reading AreaAllocation.tsx.
- I did NOT run the full web or api suites, or CI; CI-green at the merge head (R639) is the orchestrator's read.
- The formal, recorded per-requirement verdict (verification.json) is the directive-compliance-verifier's; I reproduced the requirement-linked behaviors from code + tests only.
- I verified the bar branch is unchanged via the passing S3 tests, not via a line-level diff against the parent.

Evidence paths (scratch, read-only): /tmp/claude-0/qa-m5t202/repo (archive of f0f54a04); /tmp/claude-0/qa-m5t202/kernel_lshape.py; /tmp/claude-0/qa-m5t202/repo/apps/web/src/__qa_lshape_parity__.test.ts; background outputs under /tmp/claude-0/-root-project-nyc-buildability/f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7/tasks/.

Reviewer conclusion: PASS. The web↔PDF split is bit-identical (including a concave footprint the builder never tested), the refusal reasons and wording are byte-equal across surfaces, fail-closed behavior is correct, the bar branch is unchanged, the component is mounted nowhere, and the diff touches only allowed paths. The only open item is coordination of directive R247 (mounting), which is correctly deferred to M5-T174 and should not be claimed complete at this commit.

END-OF-REPORT
