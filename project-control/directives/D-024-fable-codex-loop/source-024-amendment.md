# D-024 Amendment 24 — commissioning-package coherence hold (owner instruction 2026-08-31, relaying an external-model review)

Captured: 2026-08-31 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
message, BEFORE acting on it (D-001). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `7478100` (local == origin; M0-T127 awaiting_gate,
G0/G2/G3/G4 PASS recorded, DCV in flight on the 22-row set). Amends: `source-001.md`
(owner directive v4). Context: the owner pasted an assessment produced by a different
model and asked whether it is correct. The orchestrator verified the load-bearing claim
in code: `next_task.select_next_packet` / `record_advancement` / `advance_and_select`
have ZERO production call sites (only `plan_close_run` is wired, cli.py:2687), so the
stabilization package's presented single-cycle commissioning command cannot prove the
R393 facts "the next bounded task is selected" and "multiple successive units operate
without an owner touch", while the package simultaneously states the journey must prove
all seven facts — an unreconciled contradiction inside the presented package.
Requirement IDs assigned: D-024-R397..D-024-R399.

Reconciliation: the pasted assessment's factual core is CONFIRMED (the contradiction is
real); its status numbers are snapshots. The owner's operative instruction is the final
paragraph: do not run the presented commands — even after M0-T127 acceptance — until the
commissioning contradiction is resolved mechanically and reviewed (R397). The
stabilization package must map each of the seven R393 facts to the exact stage, command,
and wiring that proves it, naming plainly any fact NOT provable with the current
deliberately-unwired live dispatch and the prerequisite work required (R398). Whether to
wire live next-task dispatch (a supervisor code change re-triggering R247) or to accept a
staged commissioning with per-stage owner commands is a NEW owner decision the package
must present as options, never self-authorized (R399).

Forward trace: pasted-assessment contradiction paragraphs + closing question → R398
(coherence mapping duty; the verified defect); "Do not run the presented commands yet,
even if M0-T127 becomes accepted, unless the final gate explains exactly how that one
command progresses from M0-T107 into multiple subsequent tasks without another owner
command" → R397 (hold + resolution condition); the resolution necessarily involves
either new wiring or a re-scoped journey → R399 (owner-decision boundary).

Anchors: #commissioning-hold (closing paragraph), #coherence-mapping (contradiction
paragraphs), #wiring-decision (implicit resolution choice).

---VERBATIM-BEGIN---
Worked for 49s

It is much closer now. The main stabilization work is finished.

M0‑T126 is accepted at 100%.

All 17 integration defects were corrected.

The full supervisor suite passed: 2,990 passed / 2 skipped / 0 failed.

Golden certification passed: 42/42.

M0‑T127 is at 85%, currently going through final independent gates.

Latest CI: 19 passed, 1 still running, 0 failures.

Nothing is running live; the journal remains safely preserved.

PR #241 remains untouched.


The major mechanisms now built include fresh-worker orientation, checkpoint reservation, workload-sized turn limits, exactly-once advancement, correct Codex/worktree binding, rotation handling, durable forwarded prompts, between-cycle stop controls and automatic command validation. The recertification report is genuinely strong.

However, I see one important contradiction that must be resolved before you run the next command:

The report admits automatic next-task dispatch is only simulation-proven and "not wired to a live start."

The commissioning command specifies --max-cycles 1.

Yet the required live proof says it must select the next task and operate multiple successive units without an owner touch.


Those three statements do not fit together. A one-cycle command with no live next-task dispatch cannot prove multiple autonomous units. This is exactly the kind of package inconsistency that previously caused your repeated attempts.

So the honest position is:

Core stabilization: complete.
Final certification: almost complete.
Ready for owner launch: not quite—this commissioning contradiction must first be resolved mechanically and reviewed.

Do not run the presented commands yet, even if M0‑T127 becomes accepted, unless the final gate explains exactly how that one command progresses from M0‑T107 into multiple subsequent tasks without another owner command.

this from a different model is this correct 
---VERBATIM-END---
