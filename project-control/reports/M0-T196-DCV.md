# M0-T196 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `59b2ce352db1d529addc690b01171804be16d1d4` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R117.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-13 06:16 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T196 (directive D-094, 1 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated independent review, NOT a human or professional review. I produced none of this task's work or records; I re-derived each item from primary evidence (the owner's words in the directive source and Q&A log, and the task's files at the frozen head), read read-only through git plumbing.

D-093 (research and verification): I AGREE this task changes instruction pointers only. The three changed files are instruction/routing files (.claude/rules/living-files.md, .claude/rules/PROGRAM_KNOWLEDGE.md, .claude/session-handoff-profile.md); no property fact, rule reading, calculation input, result, or certainty label changes; no services/apps/packages rule JSON, no docs/research record, no zoning rule. The four owner-worded/rule files are byte-unchanged (blobs identical claim->frozen). So D-093 requires no evidence-record change here. I verified this; I did not need to open evidence records.

(1) HEAD VERIFIED
 - I read the frozen head 59b2ce352db1d529addc690b01171804be16d1d4 on task/wave24-report-v3 in /root/project/w-wave20 via git plumbing; git rev-parse confirmed it.
 - While I worked, the branch HEAD advanced to ea22522911 (one disjoint commit adding the Q&A log docs/back-and-forth-developer/2026-10-11-questions-and-answers.md §28-29); this is the carry-forward disjoint-peer case, not a predicate change.
 - The task's allowed-path file blobs are byte-identical at 59b2ce35 and ea225229, so every finding below holds at the frozen head.

(2) ROWS
ROW D-094-R117 — PASS
 - Owner's primary words are "Yes" to question L1 (source-012-amendment.md#owner-message-verbatim, raw SHA-256 85a39ab3...; Q&A log §28-29 at ea225229 records the question and this answer); the row text in requirements.json matches.
 - The map .claude/rules/living-files.md exists, is eager (line 1 has no paths frontmatter; context_budget_check.py lists it as eager, 1647B/18L), and names every living file (questionnaire, Q&A log + private copy, directives, research records + zoning-rule register + owner RQ queue, discovery backlog, master plan, program/coding lessons + working knowledge, session notes, handoff, session brief), each with the exact moment to update it; "how to check" is delegated to the handoff checklist it points to on line 3.
 - The removed PROGRAM_KNOWLEDGE.md one-liners lose no duty: backlog D-069, owner-research D-050-R002/R005/R006, loop-run pointer (shortened, same target), and the header append duty are all carried in the map; the two handoff lines (D-090-R941, D-070/D-094-R109-R113) are moved word-for-word into .claude/session-handoff-profile.md:104-109 (I diffed the removed lines against the profile text: identical), and the profile checklist has one item per map line (9) plus the memory index.
 - Session-start size: context_budget_check.py gives eager total 44872B (PASS, exit 0), i.e. +105B vs the claim head 44767B; the memory index questionnaire line shrank 239B->132B (I measured both) = -107B, net -2B whole session start. The owner's own §28 framing of "session start" includes the memory index, so "doesn't get bigger" is met in the owner's sense; the record (G3 F1 correction, producer report caveat, Q&A §29) discloses this exactly. STAYS OPEN: the net-neutral promise is unguarded (no size cap per D-093-R074; memory index is outside git), so future eager regrowth or memory re-expansion is silent, and the map only takes effect for sessions started after it reaches main (packet risk / M0-T191 snapshot); question B1 (moving further instruction-file parts) remains open beyond the lines this map replaced.

(3) BINDING B1–B5
 - B1 PASS: the contract commit ec8c68dd changed D-094 requirements.json only by appending "M0-T196" after "D-094-BOOTSTRAP" in R117's applicability.task_ids; no row text changed, and none of the three material commits (d0d4fe15, 411b623c, 2426f9f6) touch requirements.json.
 - B2 PASS: I recomputed both manifest digests at the frozen head — requirements_id_digest_sha256 = d95ad91ac144... and requirements_content_digest_sha256 (sha256_text_artifact) = 15eb26bc4d53... — both equal the manifest's declared values; 117 rows R001..R117.
 - B3 PASS: D-094 verification.json has exactly one M0-T196 row (schema v2) with applicable_requirement_ids [D-094-R117], producer "orchestrator", verifier "" (empty), requirement state "pending", reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(M0-T196) returns ok=true, applicable_ids=[D-094-R117], cited_ids=[D-094-R117], no missing/invalid/unresolved — applicable == cited.
 - B5 PASS: the registry derives only D-094-R117 as applicable to this task and it is cited, so nothing else across active directives applies uncited. Gates: G0 PASS (administrative, reviewer orchestrator, @ec8c68dd), G2 PASS (self_check, orchestrator, @0b5ff00e), G3 PASS (independent, code-reviewer, @0b5ff00e); G2 and G3 share one content identity (content_manifest d3711e5d...). validate_directive_compliance.py --check exit 0 (direct code; git log -1 confirms no transient c14). CI at the submit head 0b5ff00e is fully green: CI run 38354013342 = 21/21 jobs success including control-plane, context-budget, secret-scan and modularity (the one cancelled run at 59b2ce35 was superseded by the later Q&A-log push; ea225229 CI is all success).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while this blob-level predicate holds: the four allowed-path files keep their blob ids (.claude/rules/living-files.md ca554e73, .claude/rules/PROGRAM_KNOWLEDGE.md 704d93ac, .claude/session-handoff-profile.md 61108faa, project-control/reports/M0-T196-producer-report.md f06e9351), AND D-094-R117's row text and its M0-T196 applicability binding are unchanged (id/content digests as in B2).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets, gates, reports, other directives' bindings, ledger state), this task's own acceptance records, and a merge of main that changes none of the predicate's files. The ea225229 Q&A-log commit is already an allowed instance of this tolerance.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The committed "before" state of the orchestrator's memory index: it is outside git, so there is no git-pinned pre-trim baseline. I corroborated the -107B magnitude by measuring the old questionnaire line from my session-start snapshot (239B) against the current on-disk line (132B), but cannot cryptographically pin a before-state; this is the same limit the record discloses as unguarded.
 - Forward session behavior: that future sessions actually load the eager map and run the handoff checklist. I verified the file is eager now and the checklist exists; I cannot verify future runs (the packet itself notes it applies only to sessions started after the change reaches their branch).
 - I did not run tools/test_directive_compliance.py (forbidden; hours) or the full api suite. I relied on validate_directive_compliance.py --check (exit 0) plus the CI control-plane and context-budget jobs (success at 0b5ff00e) as the authoritative harness evidence, per the brief.
 - I measured context_budget_check.py against the on-disk worktree (now at ea225229); this is sound because the eager rule files are byte-identical to the frozen head (the only intervening commit added a docs/ file, not an eager rule).
END-OF-REPORT
```
