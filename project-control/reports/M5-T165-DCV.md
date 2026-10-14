# M5-T165 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c3b3c9abb7bbd691a799c5e43f6e7e8ac1a9676d` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R011, R012, R013, R029, R030, R037, R047, R048, R050, R051, R054, R055, R060, R070, R071, R072, R073, R078, R079, R081, R085, R089, R090.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED or UNVERIFIABLE row; every row's share is satisfied on reproduced primary evidence. The S18 whole-report "tax-map outline" residual is correctly OUTSIDE this task's allowed paths and formally narrowed by scope correction 485b8ecb to DB-245/M5-T167; within this task's texts and the whole of page 1 the GIS wording is clean ("city map outline"), which I reproduced.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 02:43 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T165 (directive D-094, 23 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is a labelled, automated, read-only verification, not a human or professional/legal review (ADR-007). I produced none of the work or records; I re-derived every row from primary evidence (the owner's words in the D-094 source files, the task's files read via git plumbing at the frozen head, the evidence records, the reference cases, and test runs on files I confirmed byte-identical to the frozen head).

(1) HEAD VERIFIED
 - I read the frozen head c3b3c9abb7bbd691a799c5e43f6e7e8ac1a9676d on task/wave24-report-v3 (base main b4704161); `git cat-file -t` = commit; its message is the M5-T165/T166 submission at 7c831652.
 - The worktree HEAD moved during my run (327e94e9 → e27bc2a0); every row's evidence was read with `git show c3b3c9ab:<path>`, never the working tree.
 - `git diff c3b3c9ab..HEAD` over all of the task's allowed-path files (report/, kit tokens, presentation-tokens.json, tests/drawings, NB-01, the fixture, scenario/three_answers) is EMPTY and `git status` is clean, so test runs I did in the worktree faithfully reflect the frozen head.
 - The task's allowed-path files are byte-identical across fd649b66 (review head) → 7c831652 (gate head) → c3b3c9ab (frozen head): all three `git diff --stat` are empty.

