# M0-T196 reviews (every return kept unchanged)

Review: G3 code-reviewer PASS at 411b623c with required correction F1 and advisories A2-A4; delta PASS at 2426f9f6 (F1 resolved). The file below holds both returns, unchanged.

Every reviewer is an AI agent; none is a human or professional review.

## G3

G3 GATE REPORT — M0-T196 (living-files map). I am an AI agent (code-reviewer); this is an automated independent review, NOT a human or professional review. Read-only, pinned head 411b623c on task/wave24-report-v3 in /root/project/w-wave20.

VERDICT: PASS with required corrections.

WHAT I CHECKED (all from the files at the pinned head):
- Full diff scope (claim 4c1458b8a -> pinned): only .claude/rules/PROGRAM_KNOWLEDGE.md (M), .claude/rules/living-files.md (A), .claude/session-handoff-profile.md (M), the producer report (M), plus ledger state.json / M0-T196.json (claim/progress side-effects). No unexpected files.
- Ran python3 tools/context_budget_check.py at the pinned head (worktree clean at pinned): exit 0, PASS, no retired/superseded section, no duplicate board.
- Verified every removed PROGRAM_KNOWLEDGE line against the map/profile; verified all mapped paths exist; verified D-094 requirement texts (R105-R108, R109-R113, R114, R117) from requirements.json; verified the four owner-worded files are byte-unchanged; verified the 107-byte memory trim.

S1 (eager, complete) — PASS. living-files.md:1 has no frontmatter; budget check lists it as eager. Names every owner/objective-listed living file; all 10 mapped paths exist on disk. Rule ids accurate.
S3 (nothing lost) — PASS. Each removed one-liner's duty is preserved: backlog D-069, Astra D-050-R002/R005/R006, header append duty ("lessons when found"), loop-run pointer (shortened, same target) -> in the map; the two handoff lines (D-090-R941, D-070) are carried VERBATIM in session-handoff-profile.md:98-104 and short-form in the map. Diff confirms PROGRAM_KNOWLEDGE changed ONLY the header + the four removed one-liners + the loop-run shortening — nothing else.
S5 (owner-worded unchanged) — PASS. git diff of CLAUDE.md, .claude/rules/research-and-verification.md, CODING_RULES.md, expansion-agent-dispatch-hold.md between the two heads is empty.
Accuracy — PASS. D-069, D-050-R002/R005/R006, D-090-R941, D-070, D-094 R105-R108/R109-R113/R114/R117, D-093, principle 20 all match their sources.

FINDINGS:

1. [REQUIRED] S2 / objective — the "session start does not grow" claim is not met by the named tool. context_budget_check.py eager total GREW: before 44767B/515L/~11135 tok -> after 44872B/516L/~11163 tok (+105B / +28 tok). I confirmed "before" arithmetically from blob sizes: 44872 − 1647 (new living-files.md) + (18182−16640) (larger PROGRAM_KNOWLEDGE at claim) = 44767, exactly the producer's figure. The objective states "The eager total reported by tools/context_budget_check.py is not larger than before" and S2 says "the after total is not larger than the before total" — literally false for that tool. Net neutrality (−2B whole session start) holds ONLY via the out-of-repo MEMORY.md trim (verified −107B: old line 239B text -> new 132B, now points at the map). Two caveats the record should state: (a) the budget is null (no cap), so the guard never fails on size and cannot enforce this promise; (b) the compensating trim is in a non-git, non-guarded file, so any future eager regrowth or memory re-expansion is SILENT. The producer report discloses the +105/−107/−2 math honestly; the required correction is to reconcile the S2/objective wording with that reality (the repo eager portion grows; net-neutral depends on the unguarded memory trim) so a future reader cannot misread it as "the guard confirms no growth." Deliverable behavior is unaffected.

