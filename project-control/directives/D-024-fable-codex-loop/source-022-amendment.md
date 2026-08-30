# D-024 Amendment 22 — ONE bounded final end-to-end stabilization and commissioning window authorized (owner instruction 2026-08-30)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
message, BEFORE acting on it (D-001). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `44465e7` (local == origin; tree clean; campaign
seq 48 — the Amendment-20/21 attempt outcome record: counted stop `no_valid_checkpoint`
at exactly 12/12 turns, eight-point proof 5 PASS / 1 FAIL / 2 not reached, journal
preserved at PAUSED_RECOVERY). Amends: `source-001.md` (owner directive v4); responds to
the options presented under R361 by expanding (A)+(B) into one bounded window. Requirement
IDs assigned: D-024-R372..D-024-R394.

Reconciliation: the owner authorizes EXACTLY ONE bounded, final end-to-end stabilization
and commissioning window (R372) whose objective is the COMPLETE journey — fresh-worker
launch, orientation, checkpoint emission, independent Codex review, exactly-once task
advancement, next-task selection, continued multi-unit operation — not merely the 12-turn
checkpoint failure (R373). All live evidence is preserved byte-for-byte and the standing
prohibitions hold throughout, including NO live launch during the window (R374/R375). The
durable checkpoint design carries seven named properties (R376–R382). Code changes are
preceded by a complete launch-to-next-task call-graph review with a ten-class defect
search (R383/R384), and every in-scope defect is corrected at ONE final frozen identity
(R385). Coverage is removal-sensitive and adversarial over preserved real artifacts as
read-only replay fixtures with a sixteen-scenario minimum (R386/R387) plus consecutive
simulated bounded advancements with no human intervention (R388). Independent review, all
applicable gates and DCV, and the full R247 recertification run ONCE at the final frozen
identity (R389/R390). After certification the window STOPS and presents one consolidated
report including the exact commissioning commands, which the orchestrator never executes
(R391/R392). Full autonomy is not declarable from tests/simulations; it requires a
separate owner-authorized live commissioning journey proving seven facts, and any live
failure stops without retry and returns one consolidated assessment for a new owner
decision (R393/R394).

Forward trace: p1 s1–s2 (one bounded window; not merely the 12-turn fix) → R372, R373;
p1 s3 (objective = every remaining seam of the complete journey) → R373; p2 s1
(byte-for-byte preservation) → R374; p2 s2 (window prohibitions incl. no live launch) →
R375; p3 items 1–7 (checkpoint design) → R376, R377, R378, R379, R380, R381, R382; p4 s1
(pre-code call-graph review + transition/surface enumeration) → R383; p4 s2 (ten-class
defect search) → R384; p4 s3 (correct all in-scope defects at one final frozen identity)
→ R385; p5 s1 (removal-sensitive adversarial coverage on preserved artifacts as read-only
replay fixtures) → R386; p5 list (sixteen-scenario minimum) → R387; p6 (consecutive
simulated advancements, no human intervention/duplicate/lost/false/unsafe) → R388; p7 s1
(independent review + gates + DCV) → R389; p7 s2 (full R247 recertification once at the
final frozen identity) → R390; p8 s1 (stop and present one consolidated report with the
named contents) → R391; p8 s2 (do not execute those commands) → R392; p9 s1–s2 (no
autonomy claim from tests/simulations; separate owner-authorized live commissioning
journey proving the seven facts) → R393; p9 s3 (live failure: stop without retry,
preserve, one consolidated assessment for a new owner decision) → R394.

Anchors: #window-authorization (p1), #preservation-and-prohibitions (p2),
#checkpoint-design (p3), #pre-code-review-and-one-identity (p4), #adversarial-coverage
(p5), #simulated-advancements (p6), #review-gates-recertification (p7),
#stop-and-present (p8), #live-commissioning-boundary (p9).

