# D-024 Amendment 12 — same-window repair + residuals + recertification + gated resume (owner instruction 2026-08-29)

Captured: 2026-08-29 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (typed in response to the M0-T113 restart-refusal report: seam defect confirmed,
M0-T115 correction proposed, loop stopped safely). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `8d47fb846829377c150951aed14d661a511a5974` (local ==
origin; clean tree). Amends: `source-001.md` (owner directive v4). Requirement IDs assigned:
D-024-R272..D-024-R276.

Reconciliation: this authorizes executing the R270-mandated correction (M0-T115) and the
carried residuals (M0-T114) in ONE certification window while remaining SEPARATE bounded
tasks, commits, evidence, and reviews; it re-affirms the no-journal-hand-edit rule (R273
generalizes the M0-T113-scoped refusal already exercised); it adds the executable
path-proof obligation (R274); it instantiates the R247/R271 recertification as a new
ledger unit (M0-T116, the M0-T112 pattern at ONE frozen final identity); and it sets the
resume conditions for M0-T107 limited-auto operation with an explicit stay-stopped-on-
failure rule (R276). No owner gate is loosened; R257 exclusions unchanged.

Forward trace: paragraph 1 sentence 1 ("Execute M0-T115 and M0-T114 in the same
certification window, while keeping them as separate bounded tasks, commits, evidence, and
reviews.") → R272; sentence 2 ("Do not broaden either task and do not manually edit the
runtime journal.") → R272 (no-broadening) + R273 (no journal edit); paragraph 2 sentence 1
("Prove the complete deny → clear recovery → restart and approve-once → restart paths
against both new and pre-fix journal records.") → R274; sentence 2 ("Then perform the full
M0-T112-pattern recertification over one frozen final identity.") → R275; paragraph 3
("Resume M0-T107 in limited-auto mode only after every suite, gate, independent review,
manifest verification, and live preflight passes. If anything fails, remain stopped and
report it rather than bypassing the gate.") → R276.

---VERBATIM-BEGIN---
Execute M0-T115 and M0-T114 in the same certification window, while keeping them as separate bounded tasks, commits, evidence, and reviews. Do not broaden either task and do not manually edit the runtime journal.

Prove the complete deny → clear recovery → restart and approve-once → restart paths against both new and pre-fix journal records. Then perform the full M0-T112-pattern recertification over one frozen final identity.

Resume M0-T107 in limited-auto mode only after every suite, gate, independent review, manifest verification, and live preflight passes. If anything fails, remain stopped and report it rather than bypassing the gate.
---VERBATIM-END---
