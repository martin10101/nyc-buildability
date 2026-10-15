# M5-T190 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `b9412f35c57b163380d34dfd14017ca1eea865e5` (branch `task/wave28-placement-wiring`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R028, R058.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. (One non-blocking observation, outside the two rows: the contract commit cb3b2cfd carries a "Co-Authored-By: Claude Opus 5.5" trailer rather than this session's own model line; it is an orchestrator/contract commit, not a builder commit, and does not bear on R028/R058 compliance — noted only for the orchestrator's awareness, not a correction for this task.)
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T15:20:11Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T190 (directive D-094, 2 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is not a human or professional review. I reproduced each item from primary evidence; the producer/orchestrator reports and the reviewers' returns were treated as claims, not proof.

(1) HEAD VERIFIED
 - Frozen head read: b9412f35c57b163380d34dfd14017ca1eea865e5 on task/wave28-placement-wiring (git rev-parse confirmed; working tree clean).
 - Build round 26d1d4bf (cherry-pick of cb226c05); contract cb3b2cfd; G0/claim 8d7cf91b; base main 86a450d4 (branch not merged to main; task status awaiting_gate, 95%).

(2) ROWS

ROW D-094-R028 — PASS (this task's share)
 - Source matches verbatim: source-001.md line 103, Provenance row 9, "Provide enough run/source/revision information to identify what actually generated this report"; the requirement text is unchanged by this task (text sha256 7cb1fb76 identical at contract parent and frozen head).
 - This task's share is the run-identity fingerprint that identifies what generated the report: run_identity._FINGERPRINT_EXCLUDE now also excludes option_id and study_id, so re-running the same request reproduces the fingerprint; I reproduced in-process on the recorded fixture (doc vs a copy differing only in the four run fields -> equal a43b9aa2c61a), and the in-process mutation to the old two-field tuple made them differ (c813b01a2619 vs 1d183b40626f).
 - The appendix placement, "clearly named appendix" and "no repeated headings" clauses of R028 are NOT this task's share and are untouched (no page text/label changes); they are held by M5-T169 (accepted), which built the appendix and run-identity column.
 - Stays open for later work: the appendix-structure / no-repeated-heading portion of R028 is M5-T169's share, not this task's; nothing of this task's fingerprint share stays open.

ROW D-094-R058 — PASS (this task's share)
 - Source matches verbatim: source-001.md line 175, "Verify that each result and diagram comes from the same result revision and scenario. Distinguish allowance, scheduled area, demonstrated site fit, preliminary apartment estimate, and legal unit limit"; text unchanged by this task (text sha256 7b2360ec identical at parent and frozen head).
 - This task's share is the harness tying every rendered figure to one document: I ran tests/drawings/report/test_report_run_identity.py under the lanes venv (11 passed, exit 0), including S4's live two-run TestClient test which is non-vacuous (option_id/study_id/results_id differ per run yet the two fingerprints are equal); a real value change (floor_area_allowance 20150->20151) moves the fingerprint (a43b9aa2c61a -> 231d8ce95ee2), so sensitivity is preserved.
 - The four excluded fields are genuinely per-run metadata, not values: results_read.py mints option_id (line 343), study_id (351), results_id (388) as uuid4().hex and computed_at (344) via _now_iso(); the read-only return-check and both reviewers found exactly four top-level differing leaves between runs and no nested per-run leak, consistent with S3 (dropping option_id/study_id leaves the hash unchanged, reproduced True).
 - Stays open for later work: the "distinguish allowance / scheduled area / demonstrated site fit / preliminary apartment estimate / legal unit limit" clause is a page-content concern unchanged by this metadata-only task and is held by M5-T162, M5-T164, M5-T169, M5-T172; this task's harness share leaves nothing open.

(3) BINDING B1–B5
 - B1 PASS: M5-T190 appended to applicability.task_ids of both rows in contract commit cb3b2cfd (R028 ...M5-T169,M5-T190; R058 ...M5-T172,M5-T190); no row text changed (per-row text sha256 identical at cb3b2cfd^ and b9412f35).
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = ef48f6d3a550e50d7f303184f75db945f9ba3427ca609192ccdd213268141af0 == manifest.requirements_content_digest_sha256.
 - B3 PASS: verification.json has exactly one M5-T190 row — applicable_requirement_ids [D-094-R028, D-094-R058], producer backend-engineer, verifier "" (empty), both requirements state pending, reviewed_sha null (schema directive_verification/v2).
 - B4 PASS: reg.evaluate_task_refs(packet) -> ok=true, applicable_ids == cited_ids == [D-094-R028, D-094-R058], missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: reg.derive_applicable(packet) over all 92 active directives (D-001..D-094) returns only {D-094-R028, D-094-R058}, both cited — nothing applies uncited; tools/validate_directive_compliance.py --check exit 0 (quiet success; git log -1 confirms no concurrent write, no transient c14).
 - Gates PASS at one content identity: G0 PASS (orchestrator, cb3b2cfd), G2 PASS (orchestrator self_check), G3 PASS (code-reviewer), G4 PASS (qa-engineer); G2/G3/G4 all carry content_manifest_sha256 714f63c786073166e77a4c70ce52b54491a1fa27575c935cca6c50645afd5a0a at reviewed_sha 21c2d3c1. The reviewers pinned 26d1d4bf while the gates stamp 21c2d3c1 (disjoint M5-T189 peer commit between); I confirmed the three allowed-path files are byte-identical across 26d1d4bf / 21c2d3c1 / b9412f35 (blobs b4b2e40d run_identity.py, 034ab7cc test, 24141bb9 producer-report). CI run 38756933248 at 21c2d3c1 (the content identity): conclusion success, 21/21 jobs success. modularity_check --check exit 0 with no warning on either edited file.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while this blob-level predicate holds: the packet's allowed-path files keep their blob ids — run_identity.py b4b2e40d75b702f381977638d57eb61b96f9c390, test_report_run_identity.py 034ab7cce5513f6d4aae38d1a55bb4c4a03127e7, M5-T190-producer-report.md 24141bb943cf475473f796bcc73fa9156b502a8b — and rows D-094-R028 / D-094-R058 keep their text (sha256 7cb1fb76 / 7b2360ec) and their M5-T190 applicability binding.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/; other packets, gates, reports, directive bindings of other tasks; new rows appended to D-094; ledger state), plus this task's own acceptance records (verification.json M5-T190 row, evidence map, reviews/gate records) and a merge of the main line that changes none of the predicate's files, without invalidating this verdict.

(5) REQUIRED CORRECTIONS
 - None. (One non-blocking observation, outside the two rows: the contract commit cb3b2cfd carries a "Co-Authored-By: Claude Opus 5.5" trailer rather than this session's own model line; it is an orchestrator/contract commit, not a builder commit, and does not bear on R028/R058 compliance — noted only for the orchestrator's awareness, not a correction for this task.)

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the full tests/drawings/report folder (225) or the full api suite (10084) or the security checks — the full api suite is forbidden to me and those are CI's job; they are green at content identity 21c2d3c1 (run 38756933248, 21/21 success), where the task's code/test files are byte-identical to the frozen head.
 - I could not run the on-disk source mutation (reverting the tuple in run_identity.py) because I am read-only and cannot edit files; I reproduced the equivalent mutation in-process (two-field tuple -> fingerprints differ), which is logically the same red-proof.
 - CI at the exact future accept head is the orchestrator's R639 step; the frozen-head commit b9412f35 CI run 38758276324 was still in_progress at my read time, but b9412f35 adds only project-control report files (the task's code/test blobs are unchanged from the already-green 21c2d3c1).
 - No preview/server/PDF print was run (forbidden; no ports touched); the rendered appendix fingerprint line is covered by the reviewers' TestClient /report runs and the green report-folder test run, which I did not execute fully myself.
 - Windows behavior was not exercised (no Windows here); CI covers it.
END-OF-REPORT
```
