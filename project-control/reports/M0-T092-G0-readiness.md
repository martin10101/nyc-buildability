# M0-T092 G0 readiness (unit F: controller state machine, safe seams, exact-once succession, outage handling)

Recorded 2026-08-27 UTC by the orchestrator (fable-orchestrator-session) at HEAD `2613d4e`.

1. **Bootstrap Gate 0 (D-024-R125..R128):** session primary cwd IS the worktree root
   (`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`); MCP-clean; unchanged since session start.
2. **Dependencies:** M0-T091, M0-T103, M0-T104, M0-T105, M0-T106 — ALL accepted (unit sequence
   complete through E). M0-T092 (unit F) is the next claimable unit at campaign seq 16.
3. **Directive binding:** `evaluate_task_refs(M0-T092)` → ok=True, missing=[]; applicable set is
   large (65 requirements incl. R002/R028–R033 section-3 states, R067 handoff packet, R102 Phase-D
   freeze evidence, R160 native-resume-never-a-seam-substitute, R180 one-backend, R125–R128 Gate-0,
   R042/R045 telemetry/worker-text). Supervisor-freeze qualifying evidence for the packet:
   **D-024-R102** (Phase D; packet-named).
4. **Session authorization + staging intent:** owner directive **D-031** extends this session to
   ~750k context then handoff; occupancy at claim ≈59% (statusLine sidecar). Unit F is the largest
   remaining unit (65 requirements, prove-and-extend across ≥9 accepted modules) and CANNOT reach a
   clean submitted+G2 seam within the remaining budget. Per D-031-R002 (land at the nearest clean
   seam, never mid-gate/mid-implementation), this session stages unit F to the **claim + G0 +
   scenario-pack/reuse-boundary seam** and hands off — the exact pattern by which THIS session was
   itself handed M0-T105 ("in flight at 20% with scenario pack"). The successor implements from the
   frozen pack with a fresh context budget.
5. **Scope sanity / reuse-first (R018/R029):** allowed_paths (`tools/agent_supervisor`, the new
   test file, the unit report) overlap no in-flight writer (no sub-agents in flight; M0-T109
   backlog). R018 requires proving the existing architecture and avoiding duplicate machinery;
   R029 says use/extend the existing state machine. The reuse surface is mapped in
   `M0-T092-controller-succession.md` §0 (state_machine.py 23 states already present;
   durable_state, lease_runtime, recovery, turnover_controller, session_continuity, preflight,
   start_gate, handoff all accepted and REUSED/extended, never duplicated).
6. **Worktree:** primary checkout (orchestrator-as-producer, M0-T104/T105/T106 precedent); tree
   clean at `2613d4e`, origin identical.

G0 verdict: **PASS** — ready to claim (staged-to-pack-seam under D-031).
