# M0-T198 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `95e6f299cb008d79ef9c4017258ee9532b2a81a6` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R307, R309, R310, R314.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. Advisory (no file change needed): the evidence map marks R309 and R310 as fully met without restating that their harness ("skill file exists on main" / "every helper's start-time instructions contain the standard") also depends on the merge to main; that shared open step is, however, captured by the R314 open line and by known_limits ("The rule reaches later sessions once this branch is merged to main"), so the open carry-over is already recorded. Treat merge-to-main as the enabling step for all four rows, not an optional follow-up.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-16 01:42:32 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T198 (directive D-094, 4 rows)
VERDICT: PASS (this task's share of all 4 rows; the on-main carry-over of every row stays open until the wave-29 branch merges to main)

(1) HEAD VERIFIED
 - I read the frozen head 95e6f299cb008d79ef9c4017258ee9532b2a81a6 through git plumbing (git -C /root/project/w-wave29 show 95e6f299:<path>) for every file judged.
 - The worktree HEAD advanced while I worked (95e6f299 -> e016a59d -> f88bdc86 -> accd28cb): peer commits of other wave-29 tasks (M5-T173 contract e89e9b86 + claim e016a59d, backlog d6f0f1bd). This is the expected disjoint-peer activity named in the brief; the working tree stayed clean.
 - All three M0-T198 allowed-path file blobs and the packet blob are byte-identical at 95e6f299 and at the current head, so my judgments are pinned to the frozen content regardless of the advancing branch head.

(2) ROWS
ROW D-094-R307 — PASS (this task's share)
 - Authorization row: source-029-amendment.md#owner-message-verbatim holds the owner's message authorizing the orchestrator to build, for its own use, a way to brief helpers in the style of the attached prompt; the requirements.json R307 text is identical to that verbatim message.
 - The deliverable .claude/skills/dispatch-brief/SKILL.md (blob eb15e1e9) is the orchestrator's own internal helper-briefing method: it states "the brief goes to the helper, never to the owner" and "do not add work the question did not ask for", so it is the approach the owner chose (R309-R311), not the private father-facing skill — honoring source-029's recorded reading.
 - Build commit d0c22841 changed only the three allowed-path files (git show --stat: 86 insertions, 1 deletion); no CLAUDE.md, agents, hooks, settings, services/, apps/, packages/ or tools/ change, so no owner-facing skill was created and the private attachment was not copied into the repo.
 - Stays open: the row's harness ("used for dispatches after they land") and later dispatch briefs are an ongoing property that takes full effect once the branch is on main; the authorization itself is fully exercised by building the skill.

ROW D-094-R309 — PASS (this task's share)
 - Obligation from source-030-amendment.md: a short skill run before every helper question that turns it into a brief naming the exact answer, the exact files and version, evidence that could change the answer, what is unknown, and how deep; the requirements.json R309 text matches the verbatim quote.
 - SKILL.md "The five parts" map 1:1 with no weakening: (1) answer needed + decision it serves; (2) exact scope with repository/branch/pinned commit = "files and version"; (3) evidence that could change the answer + one disconfirming check; (4) what is unknown and must stay unknown; (5) depth and stopping point.
 - .claude/rules/helper-briefing.md (blob 32dd7abe) instructs the main session to run /dispatch-brief (or its five parts) before any helper is sent work, satisfying the "run before every helper dispatch" obligation.
 - Stays open: the row's harness requires "the skill file exists on main"; at the frozen head it is on branch task/wave29-scenario-drawings (base main 065e3fb5), not yet merged — the on-main property is the wave-29 merge.

ROW D-094-R310 — PASS (this task's share)
 - Obligation from source-030-amendment.md: the helper half added to every helper's instructions — go to the original source; tie each finding to its evidence and to what it changes; keep facts/claims/guesses/unknowns apart; lead with the answer, then the support; the requirements.json R310 text matches the verbatim quote.
 - helper-briefing.md's helper half carries all four elements; the owner's "guesses" is rendered as "inferences, assumptions" (a faithful, non-narrowing expansion) and the standard is also appended to the skill's return contract. Nothing is softened.
 - The rule has no paths frontmatter; context_budget_check lists helper-briefing.md under "Eager (auto-loaded) project instructions" (963B, 12L, ~241 tok), so once on main it sits in every helper's start-time instructions.
 - Stays open: "every helper's start-time instructions contain the standard" is realized for fresh sessions only after the merge to main; a mid-session helper inherits its parent's snapshot and gets the standard via its brief.

ROW D-094-R314 — PASS (this task's share)
 - Obligation from source-031-amendment.md: later sessions apply the method automatically without the owner restating it — an always-loaded rule naming the skill and standard, merged to main, nothing depending on chat history; the requirements.json R314 text matches the verbatim quote.
 - helper-briefing.md has NO frontmatter at all (starts with "#"), matching the always-loaded shape of research-and-verification.md; it names /dispatch-brief and states the helper standard, so it is independent of chat history or one session's memory.
 - First-hand check: my own subagent injected context contained the other no-paths rules (research-and-verification.md, CODING_RULES.md, PROGRAM_KNOWLEDGE.md, living-files.md, expansion-agent-dispatch-hold.md) but NOT helper-briefing.md — direct confirmation both that the always-loaded mechanism reaches subagents and that this rule is genuinely not yet on main.
 - Stays open (the row's primary open item): the rule and skill are not yet on main; the carry-over to every later session takes effect only at the wave-29 merge.

(3) BINDING B1–B5
 - B1 PASS: contract commit 46c92cad appended "M0-T198" to applicability.task_ids of exactly 4 rows (4 added lines), and its requirements.json diff added/removed zero "text": lines, so this task changed no row text. At the frozen head and at the current head the 4 rows are byte-identical, and only R307/R309/R310/R314 carry M0-T198 within D-094.
 - B2 PASS: recomputed sha256_text_artifact over the frozen requirements.json = 9ed95b1792e22ed1ee627872e56f184145662f86624c434df557d093de140ad5 == manifest requirements_content_digest_sha256; the id digest = 36f3b1e3902340b3f230249e0c47cc996d39a20424b4aab97a3147f1c1602ada == manifest requirements_id_digest_sha256 (315 ids).
 - B3 PASS: verification.json (schema directive_verification/v2) at the frozen head has exactly one M0-T198 row; applicable_requirement_ids = [R307,R309,R310,R314]; producer "orchestrator"; verifier "" (empty); all four requirement sub-rows state "pending", evidence [], reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs on the packet returns ok=true, applicable_ids == cited_ids == [R307,R309,R310,R314], missing/invalid/unresolved all empty.
 - B5 PASS: scanning every requirements.json across all directives, M0-T198 appears only in those 4 D-094 rows — nothing else applies to this task uncited. R308/R311/R312/R313/R315 are bound to D-094-BOOTSTRAP only (chat returns / owner decision / go-ahead), correctly not product requirements on this task.
 - GATES: M0-T198-G0.json PASS (orchestrator, administrative, reviewed_sha 46c92cad); M0-T198-G2.json PASS (orchestrator, self_check) and M0-T198-G3.json PASS (code-reviewer, independent_review) both at reviewed_sha 8e1d5912 with the SAME content_manifest_sha256 d8b8b5c70c74ba608a678f9583d324f2900e4f4982954cf3534e87dd30e31534 — G2 and G3 at one content identity. The three allowed-path blobs are identical at d0c22841 (build), 8e1d5912 (submit/G2-G3), and 95e6f299 (frozen); CI run 38834850070 at headSha 8e1d5912 completed success, 21/21 jobs. Producer (orchestrator) != verifier; validate_directive_compliance.py --check returned EXIT 0.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while this blob-level predicate holds: .claude/skills/dispatch-brief/SKILL.md == eb15e1e9960c90d144dcd00863f68db0aca1ffc1; .claude/rules/helper-briefing.md == 32dd7abe5f30fcf79079c4a296fa7b8570ad5efe; project-control/reports/M0-T198-producer-report.md == 6b444e37e4c7e2996b60b8930903408d62fb766c; project-control/tasks/M0-T198.json == 5ed4d9c420c556a54a46cac1cae6e6c54a416300; and the four rows R307/R309/R310/R314 keep their frozen text and their M0-T198 binding.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file — other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets, gates, reports; other tasks appended to the applicability of these same rows (e.g. the wiring part M5-T173 at its contract, with its digest resync and provisional verification rows); new rows appended to the directive; and ledger state — plus this task's own acceptance records and a merge of the main line that changes none of the predicate's files. I already observed M5-T173's contract+claim land and resync the directive digests while all four predicate blobs stayed identical and the validator stayed EXIT 0, so the condition is demonstrably robust to this activity. The expected wave-29 merge to main satisfies, not voids, the open carry-over noted per row.

(5) REQUIRED CORRECTIONS
 - None. Advisory (no file change needed): the evidence map marks R309 and R310 as fully met without restating that their harness ("skill file exists on main" / "every helper's start-time instructions contain the standard") also depends on the merge to main; that shared open step is, however, captured by the R314 open line and by known_limits ("The rule reaches later sessions once this branch is merged to main"), so the open carry-over is already recorded. Treat merge-to-main as the enabling step for all four rows, not an optional follow-up.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Whether every Claude Code runtime version loads no-paths rules into subagents identically: established from this runtime's injected context and the budget tool's documented intent, but not provable for all versions from repository evidence. It does not affect the verdict, since R314 targets fresh later sessions that load from main at start.
 - Post-merge behavior (a fresh session on main loads the rule and lists the skill): cannot be exercised read-only before the merge. I have first-hand negative confirmation (helper-briefing.md absent from my own injected context because it is not on main yet); the positive post-merge load is the wave-29 merge step.
 - S4 by a fresh skill invocation: I did not dispatch a helper (read-only). I observed that the brief which dispatched me follows the five-part structure plus the return contract, but that is an observed artifact, not a fresh run of the skill.
 - Live CI at the eventual accept head: the branch head keeps advancing with peer commits. I verified CI green at the submit head 8e1d5912 (identical task blobs); reading CI green at the final accept head remains the orchestrator's at accept time (D-090-R639).
 - The private owner attachment (father-facing skill prompt): it lives outside the public repo on the build server. I confirmed only that it is referenced by path and digest in source-029 and is NOT copied into the repository, consistent with the public-repo rule.
END-OF-REPORT
```
