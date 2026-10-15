# M5-T169 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `db71dc21ba5934a5bf1e9205f8bc34812cffbea2` (branch `task/wave27-comparison-appendix`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R018, R019, R020, R023, R025, R026, R027, R028, R032, R038, R049, R054, R058, R059, R060, R061, R072, R075, R077, R084, R092, R095.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No row is VIOLATED or UNVERIFIABLE; all 22 are SATISFIED for this task's share, bindings B1-B5 pass, and every required gate is PASS at one content identity. - Advisories recorded by the reviewers (not blocking, not owed by this task): G1 A1 / DB-245 (one quantity under two names — gis "city map" vs pre-existing page-3 prose "tax-map outline"; page-3 prose is forbidden/unchanged here, routed to M5-T180); G3/G4 open-items spill to 2 printed pages (down from 3; 10-page target met) and the "(see the item above)" wording (meant item 5); G3 formatting.whole_percent_shares has no caller/test yet (its consumer is M5-T173); G4 the 10-page count and the DB-274 "(revision 7)" clarification are pinned by the recorded print diff, not an automated test; G5 F1 (pre-existing @page-CSS HTML-injection sink in layout.py, now also carrying engine-emitted run-identity values — not a T169 regression, recommend a backlog item) and F2 (non-finite numeric values fail closed via the route 500). None of these contradicts any of the 22 rows.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T12:40:44Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T169 (directive D-094, 22 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is not a human or professional review. I produced none of this work. I judged each row from primary evidence (owner source text in the directive files, then the task's code/tests/records at the frozen head, the real-preview prints, and reproduced renders), treating the producer report, reviews and evidence map as claims to reproduce.

(1) HEAD VERIFIED
 - I read the frozen head db71dc21ba5934a5bf1e9205f8bc34812cffbea2 on task/wave27-comparison-appendix in /root/project/w-wave20 (base main 76745ade).
 - The working tree sits past it at e76071c3 (M5-T186, unreviewed); I read all task/directive files at db71dc21 through git plumbing, not the working tree.
 - The material build is 6e0262a6 (cherry-pick of f9de266c); its blobs are byte-identical at db71dc21 and no commit between 6e0262a6 and db71dc21 touched this task's files (git log over the allowed paths was empty).
 - 6e0262a6 is an ancestor of the submit head c20ba45e, which is an ancestor of db71dc21; the task's report code and NB-01 are also byte-identical at the working-tree head, so the check scripts I ran apply to the frozen head.

