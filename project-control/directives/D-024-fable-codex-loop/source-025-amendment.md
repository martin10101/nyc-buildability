# D-024 Amendment 25 — Stage-3 wiring window authorized (owner instruction 2026-08-31)

Captured: 2026-08-31 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
message, BEFORE acting on it (D-001). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `fefffdb` (local == origin; campaign seq 52;
Amendment-22 window COMPLETE with M0-T125/T126/T127 accepted at frozen material `2d46fb0`;
the staged commissioning package presented Option A/B/C under the R397 hold). This message
selects OPTION A. Amends: `source-001.md` (owner directive v4). Requirement IDs assigned:
D-024-R400..D-024-R409.

Reconciliation: the owner authorizes the bounded Stage-3 wiring task (R400): wire the
already-built, simulation-proven exactly-once next-task selection and advancement machinery
(`next_task.py`) into the live limited-auto execution path so that ONE owner-authorized
start can complete M0-T107, select the next eligible campaign task, launch it in its
correctly isolated worktree, and continue across multiple bounded tasks without another
owner touch. Throughout implementation the current journal and all evidence stay untouched
(R401); every owner-only gate, fail-closed policy, budget, audit, worktree-isolation and
exactly-once requirement is maintained (R402); and during the correction window there is
no PR #241 merge, no clear-recovery, no loop start, and no live commissioning (R403).
Removal-sensitive coverage is required for the ten named live-path families (R404), and
the controller must NEVER silently select owner-gated, blocked, claimed, stale or
otherwise ineligible work (R405). Afterwards: the complete R247 recertification runs ONCE
at the final frozen identity followed by all applicable independent gates and DCV (R406);
then STOP and present one complete preflight and one owner-executed commissioning protocol
capable of proving all seven R393 facts including cross-task selection and multiple
successive tasks without an owner touch (R407), with every presented command mechanically
validated against the live CLI contract (R408) and never executed by the orchestrator
(R409).

Forward trace: p1 s1-s2 (authorize wiring; one start -> complete M0-T107 -> select next
eligible -> isolated worktree -> multiple bounded tasks, no owner touch) -> R400; p2 s1
(preserve journal/evidence) -> R401; p2 s2 (maintain gates/fail-closed/budget/audit/
isolation/exactly-once) -> R402; p2 s3 (window prohibitions) -> R403; p3 s1 (removal-
sensitive coverage list) -> R404; p3 s2 (never silently select ineligible work) -> R405;
p4 s1 (R247 once + gates + DCV) -> R406; p4 s2 (stop and present preflight + seven-fact
protocol) -> R407; p4 s3 (mechanically validate every presented command) -> R408; p4 s4
(do not execute) -> R409.

Anchors: #wiring-authorization (p1), #window-invariants (p2), #coverage-and-eligibility
(p3), #recert-and-presentation (p4).

---VERBATIM-BEGIN---
I authorize the bounded Stage-3 wiring task. Wire the already-built and simulation-proven exactly-once next-task selection and advancement machinery into the live limited-auto execution path so one owner-authorized start can complete M0-T107, select the next eligible campaign task, launch it in its correctly isolated worktree, and continue across multiple bounded tasks without another owner touch.
Preserve the current journal and all evidence untouched throughout implementation. Maintain every owner-only gate, fail-closed policy, budget, audit, worktree-isolation and exactly-once requirement. Do not merge PR #241, clear recovery, start the loop or perform live commissioning during the correction window.
Add removal-sensitive coverage for live-path cross-task selection, task eligibility, dependency ordering, isolated-worktree binding, checkpoint and Codex-review completion, duplicate advancement, crashes before and after advancement, stale campaign state, no eligible work, and stop/pause/emergency intents between tasks. The controller must never silently select owner-gated, blocked, claimed, stale or otherwise ineligible work.
Run the now-fast complete R247 recertification once at the final frozen identity, followed by all applicable independent gates and DCV. Then stop and present one complete preflight and one owner-executed commissioning protocol capable of proving all seven facts, including cross-task selection and multiple successive tasks without an owner touch. Mechanically validate every presented command against the live CLI contract. Do not execute the commissioning commands yourself.
---VERBATIM-END---
