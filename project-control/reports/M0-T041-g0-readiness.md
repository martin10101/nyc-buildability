# M0-T041 G0 readiness (administrative)

**Task:** M0-T041 — Supervisor 0A.8 gap-closure A: quota-exhaustion classifier, activation-checklist B-rows, R207 live sampling
**Recorded by:** orchestrator. **Date:** 2026-08-07 (UTC).

- Packet complete: objective (close the reproduced activation-checklist gaps in the frozen supervisor's
  defect lane), clean-glob allowed paths (tools/agent_supervisor/, tools/test_agent_supervisor_*.py,
  report, packet), acceptance scenarios AS-1..AS-5, directive_refs (26 applicable rows), gates
  G0/G2/G3/G4/G5, five independent reviewers rostered.
- Dependencies: M0-T039 **accepted** (freeze + defect-only lane on main at f65d716) — dependency-valid.
  Every change in this task cites its activation-checklist/defect evidence per the supervisor-freeze rule
  (AD-093 citation duty) — qualifying basis: reproduced gaps in M0-T036-ACTIVATION-CHECKLIST.md
  (quota classifier QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False; G3 B-1..B-4; R207 live-sampling boundary;
  G5 LOW pending_prompt hardening).
- Blockers: none reference M0-T041.
- Frozen baseline to diff against: supervisor tree e8eeb4fa240013c508042654968b2a5fc25dcbeb; suite
  baseline 1165 run / 1163 pass / 2 skip (M0-T039 freeze record).
- Producer: backend-engineer (delegated). Reviewers != producer.

**G0 result: PASS (ready to claim).**
