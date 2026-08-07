# M0-T042 G0 readiness (administrative)

**Task:** M0-T042 — Codex ephemeral review integration (0A.8 item 4; AD-081..AD-088) + minimal root AGENTS.md
**Recorded by:** orchestrator. **Date:** 2026-08-07 (UTC).

- Packet complete: objective (make the fresh-ephemeral-Codex-review loop operational end to end
  with 0A.4 budget enforcement, 0A.3 cadence policy, AD-087 anti-duplication, AD-088 worker-fallback
  recording, and a concise Section 11.1 root AGENTS.md), clean-glob allowed paths
  (tools/agent_supervisor/, tools/test_agent_supervisor_*.py, AGENTS.md, report, packet),
  acceptance scenarios AS-1..AS-5, directive_refs (13 applicable rows incl. session-2 re-dispatch
  R116), gates G0/G2/G3/G4/G5, five independent reviewers rostered.
- Dependencies: M0-T041 **accepted** (quota classifier + R207 sampling + pending_prompt hardening,
  merged PR #161) — dependency-valid. Base for this branch: origin/main
  `0ed2cdb531dc06d147c00dd8e5530828566ef27f` (includes D-010 am.5 capture, PR #165);
  `tools/agent_supervisor` tree at base: `e2a1a6395f81185233f5f68b589d2d181fdfa7a3`
  (post-M0-T041; the M0-T039 e8eeb4fa freeze identity was superseded by the accepted M0-T041
  defect-lane changes; suite baseline to re-establish: 1189 run / 1187 pass / 0 fail / 2 skip).
- AD-093 qualifying evidence (supervisor-freeze citation duty): 0A.8 item 4 names fresh ephemeral
  Codex review a BLOCKING minimum-autonomy capability, and AD-081..AD-088 are explicit directive
  requirements — directed capability work, not a speculative feature.
- SHADOW-ONLY posture unchanged; R595 remains the mandatory blocking activation prerequisite
  (D-010-R104). Nothing in this task activates anything.
- Blockers: none reference M0-T042.
- Producer: backend-engineer (delegated). Reviewers != producer.

**G0 result: PASS (ready to claim).**
