# M0-T130 G0 readiness (administrative; orchestrator)

- **Recorded:** 2026-08-31 UTC, session `session_01SfXcRw7emzdojCDJmKxNTM`, branch
  `control/D-024-fable-codex-loop`, HEAD at recording `81d5a9ba` (Amendment-28 capture +
  packet landing). Registry validator EXIT=0 at the captured Amendment-28 content.
- **Bootstrap Gate 0:** PASS — primary cwd IS the worktree root; no MCP tools attached
  (unchanged since session start).
- **Authority:** owner directive 2026-08-31 "fix it fastest way" (Amendment 28,
  `source-028-amendment.md`, rows D-024-R420..R424) — authorizes the bounded AD-093
  defect task proposed by the journey-3 consolidated assessment. Supervisor-freeze
  qualifying evidence (cited in packet + commits): the journey-3 REPRODUCED DEFECT
  (`M0-T107-commissioning-journey-3.md`) + measured installed-CLI behavior
  (2.1.251 `absorbed_mid_turn`, 2026-08-31T18:35:01Z) — a reproduced defect, provider
  CLI drift, and a measured live problem.
- **Directive-reference coverage (pre-claim):** cited refs `D-024:ALL`; the Amendment-28
  rows R420-R424 bind task id M0-T130; verification skeleton (5 pending rows) registered
  at capture.
- **Dependencies:** none. Producer: `orchestrator-defect-runner` (M0-T108
  orchestrator-as-producer precedent, authorized by R420); worktree: the primary
  checkout (single writer, no parallel producers — M0-T108 precedent). Reviewers
  (independent, producer != reviewer): code-reviewer (G3), qa-engineer (G4),
  directive-compliance-verifier (accept-time DCV).
- **Scope:** allowed_paths = `tools/agent_supervisor/claude_runner.py`,
  `tools/test_agent_supervisor_runner.py`, `project-control/reports/M0-T130-reserved-turn-fix.md`.
  Required gates G0/G2/G3/G4. Supervisor change: R247 re-triggers at acceptance (R424).
- **Preservation:** journal PAUSED_RECOVERY (transitions 26) untouched; wt-m0t107 clean
  `c5c6ff7`; wt-m0t109 clean `1c06957`; PR #241 OPEN untouched; queue + packet digests
  unchanged.
