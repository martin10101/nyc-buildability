# M3-T009 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `18b9eac5775ea6d09d93cd637e06944ed0322bbb` (branch `task/wave25-rear-yard-short-block`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R102, R104.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T02:37:32+00:00, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M3-T009 (directive D-094, 2 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only machine check — NOT a human or professional/legal review. I produced none of this work or its records. I treated every report, map, gate record and the brief as an unverified claim and reproduced the evidence from primary sources (the owner's words, the task files at the frozen head via git plumbing, the registry helpers, and CI).

(1) HEAD VERIFIED
 - I read the frozen head 18b9eac5775ea6d09d93cd637e06944ed0322bbb on branch task/wave25-rear-yard-short-block in /root/project/w-wave20 (git rev-parse HEAD).
 - The working tree is clean (git status --porcelain empty), so the validator and registry helpers read the frozen content.
 - Material commit ccf8e24b touches exactly 31 files (15 canonical zr-snapshots + 15 byte-identical bundled copies + the producer report) and no directive file (git show --stat).
 - The frozen head is NOT merged into main and the task status is awaiting_gate (not accepted); nothing was merged, accepted, deployed or dispatched for this task.

(2) ROWS
ROW D-094-R102 — PASS (this task's share)
 - Row text (source-004-amendment.md#owner-message-verbatim) is the owner's decision to start the zoning-law library as a documents-only second line of work beside the report; this task's share is the fifteen community-facility captures (DB-253).
 - I reproduced all 15 snapshots at the frozen head: snapshot_schema "zr_section_snapshot/v1", content_digest_sha256 == sha256(verbatim_excerpt) for all 15, extraction_status "extracted_draft", raw_html_verified false, no affirmative "Verified" token (grep excluding negations/ADR-007 line = none).
 - Both channels are pinned (raw_html_sha256 and raw_pdf_sha256 each 64 hex), http 200/200, host zoningresolution.planning.nyc.gov, Last Amended 12/5/2024 on all 15; each canonical file is byte-identical to its bundled copy; the diff touches no rule/scenario/drawing/test/library/report-lane file (shares no file with the report lane).
 - STAYS OPEN: the broader R102 facets (complete handled/not list, pitfall list, other option subsets — split-lot/courts, rooming/shops/parking) and 22-13's child sections 22-131..135 are owed to later capture tasks per the evidence map and producer report; this is a multi-task decision and only the community-facility slice closes here.

ROW D-094-R104 — PASS (this task's share)
 - Row text is the owner's authorization of up to 8 helpers at once (at most 3 building, research-only beyond 5, never sharing files); required evidence is session notes and dispatch records.
 - The dispatch record (session-2026-10-14c/SESSION_NOTES.md lines 40-43) shows M3-T009 was built by one research agent (official-source-researcher ae33a551) in its own worktree, at peak 2 building helpers (M3-T009 + M5-T167) and then 1 building + 1 read-only G1 reviewer — within the <=3 building / <=8 helper limits.
 - I confirmed file-disjointness from git: the intersection of M5-T167's builder commit d0611800 files and M3-T009's ccf8e24b files is empty, so no two concurrent helpers shared a file.
 - STAYS OPEN: R104 is a standing authorization for the next session's research agents generally; nothing of this task's compliance slice stays open.

(3) BINDING B1-B5
 - B1 PASS: only rows D-094-R102 and D-094-R104 carry "M3-T009" in applicability.task_ids (added in contract commit 910f46e1); the material commit ccf8e24b changed no directive file, so no row text changed by this task.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = 86a96a75...05662d equals manifest requirements_content_digest_sha256 86a96a75...05662d.
 - B3 PASS: verification.json has exactly one M3-T009 task_verifications row, applicable_requirement_ids [D-094-R102, D-094-R104], verifier "", both requirement rows state "pending", reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(M3-T009) returns ok=true, applicable_ids == cited_ids == [R102, R104], missing/invalid/unresolved all empty.
 - B5 PASS: reg.derive_applicable(M3-T009) across all directives yields exactly [R102, R104] with no notes — nothing else applies uncited. Gates: G0 PASS (orchestrator, reviewed_sha 910f46e1), G1 PASS (data-contract-verifier) and G2 PASS (orchestrator self_check) both at reviewed_sha 48b77e02 with the same content_manifest_sha256 3b809120... (G1->G2 at one content identity); validator python3 tools/validate_directive_compliance.py --check exited 0; CI run 38670334315 at 48b77e02 = 21/21 jobs success; the 31 task files are byte-identical across ccf8e24b -> 48b77e02 -> 18b9eac5.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while this blob-level predicate holds: the packet's 31 allowed-path files (15 docs/research/zr-snapshots/v1/zr-*.snapshot.json, 15 services/api/app/_zr_snapshots/v1/zr-*.snapshot.json, project-control/reports/M3-T009-producer-report.md) keep their exact blob ids, and the text of R102/R104 plus their M3-T009 applicability binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other tasks' sources under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records (verification.json M3-T009 row, reviews, evidence map, task/state) and a merge of the main line that changes none of the predicate's files. Any change to a predicate file voids the carry-forward and needs a fresh stamp.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-fetch the official DCP pages to re-prove verbatim text/table/list-letter fidelity cell-for-cell (read-only, and avoiding load on the official site); G1 (data-contract-verifier) reproduced that against HTML + print/PDF and recorded PASS. I reproduced shape, digest, channels, bundle byte-identity, host, http status, Last Amended and the no-Verified-token discipline.
 - I did not re-confirm the 5 of 15 node-ids (24-162, 24-33, 24-34, 24-35, 24-391) that G1 could not surface in HTML directly (G1 advisory A1); disclosed in the evidence map's known_limits; residual, not a defect.
 - I did not run tools/test_directive_compliance.py or the full api suite (forbidden by the brief / CI's job); the authoritative harness evidence is the validator exit 0, the gate records, and CI run 38670334315 (21 jobs green) at the submitted head.
END-OF-REPORT
````
