# M0-T045 G0 readiness (administrative)

**Task:** M0-T045 - R595 supervised rehearsal + supervised-auto promotion evidence (Section 16.2; D-010-R104)
**Recorded by:** orchestrator. **Date:** 2026-08-07 (UTC).

- Packet complete: objective (design, execute, and independently review the R595 supervised
  rehearsal that live-actuates the rotation seam - the R593 accepted residual - with full audit
  evidence, then assemble the Section 16.2 promotion-evidence pack for the shadow-to-
  supervised-auto step; bounded per R104), allowed paths (tools/agent_supervisor/,
  tools/test_agent_supervisor_*.py, the two M0-T045 report files, packet), acceptance scenarios
  AS-1..AS-3 (all executable), directive_refs (D-010 R026/R031/R074..R079/R089/R090/R104/
  R113..R115 + re-dispatch R116/R117/R118), gates G0/G2/G3/G4/G5, five reviewers rostered
  (producer != reviewers).
- Dependencies: M0-T040, M0-T041, M0-T042, M0-T043, M0-T044 all ACCEPTED - dependency-valid.
  Base for this branch: origin/main `f61a735` (includes the merged D-010 am.7 capture, R118).
- AD-093 qualifying evidence (freeze citation duty): D-010-R104 names R595 as the mandatory
  pre-activation step and simultaneously bounds it (never an open-ended supervisor-development
  project); AD-074 (staged promotion), AD-076 (prove no rotation with active children), and the
  M0-T036-ACTIVATION-CHECKLIST (D-007-R619) make the rehearsal a directed blocking capability,
  not a speculative feature. The pre-R595 hardening obligations are the THREE PINNED, ENUMERATED
  sets on the activation checklist (M0-T042 G5 L-1/I-1/I-3; M0-T044 G3 MINOR-1/MINOR-2; M0-T044
  G5 SEC-1/SEC-2/SEC-3/INFO-1) plus the M0-T041 CP-0037 items - a finite, closed list.
- Posture: SHADOW-ONLY remains in force for every autonomy tier. The rehearsal is the one
  SUPERVISED live actuation of the rotation seam that R595 itself defines (owner present,
  full audit evidence, independently reviewed); it activates nothing. The promotion decision
  is owner-gated; per AS-3 the pack claims at most shadow-to-supervised-auto readiness.
- Owner-adjacency: the live rehearsal run requires the owner's supervised window (CP-0039
  next_action; SESSION_HANDOFF session-3 checklist item 2). Pre-rehearsal engineering
  (hardening sets, rehearsal harness/runbook, promotion-pack skeleton) proceeds autonomously;
  the live run is scheduled with the owner and never executed unsupervised.
- Bounded-unit rule: if the unit cannot complete in one bounded increment chain, split per
  D-010-R103 (packet risk note) rather than extend open-endedly.
- Forbidden paths honored by construction: no .github/, .claude/, apps/, services/,
  project-control/directives/ writes by the producer.
- Blockers: none reference M0-T045.
- Producer: backend-engineer (delegated, spawned UNNAMED per the guard rule).

**G0 result: PASS (ready to claim).**
