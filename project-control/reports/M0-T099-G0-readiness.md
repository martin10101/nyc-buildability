# M0-T099 — G0 readiness (administrative)

Task: D-024 B1-follow-up — project statusLine handler + real installed-version fixture
(owner amendment 2, D-024-R129..R138) + carried M0-T089 gate-round hardening inputs.
Recorded by: orchestrator (G0 administrative class). Date: 2026-08-26 (session
session_01HfptKuEs3RDxaxsSHJjc7t).

- Dependency M0-T088 ACCEPTED (frozen content `23f0d80`, material identity `356d0f47`,
  acceptance commit `316cd8e`). M0-T089 also ACCEPTED (frozen `b7be085`, material identity
  `b42fe132`, acceptance commit `d9960d1`, checkpoint CP-D024-M0-T089 `3c8678c`). Campaign
  record seq 3 names M0-T099 as NEXT with the carried findings bundle spelled out.
- Bootstrap Gate 0 (D-024-R125..R128) PASSED for this session: primary cwd ==
  `git rev-parse --show-toplevel` == `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; branch
  `control/D-024-fable-codex-loop`; HEAD at session start `17b5198` == origin tip (fetch
  dry-run empty); working tree clean; `claude mcp list` reported verbatim "No MCP servers
  configured. Use `claude mcp add` to add a server." and the session tool roster contains
  zero `mcp__*` tools.
- Installed-version evidence (amendment-2 relevance): live `claude --version` = **2.1.220**
  this session, matching the amendment annex's installed-version proof and satisfying every
  documented statusLine version gate (2.1.205+/2.1.211+/2.1.214+).
- Packet extended pre-claim by the orchestrator (matching the M0-T088/M0-T089 precedent):
  named inputs/outputs added (amendment-2 deliverables + the ten carried M0-T089 hardening
  items listed by id), and `tools/test_agent_supervisor_telemetry_core.py` +
  `tools/test_agent_supervisor_subagent_telemetry.py` added to allowed_paths (carried items
  necessarily touch those packs: red/green proof for redaction/sdk/transcript/subagent
  hardening; G3 nit#5's dead assertion lives at `test_agent_supervisor_subagent_telemetry.py:306`).
- Packet valid after extension: `evaluate_task_refs` ok:True, applicable=10
  (D-024-R129..R138, bound via task_ids per amendment 2), cited=10, missing=[], invalid=[].
  M0-T089's 34-id set is NOT inherited — amendment-2 rows bind to this task alone.
- Supervisor-freeze (D-024 recognition): qualifying evidence = **D-024-R100 + D-024-R131/R132**
  (explicitly listed in the packet objective); citation duty carries to every commit touching
  `tools/agent_supervisor/**`.
- Boundary confirmations from amendment 2: live wiring into `.claude/settings.json` is an
  owner-visible step DOCUMENTED in the report, never performed (the path stays in
  forbidden_paths); subagentStatusLine implementation stays routed to M0-T089 (accepted);
  its live canary stays routed to the campaign canary task (D-024-R137); accepted work is
  immutable — the handler REUSES M0-T088 records/sanitization/sidecar/journal, no rebuild.
- Scope posture unchanged from M0-T089 G0: `tools/agent_supervisor` overlaps M0-T080 (D-023,
  own worktree `wt-m0t080`, own branch); reconciliation deferred to Phase D by the campaign
  plan. No claimed task holds a write lease on this branch/worktree.
- Blockers: none referencing M0-T099 (registry B-001..B-019 reviewed; none open against
  this task or `tools/agent_supervisor`).
- Outstanding-cleanup attempt recorded: the campaign-listed purge of the two harness-flagged
  qa-engineer agent worktrees (`agent-a97cd976cfb4344f0`, `agent-ac83580dbc0f69fce` under the
  pack repo's `.claude/worktrees/`) was ATTEMPTED and DENIED by the session permission
  classifier (the pack repo lies outside this session's permitted write roots). Facts
  verified read-only first: both are pack-repo worktrees at base `d8b3899` with ZERO unique
  commits; the flagged qa-engineer memory files are UNTRACKED
  (`.claude/agent-memory/qa-engineer/frozen-sha-test-harness.md` and
  `telemetry-redaction-latent-gaps.md` respectively), so directory removal destroys the
  content completely. Deferred as an owner-visible cleanup; exact commands recorded in the
  task report. Never merge agent worktree branches. This does not gate M0-T099 (different
  repo; no effect on this worktree or the ledger).

Result: PASS — backlog → ready to claim.