(2) ROWS (D-094, numeric order; each judged for THIS TASK'S SHARE)

ROW D-094-R011 — PASS
 - page_decision_summary.render() emits exactly the four kinds plus the named furniture: identity, standing label, the question, the answers+site-graphic block, the ceiling/estimate block, the uncertainties, the scope line.
 - test_report_page_one.py::test_s1_page_one_holds_the_four_kinds_and_the_named_furniture PASSED in my run and asserts "What this report covers" is absent.
 - visual-quality-reviewer PASS at 68d417fe: the whole decision summary fits one page and the result leads at headline size.
 - Open: the website first-screen parity is M5-T171 (ready, not built); nothing else stays open for the PDF.

ROW D-094-R012 — PASS
 - test_f10_r012_coverage_inventory_leaves_the_report and test_s12 PASSED; "What this report covers" is absent report-wide in my benchmark render.
 - _scope_line() prints "The material exclusions are listed at the head of the appendix."; the appendix opens with "Not yet in this report:" before "Shared assumptions" (test_s12).
 - Open: the rule that the development inventory lives in the owner update is M0-T193 (accepted); the owner updates carry it.

ROW D-094-R013 — PASS
 - page 1 shows "Estimate 17-22" linking to #estimate-B (reproduced in my render); the full estimate sentence prints once on the scenario sheet (page_scenario_sheet.py id="estimate-B").
 - test_s17_long_apartment_estimate_sentence_prints_once and test_report_pages.py::test_vc2 (count 2→1) PASSED, so the duplicate page-5 sentence is gone.
 - Open: nothing stays open for this task's share.

ROW D-094-R029 — PASS
 - My render shows "the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70" near the headline; NB-01 rev 4 records the ZONE index entry (2022-02-08, lots 1 and 70).
 - The allowance phrase "20,150 sq ft is a conditional tax-lot-only arithmetic allowance, not established remaining development rights." sits in the floor-area cell (test_s11 PASSED), set only while the zoning lot is unconfirmed.
 - NB-01 research_status is access_blocked: the zoning lot is likely but "not established until the instruments are read".
 - Open: the website summary parity is M5-T171 (not built).

ROW D-094-R030 — PASS
 - zoning_lot_item.page_one_zoning_lot_sentence returns the property-specific index-entry sentence when the condition exists; the generic "the app does not verify the zoning lot" shows only in the not-checked state and once (both test_s2 tests PASSED).
 - My render confirms the CRFN instrument id 2022000059134 is absent from page 1 (it names the index ENTRY, not the instrument).
 - Open: nothing stays open for this task's share.

ROW D-094-R037 — PASS
 - constraint_text.REAR_YARD_OPEN_CHECK names ZR 23-344(b) and (c)(3) as "not yet checked" and draws no conclusion; my whole-report render shows "not known beyond the corner area" is absent and "no rear yard is required" is absent.
 - test_s19 and test_benchmark_rear_yard_reads_as_the_open_check PASSED; no corner-only framing and no unconditional zero rear yard inferred.
 - NB-03 rev 2 is a labelled draft reading (interpretation_awaiting_review), not a DOB determination.
 - Open: the rear-yard engine's own three-state check is M5-T167 (not contracted); the record/contract/reference-case work (M5-T163/T176) is accepted.

ROW D-094-R047 — PASS
 - layout.py reads every font-size from a TYPE token; my grep found no literal numeric font-size, and only the KEY FIGURE sits at _HEADLINE_PT (30 pt) while the rest sits at body/compact tokens.
 - test_s3_headline_is_28_to_32_pt_and_every_print_size_comes_from_tokens PASSED; the tokens are headline 30 (28-32), title 22, section 14, body 10.5, table 9.5, note 8.5 — all within R047's bands.
 - Open: the printed-point-size check of every exported page is H2 / the final export task M0-T195 (not contracted).

ROW D-094-R048 — PASS
 - layout.py @page uses margin 14mm on A4 and a token/mm spacing scale; no font-size is hard-coded.
 - visual-quality-reviewer PASS at 68d417fe: the page count fell by tightening, with no font below its 8.5 pt token floor.
 - Open: the adopted paper size is owner question D1 (open); the template uses A4 meanwhile.

ROW D-094-R050 — PASS
 - labels.py defines exactly the six owner labels (Verified, Provisional, Illustrative, Conditional, Pending verification, Unresolved); page_decision_summary attaches label_chip to each answer, the ceiling, the estimate and every uncertainty.
 - test_s4 and the status-word token tests PASSED (whole tests/drawings/report suite green): ceiling Conditional, estimate Provisional, each uncertainty labelled, uncertainty not removed.
 - Open: nothing stays open for this task's share.

ROW D-094-R051 — PASS
 - _answer_cell orders result → body detail → assumption line → allowance phrase, and the estimate links to its full calculation (#estimate-B).
 - test_s6 PASSED: 0 dangling in-page anchors and #estimate-B resolves.
 - Open: the website expand-detail parity is M5-T171 (not built).

ROW D-094-R054 — PASS
 - test_s7_repeat_count_stays_at_or_below_the_before_set PASSED and my render shows page 1 at 188 visible words (baseline 330); missing values show "Not available"/document reasons, not a "not yet" flood.
 - The standing budget test (test_report_benchmark.py) caps page-1 words and total body and holds the repeat count at/below the before set.
 - Open: nothing stays open for this task's share.

ROW D-094-R055 — PASS
 - _floor_area_basis builds "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" from document-read values; test_s1 asserts that exact string.
 - NB-04 rev 2: 10,075 is basis administrative_record (recorded lot area) and the 10,387.99 gis outline is a drawing measure only; the two bases are kept distinct (conflicting_evidence), and the task re-derives nothing.
 - Open: nothing stays open for this task's share (the full HPD-basis sensitivity calculation stays on the scenario sheet, which page 1 links to).

ROW D-094-R060 — PASS (this task's HTML share)
 - page-1 #issue-<n> and #estimate-B each resolve to an existing id; test_s6 PASSED with 0 dangling anchors, and my render carried 13 law links with 0 pointing to the zoning homepage.
 - Internal references get a precise anchor destination (#issue-1/2/4, #estimate-B).
 - Open: the owner's harness is a destination check over the EXPORTED PDF; that belongs to the final export task M0-T195 (not contracted) and is not proven by HTML tests.

ROW D-094-R070 — PASS
 - My benchmark render shows the zoning-lot flag on page 1 and the 29 derivation "20,150 ÷ 680 = 29.63 → 29" in the evidence section; 13 law links, all to specific sections (e.g. .../23-344, .../23-22), none to the homepage.
 - test_db232_zoning_lot_open_item_is_first PASSED and test_report_law_links.py is unedited by this task and green.
 - Open: the page-6 flag, the page-8 29 and the specific links were built in wave 23 and are preserved here, not re-authored.

ROW D-094-R071 — PASS
 - page 1 shows "Legal ceiling 29" with the label Conditional read from the value's own state (unit_limit_text.legal_ceiling), never Provisional or settled (test_s4).
 - test_s4_no_forbidden_result_word_on_page_one PASSED and my render confirms no "buildable/achievable/can be built" on page 1; the distinction line states "neither is a demonstrated layout".
 - Open: the website guard for the 29 is M5-T171 (not built).

ROW D-094-R072 — PASS (this task's no-growth share)
 - test_s7_total_report_is_within_the_word_cap PASSED (whole body ≤ the before baseline 2448); the visual reviewer recorded the text shrank 7.6%.
 - Open: changing the option-comparison page and the building diagram is later work (M5-T169 and M5-T173, not contracted); this task delivers only the no-text-growth half for page 1 and the body.

ROW D-094-R073 — PASS
 - render leads with the results and carries no feature inventory (test_s1 and test_s12); the architect no longer has to assemble the answer.
 - visual-quality-reviewer PASS at 68d417fe: "Five-second hierarchy is strong", the answer leads.
 - Open: nothing stays open for this task's share.

ROW D-094-R078 — PASS
 - _ceiling_estimate_block holds "Legal ceiling 29" beside "Estimate 17-22" with the distinction line; my render shows both figures on page 1 in one block.
 - The distinction token byte-equals the contract quote ("The ceiling is a conditional zoning limit; the estimate is an unvalidated apartment-yield range; neither is a demonstrated layout."), asserted byte-equal by test_s4; neither figure is presented as a demonstrated layout.
 - Open: the website parity is M5-T171 (not built).

ROW D-094-R079 — PASS (this task's report-side share)
 - The report's rear-yard item is the open check naming ZR 23-344(b) and (c)(3) as not yet checked, drawing no conclusion and linking 23-344 (constraint_text; my render; test_s19 and test_benchmark_rear_yard PASSED).
 - NB-03 rev 2 (interpretation_awaiting_review, independently reviewed) and the short-block-rear-yard reference case record two independent readings that do NOT establish the exemption; the report does not present it as established.
 - Open: the engine's own 23-344(b) applicability check with its three result states is M5-T167 (not contracted); M5-T163/T164/T176 (record, contract shape, reference case) are accepted.

ROW D-094-R081 — PASS
 - render holds exactly the four kinds: prominent results, their assumptions beside them, one site graphic, and at most three uncertainties (test_s1, test_s5, test_s11 PASSED).
 - visual-quality-reviewer PASS at 68d417fe: prominent results, assumptions beside them, one site graphic, three linked uncertainties on one page.
 - Open: the website first-page parity (R081 also binds M5-T171) is owed.

ROW D-094-R085 — PASS (evaluative, this task's share)
 - Page-1 visible words fell to 188 (≤200; baseline 330) in my render and the body shrank; the result leads with its assumptions and only the few uncertainties that change it.
 - visual-quality-reviewer PASS at 68d417fe: "Five-second hierarchy is strong" — an architect sees the answer faster, not more explanation.
 - Open: the page-by-page one-minute reader check of the whole report is the final export task M0-T195 (not contracted).

ROW D-094-R089 — PASS (this task's token share)
 - presentation-tokens.json wording.area_zone_apartment = "Apartment area" and area_zone_other = "Other building area: core, circulation, walls and services", both byte-equal to the contract's quoted labels (I compared byte-for-byte).
 - test_presentation_tokens.py (wording group holds the three contract texts) PASSED; the contract states the owner's sentence full stops are not part of the label, so no trailing period is correct.
 - Open: drawing the two labelled zones on the scenario sheet is M5-T173 and the website view M5-T174 (not contracted); this task holds only the label tokens.

ROW D-094-R090 — PASS (this task's token share)
 - presentation-tokens.json wording.area_illustration_caption = "Illustrative area allocation—not a floor plan" with the dash confirmed as U+2014, byte-equal to the contract quote.
 - test_presentation_tokens.py PASSED (caption pinned to the contract quote).
 - Open: the rendered caption on the scenario sheet is M5-T173 and the website view M5-T174 (not contracted); this task holds only the caption token.

(3) BINDING B1–B5
 - B1 PASS: contract commit 574b886e appended "M5-T165" to applicability.task_ids of exactly the 23 rows; the requirements.json diff at that commit shows no change to any row's "text" or "id" (only "+M5-T165" additions).
 - B2 PASS: I recomputed directive_registry.sha256_text_artifact over the frozen-head requirements.json = bdcfaac5f6e14f1cb86589db4b112c66ccada79a90adfd61a1e297f2279e263a, which equals the frozen manifest's requirements_content_digest_sha256 exactly.
 - B3 PASS: verification.json has exactly one M5-T165 task_verification row; applicable_requirement_ids = the 23 cited ids; all 23 requirement entries are state "pending"; verifier is "" and reviewed_sha/reviewed_manifest_sha256 are null.
 - B4 PASS: at the frozen head the set of D-094 rows whose applicability.task_ids contains M5-T165 is exactly the 23 cited ids (applicable == cited).
 - B5 PASS: scanning every directive's requirements.json at the frozen head, only D-094 references M5-T165 (23 raw mentions = the 23 task_id entries); no other active directive applies to this task uncited.
 - GATES: G0 PASS (orchestrator, 485b8ecb), G1 PASS (data-contract-verifier), G2 PASS (orchestrator), G3 PASS (code-reviewer), G4 PASS (qa-engineer); G1–G4 are all recorded at the one content identity 7c831652, and the task's allowed-path files are byte-identical fd649b66→7c831652→c3b3c9ab, so the reviews carry to the frozen head. `python3 tools/validate_directive_compliance.py --check` exited 0 (VALID) at the live head, with `git log -1` showing a stable head (no transient c14).

(4) CARRY-FORWARD CONDITION
 - My PASS verdict may be stamped at a later head WITHOUT a new review while this blob-level predicate holds: every file in M5-T165's allowed_paths keeps the exact blob id it has at c3b3c9ab (the report/ modules, kit presentation_tokens.py, docs/design/presentation-tokens.json, the apps/web token generator + its test, the drawings tests, NB-01, and the producer report), AND the 23 rows' text plus their "M5-T165" applicability binding in D-094 requirements.json are unchanged, AND the verification.json M5-T165 row still carries these 23 ids.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any OTHER file — other wave-24 tasks' source under services/, apps/, packages/, docs/, .claude/; their packets, gates, reports and directive bindings; ledger state; new D-094 amendments/rows for other tasks (e.g. the source-014/015 added after the freeze) — plus this task's own acceptance records and a merge of main that changes none of the predicate's files. None of those void this verdict.

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED or UNVERIFIABLE row; every row's share is satisfied on reproduced primary evidence. The S18 whole-report "tax-map outline" residual is correctly OUTSIDE this task's allowed paths and formally narrowed by scope correction 485b8ecb to DB-245/M5-T167; within this task's texts and the whole of page 1 the GIS wording is clean ("city map outline"), which I reproduced.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The rendered PDF appearance, printed point sizes and PDF page counts: I ran no server and rendered no PDF (read-only; ports untouched). I verified the HTML/CSS source and tokens and relied on the visual-quality-reviewer PASS at 68d417fe for the printed-page fit.
 - The exported-PDF link-destination check (R060 H2) and the whole-report one-minute reader check (R085): both belong to the pass's final export task M0-T195, which is not yet contracted; I verified only the HTML anchor resolution and page-1 word count.
 - The apps/web node token mirror and the report-print e2e: CI/reviewer scope; I confirmed the Python/JSON token side (test_presentation_tokens green; JSON byte values exact) but did not run the node generator or the browser e2e.
 - Live ACRIS / ZR sources: not re-fetched; I relied on NB-01/NB-03/NB-04 saved copies (current 2026-10-11, sha-pinned) and the R6B reference cases, as D-093 permits for current records.
 - Minor observation (not a finding, does not affect the verdict): the frozen G0 gate record's reviewed_sha is 485b8ecb, while the brief also references a 7ab4bda5 G0 re-record; G0 is administrative and PASS, so this does not touch any row or binding.

END-OF-REPORT
```