2. [ADVISORY] S4 — checklist has 8 bullets for 9 map lines (session-handoff-profile.md:87-96). The handoff+brief map line (living-files.md:17-18) has no dedicated confirmation bullet (implicit in the pre-HANDOFF gate), and the research bullet (line 90) confirms only research_record_check.py --check, not explicitly the zoning-rule-review register (principle 20) or the owner-research RQ-queue seam-line/PushNotification that the map's research line bundles. Strict "one item per map line" is not fully met; coverage is substantively adequate.

3. [ADVISORY] S1 completeness — MEMORY.md (the user auto-memory index) is a file sessions keep up to date (this task itself trimmed it) but is not named in the map's lessons line. It is a harness mechanism outside the repo, so arguably out of scope; flagged for owner awareness.

4. [ADVISORY] The checklist writes the result into SESSION_HANDOFF.md "section 3," which currently is "Helpers, commands, checks" (SESSION_HANDOFF.md:23). The reference resolves (section 3 exists); a future writer may expect a dedicated living-files section.

WHAT I COULD NOT FULLY CHECK:
- The pre-trim MEMORY.md is not git-tracked; I verified the 107-byte magnitude by measuring the new on-disk line (132B) against the old line reconstructed from my session-start context snapshot (239B). I could not retrieve a committed "before" state of that out-of-repo file.
- I computed the claim-head eager total arithmetically from blob sizes rather than checking out the claim head (the read-only guard blocks git archive/checkout writes); the arithmetic matches the producer's figure exactly.

END-OF-REPORT

DELTA VERDICT: PASS. F1 resolved: YES. I am an AI agent; this is an automated independent review, not a human or professional review.

SCOPE (git-confirmed): between 411b623c and 2426f9f6 only three commits touch the task, and only the task's allowed paths and packet plus expected ledger/G0 side-effects:
- e05e80e3: packet objective/S2/S4 restatement + M0-T196-G0.md + task json
- 3cf65130: progress 70 (state.json, task json)
- 2426f9f6 [ORCH-CORRECTED per G3 F1, A2-A4]: .claude/session-handoff-profile.md + producer report
The two eager-content files (.claude/rules/living-files.md, .claude/rules/PROGRAM_KNOWLEDGE.md) are byte-UNCHANGED since my PASS at 411b623c, so my S1/S3/S5/accuracy findings carry forward unchanged. No file outside allowed paths + packet was altered.

BUDGET CHECK at HEAD 2426f9f6: `python3 tools/context_budget_check.py` exit 0; eager total 44872B / 516L / ~11163 tok (unchanged from the passed head).

F1 (REQUIRED) — RESOLVED. The objective and S2 now measure the whole session start (eager project instructions reported by the tool PLUS the memory index). Both numbers are recorded (eager +105B: 44767->44872; memory -107B; net -2B) with the explicit no-guard caveat that the tool has no size cap (D-093-R074) and the memory index is outside git, so neither is guarded against later regrowth. The producer report adds a dedicated "Caveat (G3 F1)" paragraph saying the repo eager total alone grows 105 bytes. A dated scope_corrections entry attributes the change to G3 F1. The earlier inaccurate "the tool's eager total does not grow" wording is gone.

A2 (MEMORY.md) — ADDRESSED: new checklist item "Memory index (outside git, not in the map): new owner preferences or corrections of this session saved as memories."
A3 (S4 one-item-per-line) — ADDRESSED: research item now explicitly names the zoning-rule register (principle 20) and the RQ queue's seam line + PushNotification (D-050); added a handoff+brief item and a memory-index item; S4 reworded to "one item per map line (and one for the memory index)."
A4 (section 3) — ADDRESSED: the checklist writes its result as a "Living files:" line in the handoff's section 3, and the handoff+brief item names that slot.

NOTHING NEW OR ADVERSE. G0 correctly not re-recorded (tools/project_control.py refuses an administrative gate recorded by the task's own producer, which here is the orchestrator). The deliverable behavior is unchanged from the passed head; only the packet wording, checklist, and report caveat changed.

END-OF-REPORT
