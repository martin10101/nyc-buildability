# D-024 Amendment 19 — S16.7 excess disposition + resume-path defect class + fifth recert window (owner instruction 2026-08-30)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (typed in response to the seq-39 cycle-2 live-journey report,
`project-control/reports/M0-T107-cycle2-live-journey.md`: post-dispatch S14 counted stop;
rotation-at-seam did not fire, session resumed at 640,224 tokens; resumed worker cwd = primary
checkout). Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`2cf59c9` (local == origin; tree clean). Amends: `source-001.md` (owner directive v4).
Requirement IDs assigned: D-024-R327..D-024-R347.

Reconciliation: the owner (a) dispositions the cumulative S16.7 owner-touch excess as an
accepted measurement of this failed activation campaign only — with no budget
reset/increase/erasure/reinterpretation, no restart authorization, no recovery clearing, no
additional operational authority, and the complete touch history preserved (R327–R329);
(b) authorizes the bounded rotation-at-seam defect task and its required R247
recertification window (R330), widened to the COMPLETE resume-path defect class covering
both live-reproduced failures (R331): ceiling evaluation on EVERY launch/resume path before
provider contact (R332), never resume an at-or-above-400k session (R333) — rotate at the
safe seam or fail closed before provider contact (R334), cwd bound to the packet's isolated
worktree on every launch/resume/rotation (R335) with fail-closed on primary-checkout or
unexpected cwd (R336), rotation preserving lineage/identity/budgets/audit/branch/worktree/
exactly-once succession (R337), old transcript frozen + distinct new session identity
starting in wt-m0t107 (R338); (c) requires call-site enumeration with a same-seam proof
(R339) and a deterministic bypass-sensitive reachability test (R340); (d) directs the
preserved cycle-2 journal and transcript as read-only regression fixtures (R341) with the
named test matrix (R342); (e) requires honest recording of the rc=1/missing-result terminal
evidence and forbids claiming a proven provider context-limit rejection absent primary
evidence (R343/R344); (f) prohibits restarting the live loop, clearing recovery, editing
the journal, resetting budgets, or touching PR #241 (R345); (g) requires the full standard
process through recertification, manifest verification, and the R276 preflight (R346); and
(h) sets the hard sequencing hold: AFTERWARD STOP and present the exact live-start package
for a SEPARATE owner decision — no start of any kind follows automatically (R347). Ledger
tasks allocated under this authority: **M0-T123** (resume-path defect fix) and **M0-T124**
(fifth frozen-identity recertification + live-start package presentation).

Forward trace: p1 s1 ("I disposition the cumulative S16.7 owner-touch excess as an accepted
measurement of this failed activation campaign only.") → R327; p1 s2 ("This disposition
does not reset, increase, erase, or reinterpret any budget; does not authorize another
restart; does not clear recovery; and grants no additional operational authority.") → R328;
p1 s3 ("Preserve the complete touch history.") → R329; p2 ("I authorize the bounded
rotation-at-seam defect task and its required R247 recertification window.") → R330; p3
("Treat this as a complete resume-path defect class, covering both failures reproduced
live:") → R331; item 1 (every launch/resume path evaluates the ceiling before provider
contact) → R332; item 2 s1 ("A worker session at or above the 400k ceiling must never be
resumed.") → R333; item 2 s2 ("It must rotate to a fresh session at the safe seam or fail
closed before provider contact.") → R334; item 3 s1 (cwd bound to the packet's isolated
worktree) → R335; item 3 s2 (primary-checkout/unexpected-cwd launch fails closed before
provider contact) → R336; item 4 (rotation preserves lineage, identity, budgets, audit,
branch, worktree, exactly-once succession without duplicating or losing work) → R337; item
5 (old oversized transcript receives no new events; new session distinct identity, starts
in wt-m0t107) → R338; p4 s1 (enumerate every worker-launch/resume call site + same-seam
proof) → R339; p4 s2 (deterministic reachability test failing on any bypass of either
guard) → R340; p5 s1 (preserved cycle-2 journal + transcript as read-only regression
fixtures) → R341; p5 s2 (test matrix: oversized, exactly-at-threshold, below-threshold,
missing telemetry, stale session identities, controller restarts, recovery starts, Windows
paths, cwd mismatch, concurrent controllers, provider failure, removal sensitivity) →
R342; p6 s1 ("Record the CLI return code 1 and missing result honestly.") → R343; p6 s2
("Do not claim that a provider context-limit rejection was proven unless the underlying
terminal event is recovered from primary evidence.") → R344; p7 s1 ("Do not restart the
live loop, clear recovery, edit the journal, reset budgets, or touch PR #241.") → R345; p7
s2 (complete through G0/G2/G3/G4/G5, mutation testing, independent DCV, full
frozen-identity recertification, manifest verification, R276 preflight) → R346; p7 s3
("Afterward, stop and present the exact live-start package for a separate owner decision")
→ R347.

Anchors: #s167-disposition (p1), #defect-authorization (p2), #resume-path-class (p3),
#ceiling-every-path (i1), #never-resume-oversized (i2), #cwd-binding (i3),
#rotation-preservation (i4), #transcript-freeze (i5), #call-site-proof (p4),
#fixtures-and-matrix (p5), #terminal-evidence-honesty (p6), #prohibitions-process-hold (p7).

---VERBATIM-BEGIN---
I disposition the cumulative S16.7 owner-touch excess as an accepted measurement of this failed activation campaign only. This disposition does not reset, increase, erase, or reinterpret any budget; does not authorize another restart; does not clear recovery; and grants no additional operational authority. Preserve the complete touch history.

I authorize the bounded rotation-at-seam defect task and its required R247 recertification window.

Treat this as a complete resume-path defect class, covering both failures reproduced live:

Every path capable of launching or resuming a Claude worker—including ordinary start, recovery start, controller restart, rotation, turnover, and checkpoint continuation—must evaluate the context-rotation ceiling before contacting the provider.
A worker session at or above the 400k ceiling must never be resumed. It must rotate to a fresh session at the safe seam or fail closed before provider contact.
Every worker launch, resume, and rotation must bind its cwd to the task packet’s isolated worktree. A primary-checkout or unexpected-cwd launch must fail closed before provider contact.
Rotation must preserve checkpoint lineage, task identity, budgets, audit history, branch, worktree, and exactly-once succession without duplicating or losing work.
The old oversized transcript must receive no new events after rotation; the new session must have a distinct identity and start in wt-m0t107.

Enumerate every worker-launch and worker-resume call site and prove that each passes through the same rotation and cwd enforcement seam. Add a deterministic reachability test that fails if any call site bypasses either guard.

Use the preserved cycle-2 journal and transcript as read-only regression fixtures. Test oversized sessions, exactly-at-threshold sessions, below-threshold sessions, missing telemetry, stale session identities, controller restarts, recovery starts, Windows paths, cwd mismatch, concurrent controllers, provider failure, and removal sensitivity.

Record the CLI return code 1 and missing result honestly. Do not claim that a provider context-limit rejection was proven unless the underlying terminal event is recovered from primary evidence.

Do not restart the live loop, clear recovery, edit the journal, reset budgets, or touch PR #241. Complete the bounded task through G0/G2/G3/G4/G5, mutation testing, independent DCV, full frozen-identity recertification, manifest verification, and R276 preflight. Afterward, stop and present the exact live-start package for a separate owner decision
---VERBATIM-END---
