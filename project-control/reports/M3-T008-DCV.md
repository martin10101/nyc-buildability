# M3-T008 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `b51e794d36b8bdb9c170d0c0b60ff71647859f2a` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R102, R104.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 18:10 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M3-T008 (directive D-094, 2 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only, evidence-based review — not a human or professional/legal review. I produced none of this task's work or records; I reproduced each item below from primary evidence (owner source files, the task's files at the frozen head, git objects, the registry, and the control-plane CI). I verified THIS TASK'S SHARE of the two rows.

(1) HEAD VERIFIED
 - I read the frozen head b51e794d36b8bdb9c170d0c0b60ff71647859f2a on branch task/wave24-report-v3 in /root/project/w-wave20 via git plumbing (git show b51e794d:<path>).
 - While I read, the branch tip advanced to 2097dae8 by two disjoint peer commits (8014ef9a, 2097dae8 — both M5-T179 report-pages work); b51e794d is a clean ancestor (git merge-base --is-ancestor = YES).
 - git diff b51e794d..2097dae8 touches only project-control files for M5-T179 and state.json; no M3-T008 allowed-path file, no D-094 directive file, and no M3-T008 packet changed — so my checks hold at the frozen head and at the live tip.
 - python3 tools/validate_directive_compliance.py --check returned EXIT 0 (quiet-on-success) at the live tip; requirements.json and the binding are byte-identical to the frozen head.

(2) ROWS

