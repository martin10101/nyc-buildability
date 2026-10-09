# D-024 Amendment 17 — live-journey proof standard for the restart-channel window (owner addendum 2026-08-30)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's mid-turn
addendum (typed while the Amendment-16 window was being set up — after the M0-T121/M0-T122
packet creation, BEFORE any producer dispatch; no producer was in flight, so this capture at
the immediate seam satisfies the addendum's own "next safe seam" instruction). Base identity
at capture: branch `control/D-024-fable-codex-loop`, HEAD
`2775455f20ad34218e777000b6951b164dc9c6ba` plus the uncommitted Amendment-16 capture set
(source-016, rows R302–R317, packets M0-T121/M0-T122), all bundled into the same capture
commit. Amends: `source-001.md` (owner directive v4). Requirement IDs assigned:
D-024-R318..D-024-R322.

Reconciliation: the addendum adds the completion-claim discipline for the Amendment-16
window. It (a) forbids interrupting an in-flight producer to capture a directive — captures
happen at the next safe seam (R318); (b) forbids declaring continuous operability proven
merely because the new restart command and its unit tests pass (R319); (c) defines the final
live evidence: the REAL preserved journal must be exercised end-to-end through owner
restart, preflight, a fresh Fable rotation, the independent Codex repository review, and
actual M0-T107 advancement (R320); and (d) sets the live-journey failure protocol: preserve
everything and report the new seam (R321), with no full-autonomy claim and no repeated
restarts (R322). This extends — and does not relax — Amendment 15/16: the one-attempt rule
(R316) and the Amendment-15 counted-stop enforcement (R317) stand unchanged. Rows bind
M0-T121 and M0-T122 as noted per row; the live journey itself remains the owner-typed
cycle-2 act.

Forward trace: sentence 1 ("do not interrupt an in-flight producer.") + sentence 2 ("Capture
this at the next safe seam.") → R318 (the capture-seam rule; s2 also anchors this capture's
own timing); sentence 3 ("Do not declare continuous operability proven merely because the
new command and unit tests pass.") → R319; sentence 4 ("The final live evidence must
exercise the real preserved journal through owner restart, preflight, fresh Fable rotation,
independent Codex repository review, and actual M0-T107 advancement.") → R320; sentence 5
first clause ("If that live journey fails, preserve everything and report the new seam") →
R321; sentence 5 second clause ("do not claim full autonomy or restart repeatedly.") → R322.

Anchors: #capture-seam (s1–s2), #no-unit-test-operability-claim (s3), #live-journey-evidence
(s4), #journey-failure-protocol (s5).

---VERBATIM-BEGIN---
Addendum: do not interrupt an in-flight producer. Capture this at the next safe seam. Do not declare continuous operability proven merely because the new command and unit tests pass. The final live evidence must exercise the real preserved journal through owner restart, preflight, fresh Fable rotation, independent Codex repository review, and actual M0-T107 advancement. If that live journey fails, preserve everything and report the new seam; do not claim full autonomy or restart repeatedly.
---VERBATIM-END---
