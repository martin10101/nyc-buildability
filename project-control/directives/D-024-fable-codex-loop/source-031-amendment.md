# D-024 Amendment 31 — stop at the M0-T131 acceptance seam; no recert against the obsolete 2.1.251 pin; present the combined 2.1.252-admission + single-recert plan (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
mid-turn message, BEFORE acting on its forward-looking parts (D-001). Base identity at
capture: branch `control/D-024-fable-codex-loop`, HEAD `00220b8c` (the M0-T131
acceptance capture commit, pushed; campaign seq 62). Delivery context: the message
arrived mid-turn while the acceptance capture commit was landing; its backward-looking
parts (continue the DCV uninterrupted; if PASS accept M0-T131; commit/push the complete
control-plane record normally) were already satisfied exactly as directed (DCV OVERALL
PASS 6/6; accepted; `00220b8c` pushed), and its stop landed BEFORE any R247
recertification step had begun — nothing was recertified against any pin. Amends:
`source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R431..D-024-R432.

Reconciliation: R431 — STOP at the M0-T131 acceptance seam before beginning R247
recertification; NEVER recertify against the obsolete 2.1.251 provider pin while the
installed executable is 2.1.252 (a pin-unchanged recert would force an immediate second
recertification); preserve the HALTED journal, the worktrees, all evidence, the budgets,
and every owner gate unchanged at the seam. This SUPERSEDES the Amendment-30 R430
sequencing detail "provider pin UNCHANGED at the certified 2.1.251" for the recert step;
the single-recertification principle (R428: one recert at one final identity) stands and
is now targeted at the combined post-admission identity. R432 — at that seam, report
(a) the final M0-T131 acceptance identity and (b) the EXACT proposed combined plan for
admitting the already-installed 2.1.252 identity and performing ONE single R247
recertification covering BOTH the M0-T131 supervisor tree move AND the admitted runtime.
EXPLICIT NON-AUTHORIZATION: the 2026-09-01 message does not authorize the admission, the
repin, the recertification, or any supervisor start — each remains an owner decision;
the plan is PRESENTED ONLY. The rows bind the proposed admission+recert task (assigned
id M0-T132 on authorization); until that task exists they are enforced through the
campaign record's next_action and this capture.

Forward trace: "STOP before beginning R247 recertification ... Do not recertify against
the obsolete 2.1.251 provider pin ... Preserve the HALTED journal, worktrees, evidence,
budgets and all owner gates unchanged" -> R431; "report the final M0-T131 acceptance
identity and the exact proposed combined plan ... This message does not yet authorize
the admission, repin, recertification or any supervisor start" -> R432; "Continue the
currently running DCV through completion and, if it passes, accept M0-T131 and
commit/push its complete control-plane record normally. Do not interrupt or restart the
verifier." -> already-satisfied backward-looking instruction, evidenced by the DCV
record, the acceptance, and commit `00220b8c` (no new requirement row; conduct matched
the instruction).

Anchors: #stop-no-obsolete-pin-recert (R431), #seam-report-and-non-authorization (R432).

---VERBATIM-BEGIN---
Continue the currently running DCV through completion and, if it passes, accept M0-T131 and commit/push its complete control-plane record normally. Do not interrupt or restart the verifier.

At the M0-T131 acceptance seam, STOP before beginning R247 recertification. Do not recertify against the obsolete 2.1.251 provider pin, because the installed executable is 2.1.252 and doing so would force a second recertification immediately afterward. Preserve the HALTED journal, worktrees, evidence, budgets and all owner gates unchanged.

At that seam, report the final M0-T131 acceptance identity and the exact proposed combined plan for admitting the already-installed 2.1.252 identity and performing one single R247 recertification over both M0-T131 and the admitted runtime. This message does not yet authorize the admission, repin, recertification or any supervisor start.
---VERBATIM-END---
