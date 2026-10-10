# M5-T151 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `1dd5fb51b8f894f1b009af294a10d5d4d3dbdb63` (branch `task/wave21-report-redesign`, review copy `read in place (/root/project/w-wave20)`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R783, R786, R893, R894, R895, R897, R898, R902, R903, R904, R905, R906, R907, R908, R909, R910, R911, R912, R913, R914, R916, R917, R918, R919, R920, R921, R922, R923, R924, R925, R926, R927, R929, R930, R931.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The two visual required corrections from the first review (C1 apartment-estimate usable-share basis; C2 two sentences stated once) are already applied and I confirmed them on the frozen-head print (report.txt lines 62-63 and 148/326/331) and in the delta attestations.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-10 11:23 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T151 (directive D-090, 35 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is NOT a human or professional review. I produced none of the work or records; I re-derived every item below from primary evidence (code, tests, the printed report, the registry and git objects) at the frozen head. I ran the allowed focused tests and one validator pass; I started no server and touched no ports 3000/3001/8000.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = 1dd5fb51b8f894f1b009af294a10d5d4d3dbdb63 on branch task/wave21-report-redesign; base main d459358a4de6d4fa369e8ec039ba4cc7ac318e9b. Confirmed.
 - The submit/gate head is 88afbb475; `git diff --name-only 88afbb475 1dd5fb51b8f8` touches ONLY project-control/ (gate records, task/report/state json), so the frozen head's material (code/tests/docs) is byte-identical to the reviewed material.
 - The printed report under print-final3/ was generated at the corrected head f28d065f; `git diff f28d065f 1dd5fb51b8f8 -- services/api/app/drawings/report services/api/app/api/v1/report_read.py services/api/app/main.py apps/web/e2e/harness/fixture_api.py docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` is EMPTY, so the print is valid evidence for the frozen head.
 - Focused tests at the frozen head (lanes venv, PYTHONDONTWRITEBYTECODE=1, from services/api): `pytest -q tests/drawings/report tests/api/test_report_read_api.py` = 64 passed. CI run 38047040636 at f28d065f = completed/success, 21/21 jobs success (api ruff+pytest, web-e2e vitest+Playwright, web-dependency-security, modularity, control-plane all green).

(2) ROWS
ROW D-090-R783 — PASS
 - labels.SIX_LABEL_DEFINITIONS (services/api/app/drawings/report/labels.py) carries all six label meanings word-for-word from the row (Verified/Provisional/Illustrative/Conditional/Pending verification/Unresolved); printed page 6 "Status-label key" (report.txt lines 438-452) shows them, with Verified marked "Not used in this report." (F11, not a weakening).
 - test_s8_q1_one_label_per_output_on_every_fixture (passed in my run) asserts every answer value, option row, open item, worked/not-worked building and rendered chip carries exactly one of the six; my grep of report.txt shows "Verified" exactly once (in the key only).
 - Shared with D-090-BOOTSTRAP; stays open in the registry for any later output surface (e.g. the website) beyond this report generator.
ROW D-090-R786 — PASS
 - labels.FORBIDDEN_RESULT_WORDS includes optimal, compliant, feasible, preferred (and achieved, no allowance left unused, recommended); test_s3 scans the whole visible report for them.
 - My independent `grep -Eio 'optimal|compliant|feasible|preferred|...' report.txt` returned none on the actual printed report.
 - Stays open in the registry; the website's own enforcement of this prohibition is M5-T153's share.
