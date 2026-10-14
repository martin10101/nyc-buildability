# M5-T171 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `00c8233a3e361143f84c2d8b8e3159037da8773a` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R035, R041, R051, R057, R071, R078, R081, R083.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 04:02 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T171 (directive D-094, 8 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), independent and read-only. This is not a human or professional review. I produced none of the work or records. I read everything through git plumbing at the frozen head and judged each row on primary evidence, treating the producer report, evidence map, reviews and this brief as unverified claims.

(1) HEAD VERIFIED
 - I read the frozen head 00c8233a3e361143f84c2d8b8e3159037da8773a on task/wave24-report-v3 (base main b4704161); it is a valid commit object.
 - The worktree /root/project/w-wave20 advanced to 45a6b1f6 while I worked (as warned); I read every row's evidence from the frozen blob, never the working tree.
 - The task's 8 web/test allowed-path files are byte-identical (same blob ids) at the material commit 2f69ee16, the submit head 79e2bfb9 and the frozen head 00c8233a.

(2) ROWS

ROW D-094-R035 — PASS
 - The block reads the 29 from results.answers.*.legal_unit_limit_standard and labels it via labelForWay (conditional->Conditional); S4 state A and the rendered block show "Legal ceiling 29" with the chip "Conditional", never settled.
 - apartment-figures.ts carries no "Settled"/"Confirmed" word; S4 state J proves a hypothetical settled ceiling would read "Provisional", so the conditional 29 is never promoted to a confirmed entitlement.
 - Reference cases overlay-reading.json and real-lot.json settle the 29 as conditional (20,150/680=29.63->29, resting on the unresolved lot area); the screen keeps the zoning-lot concern beside it and the line "neither is a demonstrated layout".
 - Open: correct handling of residential area/use/exemptions and the unit-limit calculation is engine work (M5-T167 etc.) and the special-density share is M5-T157/M5-T161; this website task only displays the document's conditional value.

ROW D-094-R041 — PASS
 - The website module mirrors report page 1 (page_decision_summary.py): same ceiling cell, estimate cell labelled labels.PROVISIONAL, distinction from the shared token WORDING["ceiling_estimate_distinction"], and the _floor_area_basis composition — one shared structure for this content.
 - The block is placed after the answers summary (answers -> ceiling/estimate -> uncertainties), the same section order as page 1; all figures are read from the same results document, nothing recalculated in TSX.
 - Open: parity for the remaining report sections (site/constraints, option comparison, scenario sheets, evidence) across website and PDF is M5-T174's share.

ROW D-094-R051 — PASS
 - The block orders result first (Legal ceiling 29 / Estimate 17-22), material qualification next (the distinction line), then the lot-area basis line — matching page 1's _answer_cell order.
 - Every figure is read from the document; the website's further detail stays behind existing disclosures and other panel components.
 - Open: the estimate's link to its full calculation (#estimate-B on page 1) is not carried in the website block (the Results window has no scenario sheet) — advisory, deferred to M5-T174 (DB-261); R051's PDF side is already PASS under M5-T165.

ROW D-094-R057 — PASS
 - results-layout.flag-on.spec.ts asserts the block is visible, unclipped, non-overlapping and adds no sideways scroll at 320/390/768/1024/1440/1920; it passed in CI run 38507460363 (web-e2e success).
 - block-notes.txt and the rendered screenshots (block-in-window-1024.png) show the same figures (29, 17-22, 20,150, 10,075, FAR 2.0), labels (Conditional, Provisional), distinction line (byte-equal) and lot-area line (byte-equal, x = U+00D7) as report page-01.png.
 - The zoning-lot caveat appears in both (same facts) but in a fuller form on the website vs page 1's compact index-entry sentence; the estimate's source-reference link is on the PDF, not the website block.
 - Open: byte-level parity of the zoning-lot sentence and the estimate source-reference link, plus cross-section figure/label/source-reference parity, stay open for M5-T174 (DB-261) / M0-T195.

ROW D-094-R071 — PASS
 - S2 scans the block over every committed fixture for buildable/achievable/can be built/feasible/compliant/optimal/preferred/verified/achieved/recommended — none present (CI green); the chip is Conditional and the distinction line says neither figure is a demonstrated layout.
 - The qa-engineer mutation probe (Conditional->PROVISIONAL) made S4 state A fail, proving the Conditional label is load-bearing; the 29 is never shown as a number that can be built.
 - Open: nothing stays open for this task's website share; R071's PDF side is already PASS under M5-T165.

ROW D-094-R078 — PASS
 - The block holds "Legal ceiling 29" beside "Estimate 17-22" with the one-line distinction beneath, confirmed by three-answers-panel.test.tsx (DB-214 N2 reconciliation) and the rendered block-in-window-1024.png — matching report page 1.
 - The literal CEILING_ESTIMATE_DISTINCTION is byte-equal to presentation-tokens.json wording.ceiling_estimate_distinction (S1 reads the token from disk) and ends "neither is a demonstrated layout", so neither figure is presented as a layout.
 - Open: nothing stays open for this task's website share; R078's PDF page-1 side is already PASS under M5-T165.

