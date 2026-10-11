# M0-T191 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `26b54c5a3af4614bac885926876878b6c41aa157` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-090, D-093. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R029, R032, R034, R068, R941.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. One non-blocking cosmetic ADVISORY already recorded by G3 round 2 (the inline tag "[ORCH-CORRECTED per G3 advisory...]" in M0-T191-delegated-agents.md:7 sits after "principle 21" rather than beside the "14,562 characters (14,609 bytes)" figure it corrects); the figures are correct (I measured git show 9e107bf3:CLAUDE.md = 14562 chars / 14609 bytes) and the advisory was deliberately not applied to keep the reviewed files byte-identical. Not a required correction.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 05:14 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T191 (directives D-093 and D-090, 5 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only, machine verification, not a human or professional/legal review. I produced none of the work or records and read every report, map and gate as an unverified claim, re-deriving each row from primary evidence (transcripts, git objects, the directive registry, the stdlib checks).

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = 26b54c5a3af4614bac885926876878b6c41aa157 at the start and again at the end of my pass; branch task/wave23-density-zoning-lot.
 - I read every file through git plumbing (`git show 26b54c5a:<path>`), not the working tree, because the checkout can move; the registry/packet files were clean (`git status --porcelain` empty).
 - Submit head 77980af8 (where G2/G3 are recorded) to frozen head 26b54c5a touches only gate records + this task's state/report/task files; the four material files are byte-identical across that range (git diff empty), so G2/G3 and the frozen head are one content identity.

(2) ROWS (this task's share; D-093 in numeric order, then D-090-R941)

ROW D-093-R029 — PASS
 - Harness row "New, resumed and compacted sessions recover the policy and current task state." This task's share is the delegated-agent nuance; I reproduced from the three cited transcripts that a subagent inherits its parent session's start-time instruction set.
 - Fresh post-merge session 2f0aa039 loaded research-and-verification.md (2452 chars) while subagents a1200433925ba8efc (02:58:48) and a7180378d084bf28b (03:05:24) loaded the pre-merge set (CLAUDE.md 14177, PROGRAM_KNOWLEDGE 17012, no research rule) — all char counts match the record exactly.
 - docs/RESEARCH_AND_VERIFICATION.md §9 (blob f5adba44) states the policy is attached again after a compaction and that a delegated agent gets its parent's start-time set, with the untested caveat named.
 - Stays open: whether a compaction of the parent refreshes the set its LATER subagents inherit is untested (stated in the record and §9) and I could not test it (needs a live compaction).

ROW D-093-R032 — PASS
 - Obligation "reviewer/worker launch instructions pass the applicable policy... Do not assume every delegated task receives the parent conversation... no new agent framework." §6 dispatch clause (blob f5adba44) now explains WHY every builder/reviewer brief must carry the policy + record paths: helpers do not see the conversation and inherit the parent's start-time instructions.
 - I confirmed the practice from primary evidence: the M5-T157 builder transcript a7180378d084bf28b first user message carries the clause verbatim ("Research and verification (owner directive D-093) applies: read .claude/rules/research-and-verification.md and docs/RESEARCH_AND_VERIFICATION.md in your checkout before you change anything").
 - .claude/rules/PROGRAM_KNOWLEDGE.md (blob 813ea947) adds the pointer "A subagent inherits its PARENT session's start-time instruction snapshot... reaches helpers only through the brief"; no new agent framework is introduced.
 - Nothing stays open for this row.

ROW D-093-R034 — PASS
 - Prohibition "Preserve all unrelated settings and access restrictions... do not claim coverage for a session type that was not tested." I reproduced that `git diff d4636970..26b54c5a` over the packet's paths touches only the four docs/report files; no .claude/settings.json, hook, or .claude/agents definition changed.
 - The untested session type (compaction refresh for later helpers) is explicitly named in both the evidence record ("Not tested...") and §9, so no coverage is claimed for it.
 - forbidden_paths (services/, apps/, packages/, .claude/settings.json, .claude/agents/) are untouched in the material range (confirmed by the diff).
 - Nothing stays open for this row.

ROW D-093-R068 — PASS
 - Evidence row "Context recovery... Mark untested session types honestly." The record project-control/reports/M0-T191-delegated-agents.md (blob b87e6fcc) names the untested session type honestly and corrects the over-broad M0-T190 §4 sentence beside it.
 - I confirmed the over-broad sentence exists verbatim at project-control/reports/M0-T190-verification-sessions.md line 166 ("So once the main checkout holds the D-093 files, every delegated agent loads the rule.") and that the evidence (this session's own pre-merge subagents lacked the rule) shows it is genuinely over-broad.
 - The accepted M0-T190 report is NOT edited by this task (`git diff d4636970..26b54c5a -- .../M0-T190-verification-sessions.md` empty); the correction lives in the new record.
 - Nothing stays open for this row.

ROW D-090-R941 — PASS
 - Obligation (owner 04:23 UTC "I told u to do a handoff why is 2 thinks still running"). This task's share is the pointer only, per the brief. .claude/rules/PROGRAM_KNOWLEDGE.md (blob 813ea947) adds "Owner handoff = NOTHING keeps running (D-090-R941): save each helper's unfinished work into the session folder (git diff --binary), stop it, record where it is; overrides the skill's let-helpers-finish line."
 - I checked the pointer against source-084-amendment.md and the requirements.json R941 row (classification obligation; reading: "when the owner asks for a handoff, nothing the session started keeps running"); the pointer faithfully reflects the owner's words plus the separately-labelled reading and adds nothing beyond it.
 - Stays open: the behavioral "next-handoff nothing keeps running" harness is later evidence (a future handoff); it is not provable at this docs-only head, and the session-handoff skill text itself is not edited (carried by the pointer) — both noted as open in the evidence map's known_limits.

(3) BINDING B1–B5
 - B1: Contract commit 9fa99590 appended "M0-T191" to applicability.task_ids of exactly the four D-093 rows R029/R032/R034/R068 (diff shows only task_ids + updated_at; no row text/classification edited); D-090-R941 was created in capture 5ae716eb (source-084-amendment.md) and bound to M0-T191 in 687c8719 (diff shows only +"M0-T191" + updated_at). At the frozen head all four D-093 rows and R941 carry M0-T191.
 - B2: I recomputed sha256 over LF-normalized requirements.json bytes (directive_registry.normalize_text_artifact_bytes) from the frozen content: D-093 = 3a003cfdbefa2d6a691d5c626dd511c08bcf4b164a7bedeaa51fdeac36eb2179 and D-090 = b837c0593b776f23c835eac7b3fd4068e29e2d948580b13e3bde022f68e71a92 — both equal their manifest requirements_content_digest_sha256.
 - B3: Each verification.json has exactly one M0-T191 row (schema directive_verification/v2), producer "orchestrator", verifier "", reviewed_sha null: D-093 with [R029,R032,R034,R068] all state pending; D-090 with [R941] state pending.
 - B4: DirectiveRegistry(...).load().evaluate_task_refs(M0-T191 packet) returned ok=True, applicable_ids == cited_ids == {D-090-R941, D-093-R029, D-093-R032, D-093-R034, D-093-R068}, missing_ids/invalid_refs empty, reg.errors empty.
 - B5: I scanned every requirements.json under project-control/directives/ at 26b54c5a for M0-T191 in applicability.task_ids; the ONLY hits are D-093 (R029/R032/R034/R068) and D-090 (R941) — nothing else (including D-094) applies uncited. Gates: G0 PASS (reviewer orchestrator, reviewed_sha 9fa99590 = contract head), G2 PASS (orchestrator self-check, reviewed_sha 77980af8), G3 PASS (code-reviewer, reviewed_sha 77980af8); G2 and G3 at one content identity (material files byte-identical 77980af8..26b54c5a). validate_directive_compliance.py --check exit 0; research_record_check --check exit 0; context_budget_check exit 0; test_directive_reminder 22 tests OK exit 0.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head of the same wave WITHOUT a new review while BOTH hold: (a) blob predicate — the four material files keep these blob ids: docs/RESEARCH_AND_VERIFICATION.md f5adba449833b8d0cd7a160083ae9e390b91f6a5, .claude/rules/PROGRAM_KNOWLEDGE.md 813ea947110851b8e5931e9b97078defba97cd19, project-control/reports/M0-T191-delegated-agents.md b87e6fcc16017721a5ecb39fba9df7919a43399e, project-control/reports/M0-T191-producer-report.md 076e1f50495cb019aa8c683ee9a52db0182dd1b0; and the five rows' text and their M0-T191 binding (applicability.task_ids) are unchanged. (b) broad disjoint-peer tolerance — later commits may touch any OTHER file (other tasks' product/doc files under services/, apps/, packages/, docs/, their packets/gates/reports/evidence records/directive bindings, ledger state), this task's acceptance records (this DCV report, the M0-T191 verification rows, state.json), docs/SESSION_HANDOFF.md (an allowed path that carries no part of this task's correction; it was unchanged by this task, blob 835c8eda), and a main-line merge that changes none of the four predicate files.