ROW D-090-R893 — PASS (this task's share)
 - page_site_context.py places the site plan with ONE caption and NO notes column; the constraints are a table, not a prose column; the page is A4 (visual review pdfinfo 594.96x841.92 pt).
 - The street names/context drawn INSIDE the drawing (Northern Boulevard, 215 Place, edge dimensions, reduced legend) are visible on page-2.png / report.txt lines 92-124; that in-drawing content is produced by the kit (M5-T152), to which this row is also bound.
 - Stays open: the drawing-kit street/context rendering is verified as present but owned by M5-T152; this task's page-composition share is satisfied.
ROW D-090-R894 — PASS (this task's share)
 - page_option_comparison.py builds a concise table (Option | Floor-area allowance | Scheduled building | Status | Limitation-number) with shared limitations stated once above it; page-3.png confirms no crowded repeated-state headings.
 - options.py holds the eleven options and one wording per situation; the "limitation or next requirement" is a single numbered reference.
 - Stays open: the website's comparison (R894 also binds M5-T149/M5-T153) is not this task's surface.
ROW D-090-R895 — PASS (this task's share)
 - labels.scheduled_floor_area_line emits "Scheduled floor area: N sq ft; site fit unverified"; it appears 4x in report.txt (decision summary, option row, worked-buildings list, scenario sheet) before any caveat; "achieved"/"no allowance left unused" are in FORBIDDEN_RESULT_WORDS and absent from the print (my grep).
 - test_s3 / test_d6 assert the single phrase and no forbidden words (passed).
 - Stays open: the website application of this wording (R895 also binds M5-T148/M5-T149/M5-T153).
ROW D-090-R897 — PASS
 - test_s6_no_min_base_contradiction (passed) and my read of pages 2/4: lot areas are reconciled (recorded 10,075 used in every calc; tax-map outline 10,387.99 shown and stated to disagree), Building B is "the fewest storeys reaching the minimum base height" with no "below" note.
 - test_vc2_no_long_document_sentence_printed_twice (passed) proves no page-to-page duplicated claim; the visual delta attestation confirms C2 corrections removed the two repeated sentences.
 - Stays open: nothing material for this task; registry row remains for future report changes.
ROW D-090-R898 — PASS
 - S4 scan (test_s4 benchmark+partial, passed) plus my independent grep of report.txt found no HTTP/status-code/implementation/internal-id wording; sources.py gives readable titles shown on page 6.
 - The coverage inventory lists Context maps under "Not yet" (report.txt line 76), so no page claims an output the report omits; no page is overloaded.
 - Stays open: residual trailing white space on pages 1/3/4 is a cosmetic note (no page is overloaded; the v5a page-2-empty/page-3-overloaded imbalance is resolved); registry row remains.
ROW D-090-R902 — PASS
 - The report is reorganised into six purpose-named page types around the four reader questions (builder.py page order; test_s1 passed), with status reduced to label chips and shared-limitations-once, so repeated status no longer dominates.
 - Page 1 keeps the v5a decision-summary approach (property + three answers + compact site plan); page-1.png confirms.
 - Stays open: "reads without repeated status" is partly a visual judgement; the human ten-second test (below) was not run.
ROW D-090-R903 — PASS (this task's share)
 - report_read.py serves POST /api/v1/properties/{bbl}/report from the SAME results document (delegates to results_read.post_results), built by the report package — the correction is in the program's own generator, not a hand-made sample; report-request.txt shows a real 200 from the route.
 - test_report_read_api (passed) proves the route returns the full HTML report.
 - Stays open: the "matching website components" half of R903 is M5-T153's share (also bound there).
ROW D-090-R904 — PASS
 - The page modules open with the four reader questions in order — "What can I potentially build?", "What constrains the design?", "How do the options compare?", "What remains unresolved, and what would resolve it?" (QUESTION constants in page_decision_summary/page_site_context/page_option_comparison/page_assumptions); test_s1_six_page_types_in_order asserts the questions appear in order (passed).
 - report.txt lines 14/86/160/302 show the four questions in sequence on the print.
 - Stays open: nothing; fully this task's share.
ROW D-090-R905 — PASS
 - Each page carries a type-name, its reader question, then the answer/limitation, plus a fitting visual/table: page1 answers table+site plan, page2 lot-basis+site plan+constraints, page3 options+bar chart, page4 scenario+floor-stack, page5 assumptions+open-items, page6 inputs+law tables (confirmed on page-1..6.png).
 - test_s1 / test_f7 / S2 furniture tests (passed) back the structure.
 - Stays open: the "immediately visible" quality is partly visual; human timing test not run.
ROW D-090-R906 — PASS
 - page_evidence.py holds provenance/reproducibility on page 6; page_assumptions.py puts each open item's full reason beneath its short effect in smaller type (reason-row), not in the main reading path; test_f8/test_a3 (passed) confirm.
 - My read of pages 5/6 confirms supporting explanation sits beside the result or in evidence, not in the headline.
 - Stays open: nothing; this task's share.
ROW D-090-R907 — PASS
 - formatting.py types no number and readers.py reads every figure from the document; test_s9_every_number_comes_from_the_document (passed) proves every visible number traces to the results document, so no competitor figure enters as a fact.
 - My grep of report.txt found no competitor-sourced value; the only external references are the ZR law links.
 - Stays open: nothing; this task's share.
ROW D-090-R908 — PASS
 - The report keeps all eleven options (options.ELEVEN_OPTIONS; test_s5 asserts ordinals 1..11) and all six page types plus a nine-contents coverage inventory (coverage.py), so scope is preserved with no page-count target.
 - test_s10 (partial data, passed) shows every page type still prints with a short limitation line rather than dropping content.
 - Stays open: nothing; this task's share.
ROW D-090-R909 — PASS
 - Every page type is a reusable layout module (page_decision_summary/page_site_context/page_option_comparison/page_scenario_sheet/page_assumptions/page_evidence) defined before build_report_html assembles them, and recorded in the presentation contract's page-type table before full generation.
 - The contract change (git numstat 29/0) records the page-type definition ahead of the generator.
 - Stays open: nothing; this task's share.
ROW D-090-R910 — PASS
 - Six reusable page modules exist, one per named page type, each exporting render(...) (confirmed by reading the six files); builder.py composes exactly these six.
 - test_s1_benchmark_has_six_pages / test_s10 (passed) confirm all six render.
 - Stays open: nothing; this task's share.
ROW D-090-R911 — PASS
 - Every page uses the same layout system (type-name, reader question, label chips, shared print CSS in layout.py), not only the first pages; all six pages in page-1..6.png share the design.
 - test_s2 and test_a2 (passed) check the one stylesheet applies throughout.
 - Stays open: nothing; this task's share.
ROW D-090-R912 — PASS (this task's share)
 - drawings_embed.py embeds real kit drawings (site plan, floor-stack section) and the report's own bar chart; test_a1 on the route (>=3 SVGs under the drawing flag, passed) and page-2/3/4.png confirm real dimensions, diagrams and a schedule.
 - Maps are not produced on this route's inputs path, so the report omits them and the coverage inventory says "Not yet" rather than inventing them.
 - Stays open: the drawings themselves are M5-T152's; map production on the report route remains future work (documented limitation under R923).
ROW D-090-R913 — PASS (this task's share)
 - When a drawing is unavailable the page prints ONE short line, never prose blocks or an invented shape (components.figure line_when_absent; drawings_embed returns Embedded(short_line=...)); test_s10 asserts "<svg" is absent and the site line names the missing site plan on partial data (passed).
 - My read of readers.py confirms a missing value stays missing (no computed/invented figure).
 - Stays open: the kit-side "no invented geometry" is also M5-T152's; this task's placement/fallback share is satisfied.
ROW D-090-R914 — PASS (this task's share)
 - layout.report_css sets `@page { size: A4 portrait; margin: 14mm }` and no other size; test_s2 asserts A4-only and rejects A3/A5/Letter/legal/Tabloid; all six printed pages are A4 (visual-review pdfinfo 594.96x841.92 pt).
 - test_a2 proves no non-drawing CSS rule is below 8pt and test_d1_d2 proves embedded SVGs are stamped width/height in pt == viewBox so nothing is shrunk; drawing labels >=7pt.
 - Stays open: the site drawing's own legibility at the report frame is M5-T152's; this task's page-size/no-shrink share is satisfied.
ROW D-090-R916 — PASS
 - page_evidence.py carries provenance (revision, computed date, rule versions, label-basis) and the label key on page 6; page_site_context.py carries no provenance detail (readers.label_meta_statement is moved to the evidence page per F9).
 - report.txt pages 2 vs 6 confirm detailed provenance sits on the evidence page, not the site page.
 - Stays open: nothing; this task's share.
ROW D-090-R917 — PASS (this task's share)
 - The option table shows all eleven options with available result (allowance), scheduled building, Status label and a material-limitation NUMBER — no seven-column "not computed/not worked/pending verification/outputs owed" repetition (page_option_comparison._option_rows; page-3.png); my grep found no "owed".
 - test_f7 asserts the Limitation cell holds the number only and the shared-limitation columns are gone (passed).
 - Stays open: the website comparison (R917 also binds M5-T153). Residual: "Not produced yet"/"None scheduled" recur down rows 4-11, differentiated by limitation number (much reduced; meets the requirement).
ROW D-090-R918 — PASS (this task's share)
 - options.shared_limitations numbers each shared sentence once; test_s5 asserts every shared-limitation sentence count==1 across the whole report (passed); report.txt lines 162-168 list Limitations 1-5 once, referenced by number in the table.
 - test_vc2 confirms no shared sentence prints twice.
 - Stays open: the website's shared-limitation handling (R918 also binds M5-T153).
ROW D-090-R919 — PASS
 - No page is overloaded (the oversized sheet is gone; all A4, no 5pt text) and the former near-empty/overloaded v5a pairing is resolved — the near-empty coverage sheet was folded into page 1 (coverage block on the decision summary).
 - Pages 1/3/4 carry trailing white space but none is "mostly empty while another is overloaded"; the visual review assessed this page by page and I confirmed on page-1..6.png.
 - Stays open: trailing white space is a cosmetic refinement; registry row remains.
ROW D-090-R920 — PASS (this task's share)
 - page_site_context._lot_area_basis prints the document's own sentence naming the recorded lot area (10,075 sq ft, used in calcs) and the tax-map outline area (10,387.99 sq ft) and that they disagree; readers.lot_area_basis reads it from the document, nothing retyped (test_s7 passed, report.txt lines 88-89).
 - The drawing shows the tax-map outline (103.88x99.98 ~= 10,386) and is not reshaped to the preferred figure; the caption names the tax-map basis.
 - Stays open: the measured-outline drawing is M5-T150/M5-T152; this task's "name which area each figure uses" share is satisfied.
ROW D-090-R921 — PASS (this task's share)
 - test_s6_no_min_base_contradiction asserts no "below the minimum base height" text unless the document says so of that building, and test_s6_below_min_base_only_when_document_says_so proves the note appears only on injection (both passed); the print says Building B reaches the minimum base height, with no contradicting note.
 - readers.worked_buildings carries below_min_base straight from the document; page_scenario_sheet only prints the note when it is True.
 - Stays open: the floor-stack min-base line is drawn by M5-T152; this task's text-consistency share is satisfied.
ROW D-090-R922 — PASS (this task's share)
 - The scheduled-area wording "Scheduled floor area: 20,150 sq ft; site fit unverified" is used while checks are incomplete; "achieved"/"no allowance left unused" are forbidden and absent (FORBIDDEN_RESULT_WORDS; test_s3; my grep of report.txt).
 - Same evidence as R895 on the PDF side.
 - Stays open: the website application (R922 also binds M5-T152/M5-T153).
ROW D-090-R923 — PASS (this task's share)
 - coverage.py lists Context maps as "Not yet in this report" unless a map document renders; builder.py builds no maps section when none is present, and the route builds no map document, so the inventory does NOT claim maps it omits (report.txt line 76).
 - test_q3_coverage_and_maps_with_and_without_a_map_document (passed) exercises both branches (no-map => "Not yet"; monkeypatched maps => "In this report" + SVG).
 - Stays open: actually producing the context maps on the report route is future work; the map rendering itself is M5-T152's.
ROW D-090-R924 — PASS (this task's share)
 - html.py escapes all text via stdlib html.escape; the report carries no HTTP checks, implementation notes, internal identifiers, owner-question references or backlog words — test_s4 scans HTTP/snake_case/null/true/false/None/DB-/R\d{3}/M\d-T\d/question C1-D1-B6 (passed) and my independent grep of report.txt found none.
 - sources.py converts raw rule/fact ids to readable titles so no snake_case or raw id reaches the reader.
 - Stays open: the website's and drawings' own freedom from developer wording (R924 also binds M5-T152/M5-T153).
ROW D-090-R925 — PASS
 - page_evidence.py keeps the inputs, their sources, the law links and the status-label key accessible on page 6; sources.readable_* yields readable source titles (report.txt page 6 shows "City tax-lot record", "New York City Zoning Resolution, Section 23-22", etc.).
 - test_f11 asserts the readable input names and law sections are present (passed).
 - Stays open: nothing; this task's share.
ROW D-090-R926 — PASS
 - readers.provenance + page_evidence._provenance put revision, computed date, rule versions and the label-basis statement into the evidence page (report.txt lines 428-436); no developer diagnostics appear in the report (S4).
 - test_f11 / test_s4 (passed) back this.
 - Stays open: nothing; this task's share.
ROW D-090-R927 — PASS (this task's share)
 - The report is produced by reusable presentation modules (services/api/app/drawings/report/*) and the route, not a hand-polished sample; the diff adds the report package and its tests, and report-request.txt shows the real route emitting the report.
 - No separate hand-made HTML sample is shipped as the deliverable.
 - Stays open: the website/drawings reusable logic (R927 also binds M5-T152/M5-T153).
ROW D-090-R929 — PASS (this task's share)
 - The full current-scope PDF was generated from the real route (report-request.txt: POST .../report 200) and every page rendered at A4; I inspected all six page images (page-1..6.png) and the visual reviewer rendered at 150 dpi.
 - report.pdf is 6 A4 pages; the generator is this task's package.
 - Stays open: the website print action is M5-T153's; the human render-and-inspect quality judgement is advisory.
ROW D-090-R930 — PASS (harness)
 - The inspection was done by looking at the pages, not by automated checks alone: the visual-quality-reviewer reviewed page by page (G3G4 record, Return 3) and I independently viewed page-1..6.png for legibility, overlaps, table breaks, repeated content, contradictions and whether each visual answers its page's question.
 - Automated backing exists too (test_a2/test_d1_d2/test_s2/test_vc2), but the row's "by looking" requirement is met by human-style visual review.
 - Stays open: the explicit ten-second test with a real architect and a real screen-reader pass needs a person and was NOT run (recorded as such); registry row remains.
ROW D-090-R931 — PASS (this task's share)
 - The presentation contract is updated in place additively (git numstat 29 insertions / 0 deletions; the "### Change 2026-10-10: report page types (D-090 source-081, rows R900 to R933)" block records the page-type definition and the report code paths; the adopted brief below its marker is byte-identical) — no competing guidance created (S13; test team verified 0 deletion lines).
 - This task's allowed_paths include only the contract, not CLAUDE.md or SESSION_HANDOFF.md.
 - Stays open: the "relevant project instructions and normal session handoff" updates are the orchestrator's seam work, outside this task's scope; registry row remains until those are done.

(3) BINDING B1–B5
 - B1 PASS. requirements.json base(899)->frozen(933): rows R900–R933 are ALL newly added (0 removed); they equal the source-081 reading (each new bound row's classification matches the amendment's Reading table, verified). The 7 pre-existing bound rows (R783, R786, R893, R894, R895, R897, R898) have IDENTICAL text and classification vs base; only applicability.task_ids gained M5-T151 (and, where listed, M5-T152/M5-T153). All 35 bound rows contain M5-T151. The only post-capture edits to the new rows are the recorded digest resyncs in manifest.audit_log (capture 2026-10-10T07:25:55; bind 2026-10-10T07:36:29).
 - B2 PASS. directive_registry.sha256_text_artifact(requirements.json) = 030652450f861cc0b4785cb8b44f6867c6e734cbbf453b58c9211727dbacdaa8 equals manifest.requirements_content_digest_sha256 (exact match).
 - B3 PASS. verification.json has exactly one M5-T151 entry listing these 35 requirement ids, each status null (pending) and verifier null (empty); reviewed_sha null. No producer self-attestation of PASS exists in it.
 - B4 PASS. reg.evaluate_task_refs(M5-T151) returns ok=true, applicable_ids == cited_ids (the 35 rows exactly), missing_ids=[], invalid_refs=[], unresolved=[].
 - B5 PASS. missing_ids=[] confirms nothing else across the active directives applies to this task uncited. Gate records: G0 PASS (orchestrator, head 87e13f6e), G2 PASS (orchestrator self-check, head 88afbb47), G3 PASS (code-reviewer, 88afbb47), G4 PASS (qa-engineer, 88afbb47) — G2/G3/G4 at one content identity (88afbb47), recorded after CI succeeded at the corrected head f28d065f (run 38047040636, 21/21). `validate_directive_compliance.py --check` exit 0.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided: the blob ids of services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, docs/design, apps/web/src, apps/web/e2e, apps/web/scripts, render.yaml, .github, tools, CLAUDE.md, .claude/rules and this task's reports are unchanged from the frozen head, AND the rows' text and binding (B1–B5) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of M5-T152/M5-T153 on this branch, and a merge of the main line that changes none of the predicate's files. At the frozen head 1dd5fb51 the predicate holds: the only commits above the reviewed material (88afbb47 -> 1dd5fb51) add project-control gate/state/report files, and f28d065f -> 1dd5fb51 touches project-control only.

(5) REQUIRED CORRECTIONS
 - None. The two visual required corrections from the first review (C1 apartment-estimate usable-share basis; C2 two sentences stated once) are already applied and I confirmed them on the frozen-head print (report.txt lines 62-63 and 148/326/331) and in the delta attestations.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The ten-second hierarchy test with a real architect and a real screen-reader pass: needs a person; NOT run (recorded as such). R930's "by looking at the pages" requirement is met by AI visual review; this human test is an advisory extra, not a blocker.
 - Website behaviour (the matching-components halves of R903/R894/R895/R917/R918/R922/R924/R927/R929 and R928): outside this task's files; owned by M5-T153 and not verified here.
 - The drawing-kit internals that render street names, the measured outline, the floor-stack and the report-frame sizing (the kit halves of R893/R912/R913/R914/R920/R921/R923): owned by M5-T152; I confirmed their OUTPUT is present and correct in the printed report but did not re-verify the kit code as this task's share.
 - I did not start any server or run Playwright; I relied on the orchestrator-captured print-final3/ artifacts (whose material I proved byte-identical to the frozen head) and on CI run 38047040636 for the full api/e2e suites.
END-OF-REPORT
```