---VERBATIM-BEGIN---
I authorize expanding the combined A+B correction into one bounded, final end-to-end stabilization and commissioning window. Do not treat this as merely another fix for the 12-turn checkpoint failure. The objective is to inspect, correct, test, and certify every remaining seam from fresh-worker launch through orientation, checkpoint emission, independent Codex review, exactly-once task advancement, next-task selection, and continued multi-unit operation.

Preserve the current PAUSED_RECOVERY journal, audit chain, transcripts, worktrees, budgets, owner-touch history, and all live evidence byte-for-byte. Do not restart or clear recovery, edit the journal, repin binaries, merge PR #241, weaken any policy, cross an owner-only gate, or perform another live launch during this window.

Implement a durable checkpoint design that:

1. Front-loads a compact, evidence-grounded orientation packet for every fresh or rotated worker, including its task, lineage, worktree, current progress, relevant files and exact required output.


2. Requires an early structured progress checkpoint and supports incremental checkpoints during the unit.


3. Reserves a final turn exclusively for mandatory checkpoint emission before exhaustion, preventing additional exploratory tool use during that reserved turn wherever technically enforceable.


4. Allows an honest incomplete-but-resumable checkpoint without treating it as completion or advancing the task.


5. Sizes working-turn allowances from the bounded task/workload class under a documented hard safety ceiling; do not solve this merely by raising the fixed max_turns.


6. Fails closed if checkpoint emission, validation, persistence or forwarding does not complete.


7. Preserves exactly-once checkpoint persistence and forwarding across crashes, restarts, rotations and duplicate provider output.



Before changing code, review the complete launch-to-next-task call graph and enumerate every intended state transition and operating surface. Specifically search for unreachable edges, missing CLI arguments, command/runbook drift, primary-checkout leakage, resume-path differences, fixed-budget assumptions, stale durable state, duplicated actions, incomplete recovery transitions and differences between tested command shapes and owner-presented command shapes. Correct all defects discovered within this bounded stabilization scope at one final frozen identity rather than invalidating certification one defect at a time.

Build removal-sensitive and adversarial coverage for the complete journey using the preserved real artifacts as read-only replay fixtures. Exercise at minimum:

Fresh-session and rotated-session orientation.

A worker consuming every available working turn.

Early, incremental, incomplete and final checkpoints.

Missing, malformed, duplicate and contradictory checkpoints.

Codex HALT and CONTINUE outcomes.

Missing, malformed, duplicate and stale Codex verdicts.

Codex independent-review failure and successful completion.

Exactly-once task advancement.

Interruption immediately before and after checkpoint persistence, Codex forwarding, verdict persistence and campaign advancement.

Next-task selection and dispatch.

Rotation before provider contact.

Provider crash, refusal, quota exhaustion, context exhaustion and controller restart.

Worktree isolation and primary-checkout refusal on every launch and resume path.

Preservation of audit lineage, budgets, owner gates and pending-effect invariants.

Command-document validation proving every owner-presented command contains the complete required argument set and matches the certified executable path.


Require several consecutive simulated bounded task advancements with no human intervention, no duplicate or lost work, no false acceptance and no unsafe effect. Independently review the implementation and the complete system-level evidence, run all applicable gates and DCV requirements, and perform the full R247 recertification once at the final frozen identity.

After certification, stop and present one consolidated report containing: what was changed, the full end-to-end proof, every defect found proactively, all remaining limitations, the exact frozen identity, the complete preflight, and the exact commands for one controlled live commissioning attempt. Do not execute those commands yourself.

Full autonomy may not be declared from unit tests or simulations alone. It requires a separate owner-authorized live commissioning journey proving: the over-ceiling session is never contacted, a fresh Fable 5 worker launches in the correct isolated worktree, a valid checkpoint reaches Codex, Codex completes an independent review, M0-T107 advances exactly once, the next bounded task is selected, and multiple successive units operate without an owner touch. Any live failure must stop without retry, preserve all evidence, and return one consolidated system-level assessment for a new owner decision.
---VERBATIM-END---
