# M3-T013 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `da17857ad33e5ffbbe68da3185a033107c230a82` (branch `task/wave28-placement-wiring`, review copy `git plumbing at the frozen head`). Directives D-093. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R043, R051, R052.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No row is VIOLATED or UNVERIFIABLE. - Two non-blocking advisories (carried from G3, not directive defects, recorded only): (a) a `tables` value that is not a list and an empty/non-string table_digest beside a payload have no dedicated unit test — but I confirmed the loader code raises on both paths (snapshots.py "'tables' payload is not a list" and "table payload present but no table_digest_sha256"), so behavior is covered; (b) the packet documented_test_commands/S7 and the producer report name tests/rules/test_r6b_reference_cases.py whereas the real path is tests/rules/reference_cases/test_r6b_reference_cases.py (the test was actually run at the real path). Neither affects any row's compliance.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T18:48:09Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M3-T013 (directive D-093, 3 rows)
VERDICT: PASS

I am an AI agent. This is an automated, independent, read-only directive-compliance verification — not a human or professional legal review. I produced none of the work or records under review; every finding below I re-derived from primary evidence (owner source files, the loader/test source, the snapshot bytes, git objects, the registry helpers), not from the producer map, reviews or this brief.

(1) HEAD VERIFIED
 - I read the frozen head da17857ad33e5ffbbe68da3185a033107c230a82 on task/wave28-placement-wiring in /root/project/w-wave20 via git plumbing; `git rev-parse HEAD` = that sha and the working tree is clean.
 - `python3 tools/validate_directive_compliance.py --check` run once at that head returned exit 0 (quiet-on-success); `git log -1` confirmed the head unchanged across the run (no transient c14).
 - The task's allowed-path files are byte-stable between the gate head 7785d0de and da17857a: `git diff --name-only 7785d0de da17857a` touches ONLY M3-T013 control-plane files (gates, evidence-map, reviews, packet, state), no material file.

(2) ROWS

