# D-024 Amendment 16 — restart-channel defect window: close the F-2 class, recertify, one cycle-2 attempt (owner instruction 2026-08-30)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (typed in response to the seq-35 cycle-2 start-refusal report,
`project-control/reports/M0-T107-cycle2-start-refusal.md`: owner-typed certified start refused
pre-dispatch exit 13, the `owner_explicit_restart` edge has zero call sites). Base identity at
capture: branch `control/D-024-fable-codex-loop`, HEAD
`2775455f20ad34218e777000b6951b164dc9c6ba` (local == origin; tree clean except the
`project-control/state.json` timestamp touched by the seq-35 progress record, bundled into this
capture commit). Amends: `source-001.md` (owner directive v4). Requirement IDs assigned:
D-024-R302..D-024-R317.

Reconciliation: the owner authorizes the bounded AD-093 defect task proposed at seq 35 AND the
resulting R247 full recertification window (R302), widening the scope from the single HALTED
case to the complete reproduced F-2 defect class (R303) with named deliverables (R304–R309),
explicit prohibitions and fail-closed restart preconditions (R310, R311), a required test
matrix with exactly-once semantics and a durable audited owner-restart record (R312, R313),
the standard gate/recertification process (R314), a sequencing hold — R276 rerun and cycle-2
command handover only after the new certification passes (R315) — and the cycle-2 attempt
protocol: exactly one attempt (R316); any further post-dispatch counted stop enforces
Amendment 15 with no restart (R317). Ledger tasks allocated under this authority: **M0-T121**
(the restart-channel defect fix) and **M0-T122** (the frozen-identity recertification). No
other owner gate changes: PR #241 stays unmerged; autostart, C1 canary, Telegram live send,
natural-event graduation, OS-ACL remain owner-only; the cycle-2 start itself remains the
owner-typed act.

Forward trace: paragraph 1 sentence 1 ("I authorize the bounded restart-channel defect task
and the resulting R247 full recertification window.") → R302; paragraph 2 ("Close the complete
reproduced F-2 defect class, not merely the immediate HALTED case:") → R303; item "Implement
an explicit, audited, fail-closed operator recovery surface for HALTED → IDLE." → R304; item
"Address the EMERGENCY_STOPPED sibling with an appropriately stronger explicit operator
acknowledgment; never allow automatic or ordinary restart from an emergency stop." → R305
(stronger explicit acknowledgment surface) + R306 (prohibition: never automatic/ordinary
restart from an emergency stop); item "Enumerate every blocking or terminal supervisor state
and every state-machine recovery edge." → R307; item "Prove that each intended
operator-recovery edge has exactly one documented, callable CLI surface, while intentionally
terminal edges remain explicitly unreachable." → R308; item "Add a deterministic reachability
test that fails whenever a defined recovery edge has no command call site." → R309;
paragraph 4 ("Do not add a generic state-changing command, manually edit the journal, loosen
policy, reset budgets, erase audit history, or permit restart while asks, pending effects,
surviving children, identity drift, or unsafe recovery classification exist.") → R310 (no
generic command / no journal edits / no policy loosening / no budget resets / no audit-history
erasure) + R311 (fail-closed restart preconditions); paragraph 5 sentence 1 ("Test pre-fix
journals, current journals, repeated invocation, stale runs, concurrent controllers,
emergency-stop recovery, audit-chain continuity, and removal sensitivity.") → R312; paragraph
5 sentence 2 ("The command must transition state exactly once and leave a durable audited
owner-restart record.") → R313; paragraph 6 sentence 1 ("Run the standard G0/G2/G3/G4/G5,
independent-review, DCV, mutation, CI, and frozen-identity recertification process.") → R314;
paragraph 6 sentence 2 ("Only after the new certification passes may you rerun R276 and hand
me the same cycle-2 start command.") → R315; paragraph 6 sentence 3 ("Permit one cycle-2
attempt; on any further post-dispatch counted stop, enforce Amendment 15 with no restart.") →
R316 (one attempt permitted) + R317 (Amendment-15 enforcement, no restart).

Anchors: #authorization (p1), #f2-class-scope (p2), #halted-surface (item 1),
#emergency-sibling (item 2), #edge-enumeration (item 3), #edge-proof (item 4),
#reachability-test (item 5), #prohibitions (p4), #test-matrix (p5 s1), #exactly-once (p5 s2),
#gates-recert (p6 s1), #sequencing-hold (p6 s2), #one-attempt (p6 s3).

---VERBATIM-BEGIN---
I authorize the bounded restart-channel defect task and the resulting R247 full recertification window.

Close the complete reproduced F-2 defect class, not merely the immediate HALTED case:

Implement an explicit, audited, fail-closed operator recovery surface for HALTED → IDLE.
Address the EMERGENCY_STOPPED sibling with an appropriately stronger explicit operator acknowledgment; never allow automatic or ordinary restart from an emergency stop.
Enumerate every blocking or terminal supervisor state and every state-machine recovery edge.
Prove that each intended operator-recovery edge has exactly one documented, callable CLI surface, while intentionally terminal edges remain explicitly unreachable.
Add a deterministic reachability test that fails whenever a defined recovery edge has no command call site.

Do not add a generic state-changing command, manually edit the journal, loosen policy, reset budgets, erase audit history, or permit restart while asks, pending effects, surviving children, identity drift, or unsafe recovery classification exist.

Test pre-fix journals, current journals, repeated invocation, stale runs, concurrent controllers, emergency-stop recovery, audit-chain continuity, and removal sensitivity. The command must transition state exactly once and leave a durable audited owner-restart record.

Run the standard G0/G2/G3/G4/G5, independent-review, DCV, mutation, CI, and frozen-identity recertification process. Only after the new certification passes may you rerun R276 and hand me the same cycle-2 start command. Permit one cycle-2 attempt; on any further post-dispatch counted stop, enforce Amendment 15 with no restart.
---VERBATIM-END---
