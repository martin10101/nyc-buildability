# M5-T162 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `b11e327b39af91fee7a680afa5abbf49d180eb23` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-090, D-093, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R569, R584, R007, R057, R058.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 10:25 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T162 (directives D-090, D-093 and D-094, 6 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only, independent gate — not a human or professional review. I produced none of this work. I ran validate_directive_compliance.py --check (exit 0) and research_record_check.py --check (exit 0) once each, the focused test file, and git/gh read-only plumbing against the frozen head.

(1) HEAD VERIFIED
 - Frozen head b11e327b39af91fee7a680afa5abbf49d180eb23 on task/wave23-density-zoning-lot; every read used explicit `b11e327b:<path>` plumbing.
 - During review the worktree HEAD advanced to peer commit 3fcbec86 (branch tip); b11e327b is an ancestor of it, so my frozen-head reads are unaffected.
 - 3fcbec86 changes only docs/DISCOVERY_BACKLOG.md (adds DB-239 page-1 row, DB-240 lint gap) — a disjoint doc peer, within the carry-forward tolerance.

(2) ROWS

ROW D-090-R229 — PASS
 - unit_limit_text.shown_legal_unit_limits reads only readers.present_values (which excludes way=="withheld" / non-mappings); an absent or "malformed" block yields answer_block()->{} and no shown value (verified by test_malformed_or_absent_allowance_block_is_not_shown, which I ran green).
 - "conditional" is set only when value_states[key].way=="conditional"; a missing or other state gives way=None -> conditional False (readers line 90-91), so a shown limit without a recorded state is never called conditional (test_no_value_states_entry_is_shown_plainly / _non_conditional pass).
 - legal_unit_limit_item names each withheld program as "not known" and uses NO_LIMIT_SENTENCE only when nothing is shown; the benchmark fixture confirms affordable/senior way=="withheld", standard way=="conditional".
 - Nothing stays open for this row.

ROW D-090-R569 — PASS
 - The diff touches only the "Legal apartment limit" open item and coverage entry "F" (Legal unit limits); coverage "G" (the preliminary apartment estimate: "the worked building only"/"no estimate") is byte-unchanged in coverage.py, so legal limit and estimate keep separate labels and places.
 - The G3 before/after HTML diff (reproduced in the review) shows exactly 5 changed regions, none of them the estimate line or any figure.
 - Each legal dwelling-unit limit is named by its own program (standard residences / qualifying affordable / qualifying senior); neither appears under the estimate's name.
 - Page-1 answer-table row for the legal unit limit stays open (report redesign P-3, DB-239) — not this task's scope.

ROW D-090-R584 — PASS (hold honored)
 - git diff 4b791266..b11e327b touches only the 5 report code/test files + the producer report + ledger files; no flag, config, render.yaml, .github or .claude path is touched (all in forbidden_paths).
 - The change is report wording built from the results document; no production switch is flipped and no hidden feature is emitted or displayed.
 - This is a prose change only, so the existing activation restrictions are preserved intact.
 - Nothing stays open for this row.

ROW D-093-R007 — PASS
 - No property number changes: readers.py and coverage.py diffs alter only text, no numeral; the derivation figure 29 and floor-area values live in the untouched scenario engine (forbidden_paths services/api/app/scenario/) and the unchanged fixture.
 - Unresolved inputs stay unresolved: affordable and senior remain "not known", standard stays conditional; the test asserts "29" is absent from the effect text (shown only on the derivation table).
 - No approval boundary is changed; research_record_check reports NB-05 status answered_from_primary_source, code_current True, review_state current.
 - I opened NB-05's cited primary excerpts (ZR 12-10 special density areas = Manhattan Core + Special Downtown Brooklyn; ZR 23-52(a)(2) senior = no factor, (b) factor 680; MapPLUTO Queens lot 70 R6B) — they corroborate the shown-conditional / withheld structure; nothing stays open.

