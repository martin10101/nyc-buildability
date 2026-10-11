# M5-T160 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `ddf844ca31f931a3a6d43c31465a32bc735984bc` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-093, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R038, R050, R043.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 06:11 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T160 (directives D-093 and D-094, 3 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent control-plane and source-provenance check, not a human or professional/legal review; a reading of zoning law in NB-06 ships as a labelled unreviewed draft (ADR-007) and I certify no zoning conclusion.

(1) HEAD VERIFIED
 - I read the frozen head ddf844ca31f931a3a6d43c31465a32bc735984bc via git plumbing (`git -C /root/project/w-wave20 show ddf844ca:<path>`), not the working tree.
 - The w-wave20 worktree HEAD is 0330d598 (M5-T159 builder, a disjoint later peer on task/wave23-density-zoning-lot); `git diff --stat ddf844ca 0330d598` over the directive dirs, NB-06, and all M5-T160 reports is empty, so the two checks I ran at 0330d598 validate byte-identical content. Worktree is clean (`git status --short` empty).

(2) ROWS
ROW D-093-R038 — PASS
 - NB-06 is one concise research_record/v1 record (keys: question, evidence, meaning_and_applicability, measurement_basis, conclusion, searches, implementation, review, freshness, promotion); question carries scope (property BBL 4073340070, lot_scope zoning_lot_unconfirmed, site_scope building, time_scope current_law).
 - Primary evidence = 16 items, each with authority, title, url, reference/section id, page, document_date, retrieved date, excerpt, saved_copy and sha256; permitted source material is saved under docs/research/zr-snapshots/v1/ (the established evidence location) plus the DCM data file.
 - I recomputed the sha256 of all 16 saved copies from the frozen-head blobs: every one is a RAW match to the declared digest; `python3 tools/research_record_check.py --check` → exit 0, NB-06 structurally valid.
 - Nothing of R038 stays open: the record is complete and provenance-matched.

ROW D-093-R050 — PASS
 - An independent reviewer (data-contract-verifier, ≠ producer official-source-researcher) performed G1; its full return is in project-control/reports/M5-T160-reviews.md and its entry is copied into review.agent_reviews of the record.
 - The reviewer opened the decisive captures and worked Q1/Q2/Q3 from them before reading the record's interpretation, and caught a real reading error (round-1 Finding 1: conditions[0] wrongly named the 35-631(a) line-up and glossed "prevailing street wall frontage" with the 23-431(a) eligibility test); it is not a restatement of the builder.
 - Revision 2 fixed F1 (added E16 = ZR 12-10 prevailing-street-wall-frontage, named the 23-431(a) fallback) and the reviewer re-verified in a delta review (verdict agrees, PASS at b544a4b3).
 - Nothing of R050 stays open for this task; professional/legal verification remains a separate ADR-007 matter, correctly not claimed.

