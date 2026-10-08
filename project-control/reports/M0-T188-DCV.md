# M0-T188 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `4b3048fc092f72731f83f0db27aafa6c0593f4bd` (branch `task/wave7-wiring-reading-seal`, review copy `/root/project/rv-w6-d`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R557.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08T03:25:16Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T188 (directive D-090, one row)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier); this is an automated read-only verification, not a human or professional review.

(1) HEAD VERIFIED
 - git rev-parse HEAD in /root/project/rv-w6-d = 4b3048fc092f72731f83f0db27aafa6c0593f4bd; working tree clean; claim head b416cf0d, material commits 23459ba3 + 816e4daa, and integration base 85500b94 all present as objects.

(2) ROWS
ROW D-090-R557 — PASS
 - A repair task IS contracted and built: packet project-control/tasks/M0-T188.json (task_type governance); gates G0 PASS (orchestrator, administrative), G2 PASS (orchestrator, self_check), G3/G4 PASS (code-reviewer), G5 PASS (security-reviewer); G2–G5 all carry the one content identity f347be2e9f65…; the two review records M0-T188-G3G4.md and M0-T188-G5.md each hold two returns (reading 1 at ccc3f0ae, reading 2 at eb83be8d), both PASS, no reading failed.
 - The repair does what it says: I drove tools/directive_registry.py:pattern_allowed_paths(1379) myself — a literal file, a literal folder, and a plain not-yet-existing path pass; a/**, a/*.py, a/{b,c}.py, leading ':', absolute, '..', backslash, non-list value and non-string entry are all refused; the tracked [documentId] route passes; a mixed list names only the pattern entry; the guard is wired at project_control.py claim(:910)/submit(:566)/accept(:602) and validator c18(:334), exempting the frozen map per (task,entry).
 - Nothing accepted breaks / no old record rewritten: validate_directive_compliance.py --check exited 0 (direct); tools/test_ledger_seal_literal_paths.py = 9 passed; the net diff claim-head→HEAD has ZERO deletions in all three tool files, so the identity algorithm, GIT_LITERAL_PATHSPECS, the empty-identity guard and c17 are byte-unchanged, and I recomputed the live task identity at HEAD = f347be2e (= the gates' manifest, err None); the two material commits touch only the 7 allowed paths.
 - Defect stays tracked / interim rule enforced: backlog row DB-181 is OPEN at this head; my own sweep of every task packet reproduces PATTERN_ALLOWED_PATHS_GRANDFATHERED exactly (91 tasks / 249 pairs, zero discrepancy, zero new offender outside it); the three wave-7 packets (M0-T188, M5-T134, M4-T035) carry zero non-binding entries, and c18 + the CLI guards enforce literal naming for any later packet.
 - What stays open: R557 is NOT closed by this task alone — the owner required DB-181 stay OPEN until repaired, and the reports/evidence map state plainly that the 12 in-flight listed tasks keep non-binding entries until accepted or made literal, a plain path that never comes to exist still binds nothing (caught by the unchanged empty-identity guard), and nothing was run on Windows.

(3) BINDING B1–B5
 - B1: requirements.json diff 85500b94→HEAD appends only "M0-T188" to R557 applicability.task_ids; R557 text/classification/status and every other row's text are byte-unchanged (no row text changed, no new rows added).
 - B2: sha256_text_artifact(requirements.json)=63cba9e9… equals manifest.requirements_content_digest_sha256; manifest audit_log holds the 2026-10-08T01:35 applicability_bound entry binding M0-T188→R557 with digest resync + provisional verification row, same commit.
 - B3: verification.json has exactly one M0-T188 row: applicable_requirement_ids ["D-090-R557"], state pending, verifier "" (empty), reviewed_sha null, producer backend-engineer.
 - B4: reg.evaluate_task_refs(M0-T188 packet) over the real registry = ok True, applicable == cited == ["D-090-R557"], missing/invalid/unresolved all empty.
 - B5: covers_governance(packet)=True (task_type governance; D-090 active, scope.task_types includes "governance"); nothing else applies uncited (B4 missing=[]); the single scope-correction (backend→governance, before any claim) changed task_type only — allowed_paths, required_gates, reviewer_agents, acceptance_scenarios and directive_refs are byte-identical across f46a4ee9→154a8867 (status/progress are the G0 re-record's lifecycle fields).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review iff: (a) the seven allowed-path files keep their frozen-head blob ids — directive_registry 3da2f98c, project_control 4412797b, validate c33b6712, test_project_control 71a0481c, test_ledger_seal_literal_paths b31b27ee, producer-report 360687bd, lookback 44ce8e9d (all confirmed equal to the reviewers' eb83be8d pins), AND R557's text and its M0-T188 applicability binding stay unchanged. Tolerated later commits: ones touching only project-control/** and docs/DISCOVERY_BACKLOG.md (this report, the verification row, acceptance records, backlog sweeps), and a merge of the integration branch that changes none of those seven blobs or the binding.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I ran only the two permitted commands; I did NOT run tools/test_project_control.py (the reviewers' "34 passed"), modularity_check.py --check, or the mutation proofs (they need writes) — these are the reviewers'/CI's evidence, which both reviewers reproduced.
 - Windows behavior is unrun by anyone; the posix-string + literal-pathspec claim is sound by inspection but untested on Windows.
 - I did not reconstruct pre-scope-correction packet bytes beyond the committed f46a4ee9→154a8867 diff (which shows a task_type-only material change).
END-OF-REPORT
```
