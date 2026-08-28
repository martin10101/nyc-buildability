# M0-T093 — G0 readiness record (unit H1: guardrail-refusal classification + bounded 4.8 bridge)

Recorded by the orchestrator at the seq-19 acceptance seam (M0-T094 accepted this session).
Supervisor-freeze qualifying evidence: **D-024-R103** (Phase E; packet-named).

## Bootstrap Gate 0 (D-024-R125–R128) — verified live this session

- Primary cwd IS the worktree root: `git rev-parse --show-toplevel` = the session's primary
  working directory (`ctl24` checkout); no added-directory access path.
- Branch `control/D-024-fable-codex-loop`; tree clean at the seam; HEAD == origin after the
  seq-19 push (`ba040cb`).
- MCP-clean: the session's tool surface carries no MCP servers (settings deny-all posture;
  no `mcp__*` tools present) — verified at session start before any write.

## Packet readiness

- Dependency `M0-T092` (unit F) is ACCEPTED (seq 17) and merged into the control branch;
  its `epoch_lease`/`stop_intent`/`outage_policy`/`bootstrap_gate`/`state_machine` additions
  are the substrate the bridge states build on. M0-T094 (unit G) is ACCEPTED (seq 19).
- `evaluate_task_refs(M0-T093)` resolves ok with **49 applicable requirements** (Phase-E
  core R068–R075 + R103/R110 + the standing conduct/identity/testing set); the cited refs
  (`D-024:ALL`) cover the full applicable set — no selective-citation gap.
- Allowed paths are focused (`tools/agent_supervisor`, the new matrix test file, the unit
  report); forbidden paths exclude `.claude/hooks` and `.claude/settings.json` — unit H1
  is controller-internal, no hook/skill wiring.
- Required gates: G0 (this record), G2, G3, G4, G5 — same 4-reviewer + DCV cycle as units
  F and G.

## Qualifying evidence citation

Every commit for this task cites `D-024-R103` (supervisor-freeze rule §2/§3; the packet
objective names it).
