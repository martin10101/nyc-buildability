# M5-T192 reviews (every return kept unchanged)

- Two producer rounds (backend-engineer, worktrees): round 1 7d03dd8a (cherry-pick 2c91fe92) and round 2 883d9862 (cherry-pick 0bd9d747), which closed the visual review's REQUIRED F1 (height-limit labels overlapping storey labels on buildings taller than the minimum base). 5 files, all inside the allowed paths; blobs equal to the builder commits.
- G2 orchestrator self-check at 8e1d5912: the whole api suite passed on the increment (10179 passed, 8 skipped; api-suite-B124.log); ruff, research record check and lane coverage PASS.
- Round 1: G1 data-contract-verifier PASS, G3 code-reviewer PASS, G3 visual FAIL (F1), G4 qa-engineer PASS. Round 2 delta: G3 visual-quality-reviewer PASS (F1 closed; benchmark and default byte-identical to round 1) and a code-and-test delta by code-reviewer PASS (recorded as the G4 delta; the qa-engineer's round-1 G4 follows it). section_legal_lines.py (the G1 surface) is unchanged in round 2. Carried into the wiring part: 8.0 vs 8.5 pt printed label size, the 'schematic, not to scale' label, the '(Conditional)' caption reaching the page.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

VERDICT: PASS

G1 gate (data-contract-verifier) on M5-T192 — "every drawn height is read from the document and matches the captured law and the settled reading." I am an AI agent; this is not a human or professional review. Reviewed commit 7d03dd8a71836837151a28e46799167191fe5f47 (parent b9e9d563), read-only, from a clean `git archive` snapshot at /tmp/claude-0/g1review/repo. The commit touches exactly the 5 allowed-path files (section_legal_lines.py, section.py, kit/__init__.py, test_section_legal_lines.py, producer-report.md); no forbidden path, no report_frame test, no snapshot/fixture/register/evidence record.

== CORE DATA-CONTRACT CHECKS (all verified PASS) ==

1. Schema shape — the reader matches the contract exactly. results.schema.json `$defs/answer_available` requires status=="available" + `values` array (minItems 1) of `answer_value`, each with key/label/value(number)/unit(enum incl "feet")/zr_sections(minItems 1). The reader (section_legal_lines.py `section_legal_lines`) reads precisely that: `envelope.status=="available"`, `envelope["values"]` list, per-entry key∈STANDARD_HEIGHT_KEYS, unit=="feet", finite non-negative number, non-empty label, optional zr_sections. Correct field names and units.

2. Heights come only from the document, never computed/hardcoded. Independent render (LANE_E_ENABLED, benchmark Building B) emits three legal labels whose data-source pointers resolve to the document value: "Minimum base height 30 ft" → /answers/permitted_envelope/values/0/value = 30.0; "Maximum base height 45 ft" → .../values/1/value = 45.0; "Maximum building height 55 ft" → .../values/2/value = 55.0. section.py draws only `line.value_ft` and the schedule `max_top`; no height literal anywhere in the renderer.

3. Matches captured law + settled reading. ZR 23-432 snapshot (zr-23-432.snapshot.json, content_digest 9fab7be8…) R6B row = min_base 30 / std max_base 45 / std max_building 55; this digest is the exact one cited by real-lot.json row L3 (independent by-hand calc: "Min base 30; standard max base 45, max building 55"), R6B row carries no footnote so wide/narrow does not change them. The drawn 30/45/55 agree with both.

4. Qualifying-housing keys excluded. The benchmark also carries max_building_height_qualifying_affordable_or_senior = 65 ft (matches the law's R6B qualifying column). STANDARD_HEIGHT_KEYS deliberately omits the qualifying keys; the reader never draws 65 ft here. (Per brief, whether 65 ft is ever drawn here stays UNKNOWN / not this part.)

5. No line from envelope_rows. The reader never references envelope_rows; S4 tests confirm setback/street-wall/side-yard rows (40/60 ft) never become a line. Verified in code and by in-memory probe.

6. Missing/malformed drops the line, never a 0 default. S3's 12 drop-states + single-bad-key all pass (22/22 in test_section_legal_lines.py). A genuine document value of 0.0 IS drawn ("0 ft") — correct: the rule is "never default to 0", not "never draw a document 0".

7. Coinciding 30 ft shown once. fill_rule=="to_min_base" building tops at 30 ft; independent render shows exactly 3 dashed legal lines (ys 24.0 / 60.36 / 114.91), the 30 ft line at the building top, and the bare "Minimum base height" reference suppressed. Not four lines.

8. Default byte-identical. Full `tests/drawings/kit` run = 507 passed (incl. the 88 report_frame/rework tests, unedited); test_section_legal_lines.py = 22 passed. (lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider, multi-file runs under flock heavy-run.lock.)

9. Compact / no clip. Independent render = 360.00 × 238.00 pt (≤ 515.9 × 260). Layout height is fixed by _LEGAL_STACK_TOP(24)+_LEGAL_STACK_H(200)+foot, independent of limit magnitude, so a tall limit cannot clip. overlapping_labels == [] in-test.

Disconfirming work: the read-only guard blocks shell file-writes, so I could not mutate the source on disk. Instead I (a) resolved every drawn label's data-source pointer back to the document value (structural provenance proof above), (b) ran in-memory probes of untested input states, and (c) confirmed `_num_ft` is faithful (2-dp kit format: 44.949→"44.95", 30.0→"30 ft"; ZR limits are whole feet). The test test_s2_every_line_number_is_the_document_value_at_its_source plus numbers_not_in_input structurally guarantee a hardcoded/computed number would be caught.

== FINDINGS ==

1. ADVISORY (downstream B3/W — route this) — section_legal_lines.py (`LegalLine` dataclass + `section_legal_lines`): the reader ignores `value_states` entirely. In the REAL benchmark (recorded_215_16_northern_journey.json, contract 1.5.0) all three standard heights are marked `way: "conditional"` (the withheld ones — max_lot_coverage/rear_yard/setback_above_base — are correctly absent from `values` and not drawn). The section draws them as bare "Maximum building height 55 ft" dashed lines with no conditional indicator, and LegalLine carries no `way` field, so part B3/W cannot mark them conditional without re-reading value_states. Per the owner's standard ("conditional stays conditional," common-readonly L11, now a directive), the scenario-sheet placement (B3) or wiring (W) MUST carry the conditional way. This is outside B2's objective (the packet does not require way-carrying) and the brief places placement in B3/W (UNKNOWN), so it is not a B2 FAIL — but the orchestrator should ensure B3/W either reads value_states or that LegalLine is extended with the way before this ships to a page. Correction: add a `way`/conditional field to LegalLine, or have B3/W re-read value_states and label conditional heights.

2. ADVISORY (visual-quality / placement scale) — section.py:167 (legal label `size=size`, where size=TYPOGRAPHY.label_pt=8.0, styles.py:92). Legal-line labels render at 8.00 pt nominal (independent render confirms all text is 8.00 pt). The current contract (docs/design/ARCHITECT_PRESENTATION_CONTRACT.md:82 and :258) requires drawing labels "at least 8.5 pt at the printed/final displayed size" (the "≥7 pt" rule at :98 was superseded 2026-10-11). The task's test asserts ≥7 pt, matching the section's own docstring, not the 8.5 pt scale. This is NOT a regression — every existing floor-stack label (storey/grade/top/floor-to-floor) already uses the same 8.0 pt. Whether 8 pt nominal meets ≥8.5 pt at final size depends on the B3/W placement scale (the 360-pt-wide drawing scaled onto the ≤515.9 pt / 182 mm sheet), which is UNKNOWN at B2. The visual-quality reviewer should confirm label size at the integrated/final printed size. Correction (if final scale < ~1.07×): bump the section label size or ensure placement scale ≥1.07×.

3. ADVISORY (theoretical, low risk) — section_legal_lines.py `section_legal_lines`: duplicate standard keys in `values` both emit a line (probe: two max_building_height entries → two lines). The schema does not enforce key-uniqueness in the array; in practice the emitter produces unique keys (value_states is keyed by value key). No dedupe. Correction if ever needed: keep the first entry per key. Not a defect for any real document.

4. TRIVIAL (benign, no change needed) — section.py coincidence logic (`coincides_with_min_base_top`): suppression triggers when ANY legal line's value equals the building top, not specifically the min-base line. The variable name overstates the precision, but the behavior is correct — its purpose is to avoid two overlapping horizontal lines at the same y, which it does regardless of which legal line coincides. For a to_min_base building max_top equals the min base height, so in realistic cases it is the min-base line.

== WHAT I DID NOT CHECK ==
- Full api pytest, vitest/e2e, and the real report print — these are part W's and CI's at the integrated head (B2 is renderer/reader level); I ran only the focused kit tests as the brief directs.
- B3 scenario-sheet placement and W wiring (out of scope; explicitly UNKNOWN per brief) — Finding 1 and 2 hand the conditional-way and final-label-size questions to them.
- The builder's PNG at /tmp/claude-0/M5-T192/section_legal_lines_benchmark.png — I rendered my own SVG and checked geometry/numbers/fonts via DOM instead; the rendered picture is the visual-quality reviewer's (separate G3 reviewer in the packet).
- I could not perform an on-disk source mutation (read-only guard blocks file writes); I substituted pointer-resolution provenance proof + in-memory probes.

CONCLUSION: The data contract is sound — every drawn height is read from results.answers.permitted_envelope, carries its RFC-6901 source pointer, and matches the captured ZR 23-432 R6B law and the settled real-lot.json L3 reading (30/45/55); qualifying 65 ft is excluded; no envelope_rows line; missing/malformed drops (no 0 default); the coinciding 30 ft is one line; default output is byte-identical. VERDICT: PASS, with Finding 1 (carry the conditional way in B3/W) and Finding 2 (confirm ≥8.5 pt at final printed size) to be resolved at the B3/W/integrated head before this section reaches an architect-facing page.

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 1

VERDICT: PASS (G3 visual-quality review of M5-T192, commit 7d03dd8a) — with one REQUIRED blocking-before-generalization finding (F1) and two advisories. I am an AI agent; this is not a human or professional review.

SCOPE REVIEWED: the floor-stack section renderer with and without the height-limit lines, frozen commit 7d03dd8a in worktree agent-a8940a6a78e64038a. I worked from an isolated archive I byte-verified against `git show 7d03dd8a:<path>` for all four source/test files (SAME for section_legal_lines.py, section.py, __init__.py, test_section_legal_lines.py). Only the 5 allowed-path files changed; no forbidden path touched.

HOW I VERIFIED (not from the producer's screenshot):
- Rendered the benchmark section myself from the commit (lanes venv). My SVG is byte-identical to the producer's supplied section_legal_lines_benchmark.svg, so that picture is the commit's genuine output.
- Ran the focused test tests/drawings/kit/test_section_legal_lines.py on the byte-verified tree under flock: 22 passed.
- Parsed label boxes with the kit's own text_box and the overlap helper; viewed both PNGs (with-lines and default) at 3x.

VERIFIED FACTS (benchmark Building B — the only building_alternative in the fixture, to_min_base, top 30 ft):
- Reader reads ONLY the three STANDARD keys from results.answers.permitted_envelope: min 30 / max-base 45 / max-building 55 ft, each with its RFC6901 pointer (/answers/permitted_envelope/values/{0,1,2}/value) and zr_sections ("ZR 23-432"). The qualifying-housing 65 ft keys are correctly NOT drawn. Nothing computed; nothing from envelope_rows. S3/S4/S5 pass (drop-states, envelope_rows never a line, 1.4.0 identical).
- Three dashed reference lines drawn (exactly 3, not 4); the 30 ft minimum-base line coincides with the Storey 3 top and is drawn ONCE (bare "Minimum base height" label suppressed). Confirmed in the parsed SVG and the render.
- Labels: "Minimum base height 30 ft", "Maximum base height 45 ft", "Maximum building height 55 ft" — clear, left-aligned 7 pt above each line, in empty airspace above the 30 ft building. NO overlap at pad 0, 1, or 2 pt; all labels within the 360x238 canvas.
- Line weight/color consistent with the existing reference-line convention: all legal lines use _REFERENCE_STROKE (COLOR['action'] #18577A), stroke-width 1.0, dash "4.00 2.00" — same as the pre-existing bare min-base line. Grade 1.0 (ink), band 0.75, axis ticks 0.4. No weight/color defect.
- Compact: 360 x 238 pt (238 <= 260; 360 <= 515.9). Default (legal_lines=None) is 360 x 358 pt and byte-identical to today (S1 passes: test_s1_default_render_is_byte_identical and test_s1_legal_lines_none_is_byte_identical).
- The two renders read correctly side by side: default shows the bare "Minimum base height" line (no value) on the full-height stack; with-lines shows all three valued limits and the legal headroom above the 30 ft building in a compressed stack.

FINDINGS:

F1 (REQUIRED — blocking before the section is used for any worked building whose limit lines fall inside the band stack; does NOT affect the benchmark or any current data). section.py:166-167. The legal-line label is placed with a SINGLE fixed candidate `[(_STACK_X0, y - 7.0, 0.0)]` and no collision fallback, unlike every other label in the section (storey/ff/top at section.py:139-152 pass TWO candidates each and use sheet.label -> first_free). Disconfirming check (my own synthetic buildings, reproduced on the byte-verified tree): any building whose schedule rises above its minimum base so a limit line lands inside a band produces overlapping labels:
  - 4 storeys x 10 ft (40 ft, well inside the 55 ft envelope): "Minimum base height 30 ft" overlaps "Storey 4" and its "10 ft" ff label (2 overlaps).
  - 5 storeys x 11 ft (fills to 55 ft): "Maximum base height 45 ft" overlaps "Storey 5" and "11 ft".
  - 7 storeys x 10 ft (70 ft): "Minimum base height 30 ft" overlaps "Storey 4" and "10 ft".
  The benchmark avoids this only because it is a to_min_base 30 ft building with all three lines at/above the top. Since the feature exists to show zoning lines on worked-building scenario sheets (contract page 4) and most worked buildings will not be exactly at the minimum base, this is a latent clutter defect. Correction: give the legal-line label the same multi-candidate / first_free treatment as the storey/ff labels (e.g., add an above-left-in-gutter and below-line candidate), or route it to a clear gutter. The fix is safe: it only runs when results are passed, so the legal_lines=None byte-identical baseline (S1, the 88 report-frame tests) is untouched, and for the benchmark no collision occurs so first_free keeps candidate 0 -> benchmark output unchanged.

F2 (ADVISORY — contract conformance to verify at integration, not a B2 code defect). Drawing labels render at 8.0 pt (TYPOGRAPHY.label_pt). The active presentation contract print-type-scale (docs/design/ARCHITECT_PRESENTATION_CONTRACT.md line 82, and H2 at line 90, change of 2026-10-11) requires "drawing labels at least 8.5 pt at the printed size"; the earlier ">= 7 pt" rule is explicitly superseded (line 98). The packet's test asserts only MIN_LABEL_PT = 7.0 and section.py:118/docstring line 15 still comment "7 pt" — both stale vs the current 8.5 pt contract. At the natural 1:1 scale (canvas 360 pt = 127 mm, inside the 182 mm A4 usable width) the labels are 8.0 pt, BELOW 8.5 pt. The actual printed size depends on how part W/B3 scales the drawing onto the scenario sheet (UNKNOWN here): if scaled up to fill the column it would exceed 8.5 pt; at natural size or smaller it stays <= 8.0 pt. This is section-wide and pre-existing (all section labels are 8.0 pt) and is constrained by the byte-identical baseline, so it cannot be fixed inside B2 without a cross-cutting decision. Recommend the orchestrator ensure >= 8.5 pt at the final printed size when W places the drawing, and refresh the stale "7 pt" comment/test threshold.

F3 (ADVISORY — cross-part handoff, not a B2 defect). The contract (page 4, line 56/111) requires the floor stack to be "labelled 'schematic, not to scale'". B2 renders in the report frame with caption=False (the report prints the caption beneath it, K7), so B2 draws no such label. Confirm part B3/report supplies the "schematic, not to scale" label and the section caption; otherwise it will be missing from the sheet.

WHAT I DID NOT CHECK (out of scope / not runnable here): the integrated report print and the actual on-sheet placement/scaling (part W/B3, no server used); the full api pytest / vitest / e2e (CI's job at the integrated head — the producer reports 507 kit tests pass with the 88 report-frame tests unedited, which the orchestrator should confirm green at the integrated head); whether B3 supplies the schematic label (F3).

ENVIRONMENT NOTE (for the orchestrator, not a code issue): /tmp/claude-0/ is shared across the concurrent helpers; another helper's report-page-6 check wrote files (including an inspect.py that shadowed the stdlib) into the folder I first used, corrupting my first extraction. I re-ran everything in an isolated unique directory with byte-verification against git show; all stated results are from that clean tree.

BOTTOM LINE: The delivered benchmark section meets the packet's S1-S5 and the brief's benchmark-scoped visual criteria (readable labels, no overlap, compact fit, byte-identical default, correct provenance, qualifying heights excluded) — PASS. F1 is a reproducible latent overlap that must be corrected before the section renders any worked building taller than its minimum base; F2 and F3 are integration-level items to verify.

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 2

VERDICT: PASS (G3 visual-delta review of M5-T192 round 2, commit 883d9862). I am an AI agent; this is not a human or professional review. F1 (the round-1 REQUIRED blocking finding) is closed; benchmark and default outputs are byte-identical to round 1; no regression in the delta. Two ADVISORY notes and two carry-forward integration items below.

# Gate Report
- Gate ID: G3 (visual-quality, delta round 2)
- Task ID: M5-T192 (part B2 of M5-T173)
- Reviewer: visual-quality-reviewer (AI agent, read-only)
- Producer: backend-engineer, commit 883d9862a7afcc14104d9164959b0405a424ec73 (parent d819f9f7 = round 1 cherry-picked)
- Result: PASS
- Clean environment/worktree used: yes. Archived 883d9862 from worktree agent-aacd6868cc34e1375 into an isolated scratch tree under /tmp/claude-0/M5-T192-g3v-vqr-7k2m9q/repo; LF-sha256 of section.py, test_section_legal_lines.py and the producer report all MATCH `git show 883d9862:<path>`. Delta scope confirmed: section.py + test + producer report only; section_legal_lines.py and kit/__init__.py byte-identical to round 1 (independently diffed d819f9f7 vs 883d9862).

## Acceptance criteria reviewed (visual delta per brief)
Closing REQUIRED F1 (return-T192-G3v.md): the height-limit label now gets the same multi-candidate first_free placement as the storey/ff labels, so a limit line falling inside the band stack never prints its label over a storey band or another label. Verified against the three reviewer-worked buildings (4x10, 5x11, 7x10 ft), a sweep, byte-identity of benchmark and legal_lines=None, canvas-widening safety, no dropped labels, and the mutation proof.

## Directive/requirement verification
This is the G3 VISUAL gate; full D-094 requirement re-derivation is the directive-compliance-verifier's pass. From the visual lens I confirmed the two drawing-quality obligations the delta touches: labels readable and collision-free (no clutter) and the drawing staying within the A4 report frame. Both hold within the feature's domain (see Steps). No visual contradiction with the owner's "what is drawn must agree / no clutter" standard.

## Steps independently executed (lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider)
1. ruff on the changed section.py -> All checks passed (exit 0).
2. Focused test file tests/drawings/kit/test_section_legal_lines.py -> 26 passed (22 round-1 + 4 new). Single-file run, no flock needed.
3. Independently re-rendered the benchmark + the three worked cases from the frozen tree and parsed label boxes with the kit's OWN labels.text_box / Box.overlaps and the test's overlapping_labels helper (the same basis the round-1 reviewer and the test use; no rasterizer is installed here - no rsvg/inkscape/chromium/cairosvg/PIL - so I verified label GEOMETRY, which is the authoritative lens for a collision fix).
4. Overlap analysis:
   - benchmark: w=360.00 h=238.00, 3 legal labels all at x=150 (candidate 0), 0 overlaps.
   - 4x10 (40ft): w=360 h=238, 0 pad-0 overlaps.
   - 5x11 (55ft): w=360 h=238, 0 pad-0 overlaps.
   - 7x10 (70ft): w=432 h=238, 0 pad-0 overlaps (the 30 ft line's label took the right gutter at x=306; the other two stayed at stack-left).
   - Sweep 1..12 storeys x ff 6..16 (132 cases, benchmark 30/45/55 lines): ZERO pad-0 label overlaps in every case; max width 451.2 pt (< 515.9 cap); every height 238 pt (< 260). Legal labels never dropped (all 3 present in each case).
5. Byte-identity (sha256 of the SVG string):
   - benchmark + lines: round-1 == round-2 == 6c5d5d43... (benchmark output UNCHANGED).
   - render frame with no results: round-1 == round-2 == ab3a30c1..., and == draw_floor_stack(..., legal_lines=None) (default/None path byte-identical).
   - My independent renders of the benchmark and all three worked SVGs byte-MATCH the producer's supplied files in /tmp/claude-0/M5-T192/pics/, so those pictures are the commit's genuine output.
6. Canvas-widening safety: width is computed only when legal lines are present (`if lines: ... else: width=_CANVAS_W`), capped at REPORT_MAX_W_PT=515.9; band and grade geometry are drawn at fixed x (150..300) independent of width, so widening only adds right-hand whitespace and never moves or clips the stack. Longest reader label ("Maximum building height 55 ft", 139.2 pt wide at 8 pt / char_width_em 0.6) in the right gutter reaches x1=445.2 pt -> no clip is possible for the reader's fixed label set.
7. Mutation proof reproduced: I restored the pre-fix single candidate (= round-1 section.py) and ran the round-2 F1 tests -> 3 failed (4x10, 5x11, 7x10, each reporting the reviewer's exact overlaps e.g. ('Storey 4','Minimum base height 30 ft')), 1 passed (test_f1_benchmark_keeps_every_legal_label_at_candidate_zero, correctly invariant). The tests genuinely detect F1 and the fix is what closes it.
8. Disconfirming check (tried to break a passing scenario): pad-0 overlaps reappear only at ~30 storeys / 300 ft (30x10 -> 62 overlaps, of which 5 involve a legal label). At that height the ROUND-1 compact layout (_LEGAL_STACK_H=200 vs default _STACK_H=300) shrinks each band below the 8 pt label height, so storey-vs-storey labels crowd; the DEFAULT no-lines section has 0 overlaps there because it is not compacted. Every building up to 20 storeys / 200 ft (well beyond the specified sweep and far beyond the R6B envelope these 30/45/55 ft lines describe, whose max building height is 55 ft ~ 6 storeys) has ZERO overlaps.

## Expected versus actual
- Expected (F1 closed): no overlapping labels for 4x10/5x11/7x10 and the sweep. Actual: 0 pad-0 overlaps in all named cases and all 132 sweep cases. MATCH.
- Expected: benchmark and legal_lines=None byte-identical to round 1. Actual: identical hashes. MATCH.
- Expected: widening only with legal lines, capped at 515.9, never clips/moves the stack. Actual: confirmed (default path unchanged; max observed width 451.2; stack geometry width-independent; clip impossible for the label set). MATCH.
- Expected: labels never dropped. Actual: all 3 legal labels present in every rendered case. MATCH (note nuance in A1).
- Expected: mutation proof. Actual: reproduced (3 fail / 1 pass). MATCH.

## Evidence paths
- Frozen tree: /tmp/claude-0/M5-T192-g3v-vqr-7k2m9q/repo (archive of 883d9862)
- Round-1 comparison tree: /tmp/claude-0/M5-T192-g3v-vqr-7k2m9q/repo1 (archive of d819f9f7)
- My independently rendered SVGs: /tmp/claude-0/M5-T192-g3v-vqr-7k2m9q/pics/{benchmark,worked_4x10,worked_5x11,worked_7x10}.svg (byte-match producer's /tmp/claude-0/M5-T192/pics/)
- Reviewed source: services/api/app/drawings/kit/section.py @ 883d9862 (legal-label candidate list, section.py lines ~166-186; width calc lines ~211-223)

## Human-style walkthrough findings
Reading the four sections as an architect would: the benchmark shows the three dashed R6B limits (30/45/55 ft) with clear left-aligned labels in the airspace above the 30 ft building and the 30 ft line drawn once at the storey-3 top (unchanged from round 1). For worked buildings whose limits fall inside the stack, the labels relocate cleanly - below the line or into a right-hand gutter - and read as tied to their dashed lines; the drawing stays compact and inside A4. No clutter, no label lost, no default-template look.

## Regression/security/provenance findings
- No regression in the delta: default/None and benchmark outputs are byte-identical to round 1; reader module unchanged; the 88 report-frame tests are untouched and remain green per the producer (focused folder run is CI's job at the integrated head, out of my focused scope).
- Provenance intact: the new tests assert each legal label's data-source resolves to its printed number (30/45/55 ft), values grounded in real-lot.json row L3 / ZR 23-432, never a program run. No evidence record or review_register cites a drawings module.

## Defects
None blocking.

ADVISORY A1 (section.py legal-label placement; builder return "the label is never dropped and never overlaps"): the "never overlaps" claim is unqualified but only holds within the realistic/swept domain. Via first_free, when ALL 7 candidates are occupied the label falls back to the LAST candidate (a right-gutter position) and can then overlap - this occurs only around 30 storeys / 300 ft, where the round-1 compact layout already crowds storey labels (5 of 62 overlaps there involve a legal label). This is outside the R6B envelope the 30/45/55 ft lines describe (max building height 55 ft) and outside the specified sweep, and the dominant cause is the pre-existing compaction, not the F1 fix. Correction (optional, not in B2): if worked buildings far above the envelope are ever drawn with these lines, revisit the compact-layout band spacing; no change needed for the accepted scope.

ADVISORY A2 (visual density): with legal lines the compact stack packs labels tightly - minimum inter-label gap drops to ~1.0-1.4 pt in dense worked cases (e.g. 6x10 -> 1.07 pt between 'Storey 3' and 'Minimum base height 30 ft'). This is exactly first_free's default 1.0 pt pad - identical to how the section's own storey/ff labels are already spaced - so it is consistent and legible but tight at 8 pt. No action in B2.

## Required rework
None.

## Reviewer conclusion
PASS. The round-2 delta closes REQUIRED F1 with the same multi-candidate first_free treatment the rest of the section uses: zero strict label overlaps across the three reviewer-worked buildings and the full 1-12 storey x 6-16 ft sweep, labels never dropped, drawing kept inside A4 (widening only with legal lines, capped, no clip/move of the stack), benchmark and default outputs byte-identical to round 1, and the mutation proof reproduced. A1 and A2 are advisory and non-blocking.

WHAT I DID NOT CHECK (scope/environment): no pixel raster (no rasterizer installed - I verified label geometry with the kit's own helpers, the same basis as the test and the round-1 reviewer, and byte-matched the producer's SVGs to my renders); did not re-run the full kit folder (507->511) or api/vitest/e2e (brief item 5 scopes me to this commit's focused tests; CI confirms green at the integrated head); typography F2 (8.0 vs 8.5 pt printed label size) and the "schematic, not to scale" sheet label F3 are the wiring part's (brief item 4: UNKNOWN AND STAYING UNKNOWN) and remain open integration items for part W/B3, not defects in this delta. Full D-094 requirement re-derivation is the directive-compliance-verifier's pass, not this visual gate.

END-OF-REPORT

## G3 (code-reviewer)

VERDICT: PASS

# Gate Report

- Gate ID: G3 (code review)
- Task ID: M5-T192 (part B2 of M5-T173 — floor-stack section height-limit lines)
- Reviewer: code-reviewer (AI agent; not a human or professional review)
- Producer: backend-engineer
- Result: PASS
- Reviewed commit: 7d03dd8a71836837151a28e46799167191fe5f47 (worktree HEAD confirmed = 7d03dd8a, clean)
- Clean environment/worktree used: ran read-only in the builder worktree /root/project/nyc-buildability/.claude/worktrees/agent-a8940a6a78e64038a at 7d03dd8a with PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider (the read-only guard blocks shell file-writes, so I could not `tar -x` an archive; I verified the worktree HEAD is the frozen commit and ran against it; multi-file pytest under flock /root/project/lanes-runtime/heavy-run.lock).

## Acceptance criteria reviewed
- S1 byte-identical without results / legal_lines=None — VERIFIED. Independently confirmed render_floor_stack(alt, env=ON).svg == draw_floor_stack(alt, caption=False).svg == draw_floor_stack(alt, caption=False, legal_lines=None).svg for the benchmark alternative; code path (section.py:103-112,160,178) reduces to the pre-task code when lines==(): k=_STACK_H/max_top, grade_y=44+300, empty legal loop, min-base guard `and not False`. 507 kit tests pass with the 88 report-frame/rework tests unedited.
- S2 three standard lines, tops kept, compact, one line at 30 — VERIFIED. Independent render: three legal labels "Minimum base height 30 ft", "Maximum base height 45 ft", "Maximum building height 55 ft"; storey tops 10/20/30 kept; dims 360x238 (caption off) and 360x256 (caption on), both <=260 pt tall and <=515.9 wide; exactly 3 dashed lines (dasharray "4.00 2.00") and 0 bare floor_stack_min_base label → one line carries the 30 ft value.
- S3 drop-states — VERIFIED. 12 parametrized states + single-bad-key + reader-returns all pass; reader returns None / drops the offending key only.
- S4 envelope_rows never a line — VERIFIED. Reader reads only answers.permitted_envelope.values; the 40/60 ft values in envelope_rows never appear.
- S5 1.4.0 document identical — VERIFIED (no available permitted_envelope → None → byte-identical).

## Directive/requirement verification
In-regime task (directive_refs D-094 R017/R021/R043/R076/R208). The authoritative pass is the independent directive-compliance-verifier's; the table below is my code-review-level reproduction at 7d03dd8a. None of the cited requirements is violated by this commit.

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-094-R208 (compact section showing relevant levels and heights from the result) | 7d03dd8a | PASS | The section now draws the document's three standard height limits read from answers.permitted_envelope in a compact (<=260 pt) layout; values are the document's own, not computed. |
| D-094-R017 (yard/setback drawn only when geometry+basis established) | 7d03dd8a | PASS (respected by omission) | No yard/setback/street-wall geometry drawn; reader explicitly ignores envelope_rows (S4). Only horizontal height reference lines from permitted_envelope. |
| D-094-R021 (keep compact schematic, no placement, until calculated placement exists) | 7d03dd8a | PASS (contributing) | Caption "Drawn from the floor schedule; no placement on the lot." kept; no footprint/placement added. The "schematic/not to scale" label is the report-frame/B3 responsibility (contract page 4). |
| D-094-R043 (finish one meaningful spatial example) | 7d03dd8a | PASS (partial contribution) | M5-T173-wide obligation; B2 supplies the section's legal levels/heights only; incomplete state preserved elsewhere. |
| D-094-R076 (building diagram shows more than stacked floors, status-labelled) | 7d03dd8a | PASS (partial contribution) | Footprint/placement/circulation belong to other parts (W/B3); B2 adds the legal height lines to the section and claims nothing about placement. |

## Steps independently executed (commands reproducible from services/api in the worktree at 7d03dd8a; venv /root/project/lanes-runtime/venv)
1. ruff: `python -m ruff check app/drawings/kit/section_legal_lines.py app/drawings/kit/section.py app/drawings/kit/__init__.py` → "All checks passed!" (exit 0).
2. focused tests: `pytest -q -p no:cacheprovider tests/drawings/kit/test_section_legal_lines.py` → 22 passed (exit 0).
3. full kit regression (under flock): `pytest -q -p no:cacheprovider tests/drawings/kit` → 507 passed (exit 0).
4. `python tools/modularity_check.py --check` → exit 0; warn rows are all pre-existing out-of-scope files (maps/, rules/, scenario/, tools/); none of the three edited files is listed. Line counts: section_legal_lines.py 101, section.py 197, __init__.py 104.
5. Independent render/measure via python -c against the benchmark fixture (byte-identical, dims, qualifying-exclusion, dashed/bare counts, provenance, zero/duplicate edges).
6. D-093 grounding read: real-lot.json row L3 (lines 289-291,300) = standard min base 30 / max base 45 / max building 55 ft, source-backed by return-independent-hand-calculation-1.md Task 1(d) (line 304); benchmark answers.permitted_envelope carries exactly 30/45/55 (standard keys) with unit feet, labels, zr ["ZR 23-432"]; qualifying keys (incl. 65 ft) present but excluded by STANDARD_HEIGHT_KEYS.

## Expected versus actual
- Expected heights 30/45/55 from the document only → actual: exactly those, each with a /answers/permitted_envelope/values/<i>/value RFC6901 pointer that resolves to the printed number (test_s2_every_line_number...). Nothing computed/hard-coded in the renderer.
- Expected missing/malformed drops the line, never defaults to 0 → actual: reader drops and returns None when none survive; renderer never injects a value.
- Expected one line where min base coincides with building top → actual: 3 dashed lines, 0 bare min-base label.
- Expected qualifying 65 ft not drawn here → actual: excluded.

## Evidence paths
- Source: services/api/app/drawings/kit/section_legal_lines.py (new pure reader), section.py (draw_floor_stack legal_lines=; compact _LEGAL_STACK_TOP=24/_LEGAL_STACK_H=200; coincidence suppression section.py:159-185), __init__.py (render_floor_stack results=).
- Tests: services/api/tests/drawings/kit/test_section_legal_lines.py.
- Fixture: packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json (contract_version 1.5.0; alt[0] fill_rule to_min_base, tops 10/20/30).
- Grounding: docs/reference-cases/R6B/cases/real-lot.json row L3; answers.permitted_envelope standard keys.

## Human-style walkthrough findings
I rendered the section myself rather than trusting the producer's /tmp/claude-0/M5-T192/*.png. The three dashed limit lines stack above the building (30 at the building top, 45 mid, 55 near the canvas top at y=24); the top label baseline is y=17 (≈8 pt ascent → top of text ≈y9 > 0), so no top clipping; test overlapping_labels()==[] confirms no label collisions; legal-line labels sit at x=_STACK_X0 (right of the left-axis top labels). Labels are the document's own prose with the document number appended.

## Regression/security/provenance findings
- Regression: 88 report-frame/rework tests and the full 507-test kit suite pass unedited; default/caption paths byte-identical. No regression.
- Provenance: every drawn line carries its JSON pointer as data-source; the LegalLine keeps the document label + zr_sections; no number is typed by the renderer. Matches principle 2 and the owner's standard (missing stays missing; no claim of a permitted building; no rooms/units drawn).
- Scope/security: commit touches exactly the 5 allowed-path files; no forbidden path, no test_report_frame*.py, no fixture/record/register edit; no circular import (suite green).
- Modularity (7 boundaries): responsibility split clean (reader vs renderer vs facade); new 101-line module is the extraction, not growth of section.py; keyword-only optional args keep draw_floor_stack/render_floor_stack backward-compatible; boundary tests present; modularity_check --check exit 0; none of the files on a warn row.

## Defects
None blocking.

## Required rework
None for B2.

## Advisory items (non-blocking for this gate; flag forward to part W / visual-quality / integrated M5-T173)
1. ADVISORY — label size. Actual drawing-label size = TYPOGRAPHY.label_pt = 8.0 pt (section.py:118, styles.py:92), reused for the new legal-line labels. The ACTIVE presentation contract (docs/design/ARCHITECT_PRESENTATION_CONTRACT.md line 82, "Print type scale" 2026-10-11) requires drawing labels "at least 8.5 pt at the printed size"; the superseded older scale (line 98) said 7 pt, which is what the section docstring (line 15) and the test's MIN_LABEL_PT=7.0 still pin. B2 is in-spec because the packet objective says "at the existing label size" and 8.0 pt matches every other section label — B2 introduced no new/smaller size. Whether the PRINTED size meets 8.5 pt depends on part W's embed scale (explicitly UNKNOWN for this gate), so I cannot conclude a violation at B2. Correction owed at integration: part W / the visual-quality reviewer must verify the placed/printed label height >= 8.5 pt (or scale the section accordingly) and update the 7 pt note/MIN_LABEL_PT if the whole section is standardized.
2. ADVISORY — reader keeps value == 0.0 (section_legal_lines.py:_finite_non_negative uses `value >= 0.0`). A document value of 0 ft would be kept and drawn as "<label> 0 ft" at grade. This matches the packet's "finite non-negative" wording and is not reachable from the benchmark or a well-formed engine output, but a 0-ft height limit is never meaningful; consider `> 0.0` if the engine can never emit 0.
3. ADVISORY — reader does not dedupe by key. Two entries with the same standard key both become lines (verified: duplicate min_base_height → 2 lines at the same y with identical label → would overlap). Not reachable from a well-formed permitted_envelope (one entry per key); low risk.

## Reviewer conclusion
PASS. The commit is a faithful opt-in reader+renderer: heights come only from results.answers.permitted_envelope with per-value provenance, nothing computed or hard-coded, nothing from envelope_rows, qualifying keys excluded, missing/malformed dropped (never defaulted), the 30 ft coincidence collapsed to one line, compact layout <=260x515.9, and the default/legal_lines=None output byte-identical (507 kit tests + the 88 report-frame tests unedited). Ruff clean, modularity clean, scope clean, D-093 grounding confirmed in a source-backed reference case. The three advisory items are non-blocking for B2's G3; item 1 (printed label >= 8.5 pt) should be verified at the integrated/printed stage by part W and the visual-quality reviewer.

Not checked (out of scope / unverifiable here): the actual printed/placed size of the section in the report (part W/B3 — UNKNOWN by the brief), the scenario-sheet placement (B3), the full api pytest / vitest / e2e / real report print (CI at the integrated head), the producer's PNG image (I rendered independently), and the authoritative directive verification.json (owned by the directive-compliance-verifier).

END-OF-REPORT

## G4 (code-reviewer)

VERDICT: PASS

Gate: G3 (code) + G4 (tests) for the M5-T192 round-2 delta. I am an AI agent; this is not a human or professional review. Read-only; all work on scratch copies under /tmp/claude-0/M5T192-g3g4-codereviewer-7k2p9x (repo1=round1 d819f9f7, repo2=round2 883d9862); lanes venv /root/project/lanes-runtime/venv/bin/python; heavy runs under flock heavy-run.lock.

== SCOPE CONFIRMED ==
Worktree HEAD = 883d9862 (verified). Delta d819f9f7..883d9862 touches ONLY:
- services/api/app/drawings/kit/section.py (+35/-3)
- services/api/tests/drawings/kit/test_section_legal_lines.py (+76)
- project-control/reports/M5-T192-producer-report.md (+59)
section_legal_lines.py and kit/__init__.py are byte-identical (LF) across round 1 and round 2 (diff empty). Matches the brief's "only section.py, the test file and the producer report changed in round 2."

== WHAT I VERIFIED (reproducible) ==
1. Focused tests on the round-2 scratch copy (cwd services/api, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider):
   - `ruff check .` -> All checks passed
   - `pytest -q tests/drawings/kit/test_section_legal_lines.py` -> 26 passed (22 round-1 + 4 new F1)
   - `flock heavy-run.lock pytest -q tests/drawings/kit` -> 511 passed in 26.5s
   - `tools/modularity_check.py --check` (run in the worktree; scratch isn't a git repo) -> exit 0; NO delta file appears in any warn row (warnings are pre-existing on unrelated files: site_context_plan.py, integration.py, breakeven.py, max_envelope.py, result_ways.py, three_way_document.py, cli.py, codex_reviewer.py). section.py is 226 lines; the +29 net lines stay inside draw_floor_stack's existing responsibility (placing its own labels, sizing its own canvas) — no new responsibility mixing.

2. Byte-identity to round 1 (rendered benchmark fixture recorded_215_16_northern_journey.json in each head, compared sha256 of the SVG string):
   - benchmark WITH legal lines: sha 6c5d5d43... identical r1==r2, width 360 height 238
   - legal_lines=None / default: sha ab3a30c1... identical r1==r2, width 360 height 358
   Confirms "benchmark output and legal_lines=None output byte-identical to round 1."

3. Three reviewer worked cases (fill_envelope, drawn with the benchmark's own 30/45/55 ft limits): 4x10, 5x11, 7x10 ft -> overlapping_labels == [] for all three; widths 360/360/432 (<=515.9), height 238 (<=260), min font 8.0pt (>=7), exactly 3 legal labels each, every label's data-source resolves to the printed number, no label clipped. Labels never dropped.

4. Mutation reproduced via the literal pre-fix commit (round 1 = the single-candidate `[(_STACK_X0, y-7.0, 0.0)]` placement this delta replaced). Running round 1 WITH legal lines reproduces the EXACT F1 finding:
   - 4x10: [('Storey 4','Minimum base height 30 ft'),('10 ft','Minimum base height 30 ft')]
   - 5x11: [('Storey 5','Maximum base height 45 ft'),('11 ft','Maximum base height 45 ft')]
   - 7x10: [('Storey 4','Minimum base height 30 ft'),('10 ft','Minimum base height 30 ft')]
   i.e. the legal label over the storey label AND its floor-to-floor label — precisely the reviewer's F1 defect. Round 2 drives all three to 0. Under the mutation the benchmark stays byte-identical (candidate 0, x=150, width 360), so the benchmark-keeps-candidate-0 test stays green — matching the producer report's mutation claim.

5. Canvas widening: stack bands always use fixed x 150/300 regardless of canvas width (e.g. 7x10 band d = "M150.00 .. L300.00 .."), so widening never moves the stack. width = min(515.9, max(360, max_label_box.x1 + 6.0)). The widest label box.x1 is 445.2 — fixed by the longest standard label ("Maximum building height 55 ft", 29 chars x 8pt x 0.6 char_width_em) at the fixed gutter x=306 — so the 515.9 cap is NEVER reached and the three standard labels can never be clipped at any storey count. Only active when legal lines are present (else width is the fixed 360).

6. Realistic-domain sweep (1-10 storeys x ff 8-14 ft, WITH legal lines): 0 overlaps everywhere. Up to 20 storeys @8ft: 0 overlaps. Round 2 is strictly >= round 1 at every storey count (round 1 overlapped across the ENTIRE realistic range — 46 of 70 combos — and worse at tall counts).

== FINDINGS ==
F1 (ADVISORY, section.py ~line 165-186 and producer report line 49): the code comment and producer report state the legal-line label "is never dropped and never overlaps." The first half is true (it is always drawn). The "never overlaps" half is an over-statement: `first_free` (labels.py) returns the LAST candidate when all 7 candidates collide, so overlaps reappear for buildings of >=22 storeys (disconfirming sweep: 22x8ft -> 3 overlaps, 24x8ft -> 48, 30x8ft -> 63). These are physically impossible R6B inputs — a building 3-6x taller than its own 55 ft maximum-building legal line — and (a) never occur for a worked building that fits its envelope (building height <= max building height), and (b) are NOT a regression: round 1 overlapped at those counts too and worse (22x8ft: 9 vs 3). The base section's own storey/ff labels never overlap even at 30 storeys (default render: 0 overlaps), so this is purely the gutter/storey-label crowding at impossible densities. Non-blocking. Optional correction: qualify the comment to "collision-free for any worked building that fits its envelope" rather than an absolute "never overlaps."

No REQUIRED findings. Every brief scenario is satisfied: reviewer worked buildings collision-free; realistic sweep collision-free; benchmark + None byte-identical to round 1; widening capped at 515.9 and never clips or moves the stack; labels never dropped; mutation reproduces the exact overlaps.

== NOT CHECKED (out of this gate's depth) ==
- Full services/api pytest, vitest/e2e, and the real report print — CI's and part W's job at the integrated head (brief point 5; renderer-level gate only).
- PNG rasterization/visual look — no SVG->PNG converter in the api venv; this is the separate G3-visual role. I verified label geometry/overlap with the SAME text-box math the tests and placement use (authoritative), not by eye.
- Independent verification of the 30/45/55 ft legal VALUES against primary ZR 23-432 sources — unchanged by this delta (round 1 already drew them; this delta only moves labels); out of scope.
- Printed label point size (8.0 vs 8.5) and the 'schematic, not to scale' label — explicitly the wiring part per the brief (point 4), not this delta.

END-OF-REPORT

## G4 (qa-engineer)

VERDICT: PASS (G4 / qa-engineer) for M5-T192 at commit 7d03dd8a71836837151a28e46799167191fe5f47.

I am an AI agent; this is an independent, read-only engineering gate, not a human or professional review. I reviewed exactly the committed content: the LF sha256 of all four code/test files equals the builder's reported digests (section_legal_lines.py 4cd0418f, section.py 77a68418, __init__.py dc52e287, test file 213e318c), and my scratch copy's restored files match the git blobs byte-for-byte, so the test runs below ran on genuine committed source.

WHAT I RAN (lanes venv /root/project/lanes-runtime/venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider, scratch copy /tmp/claude-0/qa-g4/repo; multi-file run under flock heavy-run.lock):
- ruff check on the 4 files -> All checks passed!
- pytest tests/drawings/kit/test_section_legal_lines.py -> 22 passed (0.35s)
- pytest tests/drawings/kit (full) -> 507 passed (26.75s); includes the 88 report-frame/rework tests UNEDITED (diff touches no test_report_frame*.py)
- scope: git diff --name-status b9e9d563..7d03dd8a = exactly the 5 allowed_paths files, zero forbidden paths

CLAIMED MUTATIONS — all reproduced (each applied to scratch, run, reverted; pristine restored and digest-verified):
1. render ignores results (force legal_lines=None in __init__.py): 3 S2 tests FAIL, 19 reader tests PASS. Matches claim.
2. remove coincidence suppression (drop `and not coincides_with_min_base_top` in section.py): test_s2_one_line_where_the_minimum_base_coincides FAILS (bare "Minimum base height" reappears). test_s2_benchmark_draws_the_three_standard_height_lines ALSO fails (overlap/4th line) — broader catch than the builder claimed, not narrower.
3. remove reader unit=='feet' guard: S3[unit is not feet] FAILS. Matches.
4. remove reader finite/non-negative guard: S3[NaN], [+inf], [negative], [a string], [a boolean] and test_s3_a_single_bad_key_drops_only_that_line all FAIL. Matches.
Conclusion: the tests are not vacuous; each guard is pinned by at least one failing assertion.

INDEPENDENT RENDER of benchmark Building B (results=doc), measured from my own SVG (not the builder's picture):
- width=360.0 pt, height=238.0 pt -> within 515.9 x 260. 
- 3 dashed reference lines (dasharray "4.00 2.00"); legal labels "Minimum base height 30 ft", "Maximum base height 45 ft", "Maximum building height 55 ft", each data-source=/answers/permitted_envelope/values/{0,1,2}/value (provenance intact).
- no bare floor_stack_min_base label (coincidence suppression works); the 30 ft line sits at the grade-nearest y (114.91) and is the only dashed line there.
- storey tops 10/20/30 ft kept; min font-size over all labels = 8.0 pt; the qualifying 65 ft value appears nowhere in the SVG (risk 2 satisfied).

D-093 GROUNDING (verified against source, not a program run): the 30/45/55 ft literals in the test are grounded in docs/reference-cases/R6B/cases/real-lot.json row L3 (lines 289-291, 300: min base 30 / max base 45 / max building 55 ft, ZR 23-432, R6B row carries no footnote so wide/narrow unchanged) and the zr-23-432 snapshot cited there. The benchmark fixture carries exactly these in answers.permitted_envelope (status available). Correct and independent.

DISCONFIRMING CHECK — input states the builder did NOT test (exercised against the pristine reader; all handled correctly):
- answers is a list (non-Mapping) -> None
- permitted_envelope is a list (non-Mapping) -> None
- values is an EMPTY list -> None (never a default)
- label is None -> None; label key missing -> None; unit key missing -> None
All robustly dropped. No defect found in these.

ADVISORY items (none blocks the G4 verdict):
A1 [ADVISORY] Drawing label size vs presentation contract. The renderer emits labels at TYPOGRAPHY.label_pt = 8.0 pt (section.py:118; styles.py:92). docs/design/ARCHITECT_PRESENTATION_CONTRACT.md line 82 (R047/R048 print type scale) and line 258 require "drawing labels at least 8.5 pt at the printed / final displayed size". The 8.0 pt is the section's long-standing size for EVERY label (grade/storey/top/ff and the pre-existing min-base line) and is NOT changed by this task — the new legal lines just inherit it. Whether the final printed label is >= 8.5 pt depends on the part-W / B3 embedding scale of the section on the scenario sheet, which is explicitly out of this packet's scope and UNKNOWN to me. This is a visual-quality-reviewer (G3) / part-W determination at the embedded scale, not a G4 test-correctness defect. The task's own scenario S2 requires only >= 7 pt and passes. Flagging so the visual reviewer verifies label size at the real printed scale and so part W does not place the section at <1:1.
A2 [ADVISORY] section_legal_lines.py:48-54,81 — a GENUINE value == 0.0 passes the finite/non-negative guard (value >= 0.0) and would draw a line at grade. Spec-compliant ("each a finite non-negative number"); the "never 0" requirement is about not defaulting a MISSING value to 0, which is satisfied. Real R6B heights are never 0, so no real-world impact; only noted as a boundary behavior.
A3 [ADVISORY] section_legal_lines.py:72-96 — duplicate standard keys are not de-duplicated; two identical entries would draw two overlapping identical lines. Real documents / the results schema do not carry duplicate keys, so no real-world impact.

NOT CHECKED / LIMITATIONS:
- tools/modularity_check.py could not run in my sandbox (the git-archive extraction is not a git repo; the check needs `git ls-files`). The files are small and cleanly separated (section_legal_lines.py 101 lines pure reader; section.py 197 lines renderer; __init__.py 104 lines wiring) — well within bounds; the builder reported exit 0 and the orchestrator can confirm from the committed tree.
- How part B3 (scenario sheet) and part W (wiring) place/scale the section, and whether the qualifying 65 ft is ever drawn elsewhere — explicitly out of scope / UNKNOWN per the brief.
- The real report-print path, full api pytest, vitest/e2e and CI green are part W's / CI's job at the integrated head, not this renderer-level gate.
- The directive-compliance (D-094 R017/R021/R043/R076/R208) independent re-derivation is the directive-compliance-verifier's pass, not mine.

Net: tests are correct, reproducible and mutation-proof; scope and provenance are clean; the reader is robust against the extra states I added; no 65 ft leak; byte-identical default confirmed by the 507-test suite and by code reading of the None path. The only open items are ADVISORY and belong to the visual-quality-reviewer / part W, chiefly A1 (8.0 pt vs the contract's 8.5 pt at printed scale).

END-OF-REPORT