ROW D-094-R057 — PASS (this task's share)
 - The report HTML is the single shared source both the PDF print and the website preview render; the task removes the contradiction where the PDF denied a figure page 8 shows.
 - test_s5_guard_no_denial_while_a_limit_is_shown builds the real HTML and asserts neither "No legal apartment limit is shown." nor "the legal unit limit is withheld" appears, on the decision-summary slice and the open-items slice (I ran it green).
 - The full R057 harness — rendering website at desktop/mobile sizes and confirming identical figures/labels/caveats/source refs in both rendered outputs — is not this task's deliverable and I cannot render it; it stays with CI/the orchestrator at the accept head.
 - The page-1 answer table still lacks a legal-unit-limit row (DB-239, report redesign P-3) stays open.

ROW D-094-R058 — PASS (this task's share)
 - The legal unit limit is stated accurately and apart from the apartment estimate: shown for standard residences as a conditional ceiling only when its own state is conditional, otherwise "shown for" plainly (unit_limit_text.legal_unit_limit_item lines 133-146; test_way_* pass).
 - Qualifying affordable and qualifying senior are kept distinct, each with its own reason and resolver read verbatim from the document (reason/resolve built per withheld row, lines 147-162; S1 test asserts both programs' strings).
 - The five result families stay distinct: this change moves no allowance, scheduled-area, site-fit or estimate text (G3 HTML diff: only the legal-limit item and coverage F moved).
 - The on-page-1 distinctness of the legal unit limit (its own answer-table row) stays open to DB-239 / P-3.

(3) BINDING B1–B5
 - B1 PASS: at contract commit e534dbdb the only requirements.json edits are M5-T162 appended to applicability.task_ids for R229, R569, R584 (D-090), R007 (D-093), R057, R058 (D-094) plus an updated_at bump; no row text changed. Registry files are unchanged from e534dbdb to b11e327b.
 - B2 PASS: dr.sha256_text_artifact(requirements.json) == manifest.requirements_content_digest_sha256 for all three (D-090 a1f1e85f…, D-093 49bb8596…, D-094 54edc0bd…).
 - B3 PASS: each directive's verification.json has exactly one M5-T162 row, schema v2, producer backend-engineer, verifier "", every requirement state "pending", evidence [] — D-090 {R229,R569,R584}, D-093 {R007}, D-094 {R057,R058}.
 - B4 PASS: reg.evaluate_task_refs(packet) -> ok True, applicable_ids == cited_ids == the 6 rows, missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: applicable_ids are exactly those 6; nothing else across active directives applies uncited. Gates: G0 PASS (reviewed_sha d91686fc), G2 PASS (self-check, orchestrator), G3 PASS (code-reviewer), G4 PASS (qa-engineer); G2/G3/G4 share one content identity content_manifest_sha256 febee0f8… at reviewed_sha 6a359553. The 5 reviewed code/test files + producer report are byte-identical (same blob ids) across cc794c74 (review), 6a359553 (submit/gate) and b11e327b (frozen).

(4) CARRY-FORWARD CONDITION
 - My PASS may be stamped at a later head without re-review while the blob-level predicate holds: coverage.py, readers.py, unit_limit_text.py, test_report_pages.py, test_report_unit_limit_text.py and M5-T162-producer-report.md keep their b11e327b blob ids, and the 6 rows' text and their M5-T162 applicability binding are unchanged (digests still match their manifests).
 - Broad disjoint-peer tolerance: later commits may touch any other file — other tasks' source under services/, apps/, packages/, docs/ (the DB-239/DB-240 backlog sweep 3fcbec86 already did), their packets/gates/reports/bindings, ledger state — plus this task's own acceptance records and a merge of the main line that changes none of the predicate files. Such commits do not void this verdict.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not render the actual PDF or start any server / open the website at desktop or mobile sizes (forbidden: ports 3000/3001/8000); the end-to-end website-vs-PDF parity harness of R057 is the orchestrator's/CI's at the accept head.
 - I did not run the full services/api suite or tools/test_directive_compliance.py (forbidden). I ran only the focused tests/drawings/report/test_report_unit_limit_text.py (10 passed) and relied on the G4 full-suite run (1658 passed) and CI run 38130904594 at cc794c74 (21/21 jobs success) — valid for b11e327b because the reviewed files are byte-identical there.
 - I read NB-05's primary-source excerpts and their sha256-pinned saved snapshots as embedded in the evidence record; I did not re-fetch ZR 12-10 / 23-52 from the live NYC portal or re-verify those snapshot digests against the portal.
 - The underlying legal interpretation (that lot 70's zoning-lot scope keeps the standard limit conditional) is a research/professional matter the record marks for that path, not a directive-compliance item I verify.

END-OF-REPORT
```
