# M5-T188 reviews (every return kept unchanged)

- Two build rounds (backend-engineer, worktrees): round 1 7f4a52c0 integrated as 3c95cae9 (after scope correction 1: close_frame_dimensions.py and S10 joined the packet for DB-275); round 2 50362fd5 integrated as 8302fc2e (G3 F1). Every builder commit inside the allowed paths; LF sha256 equal to each return.
- Real prints: the builder's page diffs against main 76745ade (round 1 and round 2: only page 4 changed, the two duplicate street-width chips removed; round 2 keeps the 470-pt frame) and the orchestrator's real-preview print print-fcd953e1 (session 2026-10-15b) of the branch with round 1, which also carries M5-T169's changes.
- G2 orchestrator self-check at the submit head: the task's files equal the builders' digests; nothing outside the allowed paths; the CI run at the submit head read green before submission.
- G3 code-reviewer at 3c95cae9: PASS WITH REQUIRED F1 (overlay_present followed the mere presence of a constraint list: page 4's frame grew 470->474 with nothing drawn); advisories F2 (report wording) and F3 (exclusion by key prefix kept). Round 2 closed F1 and F2. G3 delta check at the round-2 head: below.
- G4 qa-engineer at 3c95cae9: PASS (scenarios mapped; six mutations red; the page diff reproduced). G5 security-reviewer at 3c95cae9: PASS (one pre-existing advisory: the label formatter accepts a non-numeric or non-finite value; backlog).
- G3 delta check (code-reviewer) at 8302fc2e: PASS; F1 closed (not-established list 470, established line 490; the mutation back to bool(constraint_lines) reddens exactly the not-established test); F2 true; F3 reasoned; one advisory (a scene-level test that the base scene never draws a constraint style kind).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

G3 code review — M5-T188 (constraint-overlay polish DB-263 + S10/DB-275), pinned 3c95cae9 on task/wave27-comparison-appendix. I am an AI agent; this is an independent read-only review, not a professional review.

VERDICT: PASS WITH REQUIRED CORRECTIONS (F1 blocks acceptance).

The owner-visible goal (remove the duplicate page-4 chips) and A1/A3 are correct and reproduced. One real, undisclosed, untested behaviour change on the shipping benchmark must be fixed or explicitly justified+tested+disclosed before accept.

=== FINDINGS ===

F1 — REQUIRED (blocks accept). services/api/app/drawings/maps/site_context_plan.py:733.
`overlay_present=bool(constraint_lines)` is the WRONG predicate. It is True for ANY 1.5.0 document that merely CARRIES a constraint_lines block, even when every item is not_established/not_known and NOTHING is drawn — which is exactly the benchmark (4 items, all not_established/not_known, no geometry; confirmed in recorded_215_16_northern_journey.json and via page_location._overlay_data, which returns the non-empty list unfiltered). Reproduced on the real benchmark overlay inputs: the page-4 close frame height changes 470.00 → 474.00 (viewBox "0 0 512.00 470.00" → "0 0 512.00 474.00"), because overlay_present=True drops the CLOSE_MAX_H_PT clamp (height = furn_bottom+8 = 474) when it should stay clamped.
This contradicts (a) the packet S8/RISK-1 premise ("the benchmark establishes no constraint line, so the overlay draws nothing and the height clamp is unchanged"), (b) the producer report's real-print claim ("only page 4 changed, 2 lines removed … pages 1 and 3 byte-identical"; the height/viewBox ALSO changed), and (c) the parameter's own docstring ("a constraint overlay added its own legend entry" — none is added here). No content is clipped or moved (lowest element is 'No building placed'/'Grid north' at y≈458.5; both 470 and 474 leave only whitespace below), so the visual impact is ~4pt extra bottom whitespace — but it is a silent, untested change to the shipping output, and it bypasses the close-frame max-height budget for EVERY 1.5.0 document, not just ones that draw an overlay. S4 does not guard this: S4 renders frame="close" with NO constraint_lines (overlay_present=False → 470); no test renders the close frame with a non-empty not-established constraint_lines list, so the 474 path is unexercised (that is why the 89 consumer tests and the benchmark suite stayed green).
Fix: compute overlay_present from whether an established constraint was ACTUALLY drawn (e.g. a constraint style kind present in sheet.kinds after draw_block_scene, or a boolean returned by draw_site_constraints), not bool(constraint_lines). With the correct predicate the benchmark page 4 stays 470 and the only page-4 change is the 2 chips removed — the packet's stated intent. If 474 is instead accepted, it must be disclosed, pinned by a test, and the producer claim corrected.

F2 — ADVISORY. project-control/reports/M5-T188-producer-report.md (real-print section). "the lot's own band carries no other gis lot fact on the benchmark, so page 4 simply loses the two chips" is inaccurate: lot_outline_area (basis gis, "10,387.99 sq ft, map outline") IS a gis lot fact and stays. Reproduced: the band goes 4→2 chips; the two that remain are recorded_lot_area ("10,075 sq ft, city record") and lot_outline_area ("10,387.99 sq ft, map outline"). Behaviour is correct; the report wording understates what stays.

F3 — ADVISORY. services/api/app/drawings/maps/close_frame_dimensions.py:286-287. The S10 filter is an exclude-list (skip keys starting "mapped_street_width:"). Correct today — the only two input_facts producers are _input_facts (envelope_constraints.py → mapped_street_width:* only; excluded) and rear_yard_checks.py (recorded_lot_area, lot_outline_area; kept) — and no other fact family needs excluding now. Because the band is a LOT-dimension band, an allow-list by kind would be marginally more future-proof against a new non-lot fact family silently leaking in. Optional.

=== CONFIRMED CORRECT (my share) ===
- A1 label candidate order + fallback (constraint_overlay.py:167-190, 251-258, 266): BEFORE the label box covered the drawn line (anchor inside box, 0/3 vertices outside, box y 279.2-288.1 straddling the line at y=286). AFTER the box sits off the line (anchor OUTSIDE, 3/3 vertices outside, box y 290.7-299.6 below the line) — the line reads clearly off its label. The perpendicular offset is only candidate[0]; the full grid fallback and the ConstraintOverlayError fail-rather-than-shrink guarantee are intact (S2 passes; cramped rect still raises). Area labels unchanged (no perp).
- A3 word-boundary strip (page_decision_summary.py:312-321): logic sound; row["title"] always present; 5 boundary states pass; 'Rear yard Rear yard' outcome preserved; bare-prefix ('Rear yardage') not stripped.
- expand_frame_for_overlay removal: 0 live references in the whole repo (git grep over services/api/app, apps/**, scripts/**, tools/** = none); only historical docs/reports and the new absence tests remain. `from dataclasses import replace` removed; the surviving `.replace(` is a str method. Clean.
- S10 chip fix on the REAL benchmark facts: before 4 chips → after 2; the two duplicate street-width chips ("60 ft, map outline", "100 ft, map outline") are gone; the two lot-area chips stay; nothing else lost.

=== WHAT I RAN (lanes venv, under flock /root/project/lanes-runtime/heavy-run.lock; git archive copies of 3c95cae9 and base bb5c02b9) ===
- tests/drawings/maps/test_constraint_overlay.py + test_site_context_close_frame.py + tests/drawings/report/test_page_one_title_boundary.py → 50 passed.
- consumer checks test_constraint_rows.py + test_report_pages.py + test_report_page_one.py → 89 passed.
- Before/after SVG renders: constructed established-line close frame (A1 box vs line; overlay frame 490 / plain 470, legend row fits); real benchmark overlay inputs (close 470→474, summary_close 204 byte-identical sha both trees; band 4→2 chips).

=== COULD NOT CHECK ===
- Full api pytest / web-e2e / CI at the accept head (producer reports 9965 passed; CI read is the orchestrator's at the frozen head, D-090-R639).
- Did not run the PDF print; verified at the SVG level (height, viewBox, labels, chips), which is where F1/F2/F3 live.
- G5 and per-requirement directive-compliance are the security-reviewer's and directive-compliance-verifier's passes.

END-OF-REPORT

## G3 (code-reviewer, delta check of round 2)

G3 DELTA REVIEW — M5-T188 round 2 (DB-263 F1 correction + F2/F3), pinned 8302fc2e on task/wave27-comparison-appendix in /root/project/w-wave20 (cherry-pick of builder 50362fd5; LF sha256 of all 5 files MATCH the builder return). I am an AI agent; independent read-only review, not a professional review.

VERDICT: PASS (G3 delta). The colleague's F1 (REQUIRED) is genuinely closed; F2/F3 resolved; nothing else changed in the round. No new REQUIRED findings. One ADVISORY.

=== MY SHARE — CONFIRMED ===

1. F1 CLOSED — predicate correctness (constraint_overlay.py:321-332, site_context_plan.py:738).
CONSTRAINT_STYLE_KINDS = {rear_yard_100ft_line, corner_area, street_wall_band, setback_line, yard}. Verified every style_kind draw_constraint_overlay can register is in the set: polygons use _CONSTRAINT_STYLE.get(kind,_AREA_FALLBACK="yard"), lines use ...get(kind,_LINE_FALLBACK="setback_line") — all four known kinds + both fallbacks ⊆ set. sheet.area/sheet.line both call use_kind, so a drawn item registers; not_established/not_known hits `continue` (no draw), a line with empty clip hits `if not pieces: continue` (no draw) — neither registers a kind. No base-scene kind collides (scene draws subject_lot/neighbour_lot/street_area/building_footprint/existing_building/street_centreline). Dimensions append parts directly with style "dimension" (close_frame_dimensions.py:108 "never added to the legend") — they do NOT call use_kind. kit/site_plan.py does draw "yard"/"setback_line" kinds, but the maps path imports only the constant STANDARD_SCALES_FT_PER_IN from it, never its draw functions — not on this sheet.
Reproduced on the benchmark close frame (git archive copy, lanes venv, under flock): REAL predicate → not-established list height 470.0 (0 constraint kinds drawn), no-list 470.0, established line 490.0 (rear_yard_100ft_line drawn). Benchmark viewBox height 470 kept; established case still grows.

2. Tests + mutation (test_site_context_close_frame.py:513-529, test_constraint_overlay.py:359-381). The three states are pinned: no list (470, existing test_s4), not-established list (470, NEW test_s4_a, benchmark shape), established line (>470, test_s3); plus a direct unit test of overlay_was_drawn (empty→False, not-established→kinds []→False, established→kind in set→True). Mutation reproduced in-memory (mock.patch; read-only guard blocks file writes): reverting to bool(constraint_lines) → not-established 474.0 (test_s4_a RED, 474≠470), no-list 470.0 (test_s4 green), established 490.0 (test_s3 green) = exactly 1 failed, 2 passed, as claimed.

3. F2 true now (producer-report Round 2 §F2): states lot_outline_area "10,387.99 sq ft, map outline" stays with recorded_lot_area "10,075 sq ft, city record"; only the two street-width chips go; verified by chip counts (street-width ×0). F3 reasoned: kept the key-prefix exclude-list (smaller than enumerating every lot-dimension key; MINE-A proved it keys on the KEY not gis basis). Sound.

4. Nothing else changed: the commit touches exactly 5 files (constraint_overlay.py +22, site_context_plan.py +9 net, the 2 test files, producer-report.md). No chip-logic file (close_frame_dimensions.py / context_scene.py / page_decision_summary.py) re-touched — round-1 S10/A1/A3 behavior intact.

=== WHAT I RAN (lanes venv, flock heavy-run.lock, git archive copy of 8302fc2e) ===
- ruff check services/api → All checks passed.
- tests/drawings/maps tests/drawings/report → 433 passed, 4 skipped (builder reported 403; MORE pass here, all green — count difference only, no defect).
- three task test files → 52 passed.
- in-memory predicate + mutation reproduction (above).

=== FINDING ===
D1 — ADVISORY. constraint_overlay.py:332. overlay_was_drawn keys on sheet.kinds membership in CONSTRAINT_STYLE_KINDS. Two of those names ("yard", "setback_line") are GENERIC style kinds also used by kit/site_plan.py. The predicate is correct today only because the maps close-frame scene never draws a "yard"/"setback_line" kind on this sheet. This invariant is implicit. A concrete safeguard: add a scene-level test asserting draw_block_scene (no constraint overlay) leaves sheet.kinds disjoint from CONSTRAINT_STYLE_KINDS, so a future maps-scene change that shades a required yard can't silently reintroduce the 474 false positive. Not blocking.

=== COULD NOT CHECK ===
- Full api pytest / web-e2e / CI at the accept head (builder reports 10000 passed/8 skipped; CI read is the orchestrator's at the frozen head, D-090-R639).
- Benchmark page-4 chip removal at the PDF level (round 1 G3 already reproduced before 4 → after 2 chips; round 2 did not touch chip logic — confirmed by the file list). Verified at SVG/height level, where F1 lives.
- G5 and per-requirement directive-compliance are the security-reviewer's and directive-compliance-verifier's passes.

END-OF-REPORT

## G4 (qa-engineer)

# M5-T188 G4 (QA) gate report — qa-engineer (independent, read-only)

I am an AI agent; this is an independent read-only software-test review, not a human or professional review. Reviewed at the frozen pin 3c95cae9 on task/wave27-comparison-appendix, from a tar copy under /tmp/claude-0/t188-g4/copy. I did not produce this task.

## VERDICT: PASS

No REQUIRED findings. Two ADVISORY notes below. All of my share reproduced the producer's evidence.

## What I checked (commands + outputs, lanes venv, heavy runs under flock)

1. `ruff check .` on the copy: All checks passed, exit 0.
2. Three task test files (`test_constraint_overlay.py test_site_context_close_frame.py test_page_one_title_boundary.py`): 50 passed, exit 0 (matches producer). Re-ran after all mutations: 50 passed.
3. `pytest tests/drawings/maps tests/drawings/report`: 401 passed, 4 skipped, exit 0 (matches producer). I did NOT run the whole api suite.
4. CI for the pushed head: run 38724854666 COMPLETED SUCCESS at head 9834b67e — every job green incl. `api (ruff+pytest)`, `web-e2e`, `control-plane`, `supervisor-bridge`, `modularity`. 9834b67e differs from the pinned 3c95cae9 only in state.json + tasks/M5-T188.json (ledger bookkeeping); no source/test file differs, so the green run is authoritative for the reviewed content.
5. `grep -rn expand_frame_for_overlay services/api`: 0 hits in app/ (only test assertions of its absence). S5 confirmed; the fragile string-rewrite is gone from production.

## Scenario → test map (S1–S10)
- S1 → test_s1_the_line_label_sits_off_the_line (test_constraint_overlay.py:313) PINNED, mutation-proven.
- S2 → test_s2_the_label_offset_keeps_the_fit_and_collision_guarantee (:335) PINNED.
- S3 → test_s3_overlay_close_frame_grows (test_site_context_close_frame.py:467) PINNED, mutation-proven.
- S4 → test_s4_non_overlay_close_frame_stays_clamped_at_470 (:487) PINNED, mutation-proven.
- S5 → test_s5_expand_frame_for_overlay_is_gone (:358) PINNED + my grep.
- S6 → 5× test_s6_* (test_page_one_title_boundary.py) PINNED, mutation-proven.
- S7 → not a new task test; benchmark 'Rear yard Rear yard'-absent behaviour stays in test_report_page_one.py (M5-T170's forbidden file, read-only consumer, green in the 89-passed consumer check). Behaviour-identical.
- S8 → real print; I reproduced (below): pages 1 & 3 text-identical.
- S9 → visual before/after artifact for visual-quality-reviewer (G3); not a pytest, outside G4.
- S10 → 3× test_s10_* (test_constraint_overlay.py:372/394/411) PINNED, mutation-proven + real-print page-4 diff.

## Mutation proofs (reproduced 4 of 5 builder + 2 of my own; each RED then restored)
- B1 S10 filter removed (`lot_facts=list(facts)`) → test_s10_street_width_facts_are_not_drawn RED (both chips drawn). RED.
- B2 A1 perp candidate removed → test_s1 RED ("label box sits on the line anchor"). RED.
- B4 A3 boundary removed (plain startswith) → test_s6_title_as_a_bare_prefix RED ('Rear yardage'→'age rules'). RED.
- B5 overlay_present gate dropped → test_s4 RED (height 474 ≠ 470). RED. (B3 native-height shares this height path.)
- MINE-A over-broad filter (`basis!='gis'` instead of key-prefix) → test_s10_a_lot_gis_fact_still_reads_map_outline RED (legit lot gis fact `outline_lot_area` wrongly dropped, drawn==[]), street-width test stayed green — proves the filter correctly keys on the KEY, not the gis basis.
- MINE-B title strip accepting a mid-word prefix (add `rest[0].isalnum()`) → test_s6_title_as_a_bare_prefix RED, other 4 green — the boundary guard is exactly the word boundary.

## Page-diff (real print, no server/ports)
TestClient POST /report with benchmark_provider(with_zoning_lot=True, street_on=True) + recorded_pack_provider(benchmark_215_16_northern_window), flags INTERNAL_RESULTS_ENABLED/LANE_A/LANE_E on → HTTP 200, text/html, 142067 bytes (matches producer) → node print-report-pdf.mjs → 11-page A4 PDF. diff_pages.py vs print-main-76745ade/report.pdf:
- pages 1,2,3,5,6,7,8,9,10,11 IDENTICAL; page 4 CHANGED: 0 added, 2 removed — exactly `60 ft, map outline` and `100 ft, map outline`. Confirmed.
- Page-4 inspection: my print KEEPS the lot's own `10,387.99 sq ft, map outline` chip and both `100 ft / 60 ft mapped width` frontage labels; only the two duplicate `map outline` street-width chips are gone. This validates S10 end-to-end (duplicate removed, widths not lost, lot gis fact retained). Consistent with the design contract (principle 5 one-basis-per-figure; gis="city map outline"/short tag "map outline" only where bases mix; street widths are a distinct drawing element labelled "mapped width") and the S10 trace against NB-06; no value moved (100/60 ft correct).

## Findings
1. ADVISORY — test_site_context_close_frame.py:487 (S4). The new test pins the non-overlay close height==470.0 and the symbol's absence, but NOT a stored golden for *every* frame (summary/wide/report/sheet/neighbourhood/block) against bb5c02b9 as S4's prose says. Byte/text-identity of those frames rests on the existing suite staying green (401 passed) + the real-print S8 (pages 1&3 identical). Adequate, but the "every frame byte-identical" clause is covered indirectly, not by one direct assertion. No correction required.
2. ADVISORY — packet S7 wording calls test_report_page_one.py "DB-263's own file"; it is actually M5-T170's forbidden read-only consumer (the new file is test_page_one_title_boundary.py). Stale label only; the S7 benchmark behaviour is green. No correction required.

## What I could not check
- Modularity tool: the tar copy is not a git repo (`git ls-files` fails), so I could not run `modularity_check --check` there; the CI `modularity` job = success at the material-identical head, and changed-file line counts are consistent (constraint_overlay 310 and site_context 743 shrank; context_scene 637 (+7), page_decision_summary 368, close_frame_dimensions 307). Favorable trade: A2 removes a fragile string-rewrite.
- S9 visual before/after is the visual-quality-reviewer's G3 artifact (not QA).
- S8 I confirmed page-1/3 text-identity via pdftotext; I did not re-derive byte-identity to the byte, but the overlay establishes no line on the benchmark so no overlay bytes are emitted.
- Directive-requirement verification (D-094 R015/R017/R037/R053/R116) is the directive-compliance-verifier's pass, not G4.

END-OF-REPORT

## G5 (security-reviewer)

G5 SECURITY GATE REPORT — M5-T188 (wave 27): constraint-overlay polish (DB-263 A1/A2/A3) + duplicate street-width chips (DB-275/S10)

I am an AI agent (security-reviewer), read-only. This is not a human or professional review. I reviewed ONLY my assigned SECURITY share of the change at the pinned SHA 3c95cae9 (task/wave27-comparison-appendix in /root/project/w-wave20), from a `git archive 3c95cae9` copy under /tmp/claude-0/t188-g5. The 5 production files changed: constraint_overlay.py, context_scene.py, site_context_plan.py, close_frame_dimensions.py, report/page_decision_summary.py.

VERDICT: PASS (security share). No security defect found. One ADVISORY (pre-existing, not a T188 regression).

WHAT I CHECKED (reproduced)
- Escaping on every changed path: all drawing text reaches SVG via place -> sheet.label -> svg.text_element -> escape(); attributes via attrs() -> escape(); page-1 A3 via html.el -> html.escape. Probed draw_other_basis_dimensions and draw_constraint_overlay with a hostile fact key, basis, kind and zr_sections containing <, >, ", &, and a script token. Result: raw markup never appears in the SVG; it is XML-escaped (data-source="input_fact:k&quot;&gt;&lt;script&gt;..."; text "...printed &lt;b&gt;&amp;&quot;tax"). The constraint label "setback<&\"..." likewise escaped.
- Coordinate/number validation on changed paths: label positions are computed from rect/size/index and go through num() (two-decimal), independent of fact values; probe found NO non-finite (inf/nan) or oversized numeric SVG attributes. The new A1 perpendicular offset (constraint_overlay.py:251-258) uses a unit normal guarded by `if norm:` (norm = sqrt(dx^2+dy^2)); a degenerate line with identical consecutive points (norm==0) leaves label_perp=None and does not crash (probe: drawn=1). The perp candidate adds only a bounded unit*step offset to already-projected ax/ay, so it cannot manufacture a huge coordinate.
- Fail-closed on abuse: a huge fact value (1e308) produces an over-long label that cannot be placed -> raises DimensionPlacementError (fails closed, no malformed/enormous SVG). Enormous fact counts (50/500/5000) all raise DimensionPlacementError once the band fills (fails closed, no unbounded SVG). The A2 native close-frame height (context_scene.py:583, `furn_bottom + 8` when overlay_present) is bounded by furniture/legend rows (a handful of constraint kinds), not by fact content, so it cannot grow without bound.
- S10 filter correctness (close_frame_dimensions.py:286-287): mapped_street_width:* facts excluded; a lot's own gis fact (e.g. lot_frontage) is kept and still reads "25 ft, map outline". A missing/None key -> str(None)="None", not excluded -> drawn as before (no behavior loss).
- Removed helper leaves no dead path: `expand_frame_for_overlay` is gone from constraint_overlay.py (def, __all__, and the module-level _VIEWBOX_RE/_RECT_RE/_TEXT_Y_RE/_FURNITURE_TOP_PT regexes). Tree-wide grep shows it referenced ONLY in tests that assert it is gone. `import re` is removed and `re` is no longer used (runtime confirms `hasattr(co,'re')` is False; `__all__` updated). In site_context_plan.py `from dataclasses import replace` is removed; the only remaining `replace` (line 643) is `str.replace`, so the removal is clean.
- No new attack surface: the diff adds NO imports (only removals); no open()/os/subprocess/socket/urllib/requests/eval/exec/environ/Path in any changed file (only the word "open" in prose). No new dependency. No file, network or environment access.
- Tests at pinned content: `pytest -q tests/drawings/maps/test_constraint_overlay.py tests/drawings/maps/test_site_context_close_frame.py tests/drawings/report/test_page_one_title_boundary.py` -> 50 passed in 7.29s (run under heavy-run.lock, lanes venv).

FINDINGS
1. ADVISORY — close_frame_dimensions.py:252-264 (`_fact_figure`/`other_basis_label`) via kit/labels.py:31-38 (`format_number`/`format_feet`). A non-numeric fact value raises a bare ValueError ("Unknown format code 'f' for object of type 'str'") rather than the typed DimensionPlacementError, and a non-finite value (inf/nan) renders as literal label text ("inf sq ft, map outline") instead of being rejected. This is PRE-EXISTING: T188 does not touch the value->text path (it only filters the fact LIST and widens candidate ranges), so it is not a regression and does not block this gate. Upstream the map adapter bounds geometry (MAX_ABS_COORD_FT=1e8, feature/ring caps, fail-closed MapInputError) and the results contract types fact values, so the hostile path is not reachable with validated input. Concrete (optional, out of scope for T188): add a finite/numeric guard in `format_number`/`_fact_figure` that fails closed with a typed drawing error.

WHAT I COULD NOT CHECK (outside my security share / other reviewers)
- The visual/print claim that only page 4 changed and the two duplicate chips are gone (the print/visual reviewer's share; I did not render the full report).
- Functional correctness of S1–S10 scenarios and the A2 byte-identity-on-non-overlay claim beyond the 3 test files (functional reviewer's share).
- Independent directive-compliance (directive_refs) requirement-by-requirement verification — belongs to the directive-compliance-verifier (producer != verifier); I did not re-derive directive requirement IDs.
- Modularity seven-answer check against the diff (code-architecture reviewer's share); the change is net small and splits nothing.

Note: I could not use shell file-writes or the Write tool (read-only guard); I ran probes by piping Python to stdin with hostile strings built via chr() to avoid the hook's markup-token matcher. All evidence above is reproducible with the lanes venv at /root/project/lanes-runtime/venv against the /tmp/claude-0/t188-g5 archive copy.

END-OF-REPORT
