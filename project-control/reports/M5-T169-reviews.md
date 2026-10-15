# M5-T169 reviews (every return kept unchanged)

- One build round (backend-engineer, worktree): commit f9de266c integrated as the cherry-pick 6e0262a6 (28 files, inside the allowed paths; LF sha256 equal to the builder's return). Two packet pre-checks before contract (return-precheck-M5-T169.md and its delta at b531be9d).
- Real-preview print (the owner's report printed from the branch through the preview, session 2026-10-15b print-fcd953e1) diffed page by page against main 76745ade: 10 pages (from 11); pages 1-3 and 6 identical; page 5 and the appendix changed as intended; page 4's change belongs to M5-T188.
- G2 orchestrator self-check at the submit head: the task's files equal the builder's digests; nothing outside the allowed paths; research_record_check PASS; the CI run at the submit head (api, web, web-e2e with the report-print spec) read green before submission.
- G1 data-contract-verifier at 6e0262a6: PASS (one advisory: the outline area's two names, DB-245/M5-T180). G3 visual-quality-reviewer at 6e0262a6: PASS (three advisories). G4 qa-engineer at 6e0262a6: PASS (advisories on test coverage and names). G5 security-reviewer at 6e0262a6: PASS (two pre-existing advisories, DB-277 and DB-278).

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

G1 DATA-CONTRACT GATE REPORT — M5-T169 (option comparison / merged evidence appendix / run identity)

Reviewer: data-contract-verifier (independent, READ-ONLY AI agent — not a human/professional review). Reviewed at the pinned frozen SHA 6e0262a6 on task/wave27-comparison-appendix in /root/project/w-wave20. Real-preview print inspected at fcd953e1 (print-fcd953e1/report.html — the integration head; page-4 there is M5-T188, not this task).

VERDICT: PASS (one ADVISORY, no REQUIRED defects).

My share = every fact/figure/source in the merged appendix and the comparison print. All six items verified against primary sources and the real rendered report; nothing invented.

(1) INPUT-FACTS ROWS — PASS. readers.input_facts reads the document's 4-entry input_facts block (no hard-coding; open_items.input_fact_rows formats it). Benchmark block and rendered appendix "Inputs and their sources" agree exactly: Recorded lot area 10,075 sq ft / basis "city record" (administrative_record) / MapPLUTO 26v2 (as of 2026-09-30); Lot outline area (city map) 10,387.99 sq ft / "city map (GIS measurement)" (gis) / MapPLUTO 26v2; Mapped street width - 215 Place 60 ft / "city map (GIS measurement)" / DCP Digital City Map street center lines; Mapped street width - Northern Boulevard 100 ft / same. One basis each; street-width rows are "Mapped street width - ..." never "city map outline"; no gis value's BASIS labelled "tax map"; sources/dates real; no figure mixes bases. Basis labels match the design-contract G-10 nine-bases table (line 84): administrative_record="city record", a lot area reads "recorded lot area" — implemented exactly. The gis label "city map (GIS measurement)" (not the contract's drawing-note literal "city map outline") is CORRECT and REQUIRED by packet S4's delta (the label must fit both outline and street-width gis facts; a street width is never an "outline"); it honors the contract's hard prohibitions.

(2) WORKED ARITHMETIC / COMPARISON — PASS. Appendix renders "Maximum residential floor area: 10,075 sq ft (recorded lot area, city record) × 2.0 (FAR, zoning law) = 20,150 sq ft" and "Legal dwelling-unit limit (standard residences): 20,150 ÷ 680 = 29.63 → 29" — uses the RECORDED lot area (10,075), never the gis outline 10,387.99; operands read from the document, RHS read from the block, reconciles. I independently recomputed all four canonical figures: 10,075×2.0=20,150; 10,075×2.4=24,180; 20,150/680=29.63→29 (.63<.75); 24,180/680=35.56→35. These equal the settled cases real-lot.json (20,150; 24,180; 29 std units; 35 qual-affordable; senior=None), benchmark-options-2-3-6-7.json (opt2/3 FA=24,180=2.40×10,075; GIS 10,387.99 "display-only, never mixed", NB-04) and benchmark-options-5-8-9-10.json. Comparison table: opt1 "Standard residences" 20,150 FAR 2.0; opt2/3 "Qualifying affordable/senior" 24,180 FAR 2.4 (None scheduled); opts 4-11 "Not evaluated in this report" (count=8). 35 is correctly NOT emitted (the document carries no qualifying unit-limit value) — honest, nothing invented.

(3) LAW LINKS — PASS. All 14 cited ZR sections (11-25, 12-10, 23-22, 23-335, 23-342, 23-344, 23-362, 23-432, 23-433, 23-52, 34-232, 34-24, 35-631, 35-632) have captured snapshots under docs/research/zr-snapshots/v1/. sources.zr_section_page_number resolves "ZR 23-52(b)"→section page 23-52 while the visible label keeps the sub-paragraph (correct section-page granularity). M5-T159 resolution untouched.

(4) NB-01 REVISION 9 — PASS. readers.py LF sha256 at 6e0262a6 = 12b2c0c318648eac45a8c037c6f1b210222e66e49fa03da7df6e0a778537c53d; NB-01 implementation.code_identity[readers.py] equals it. I independently recomputed LF sha256 for all 13 code_paths — all 13 code_identity entries MATCH the files at the pinned head. New dependency_assessment[8] "Revision 9 (M5-T169…)" is honest (defensive input_facts reader, empty on 1.4.0, byte-identical zoning-lot behaviour, research_status stays access_blocked). DB-274 clarification in [7] honest (the stale "(revision 7)" is now "the M5-T170 work landed across revisions 7 and 8"), consistent with revision counter 9. research_record_check --check: producer-run exit 0; I reproduced its core identity check (13/13). (Could not re-run the tool at the pinned SHA — the working tree sits on a moving branch; I verified content identity instead.)

(5) RUN IDENTITY — PASS. run_identity.document_fingerprint hashes all top-level values EXCLUDING results_id and computed_at (_FINGERPRINT_EXCLUDE); deployed_commit returns "unknown" unless RENDER_GIT_COMMIT/GIT_COMMIT_SHA is a hex id, without importing app.api.v1.build_info. Rendered appendix: "Document fingerprint: ffab545ea162 · Code commit: unknown · Results revision: 1 · Computed: 2026-10-15" — commit honestly "unknown" (env unset in harness). Producer mutation proof shows fingerprint stable across runs and flips on any value change.

(6) NO VERIFIED/COMPLIANT/FEASIBLE/OPTIMAL; PAGES AGREE — PASS. report.html: "compliant"=0, "feasible"=0, "optimal"=0, "preferred"=0. "Verified"=1, only in the status-label key, which reads "Verified — Supported by completed checks and evidence. Not used in this report." Lowercase "verified" (4×) is all "site fit unverified" (honest non-claims). Single result revision 1 / computed 2026-10-15 in every page footer and body — one document for all figures/diagrams. Legal dwelling-unit limit (29, conditional) is kept separate from the practical "Preliminary apartment estimate: about 17 to 22 apartments" (not conflated). Page-1 decision figures, page-3 figures table (20,150 FAR 2.0), the chart (allowance 20,150 / Building B scheduled 20,150 / Placed on site "Not demonstrated") and the appendix worked arithmetic all agree.

ADVISORY A1 (not REQUIRED; out of this render-only task's scope). The new input-facts table (appendix) labels the 10,387.99 figure "Lot outline area (city map)" / basis "city map (GIS measurement)", while PRE-EXISTING prose on page 3 and in the appendix open items calls the same figure "the tax-map outline". Within M5-T169 the new label is correct (G-10 + S4; it does not call the gis value a "tax map" in its basis). But the report now shows one quantity under two names, which could momentarily confuse a reader. The prose is pre-existing (page-3 text is IDENTICAL vs main per the recorded diff; page-3 prose is forbidden/out-of-scope here) and tracks the settled research (real-lot.json calls the MapPLUTO polygon an "approximate tax-map boundary"). Correction: route report-wide "tax-map outline" vs "city map outline" prose reconciliation to the records/prose task; no change owed by M5-T169.

WHAT I CHECKED: packet M5-T169.json (scenarios S1-S17, allowed/forbidden paths, path_notes); G0 and producer reports; open_items.py, run_identity.py, readers.py, options.py, sources.py (at 6e0262a6); the benchmark fixture input_facts and floor_area_allowance blocks; settled cases real-lot.json, benchmark-options-2-3-6-7.json / -4-11 / -5-8-9-10.json; NB-01 (code_paths, code_identity ×13, dependency_assessment, review); zr-snapshots coverage; the real-preview report.html (labels, input facts, arithmetic, run identity, revision consistency).

WHAT I COULD NOT CHECK (belongs to other gates/CI, not grounds for BLOCKED): the full services/api pytest (9982 passed — producer-claimed; heavy, and the worktree has moved off the pinned SHA), research_record_check.py --check exit code at the pinned SHA (reproduced its identity core instead), modularity_check, and Playwright e2e. These are G3/G4/CI evidence; recommend the orchestrator confirm CI green at the accepted head (D-090 R639).

END-OF-REPORT

## G3 (visual-quality-reviewer)

G3 GATE REPORT — M5-T169 (option comparison, evidence appendix, run identity). Reviewer: visual-quality-reviewer (independent, read-only). I am an AI agent; this is not a human or professional review. Pinned SHA 6e0262a6 on task/wave27-comparison-appendix. Verified against an archive copy of the pinned tree and the real-preview prints.

VERDICT: PASS (three ADVISORY findings, none blocking).

== WHAT I VERIFIED (reproduced) ==
Real-preview prints (print-fcd953e1 vs print-main-76745ade), page by page:
- Page 5 (option comparison): the 11-row table leads BEFORE any caveat; the "Limitation N." paragraphs are gone (build_report_html count of "<p><strong>Limitation" = 0); options 1-3 carry figures (FAR 2.0/2.4), options 4-11 read "Not evaluated in this report" (count = 8) in owner order, never readable as infeasible/achieved; the chart is legible and honest — "Floor-area allowance", "Building B scheduled", and "Placed on site: Not demonstrated" (no bar; count "Not demonstrated" = 1) on one zero-based scale.
- Merged appendix (pages 7-10): one section id="appendix", 5 report-page sections total; clear headings (Shared assumptions, Open items, Inputs and sources, Worked arithmetic, Figures and their law sections, Rules and their review state, Drawing notes, Run identity, Status-label key); scope note ("Not yet in this report") heads it; run identity visible and plain (fingerprint ffab545ea162, code commit "unknown", results revision 1, computed 2026-10-15); the status-label key prints once and "Verified" appears exactly once (visible count = 1), in the key.
- input_facts (page 9): 4 rows; GIS basis labelled "city map (GIS measurement)", never "tax map" (G-10 held); source titles distinguish the outline from the two street-width rows; worked arithmetic 10,075 x 2.0 = 20,150 and 20,150 / 680 = 29.63 -> 29, each input naming its basis, no figure mixing two bases.
- Print type scale: every font-size in the rendered HTML is within contract (title 22pt, headline 30pt, headings 14pt, body 10.5pt, table 9.5pt, footer/labels 8.5pt). Nothing below the 8.5/9.5pt minimums; nothing clipped or overlapping on any page.
Code: modularity_check --check = 0 failures (none of the task's files flagged); new logic placed in open_items.py (279 ln) and run_identity.py (86 ln); readers.py (700 ln) and the page modules stay thin and unflagged; run_identity() wired into page_evidence.py; deployed_commit into report_read.py; basis_label/document_fingerprint used internally. id="issue-1..10" anchors and all href="#issue-N" + "see item N" links are byte-identical to main (only the removed "see Limitation 1" caption became "see the evidence appendix" — a necessary consequence, handled sensibly). Word count: build_report_html(benchmark) visible words = 2217 <= TOTAL_WORD_CAP 2448 (reproduced; matches producer). Tests reproduced green on the pinned tree: tests/drawings/report + test_report_read_api.py = 229 passed; word-cap/appendix/comparison/run-identity/pages = 92 passed; research_record_check --check = PASS (NB-01 revision 9 structurally valid).

== FINDINGS ==
1. ADVISORY — services/api/app/drawings/report/formatting.py:67 (whole_percent_shares, exported at :18). The largest-remainder helper carries a clear line-scoped boundary justification (ruling X7; "computes no zoning quantity") — good — but it has NO caller and NO test anywhere in services/api at this SHA (its consumer M5-T173 is a future task). It is therefore currently dead, untested code shipping an off-by-one-prone rounding step. Correction: add a focused unit test pinning the output now (e.g. [1,1,1]->[33,33,34]; invalid/single/negative -> None), or defer the helper to M5-T173 where it has a caller. Within contracted scope (objective part C), so advisory not blocking.

2. ADVISORY (producer-flagged; I judge ACCEPTABLE) — DB-270 S16 sub-clause "open items no longer spill onto a second page" is NOT literally met: the open-items table spans printed pages 7-8. The primary, test-pinnable requirement (<=10 printed pages) IS met: 10 pages, down from main's 11. The spill is a normal table continuation with the header row repeated on page 8 — nothing clipped, overlapping, or below type scale. Against the design contract (lines 80/112: scope note -> shared assumptions -> open items) the only ways to force one page are to reorder (put open items before the 12 shared assumptions — contract-violating) or cut owner assumption content, and the producer's break-before experiment regressed to 11 pages (worse). The 3->2 page reduction is a genuine improvement and the correct call. No required fix. Clean future path if the owner insists: shorten the shared-assumptions list (owner content; needs owner approval) so the table starts higher on page 7 — not a reorder.

3. ADVISORY (minor) — open_items.py:185 (_CHECK_WORD_AGAIN = "A check of the same kind (see the item above)."), rendered as open-item 10 on page 8. The honest de-duplicated sentence it points to is item 5 ("A check not yet made against an independently worked example."), five rows up — not the immediately-preceding item 9 — so "the item above" is imprecise for a scanning reader. Correction: name the item, e.g. "(see item 5)". The R054/S3 "at most once" requirement is itself met.

== WHAT I COULD NOT CHECK ==
- H2 PDF-extracted word total (<=2,993 hard / <=2,713 target): I confirmed HTML visible words (2217) and the 10-page count, but did not extract PDF text — that is the H2 reviewer's check.
- Playwright e2e and CI-green-at-head: CI's job; not run here.
- Per-requirement D-094 directive verification and the NB-01 G1 delta review: the directive-compliance-verifier and data-contract-verifier own those; I confirmed research_record_check --check PASS and NB-01 at revision 9 structurally.
- The print also carries M5-T188 round-1's page-4 change (2 removed map-outline lines); out of this task's scope — I confirmed it does not affect page 5 or the appendix.

VERDICT: PASS. The visual change meets the design contract and the owner's "comparison before caveats / less text / one evidence appendix / keep the anchors" rows; the three findings above are advisory and non-blocking.
END-OF-REPORT

## G4 (qa-engineer)

# Gate Report — M5-T169 (G4 QA, qa-engineer)

- Gate ID: G4
- Task ID: M5-T169 (option comparison reordered, evidence appendix merged, run identity)
- Reviewer: qa-engineer (independent, read-only AI agent — NOT a human/professional review)
- Producer: backend-engineer (I did not produce this)
- Result: **PASS**
- Clean environment: scratch copy `git archive 6e0262a6 | tar -x` at `/tmp/claude-0/t169-g4/src`; lanes venv (python 3.12.3, pytest 9.0.3, ruff 0.13.0); heavy runs under `flock .../heavy-run.lock`. Pinned reviewed identity `6e0262a6` on `task/wave27-comparison-appendix` (parent `4e8b4b3a`; 28 files).

## Checks independently executed (my share item 1)
| Check | Command | Result |
|---|---|---|
| ruff | `ruff check .` (services/api) | **exit 0** All checks passed |
| report suite | `pytest -q tests/drawings/report tests/api/test_report_read_api.py` | **exit 0 — 229 passed** (producer's "224" = report dir only; +5 in test_report_read_api) |
| three-answers emit slice | `pytest -q .../test_three_answers_three_way_emit.py` | **exit 0 — 60 passed** |
| modularity | `tools/modularity_check.py --check` | **exit 0** — no FAIL; none of the T169 report files flagged |
| research record | `tools/research_record_check.py --check` | **PASS (exit 0)** |
| word cap S10 | `test_s7_total_report_is_within_the_word_cap` | pass (≤2448; producer measured 2217) |

**CI at exact content identity (D-090 R639):** the pinned head `6e0262a6` got no dedicated run (own-push cancellation). `fcd953e1` = the T169 ledger commit; `git diff 6e0262a6 fcd953e1` = only `state.json` + `M5-T169.json` (ledger, no code). CI run **38727929261 at fcd953e1 = SUCCESS, all 21 jobs green**, including **web-e2e (vitest + Playwright report-print spec T169 edited)**, **api (ruff + pytest)**, **modularity**, **web (lint/typecheck/build)**. This is green CI on byte-identical T169 code.

## Scenario→test map; unpinned items (item 2)
S1→test_report_comparison.test_s1_table_comes_before_the_chart_and_no_limitation_paragraphs/_eleven_options_in_order; S2→test_s2_chart_{allowance_and_scheduled,allowance_present_no_scheduled,neither,placed_on_site_shows_a_status_not_a_bar} (all three input states); S3→test_report_appendix.test_s3_five_field_issue_records; S4→test_s4_{input_facts_bases,g10_no_gis_outline_called_tax_map,mutation_basis_word,103_88_approximate_tax_map}; S5→test_s5_worked_arithmetic/_mutation_no_single_figure_mixes_two_bases; S6→test_s6_every_rule_maps_to_a_register_entry + test_report_law_links; S7→test_report_run_identity.test_s7_* (8); S8→test_s8_area_illustration_{present,bar_or_zones,absent}; S9→test_s9_one_merged_appendix_section + test_report_pages/_benchmark section-id lists; S10→test_s7_total_report_is_within_the_word_cap; S12→test_s12_unavailable_options; S14/S15→test_s15_new_blocks_render_only_from_1_5_0_fields + research_record_check + modularity.
**Unpinned (verified by inspection/print only):** S16 physical **10-page count has NO automated test** — pinned only by the recorded print diff (I reproduced 10; see item 5); S17 **"(revision 7)" clarification has no automated text test** (research_record_check validates structure, not wording — I verified by diff); S11 (R032) **verified by absence** (39,934 absent from benchmark), no prohibition guard; S13 real-print is manual.

## Mutation proofs (item 3) — 3 builder + 2 mine, all hold
Reproduced: (M1) table-before-chart: real True; a genuine swap of the rendered `<table>`/`<figure>` → False (assertion flips). (M3) `document_fingerprint`: identical across two runs differing only in results_id/computed_at (`c813b01a2619`==`c813b01a2619`), changes on any value (`b74d8fa0feab`); a fingerprint INCLUDING results_id is unstable. (M4) `basis_label("gis")`="city map (GIS measurement)" (no "tax"); 3 rendered gis rows carry no "tax". **Mine:** (MA) real comparison has no `<p><strong>Limitation`; a reintroduced paragraph is detected. (MB) all 7 `href="#issue-N"` resolve to `id="issue-N"`; renaming one anchor breaks resolution.

## Six breakers reworked, not weakened (item 4)
All mechanical id/slice updates tracking `appendix`: test_location_sheet (6→5 count, id list), test_report_scope_note_maps/_report_law_links/_three_answers_emit/_report_unit_limit_text (slice `assumptions-open-items`→`appendix`; unit_limit broadened to `[appendix:]` = stricter), test_constraints_page (id list 6→5). Underlying assertions preserved/strengthened. test_report_benchmark rear-yard assertion moved from a rendered chip to `readers.open_items(...)["status_label"]=="Conditional"` — correct, since five-field appendix records carry no status column and the Conditional chip still renders on page 3 (confirmed in print). test_report_pages test_s9 figure-scan excludes only the Run-identity block (fingerprint/commit are hashes) — scoped, sound.

## Real print + page diff (item 5)
In-process TestClient POST /report with `benchmark_provider(with_zoning_lot=True, street_on=True)` + `recorded_pack_provider(benchmark_215_16_northern_window)` (no server/port) → `report.html` → main checkout `print-report-pdf.mjs` → `report.pdf`. `diff_pages.py` vs `print-main-76745ade`: **pages: before 11, after 10.** Confirmed: page 5 table leads, "Shared limitations/Limitation 1..5" gone, options 1-3 figures / 4-11 "Not evaluated in this report" in owner order, chart "Placed on site: Not demonstrated"; pages 7-10 "Appendix" with five-field records, input table with **Basis** ("city record", "city map (GIS measurement)" — no gis outline called tax, street widths named "Mapped street width - ..." not "city map outline"), worked arithmetic **10,075×2.0=20,150** and **20,150÷680=29.63→29** (floor-area uses recorded lot area, not the 10,387.99 gis outline), run identity (fingerprint `6d03407a408d`, commit `unknown`), status-label key. **"Verified" appears exactly once.** Area-illustration method correctly ABSENT (no area_allocation). 39,934 absent (R032).

**NB-01 (S14/S17):** revision 8→9; readers.py LF-normalized sha256 independently recomputed = `12b2c0c3…537c53d` (exact match to NB-01); the stale "(revision 7)" entry clarified to "landed across revisions 7 and 8"; NB-05's half correctly not touched (no readers.py in its code_paths).

## Findings (all ADVISORY — no REQUIRED defects)
1. **ADVISORY** DB-270 sub-clause "open items no longer spill to a second page" NOT met — open items span **2 physical pages** (down from 3); the primary ≤10-page requirement IS met. Producer disclosed this honestly as owed. No code defect.
2. **ADVISORY** S16 physical 10-page count unpinned by any automated test (only the recorded print diff); S17 clarified-parenthesis unpinned by any test. Consider a print-diff page-count pin.
3. **ADVISORY** `test_s1_mutation_reversing_the_order_would_fail` is a tautology (asserts `table_at<chart_at` then its logical negation), not a constructed-mutant render; the order is genuinely pinned by `test_s1_table_comes_before_the_chart…`. I proved the true flip myself.
4. **ADVISORY** `test_s12_six_sections_and_page_one_wrapper_untouched` name is stale (now checks 5 sections).
5. **NOTE (not a defect)** S15's literal "report byte-identical on a 1.4.0 document" is not achievable — the appendix merge (6→5, id `appendix`, new question text) is a global presentation change applying to 1.4.0 too; this is the intended task outcome. test_s15 correctly verifies only that the new 1.5.0 *data* blocks are field-gated.
6. **NOTE** Page 4 differs from main (`60 ft/100 ft, map outline` reflow) — from co-resident accepted `drawings/maps/` tasks (M5-T188) present in the base, forbidden to and untouched by T169; NOT a T169 change.

## What I could not check
- Directive requirement-by-requirement verification (D-094 R018…R095) is the directive-compliance-verifier's G5 pass (producer≠verifier) — out of my G4 scope.
- The G1 NB-01 agent delta review is the data-contract-verifier's to record.
- H2 PDF-extracted word total (≤2,993/≤2,713) — an H2 reviewer check; HTML words 2217 and 10 pages are well within budget.
- Playwright e2e I did not execute locally (ports forbidden); verified green in CI web-e2e at the byte-identical head.

## Conclusion
All assigned checks pass; functional behavior matches the packet and the producer report; CI is green on byte-identical code; mutation proofs and the real print confirm correctness; the six consumer breakers were reworked, not weakened. Findings are advisory test-coverage/wording observations with no REQUIRED rework. **Verdict: PASS.**

END-OF-REPORT

## G5 (security-reviewer)

G5 SECURITY GATE REPORT — M5-T169 (Option comparison, evidence appendix, run identity)
Reviewer: security-reviewer (independent, read-only AI agent — this is not a human/professional review). Pinned SHA 6e0262a6 on task/wave27-comparison-appendix, extracted via `git -C /root/project/w-wave20 archive 6e0262a6`. My share: the report HTML and report_read.py security properties.

VERDICT: PASS (2 ADVISORY findings; no REQUIRED defect introduced by this task).

=== WHAT I VERIFIED (all PASS) ===
1. Document-derived strings escaped — the task's NEW code escapes every document string. Input-fact name/value/basis/source and worked arithmetic (open_items.py) render through html.table()/_nowrap/escape() (page_evidence.py:68-99, 110-125; page_assumptions.py:45-81). Run identity (fingerprint/commit/revision/computed_at) renders through el() (page_evidence.py:116-125). Option page escapes name/scheduled/allowance/far/detail (page_option_comparison.py:48-92). SVG chart escapes building names and value labels with xml.sax.saxutils.escape (drawings_embed.py:261-282). label_chip/short_line escape via el(). Reproduced: a source_title of `<script>alert(1)</script>` renders as `&lt;script&gt;alert(1)` — no raw tag (built the full report with recorded_215_16_northern_journey.json).
2. Links only via the official-URL validator — the single href sink (page_evidence.py:51) is built only when law_links.section_url() returns a URL, which passes official_zoning_text_url() (law_links.py:51-81): https-only, host==zoningresolution.planning.nyc.gov, no query/credentials/port, path+fragment regex, canonical rebuild. javascript:/foreign hosts cannot pass; url also goes through escape_attr. No other href in the changed files.
3. Run identity leaks nothing secret — deployed_commit (run_identity.py:50-58) reads ONLY RENDER_GIT_COMMIT then GIT_COMMIT_SHA, accepts only `[0-9a-f]{7,64}` (lowercased), else "unknown"; byte-for-byte the same contract as build_info.py:_deployed_commit. Reproduced: envs `$(whoami)`, `rm -rf /`, `/etc/passwd`, `HELLOSECRET`, empty → all "unknown"; `ABCDEF1`→`abcdef1`. report_read.py:112 passes the validated commit through build_report_html (no app.api.v1.build_info import into drawings/report — RISK 6 honoured).
4. Fingerprint over document content only — document_fingerprint (run_identity.py:61-70) is sha256 over json.dumps(results minus results_id/computed_at); pure hash, no I/O, cannot read anything.
5. No new network/env access; one benign new file read — only env access is the two commit vars above. No network/subprocess/eval/exec anywhere in the changed files (grep clean). The one new file read is open_items.py:235-257 register.json via a STATIC in-repo path (Path(__file__).parents[2]/rules/review_register/register.json), read defensively (OSError/ValueError/UnicodeError→empty), cached, not influenceable by the document — no traversal/SSRF. This read is mandated by the task (map results to the existing review register) and is not a security risk.
6. No new dependency — new modules import only stdlib (hashlib/json/os/re/pathlib) and in-repo modules; no requirements/lockfile touched.
7. Log redaction — report_read.py logs only correlation_id (lines 79, 115); no document content, no secrets, no stack trace (no exc_info).
8. Hostile document — markup in a source title: escaped (above). Huge input_facts block (5,000 rows): builds cleanly (~722 KB), all escaped, no crash. Non-finite: handled fail-closed (see F2).

=== FINDINGS ===
F1 — HTML-injection via the @page CSS margin boxes (`</style>` breakout). MEDIUM severity, ADVISORY (pre-existing; NOT in this task's diff; not worsened by T169).
 File/line: layout.py:29-38 (_css_string) and :53-63; fed by builder.py:39-45 (_footer_line) / :56-57 / :104-105.
 Evidence: _css_string escapes only `\`, `"`, `\n`, `\r` — not `<`/`>`/`/`. The running identity (header) and footer (which include the run-identity fields revision and computed_at) are written literally into `<style>@page{content:"…"}`. A document-derived value containing `</style>` closes the style element and injects arbitrary HTML/JS. Reproduced: report_css('</style><script>alert(1)</script>','footer') emits the literal `</style><script>alert(1)`; a full build with revision='</style><script>XSS</script>' yields raw `</style><script>XSS` in the HTML. Exploitability is limited because these fields (revision, computed_at, borough/block/lot, district) are engine-emitted and schema-validated, not directly user-supplied, and _footer_line/_css_string pre-date T169 — so this is not a T169 regression. But it is a genuine latent stored-injection sink that now also carries run-identity values.
 Correction: in _css_string also neutralize angle brackets (e.g. strip/encode `<` and `>`, or reject any `</`), OR HTML-escape header/footer before CSS-escaping, OR render the identity as DOM text rather than inside `<style>` content. Recommend the orchestrator open a backlog item; it does not block T169.

F2 — Non-finite numeric document values crash figure formatting. LOW severity, ADVISORY.
 File/line: formatting.py:22-40 (_as_float/format_int_commas) and :49-58 (format_ratio).
 Evidence: _as_float passes float('inf')/float('nan') through; format_int_commas then calls int(number) → OverflowError (inf) / ValueError (nan). Reproduced: an input_fact value of inf raises OverflowError during build. format_ratio yields the nonsense strings 'inf.0'/'nan.0' (escaped, so no XSS). Via the live route this fails CLOSED: report_read.py:103-119 wraps build_report_html in try/except→_internal_error_500 (typed JSON, no stack trace), which satisfies "fails closed." Note Python json.loads accepts Infinity/NaN by default, so a crafted/garbage document body is the realistic trigger; it is otherwise engine-emitted and contract-guarded upstream.
 Correction: make _as_float return None for non-finite (`math.isfinite`), so a bad value degrades to "missing" rather than relying on a 500; fix format_ratio's inf/nan output similarly.

=== WHAT I COULD NOT CHECK ===
- I did not run the full pytest/e2e suites (CI's job; heavy-run lock honoured). I ran targeted in-process probes with /root/project/lanes-runtime/venv against the extracted 6e0262a6 tree.
- I did not execute the live POST /report route (no server/ports, per the read-only rules). I verified its fail-closed behaviour by reading report_read.py's try/except→_internal_error_500 and by reproducing the underlying render crash directly; I did not observe the 500 end-to-end.
- Upstream schema/engine constraints on revision/computed_at/district (which bound F1's exploitability) were reasoned from the fixture, not re-derived from results.schema.json.

Security dimension of G5: PASS. No REQUIRED correction; F1 and F2 are ADVISORY (F1 pre-existing, recommend tracking).
END-OF-REPORT