ROW D-094-R043 — PASS (this task's share only)
 - M5-T160's share is the "relevant constraints" of the one meaningful spatial example; the record researches them and I verified each against the primary captures: street wall = 35-631(b) via the overlay chain 34-11→34-24(b)(1)→35-63→35-631 (residential-only) and 35-01→35-63 (mixed), 70% of each frontage within 8 ft of the street line, with 35-631(a) confirmed inapplicable (R8–R12 Manhattan Core only).
 - Setback: 23-432 R6B table row = 30/45/55 ft (I pulled the structured row); 23-432/23-433/35-632(a) trigger a setback only for street wall above the 45 ft maximum base height, so a building at or below it (incl. the 30 ft benchmark) needs none — depth 10 ft wide / 15 ft narrow applies only above 45 ft.
 - Side yards: 23-335(b) requires none for R6B residences other than single/two-family detached; 34-232 removes it for any residential building in C1–C6; optional with a 5 ft minimum. All faithful to the captured text.
 - What stays open: the placed footprint, section/massing and reconciled schedule of the full spatial example are later tasks (D-094 plan P-6.1–P-6.3); the record keeps an explicit incomplete state (research_status interpretation_awaiting_review, promotion.requested_label null, conditions unresolved for prevailing-street-wall-frontage adjacency and the operative street-line position).

(3) BINDING B1–B5
 - B1 PASS: contract commit e3ea1427 appended only "M5-T160" to applicability.task_ids of D-093-R038, D-093-R050 and D-094-R043 (and bumped updated_at); no requirement body changed. The requirements.json blobs are byte-identical at e3ea1427 and ddf844ca (D-093 6c0074d84..; D-094 a6470fc63..).
 - B2 PASS: I recomputed, from the frozen-head blobs, requirements_content_digest = sha256(LF-normalized file) and requirements_id_digest = sha256(sorted ids joined by \n); both match each manifest (D-093 2a6e30d6../796fbc27..; D-094 3c446844../f74274df..). All three source content_digest_sha256 (D-093 source-001 f0cb7376.., source-002 d5cd38ee.., D-094 source-001 2713f603..) match too.
 - B3 PASS: each verification.json has exactly one M5-T160 task row — D-093 with applicable ids [R038,R050], D-094 with [R043] — verifier "" (empty), reviewed_sha null, every requirement row state=pending; producer recorded as official-source-researcher (the material producer).
 - B4 PASS: `reg.evaluate_task_refs(M5-T160 packet)` → ok=True, applicable_ids == cited_ids == [D-093-R038, D-093-R050, D-094-R043], missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: I scanned every directive dir at the frozen head; the only requirements with M5-T160 in applicability.task_ids are those three. `python3 tools/validate_directive_compliance.py --check` → exit 0. Gates: G0 PASS (reviewer orchestrator, reviewed_sha e3ea1427 = contract head), G1 PASS (data-contract-verifier, reviewed_sha bb8e335b), G2 PASS (self-check recorded by orchestrator, reviewed_sha bb8e335b); G1 and G2 share the one content identity bb8e335b (the submit head).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while: (predicate) the M5-T160 allowed-path files keep their frozen-head blob ids — docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json, docs/research/evidence-records/README.md, project-control/reports/M5-T160-producer-report.md — and the three rows' text plus their M5-T160 applicability binding stay unchanged (requirements.json blobs D-093 6c0074d84.., D-094 a6470fc63.., and both manifest digests unchanged).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/ including other evidence records, their packets/gates/reports/directive bindings, ledger state), this task's own acceptance records (reviews, evidence map, gate records, verification rows), and a merge of main that changes none of the predicate files. The present head 0330d598 (disjoint peer M5-T159) already meets this.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The verbatim ZR 12-10 "street, narrow"/"street, wide" definitions are not in the repo snapshots (the live page truncates before them, as the record's S3 condition states). I confirmed the DCM mapped widths (Northern Boulevard 100, 215 Place 60) from the E15 data file; the wide/narrow classification then rests on the owner-approved D-052 policy — correctly left as a documented open item with a print/PDF-capture next step. I did not fetch live sources (read-only, no network).
 - Past/live events: the E15 HTTP Last-Modified header, any live DCM/ZR re-fetch, the block's "prevailing street wall frontage" adjacency, and the operative street-line position — all correctly left unresolved in the record; I verified saved content + SHA only.
 - The captures are HTML-channel snapshots (extraction_status extracted_draft), not print/PDF-class; I verified content and sha256 against the saved copies, not against an independent re-fetch.
 - Legal correctness of the 34-11→34-24(b)(1)→35-63→35-631(b) cross-reference chain is an ADR-007 professional matter outside this gate; I verified the reading is internally faithful to the captured text, nothing more.
 - Per the brief I did NOT run tools/test_directive_compliance.py or the full api suite (CI's job); my harness evidence is validate_directive_compliance.py --check (exit 0) and research_record_check.py --check (exit 0).
END-OF-REPORT
```
