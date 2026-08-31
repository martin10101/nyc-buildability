# D-024 Amendment 29 — reviewer-access diagnostic + fix task authorized (owner instruction 2026-08-31)

Captured: 2026-08-31 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
message, BEFORE acting on it (D-001). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `158cce91` (local == origin; campaign seq 61).
Delivery context: direct reply to the journey-4 consolidated assessment
(`reports/M0-T107-commissioning-journey-4.md`; campaign seq-61 NEXT), which recommended
"authorize a bounded reviewer-access diagnostic + fix task — step 1 is a single
authorized minimal live probe (a tiny codex exec in a scratch git folder to measure
exactly what its read-only harness permits on this host), step 2 the measured fix
(Windows-compatible read access or a self-contained reviewer clone — never write
access), then the fast R247 recert" and offered the authorization line. "ok do it"
AUTHORIZES that task. Amends: `source-001.md` (owner directive v4). Requirement IDs
assigned: D-024-R425..D-024-R428.

Reconciliation: one bounded defect-lane task (M0-T131) under the standard gates.
Step 1 (R425/R426): ONE owner-authorized minimal live `codex exec --sandbox read-only`
probe on this host, in a SCRATCH git directory + linked worktree (never the real
repositories), measuring what the codex 0.146.0 non-interactive read-only harness
permits: command execution at all, git operations, plain file reads, and the
linked-worktree `.git`-redirection reach — recorded as a measured installed-version
fixture (R233 discipline). Step 2 (R427): the fix the measurement dictates, preserving
the reviewer's read-only-with-respect-to-the-real-tree invariant (S13.12 invariant 10;
NEVER write access to worker or control trees). R428: any supervisor change
re-triggers R247 at the new frozen identity; afterwards the restart sequence
(owner-restart, then the start) is re-presented and remains owner-typed only
(R409/R414/R419 unchanged); S16.7 remains an unaltered owner measurement.

Forward trace: "ok do it" -> authorize the recommended bounded task -> R425; step-1
measurement duty (one minimal probe, scratch-only, fixture recorded) -> R426; step-2
measured fix preserving invariant 10 -> R427; recert + owner-typed restart sequencing
-> R428.

Anchors: #reviewer-access-authorization (R425), #probe-measurement (R426),
#measured-fix (R427), #recert-and-restart (R428).

---VERBATIM-BEGIN---
ok do it
---VERBATIM-END---
