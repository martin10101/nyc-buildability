# M0-T096 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T096 (unit I: integrated canaries, two-unit golden run, activation package, Amendment-7
watcher + pending_live_observation register; D-024 Phase H).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-28, campaign seq 22.
Supervisor-freeze qualifying evidence: **D-024-R106** (packet-named, Phase H).

1. **Bootstrap Gate 0 (R125–R128):** passed at session start — primary cwd IS the worktree
   root (`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`), branch
   `control/D-024-fable-codex-loop`, clean tree, local == origin at `65f282c`; NO MCP tools
   attached (session toolset carries zero `mcp__*` entries).
2. **Dependencies:** M0-T093 (H1), M0-T094, M0-T095 (H2) are all `accepted` (ledger);
   campaign seq 22 names M0-T096 as the authorized NEXT.
3. **Packet integrity:** inputs/outputs/allowed/forbidden paths present; directive_refs
   `D-024:ALL`; `evaluate_task_refs` resolves ok=true, **83 applicable ids** (incl.
   Amendment-7 rows R220–R230), no missing/invalid/unresolved (selective-citation guard
   satisfied at claim).
4. **Owner resume prompt (2026-08-28) classification:** citation-only restatement of the
   captured seq-22 NEXT + Amendment 7 + standing holds (R187/R595, PR #241, R125–R128,
   shadow-only). Every prompt item maps to an existing requirement (lane-1 authorization →
   R186/R182/R106/R222; no-wait/no-provoke → R220/R221; INJECTED labeling → R223;
   pending_live_observation → R224; watcher → R225/R226; compare-then-graduate → R227;
   feature-specific gating → R228; activation hold → R187). No new atomic requirement beyond
   D-024 R001–R230 → no new directive record (per /directive-compliance §0).
5. **Scope sanity:** allowed_paths cover `tools/agent_supervisor`,
   `tools/test_agent_supervisor_golden_run.py`, and the two output reports
   (`M0-T096-golden-run-evidence.md`, `M0-T096-activation-package.md`). The Amendment-7
   watcher is a new module under `tools/agent_supervisor` reading only existing sanitized
   telemetry/journal records (R225/R226) — in scope. `.claude/hooks`, settings, and every
   forbidden path untouched by the plan. GitHub effects SHADOW-ONLY (injected runners;
   R595 untouched).
6. **Lane discipline staged:** lane-1 injected/deterministic proofs only; all injected
   evidence labeled INJECTED (R223); natural-event evidence stays
   `pending_live_observation` (R224); never wait for or provoke a natural Fable 5 event
   (R220/R221). R187 HOLD after the golden run — continuous mode stays disabled.

Verdict: **PASS** (administrative readiness; independent review comes at G3/G4/G5 + DCV).