(2) ROWS (this task's share; numeric order)

ROW D-094-R018 — PASS
 - page_option_comparison.py renders the 11-row table before the chart; reproduced render shows "Not evaluated in this report" exactly 8 times and all eleven options in owner order (options.ELEVEN_OPTIONS).
 - Options 1-3 carry worked figures (20,150 sq ft / 24,180 sq ft); drawings_embed.allowance_bar_chart_svg distinguishes allowance vs scheduled vs a placed-on-site status, so the "two equal bars" are gone.
 - test_report_comparison.test_s1_table_comes_before_the_chart_and_no_limitation_paragraphs and test_s1_eleven_options_in_order_figures_then_not_evaluated pass (in the 229-pass run).
 - Nothing stays open for this task; worked figures for options 4-11 arrive via the R6B reference-case/engine tasks (M5-T185/186) and M5-T172.

ROW D-094-R019 — PASS
 - The "<p><strong>Limitation" paragraphs are removed from the comparison section; I reproduced build_report_html(benchmark) and the string is absent, and the real print page 5 diff shows "Shared limitations / Limitation 1..5" removed.
 - The material limitations are preserved (not deleted) as appendix five-field issue records (open_items.appendix_issue_records), per R025.
 - This task's share is removing the inventory from the comparison page; the destination "owner update" is the PDF/session bullets/backlog, outside this render task's files.
 - What stays open: placing the detailed missing-work inventory into the owner update is owned by the owner-update channel, not this packet.

ROW D-094-R020 — PASS
 - drawings_embed._status_row renders placed-on-site as italic text "Not demonstrated" with no <rect>, never a bar; allowance and scheduled are bars on one zero-based scale (scale = max of allowance and scheduled).
 - test_s2_chart_placed_on_site_shows_a_status_not_a_bar asserts no "<rect" after "Placed on site" and that placed vs not-placed renders differ (not placement-invariant).
 - Reproduced render contains both "Placed on site" and "Not demonstrated"; nothing implies the scheduled area is achieved on site.
 - Nothing stays open.

ROW D-094-R023 — PASS
 - open_items.worked_arithmetic reads operands from the document and renders "10,075 sq ft (recorded lot area, city record) × 2.0 (FAR, zoning law) = 20,150 sq ft" and "20,150 ÷ 680 = 29.63 → 29", each result read from the document block.
 - test_s5_worked_arithmetic_reads_from_the_document_with_bases and the mutation test_s5_mutation_no_single_figure_mixes_two_bases pass; displayed rounding (29.63 → 29) reconciles with the document's value.
 - I independently reproduced "20,150" and "29.63" in the rendered appendix.
 - Nothing stays open.

ROW D-094-R025 — PASS
 - appendix_issue_records emits exactly issue / consequence / next action / responsible role / evidence reference (plus a stable number and an optional material-reason detail).
 - Site-document categories (zoning_lot, lot_area) carry "Owner or surveyor"; program work carries "This program"; test_s3_five_field_issue_records confirms both roles and the Zoning-lot item as a site document.
 - Material limitations are kept as short references via the detail field for coverage/legal_unit_limit; page_assumptions.open_items_table renders the five headers and id="issue-N".
 - Nothing stays open.

ROW D-094-R026 — PASS
 - open_items.input_fact_rows reads the 1.5.0 input_facts block and names real sources/dates (MapPLUTO 26v2 as of 2026-09-30; DCP street center lines); the real print replaces the old "City records"/"Approximate tax map" with these.
 - basis is in plain words via the nine-bases map (administrative_record="city record", gis="city map (GIS measurement)"), and worked_arithmetic supplies real calculations.
 - test_s4_input_facts_bases_read_from_the_four_entry_block and test_s5 pass; values are read from the document, never hard-coded.
 - Nothing stays open for this task (R026 also binds M5-T164/M5-T167 for their own pages).

ROW D-094-R027 — PASS
 - page_evidence._law_links links only to the exact captured section URL (law_links.section_url), printing plain text when there is no capture — never the zoning homepage.
 - open_items.register_rule_rows maps each rule_versions entry to its EXISTING review-register entry and review state, reading register.json defensively and never writing it (G-11).
 - test_report_law_links.py (reslice to id="appendix", assertions preserved) and test_s6_every_rule_maps_to_a_register_entry_with_review_state pass; G1 reproduced 14 captured sections.
 - Nothing stays open for this task; register.json itself is M5-T172's scope.

ROW D-094-R028 — PASS
 - One clearly-named id="appendix" section holds the status-label key once; reproduced render shows "Verified" exactly once (in the key) and report-page section count 5.
 - run_identity renders document fingerprint, code commit, results revision and computed date (test_s7_run_identity_renders_in_the_appendix).
 - test_s9_one_merged_appendix_section confirms the old ids are gone and no repeated headings remain.
 - Nothing stays open.

ROW D-094-R032 — PASS
 - git grep over services/api/app/drawings/report found no 39,934 / remaining_capacity computation; the reproduced benchmark render contains no "39,934" and no "remaining capacity".
 - The report emits no auto-subtracted remaining-capacity figure; NB-02 is read, not revised (it is a read-only input in the packet).
 - G4 independently verified the field's absence on the real print.
 - Nothing stays open.

ROW D-094-R038 — PASS
 - readers.input_facts is a new reader over the document's own 1.5.0 input_facts block; open_items reads value/basis/source from it rather than hard-coding — the data path is fixed, not just the wording.
 - run_identity.document_fingerprint and the rendered revision prove every figure comes from one result revision; test_s4 asserts the pairs are read from the 4-entry block.
 - The real print shows the old reworded "City records" prose replaced by read-from-document source identifiers.
 - What stays open: the broader "research incorporated / older fixture or cache" sweep across other pages is other tasks' share (R038 also binds M5-T175/M5-T167); this task fixed the appendix/inputs data path.

ROW D-094-R049 — PASS
 - Tables use short column headings (Input/Value/Basis/Source; Figure/Value/Law; Label/Meaning; Option/Floor-area allowance/Scheduled building/Status); values are right-aligned via nowrap spans.
 - page_evidence._label_key carries an explicit "no caption duplicating a section title (R049)" note; the figures/inputs captions differ from their section h3, so no caption duplicates its title.
 - Units are carried inline in the value cells ("10,075 sq ft", "FAR 2.0") rather than in headings; R049's units-in-headings is a soft "where possible", and G3 (visual-quality-reviewer) PASSED on the type scale and layout.
 - Nothing material stays open.

ROW D-094-R054 — PASS
 - appendix_issue_records prints the honest "A check not yet made against an independently worked example." at most once (check_word flag); a second not-checked item points back via _CHECK_WORD_AGAIN.
 - test_s3 asserts that sentence appears <= 1 time; the old repeated "not yet" paragraphs of page 5 are gone (real print diff).
 - Unfinished states read once and plainly ("Not evaluated in this report"; "Placed on site: Not demonstrated").
 - What stays open: nothing material; the pointer wording "(see the item above)" is a minor G3 advisory, not a violation.

ROW D-094-R058 — PASS
 - run_identity.document_fingerprint hashes the document's values excluding results_id and computed_at, so every figure/diagram is provably from one document; the rendered run identity shows one results revision.
 - The chart keeps allowance, scheduled area and site-fit distinct; the appendix renders the legal dwelling-unit limit (29) separately, and G1 confirmed the preliminary estimate (17-22) is not conflated with it.
 - test_report_run_identity fingerprint-stability and value-change tests pass; "Verified" (the status key) is distinct from the estimate/limit.
 - What stays open: nothing for this task; R058 is a cross-page harness row also bound to M5-T162/M5-T164, checked by G1.

ROW D-094-R059 — PASS
 - All eleven options render (test_s12 asserts each "N. name" present); options 4-11 read "Not evaluated in this report" and carry no figures.
 - test_s1_eleven_options_in_order_figures_then_not_evaluated asserts no "infeasible/not feasible/achieved/cannot be built" text — unavailable options cannot read as evaluated alternatives.
 - Reproduced render shows exactly 8 "Not evaluated in this report" rows.
 - Nothing stays open.

ROW D-094-R060 — PASS
 - page_assumptions.open_items_table renders id="issue-N" for each record; the reproduced render has 10 such anchors, and the page-1/page-3 "see item N" links live in forbidden files unchanged by this task.
 - _law_links resolves each law citation to its exact captured section anchor/URL, never the homepage.
 - G4 reproduced that all seven href="#issue-N" resolve to their anchors on the real print.
 - What stays open: nothing material; the "(see the item above)" wording for open-item 10 (meant: item 5) is a G3 advisory, not a broken anchor.

ROW D-094-R061 — PASS
 - The appendix states the applicable law (captured ZR sections) and the worked figures; genuinely unresolved site facts (the zoning lot, the lot-area basis) stay named as conditions in the open items, not as "unknown because software is unfinished".
 - The real print shows "Zoning lot" and "Maximum lot coverage" as conditioned open items with their next actions, and the worked arithmetic is shown rather than suppressed.
 - No legal source fact in the rendered appendix is marked unknown due to an unfinished feature.
 - What stays open: nothing for this task; R061 is a cross-task harness row (also M5-T163/T167/T170/T175); I verified this render's share.

ROW D-094-R072 — PASS
 - The option-comparison page changed (table first, limitation paragraphs removed), satisfying the "must change" clause; the building-diagram page change is another task's file scope.
 - Text did not grow: I reproduced 2217 visible words against TOTAL_WORD_CAP=2448 (test_s7_total_report_is_within_the_word_cap); the report shrank from 11 to 10 printed pages (real print diff).
 - The cap is the standing G-9 value (unchanged in this task's test diff).
 - What stays open: the "building-diagram pages" change in R072 is owned by the diagram tasks, not this render packet.

ROW D-094-R075 — PASS
 - The comparison table comes before any limitation text (index of <table> < index of chart; no "<p><strong>Limitation") and carries worked results (options 1-3 figures).
 - test_s1_table_comes_before_the_chart_and_no_limitation_paragraphs passes; the real print page 5 leads with the table.
 - Options 1-3 show 20,150 / 24,180 sq ft worked figures rather than rows of unfinished calculations.
 - What stays open: nothing for this task; more worked option rows arrive via M5-T185/186 and M5-T172.

ROW D-094-R077 — PASS
 - Page-type sections 5 and 6 are merged into one id="appendix" (old ids assumptions-open-items and calculations-evidence removed); section count 6 -> 5 (reproduced).
 - Repeated explanations are removed: the scope note heads the appendix once, categorical inputs are not re-listed, and the status-label key prints once.
 - test_s9_one_merged_appendix_section and test_s9_scope_note_heads_the_appendix pass.
 - Nothing stays open.

ROW D-094-R084 — PASS
 - All eleven options remain in the report (listed in the table); finishing scenario work does not remove options 4-11 — they render as "Not evaluated in this report", not dropped.
 - test_s12_unavailable_options_are_not_evaluated_alternatives confirms each option is present and unavailable ones cannot read as evaluated.
 - Reproduced render keeps the full eleven-option set.
 - Nothing stays open.

ROW D-094-R092 — PASS
 - worked_arithmetic uses the recorded lot area (administrative_record), never the gis outline (10,387.99); test_s5_mutation_no_single_figure_mixes_two_bases asserts the outline value and the gis label do not enter the floor-area figure.
 - The area-illustration method carries the G-14 statement "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" (test_s8), so zoning floor area is never treated as the physical floor-plate.
 - On the benchmark the area_allocation block is absent, so the illustration method is correctly not yet shown there (test_s8_area_illustration_absent_on_the_benchmark).
 - What stays open: the benchmark's area-allocation illustration is added by M5-T172; this task implemented and tested the compatible-measure method on M5-T164's fixtures.

ROW D-094-R095 — PASS
 - page_evidence._area_illustration_method renders the methodology in the appendix (one block), not beside the drawing; test_s8_area_illustration_method_present_with_a_block confirms it appears with a block and test_s8_area_illustration_absent_on_the_benchmark confirms it is absent without one.
 - The method names the stated share, the measure, the G-14 conversion statement and the bar-or-zones rule.
 - The one-short-caption-beside-the-drawing part belongs to the illustration/drawing task (benchmark has no block yet).
 - What stays open: the short caption beside the actual area illustration on the benchmark is M5-T172's share; this task placed the method text in the appendix.

(3) BINDING B1–B5
 - B1 PASS. Contract commit 4f3943cb appended M5-T169 to applicability.task_ids of all 22 rows; a base-main-vs-frozen-head diff shows every row's text and all non-applicability fields unchanged (base had no M5-T169, head has it). The same commit resynced requirements_content_digest, added an audit_log entry naming the bind + resync + provisional row, and added the provisional verification row — all in one commit. Gate records PASS for G0 (orchestrator, at contract head 4f3943cb) and G1 data-contract-verifier, G2 orchestrator, G3 visual-quality-reviewer, G4 qa-engineer, G5 security-reviewer, with G1-G5 all at one content identity c20ba45e (the task's files are byte-identical from the build 6e0262a6 through c20ba45e to the frozen head).
 - B2 PASS. At the frozen head I recomputed the LF-normalized sha256 of requirements.json = 209ddf6b1a528283012f6fd60c9306305bd6c7d543f31d8c0f266cb59afe29e1, equal to manifest.requirements_content_digest_sha256; the id digest also matches (f56cd5d6...). validate_directive_compliance.py --check exited 0.
 - B3 PASS. verification.json (directive_verification/v2) has exactly one M5-T169 task_verifications row: producer backend-engineer, verifier "" (empty), reviewed_sha null, and 22 requirement rows exactly equal to the cited ids, all state "pending" — the expected pre-stamp state.
 - B4 PASS. I replicated the registry applicability logic across ALL active directives at the frozen head: the applicable set for M5-T169 (task_id M5-T169, type backend, milestone M5, its allowed_paths) is exactly the 22 cited rows; applicable == cited, no missing, no invalid.
 - B5 PASS. No requirement in any other active directive, and no further D-094 row, applies to M5-T169 uncited (applicable − cited is empty). Only D-094 contributes, via explicit task_id matches.

(4) CARRY-FORWARD CONDITION (stated up front so this PASS may be stamped at a later accept head without a new review)
 - Blob-level predicate: the PASS holds at any later head where every file in the packet's allowed_paths keeps the exact blob id it has at db71dc21 (notably the report modules under services/api/app/drawings/report/, report_read.py, NB-01-zoning-lot-instruments.json, the report/test files listed, and apps/web/e2e/report-print.flag-on.spec.ts), AND all 22 rows' text plus their M5-T169 applicability binding are unchanged, AND the requirements_content_digest/id_digest still match the manifest, AND the M5-T169 verification row still carries these 22 ids.
 - Broad disjoint-peer tolerance: later commits MAY touch any other file — other tasks' source under services/, apps/, packages/, docs/, .claude/; other tasks' packets/gates/reports/directive bindings; new rows appended to D-094; ledger state.json; plus this task's own acceptance records (its verification row stamp, gate records, evidence map, reviews, task status) and a merge of the main line that changes none of the predicate's files. Any such change does NOT require re-review.

(5) REQUIRED CORRECTIONS
 - None. No row is VIOLATED or UNVERIFIABLE; all 22 are SATISFIED for this task's share, bindings B1-B5 pass, and every required gate is PASS at one content identity.
 - Advisories recorded by the reviewers (not blocking, not owed by this task): G1 A1 / DB-245 (one quantity under two names — gis "city map" vs pre-existing page-3 prose "tax-map outline"; page-3 prose is forbidden/unchanged here, routed to M5-T180); G3/G4 open-items spill to 2 printed pages (down from 3; 10-page target met) and the "(see the item above)" wording (meant item 5); G3 formatting.whole_percent_shares has no caller/test yet (its consumer is M5-T173); G4 the 10-page count and the DB-274 "(revision 7)" clarification are pinned by the recorded print diff, not an automated test; G5 F1 (pre-existing @page-CSS HTML-injection sink in layout.py, now also carrying engine-emitted run-identity values — not a T169 regression, recommend a backlog item) and F2 (non-finite numeric values fail closed via the route 500). None of these contradicts any of the 22 rows.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The full services/api pytest (~9,982 tests) and test_directive_compliance.py — forbidden by the brief; I ran only the focused report suite (229 passed) and relied on CI for the rest.
 - CI I confirmed by read only: run 38732460088 at the submit head c20ba45e is completed/success with 21/21 jobs non-failing; I did not re-execute CI.
 - Playwright e2e and the live POST /report route on ports 3000/3001/8000 — forbidden; I reproduced the render in-process via build_report_html and relied on the orchestrator-captured prints (print-fcd953e1 vs print-main-76745ade) for the 10-page / page-by-page evidence.
 - The H2 PDF-extracted word total (<=2,993 hard / <=2,713 target) — I confirmed 2217 HTML visible words and 10 pages, which are within budget, but did not extract PDF text.
 - The engine/schema correctness of the underlying document values (revision, computed_at, input_facts) — out of this render task's scope; I verified they are read from the document, not hard-coded, and preserved the work-order-vs-fixture conflict (103.88 is approximate_tax_map, not the gis basis; the gis outline is 10,387.99), consistent with the settled R6B cases.
 - The check scripts (research_record_check --check = PASS/NB-01 code_current True; modularity_check --check = 0 failures; validate_directive_compliance --check = exit 0) ran against the working-tree head e76071c3; I confirmed this task's report code and NB-01 are byte-identical there to the frozen head, so the results apply.

END-OF-REPORT
```