ROW D-094-R102 — PASS
 - The row (classification decision, source-004-amendment.md#owner-message-verbatim) directs starting the zoning-law library in the next session as a documents-only line beside the report; THIS TASK'S SHARE is the affordable/senior-housing capture subset, and it is present and well-formed at the frozen head.
 - I independently checked all 11 captures (zr-27-111, -27-131, -27-133, -27-14, -27-151, -27-16, -27-161, -27-162, zr-appendix-f, zr-12-10-affordable-independent-residence-for-seniors, zr-12-10-long-term-care-facility): every file is snapshot_schema "zr_section_snapshot/v1", content_digest_sha256 == sha256(verbatim_excerpt), extraction_status "extracted_draft", raw_html_verified false, snapshot_id == filename stem, and its services/api/app/_zr_snapshots/v1 bundled copy is byte-identical to the canonical file; the production loader (app.rules.snapshots load_snapshot_file / SnapshotStore().load()) loaded all 11 with no error.
 - Provenance holds: each request_url is the official zoningresolution.planning.nyc.gov page (article-ii/chapter-7 sections; the appendix-f landing page; article-i/chapter-2/12-10 for the two terms), the 8 sections and Appendix F carry a pinned raw_pdf_sha256, the two 12-10 terms carry the disclosed DB-167 504/403 HTML fallback in cross_check.method, every "Verified" occurrence is the negated ADR-007 phrase (nothing labelled Verified), the renamed plural senior file is absent from both trees, and no 23-154 snapshot exists while its 2026-10-14T03:26:00Z HTTP 403 re-attempt is recorded in the producer report.
 - Stays open for later (not this task): the other DB-253 capture subsets (B community-facility, C1 split-lot/courts, C2 rooming/shops/parking); updating the library doc's NOT CAPTURED flags (docs/zoning-law-library/ is a forbidden path here); any rule citing these sections (a later rule task under D-093); ZR 23-154 stays access-blocked and owed; and R102's wider parts (handoff tells the next session, the handled/not-handled list, the pitfall list) are carried by M3-T006 and M3-T007 (both accepted), not by M3-T008.

ROW D-094-R104 — PASS
 - The row (classification authorization, source-004-amendment.md) allows up to 8 helpers at once when the extras only read/research, at most 3 building, never sharing files; THIS TASK'S SHARE is that M3-T008's own execution honored those limits.
 - Session notes 2026-10-14b record M3-T008's builder (official-source-researcher af20321c166ac7653, own isolation worktree) running as one of at most 3 builders ("3 building (M5-T171, M5-T175, M3-T008)"), with helper totals of 6 then 8 in those windows — within ≤3 building and ≤8 helpers; session notes 2026-10-14c record the rework builder (a48dfa7f8b2) as the sole builder ("DISPATCHED 5 (limit 5; 1 building, 4 reviewing)", "Running 6 (limit 8 when the extra only researches): 1 building").
 - M3-T008's reviewers (G1 round-1 data-contract-verifier, G1 delta data-contract-verifier, and this DCV) are read-only; the task's files (ZR snapshots) are disjoint from the concurrent builders' files (M5-T171 apps/web; M5-T175 report/maps; M5-T179 report pages), and the packet path_notes require disjoint snapshot filenames — so no two helpers shared a file.
 - Stays open for later: nothing of this task's share stays open; R104 is a standing authorization that continues to govern later library/research work (it is not a per-task deliverable).

(3) BINDING B1–B5 — all PASS
 - B1: R102 and R104 each carry "M3-T008" in applicability.task_ids (bound 2026-10-14T02:53:41 per the manifest audit_log); both material commits (05e4ccb4 ten captures; 7a794e61 rework F1-F4) touch ONLY docs/research/zr-snapshots/v1, services/api/app/_zr_snapshots/v1 and the producer report — no directive file — so no row text was changed by this task, and both row texts match the owner's source-004 capture verbatim (R102/R104 are in locked_requirement_ids and the validator passes).
 - B2: tools.directive_registry.sha256_text_artifact(requirements.json) = ac5261694f186ca7999d8d373ff9eebb2f4ef702e962e5f20ebc7892111a29d3, equal to manifest.requirements_content_digest_sha256.
 - B3: verification.json holds exactly one M3-T008 task_verification with applicable_requirement_ids [D-094-R102, D-094-R104], producer official-source-researcher, verifier "" (empty), and both requirement rows state "pending" with empty evidence.
 - B4: registry.evaluate_task_refs(M3-T008 packet) returned ok=True, applicable_ids == cited_ids == [D-094-R102, D-094-R104], missing_ids [], invalid_refs [], unresolved [].
 - B5: derive_applicable across all active directives yields exactly R102 and R104 for this task (nothing else applies uncited). Gates: G0 PASS (orchestrator, reviewed_sha 6135f18c), G1 PASS (data-contract-verifier) and G2 PASS (orchestrator) both at content_manifest_sha256 a4b2c32e / reviewed_sha c2edfd8e — one content identity; the task's allowed-path files are byte-identical from c2edfd8e through 7a794e61 to the frozen head; CI run 38610080172 at c2edfd8e is the "CI" workflow completed success, 21/21 jobs. (The "CI" run at b51e794d, 38611471798, shows CANCELLED — the known own-push-cancels-in-flight signature, superseded ~1 min later by the 2097dae8 push; secret-scan and context-budget passed at b51e794d.)

(4) CARRY-FORWARD CONDITION (stamp this PASS at a later head without re-review while BOTH hold)
 - Blob-level predicate: at the stamping head the packet's allowed-path files keep their frozen-head blob ids — the 11 canonical snapshots (docs/research/zr-snapshots/v1/zr-27-111, -27-131, -27-133, -27-14, -27-151, -27-16, -27-161, -27-162, zr-appendix-f, zr-12-10-affordable-independent-residence-for-seniors, zr-12-10-long-term-care-facility), their 11 byte-identical bundled copies under services/api/app/_zr_snapshots/v1/, and project-control/reports/M3-T008-producer-report.md — AND D-094 rows R102/R104 text plus their M3-T008 applicability binding are unchanged (requirements_content_digest_sha256 ac526169… intact, validator EXIT 0).
 - Broad disjoint-peer tolerance: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, new rows appended to D-094, and ledger state.json), plus this task's own acceptance records, plus a merge of the main line that changes none of the predicate's files — none of these void this verdict.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Live-source fidelity: I did not re-fetch the official ZR portal (read-only; no live-site fetch). That the verbatim_excerpts match the live HTML/print-PDF word-for-word was reproduced by the data-contract-verifier at G1 (it re-fetched the pages and re-derived F1-F4); I relied on that reproduction and the settled R6B readings per my brief, and I confirmed the deterministic properties (schema, digest equality, status fields, bundle byte-identity, official URLs, PDF pins, loader) myself.
 - Real-time helper concurrency: the exact simultaneous-helper counts rest on the orchestrator's private session notes (2026-10-14b/c), which are producer records; I corroborated the structural facts independently (M3-T008 builder in its own worktree, snapshot files disjoint from the concurrent builders' paths, reviewers read-only) but could not re-observe the live dispatch counts.
 - Forbidden harnesses: per my brief I did not run tools/test_directive_compliance.py or the full services/api pytest suite; the authoritative harness evidence I used is validate_directive_compliance.py --check (EXIT 0) plus the green control-plane CI job at c2edfd8e (content-identical to the frozen head) and the three recorded gate PASS records.

END-OF-REPORT
```