ROW D-094-R081 — PASS
 - The website results carry the same decision content as page 1: the main answer with its assumption line, the ceiling beside the estimate with the distinction, the lot-area assumption and the zoning-lot uncertainty — the "prominent results + their assumptions" half of R081.
 - The block renders correctly at six widths (CI + screenshots) and reads every figure from the document.
 - Open: the block sits below the first screen at every width (block top 1151-1583 px; advisory, DB-261), and the "one useful site graphic" and the first-page layout rebuild for the website are M5-T174's share; R081's PDF page-1 rebuild is already PASS under M5-T165.

ROW D-094-R083 — PASS
 - The changed website view was rendered from the branch at 97b2a492 and photographed at six widths (after-97b2a492/block-*.png and block-in-window-*.png), which I viewed; the block renders with the figures, chips, distinction and lot-area line.
 - The visual-quality-reviewer's delta review looked at all twelve pictures against the design contract "Change 2026-10-11" and recorded PASS (the one required correction — capture the block — met); block-notes.txt records 0 px horizontal overflow at each width.
 - The web files are byte-identical across the material/submit/frozen heads, so the CI evidence applies to the pictured work; the before set is M0-T194's frozen baseline.
 - Open: the whole-pass before/after set across every changed page is M0-T195's share.

(3) BINDING B1-B5
 - B1 PASS: all 8 rows carry M5-T171 in applicability.task_ids at the contract head 574b886e, and their text/classification/source_ref and task_ids are byte-stable 574b886e->00c8233a; the material commit 2f69ee16 touched only web files + the producer report, not requirements.json. No row text changed by this task.
 - B2 PASS: I recomputed sha256_text_artifact(requirements.json) at the frozen head (CRLF/CR->LF normalize, then sha256) = a6810f2256c7af074f99810dc2191c48332275437da3b8d644954632c646b579, equal to manifest.requirements_content_digest_sha256.
 - B3 PASS: verification.json holds exactly one M5-T171 task_verifications row listing the 8 ids, producer frontend-engineer, verifier "" (empty), every requirement state "pending", reviewed_sha null.
 - B4 PASS: reproducing derive_applicable/evaluate_task_refs across all 94 active directives at the frozen head yields applicable == cited == the 8 rows (missing [], extra []); the packet cites exactly those 8.
 - B5 PASS: no other active directive (D-001..D-094) has a row applicable to M5-T171 that is uncited; there are zero entirely-empty-applicability wildcard rows; nothing matches by task_type (frontend, not governance), milestone or path.
 - Gates: G0 PASS (administrative, re-recorded at the scope-correction head), G2 PASS (orchestrator self-check), G3 PASS (visual-quality-reviewer), G4 PASS (qa-engineer); G2/G3/G4 all at reviewed_sha 79e2bfb9 with the same content_manifest_sha256 c9a195ff (one content identity). CI run 38507460363 at 79e2bfb9 = 21/21 jobs success; validate_directive_compliance.py --check exit 0.

(4) CARRY-FORWARD CONDITION
 - Blob-level predicate: this verdict may be stamped at a later head while these blob ids stay unchanged from 00c8233a — ApartmentFigures.tsx dfe32ff9, apartment-figures.ts c1fa4352, ThreeAnswersPanel.tsx 9e57f1c5, three-answers.css 442af1a8, AnswerCard.tsx 459b43da, apartment-figures.test.tsx aa748f38, three-answers-panel.test.tsx 05ffa820, results-layout.flag-on.spec.ts 074ffee4, M5-T171-producer-report.md fe02b4b5 — AND the 8 rows' text and their M5-T171 binding in requirements.json unchanged (requirements_content_digest a6810f22, or the 8 rows byte-stable).
 - Broad disjoint-peer tolerance: later commits may touch ANY other file — other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets, gates, reports, other tasks' directive bindings, new rows appended to D-094, ledger state — plus this task's own acceptance records (its verification.json row, gates G0/G2/G3/G4, evidence-map, reviews, task status) and a merge of the main line that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-run the web vitest/Playwright suites: the worktree advanced to 45a6b1f6 during my review, so a run would be against a moving tree, not the frozen blobs; I relied on reading the test source at the frozen head, CI run 38507460363 (21/21 success) and the gate records.
 - I did not start/stop any server or touch ports 3000/3001/8000, and did not run the full api suite or tools/test_directive_compliance.py (forbidden); the validator --check (exit 0) and the CI control-plane job are the harness evidence.
 - The six-width pictures are the orchestrator's captures on the private build server; I viewed them and the extracted block text, but did not render the page myself.
 - Whether the below-the-first-screen placement, the fuller zoning-lot wording and the missing estimate link are acceptable to the owner is a design decision deferred to M5-T174 (DB-261); I verified they are documented, not that the owner accepted them.
 - A real-person ten-second usability test was not run (it needs a person).
END-OF-REPORT
```
