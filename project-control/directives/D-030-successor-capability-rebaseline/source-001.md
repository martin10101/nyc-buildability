# D-030 source-001 — owner instruction (verbatim)

- **Received:** 2026-08-26 (UTC), owner `/session-handoff` invocation (reason argument) in session
  `session_01HfptKuEs3RDxaxsSHJjc7t` (branch `control/D-024-fable-codex-loop`), at the M0-T091
  SEAM READY hold (D-029 wait state).
- **Channel:** owner terminal `/session-handoff` command argument.
- **Capture rule:** text below the marker is the owner's reason argument, verbatim and complete.
  IMMUTABLE once D-030 is active (append-only amendments).

---VERBATIM-BEGIN---
owner-requested turnover after M0-T091; the successor must perform the native Claude Code capability re-baseline before claiming M0-T092 or any later D-024 task
---VERBATIM-END---

## Orchestrator interpretation note (not owner text)

Read as: (1) perform the session handoff NOW per the global `/session-handoff` skill and this
repository's `.claude/session-handoff-profile.md`; (2) the SUCCESSOR session must perform the
native Claude Code capability re-baseline — the M0-T086 pattern (D-024 §21 / Phase A item 2):
re-run the deterministic live probe (`python -m tools.agent_supervisor.capability_probe`),
re-verify `tools/agent_supervisor/fixtures/capability_matrix_v1.json` against the INSTALLED
`claude`/`codex` versions and current official docs, and record the refreshed evidence durably
as a bounded, gated ledger task (no untracked work) — BEFORE claiming M0-T092 or any later
D-024 campaign task. (3) This instruction is the owner's next instruction that D-029-R006 was
waiting for: it discharges the D-029 wait state and CONVERTS the D-029-R002 hold into the
re-baseline prerequisite — after the re-baseline task is accepted, the successor continues the
D-024 campaign chain (M0-T092 onward) under the standing authorizations; no separate further
owner release is required by this text. The 2026-08-25 baseline (claude 2.1.220 / codex
0.146.0) is treated as potentially stale; absence of drift must be PROVEN live, never assumed
(D-024-R001 discipline).