ROW D-093-R043 — PASS (this task's share of a standing prohibition)
 - Source verbatim at source-001.md line 117 ("Reuse existing fields and status terms where possible. Do not build a second evidence platform or expand every record into an essay."); the requirements.json row text reproduces it unchanged and lists M3-T013 in applicability.task_ids.
 - The task adds exactly ONE additive sibling field, table_digest_sha256, to each of the 37 table-bearing captures and verifies it in the EXISTING loader snapshots.py; per-file diffs (zr-22-131, zr-23-432, zr-24-522 against claim head 1cbc8ccf) add one line and change/remove nothing — no second evidence platform, no new status vocabulary.
 - NB-06 gained only a concise single dependency_assessment entry (list 7->8) plus the E10 re-pin; research_status stays interpretation_awaiting_review and promotion.requested_label stays null — the record was not grown into an essay and reuses existing status terms.
 - Nothing stays open: this task's share of the prohibition is met; R043 continues to bind D-093-BOOTSTRAP and M0-T190 independently.

ROW D-093-R051 — PASS (this task's share)
 - Source verbatim at source-001.md line 135 ("For changed logic, test meaningful boundaries... Avoid tests that merely copy the implementation's formula. A synthetic fixture must never be relabeled as a professionally verified real-site result."); the row text reproduces it and lists M3-T013 in task_ids.
 - The changed logic (the loader's table-digest check) is tested at meaningful boundaries by services/api/tests/rules/test_zr_snapshot_table_digest.py; I ran it at the frozen head with the lanes venv: 13 passed, exit 0 (tampered value, both fail-closed directions, all three shapes, non-table pass, canonicalization stability, glob==digest set incl. zr-22-131).
 - The tests do not copy the formula: the test's _canonical_table_json is defined independently (production helper NOT imported), so stored-vs-recomputed assertions are non-tautological; the mutation and blind-direction proofs (test_pre_change_excerpt_digest_is_blind_to_the_table_edit) drive the real loader behaviorally. I reproduced in-memory on the real zr-23-432 payload that a flipped value raises "table_digest_sha256 mismatch", payload-without-digest, digest-without-payload, and both-table+tables all raise, and a non-table dict loads.
 - No synthetic fixture is relabeled verified: fixtures are built in tmp_path and nothing is labelled Verified. Nothing of this task's share stays open; R051 still binds M5-T157/T158/T161, M0-T190 and BOOTSTRAP separately.

ROW D-093-R052 — PASS (this task's share of a shared obligation)
 - Source verbatim at source-001.md line 137 ("Add the smallest appropriate check to the existing validation/review process... Automated checks can validate references, required fields, dependency status and test coverage. They cannot certify that a zoning interpretation is legally correct. Do not invent a `verified: true` field and treat its presence as proof."); the row text reproduces it and lists M3-T013 in task_ids.
 - This task's share adds the smallest additive integrity check to the EXISTING validation process (snapshots.py load_snapshot_file, after the unchanged content_digest check) so a result resting on a silently edited FAR/height table value fails to load; I reproduced the load-time refusal of a tampered value on the real zr-23-432 table.
 - It validates structure only and certifies nothing: the check is a sha256 fingerprint; `tools/research_record_check.py --check` run at the frozen head returned exit 0 and printed "structural check only; not a professional verification" and "no record claims the Verified label without meeting every condition"; no verified:true field is invented or trusted (NB-07 carries requested_label=Provisional, none Verified).
 - The one evidence record that pinned a changed capture by its whole file (NB-06 E10) is re-pinned to the signed file's LF sha256 ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898 (I recomputed `git show da17857a:...zr-23-432.snapshot.json | tr -d '\r' | sha256sum` = that value, canonical and bundled identical), so the existing staleness check stays green (NB-06 code_current=True) — no stale evidence can back a current result.
 - What stays open for later work: the broader R052 obligation — the structural promotion check itself (research_record_check) refusing to mark a result verified when its record is absent/stale/unresolved — is owned by M0-T190 and M3-T012 (both also carry R052); this task extends the capture-integrity guard and keeps that check green, and the remainder of R052 is verified under those tasks, not here.

(3) BINDING B1–B5
 - B1 PASS: contract commit ba059a58 appended ONLY "M3-T013" to the task_ids of R043/R051/R052 (three one-line additions) plus an updated_at bump; `git show ba059a58 -- requirements.json` shows no row-text change; requirement_count stays 75.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = e4564d9b0f4239f919b67425948cbee25bfd6703c257beda51812c81955db6e4 == manifest.requirements_content_digest_sha256 (same value).
 - B3 PASS: verification.json has exactly one M3-T013 row (schema directive_verification/v2), applicable_requirement_ids = [D-093-R043, D-093-R051, D-093-R052], producer backend-engineer, verifier "", all three requirements state=pending, reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(packet) = ok:true, applicable_ids == cited_ids == [R043,R051,R052], missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: reg.derive_applicable(packet) across all active directives returns exactly {R043,R051,R052} with an empty error list; the validator passed at the head — nothing else applies to this task uncited.
 - GATES PASS: G0 PASS (orchestrator, re-recorded at scope-correction head 55644820, an ancestor of the frozen head that carries the packet), G1 PASS (data-contract-verifier), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer, round-1 F1 closed in round 2); G1–G4 all at one content identity 7785d0de, and CI run 38786051959 at 7785d0de completed success, 21/21 jobs.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while a blob-level predicate holds: the packet's allowed-path files keep their frozen-head blob ids (services/api/app/rules/snapshots.py, services/api/scripts/sync_zr_snapshots.py, the 37 canonical snapshots under docs/research/zr-snapshots/v1/ and their 37 bundled copies under services/api/app/_zr_snapshots/v1/, docs/RULES_ENGINE_ARCHITECTURE.md, services/api/tests/rules/test_zr_snapshot_table_digest.py, docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json, docs/research/evidence-records/README.md, project-control/reports/M3-T013-producer-report.md), AND the text of rows R043/R051/R052 and their M3-T013 applicability.task_ids binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits MAY touch any other file (other wave-28/other tasks' files under services/, apps/, packages/, docs/, .claude/; their packets, gates, reports and directive bindings; new rows appended to D-093 or any directive; ledger state), PLUS this task's own acceptance records (its verification.json row, gate records, evidence map, reviews, packet status/state), PLUS a merge of the main line that changes none of the predicate's files. Any such change leaves this verdict valid.

(5) REQUIRED CORRECTIONS
 - None. No row is VIOLATED or UNVERIFIABLE.
 - Two non-blocking advisories (carried from G3, not directive defects, recorded only): (a) a `tables` value that is not a list and an empty/non-string table_digest beside a payload have no dedicated unit test — but I confirmed the loader code raises on both paths (snapshots.py "'tables' payload is not a list" and "table payload present but no table_digest_sha256"), so behavior is covered; (b) the packet documented_test_commands/S7 and the producer report name tests/rules/test_r6b_reference_cases.py whereas the real path is tests/rules/reference_cases/test_r6b_reference_cases.py (the test was actually run at the real path). Neither affects any row's compliance.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run tools/test_directive_compliance.py or the full services/api pytest suite (both forbidden by the brief); I ran only the focused test file, research_record_check, validate_directive_compliance.py --check, and in-memory loader drives. The full suites are CI's job (21/21 green at 7785d0de).
 - CI at the frozen head da17857a: two workflow runs completed success and one was still in_progress at my read time; the material head 7785d0de is fully green. Confirming the full live rollup green at the accept head is the orchestrator's read before accept (D-090-R639), not mine.
 - I did not re-fetch live ZR pages; the R6B base-height readings are settled in docs/reference-cases/R6B/cases/ and this task changed no captured value — I confirmed the NB-06 E10 excerpt (R6B base 30/45/55, qualifying 45/65) is byte-identical across revision 5->6, so no re-derivation was owed.
 - I verified the control-plane mechanics via the registry helpers and git objects at the frozen head; I did not and may not run any project_control.py write, git write, or gh write command (read-only verifier). Recording this gate and writing verification.json are the orchestrator's actions.
END-OF-REPORT
```
