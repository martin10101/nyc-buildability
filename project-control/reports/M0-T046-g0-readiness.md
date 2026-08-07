# M0-T046 G0 readiness (administrative)

**Task:** M0-T046 - Owner am.12 pre-activation hardening: park-to-approve operator-digest binding,
estop audit-fork regression lock, controller-config Windows OS-ACL boundary
**Recorded by:** orchestrator. **Date:** 2026-08-07 (UTC).

- Packet complete: objective (execute the owner pre-activation decision D-010 am.12 as exactly ONE
  narrowly bounded task containing ONLY the three R124/R125-R126/R127-R128 scopes, with the R129
  prohibition), allowed paths (tools/agent_supervisor/, tools/test_agent_supervisor_*.py, the
  M0-T046 producer report, packet), acceptance scenarios AS-1..AS-6 (executable; AS-6 is the
  boundary/prohibition scenario verified over the diff surface), directive_refs (D-010
  R122..R133 - the full am.12 set per the session-5 handoff instruction), gates G0/G2/G3/G4/G5,
  five reviewers rostered (producer != reviewers). R130 names the normal independent engineering,
  QA/security, and directive-compliance gates - satisfied by the G3/G4/G5 roster + DCV at accept.
- Dependencies: M0-T045 ACCEPTED (R595 rehearsal complete, all legs live-proven; gates
  G0/G2/G3/G4/G5 PASS) - dependency-valid. Base for this branch: origin/main `ae627e5`
  (PR #176 merge; the closed D-009/M0-T019/M2-T014 seam required by R122).
- AD-093 qualifying evidence (freeze citation duty): every scope is directive-cited work, named
  verbatim in am.12 - (1) the M0-T045 G5 LOW-1 finding (M0-T045-g5-security.md; activation-checklist
  'M0-T045 G5/G4 additions' item 1), (2) the M0-T045 G4 estop audit-fork follow-up
  (M0-T045-g4-qa-review.md MATERIAL FINDING; checklist item 2) with the R126 owner acknowledgement
  captured verbatim, (3) the activation-checklist OS-ACL judgment item (G5-L-2), which the owner
  RESOLVED in R127: the current single-account writable ACL is NOT sufficient for activation.
  am.12 states these satisfy the 0A.10 freeze/AD-093 evidence requirement. A finite, closed list.
- Sequencing (R122/R123): the D-009/M0-T019/M2-T014 batch reached its clean committed verified
  seam (PR #176 merged, CP-0042, accepted count 66) - R122 satisfied before this packet was cut.
  This is the ONE inserted pre-activation task; M2-T015 has not begun (R123, R133).
- Posture: SHADOW-ONLY remains in force. Nothing in this task activates supervised-auto; R131
  keeps activation an owner-typed decision AFTER acceptance + mechanical checklist reconciliation,
  and R132's decision-line return item happens after that. No activation flag flips in scope.
- Owner-adjacency note (R128): applying a stricter ACL to the live owner config path requires an
  ELEVATED owner action by definition of the boundary itself. The producer delivers the hardening
  artifacts (elevated apply/rollback script + bounded unelevated probes + digest-verification
  retention); the elevated apply is an owner/UAC step surfaced explicitly - consistent with D-008
  (credentials/elevation stay with the owner). Probes run unelevated and are bounded and
  non-destructive; ambiguous ACL state fails closed (AS-5).
- Prohibition honored by construction (R129): no service, daemon, enterprise identity system,
  separate infrastructure project, or supervisor redesign; diff confined to allowed_paths.
- Forbidden paths: .claude/, apps/, services/, .github/, project-control/directives/, and all
  dependency manifests/lockfiles - no producer writes there.
- Blockers: none reference M0-T046. Standing holds (deployment/G6/Graphify/expansion) untouched.
- Producer: backend-engineer (delegated, spawned UNNAMED per the guard rule), working in the orch
  worktree on a fresh branch from origin/main.

**G0 result: PASS (ready to claim).**