(5) REQUIRED CORRECTIONS
 - None. One non-blocking cosmetic ADVISORY already recorded by G3 round 2 (the inline tag "[ORCH-CORRECTED per G3 advisory...]" in M0-T191-delegated-agents.md:7 sits after "principle 21" rather than beside the "14,562 characters (14,609 bytes)" figure it corrects); the figures are correct (I measured git show 9e107bf3:CLAUDE.md = 14562 chars / 14609 bytes) and the advisory was deliberately not applied to keep the reviewed files byte-identical. Not a required correction.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The D-090-R941 "nothing keeps running at the next handoff" behavioral harness: later evidence at a future handoff; not provable at this docs-only head.
 - Whether a parent-session compaction refreshes the instruction set its LATER subagents inherit: untested by the producer (stated honestly) and I cannot run a live compaction.
 - The full tools/test_directive_compliance.py suite: forbidden by the brief (hours); authoritative harness evidence here is validate_directive_compliance.py --check (exit 0) plus the control-plane CI job at a verified head, which I relied on.
 - validate_directive_compliance.py --check executed at the primary /root/project/nyc-buildability checkout (main); I compensated by recomputing B2 digests and running evaluate_task_refs directly at the frozen head.
 - Authenticity/completeness of the transcript corpus: I confirmed the three cited transcripts exist on the private build server and that every quoted file list, size, timestamp and the code-reviewer's "not in my instructions" answer reproduce exactly; I cannot rule out other transcripts, but every specific record claim is reproduced.
END-OF-REPORT
```
