# M0-T105 G0 readiness (administrative; orchestrator)

- **Recorded:** 2026-08-27 UTC, session `session_01HfptKuEs3RDxaxsSHJjc7t`, branch
  `control/D-024-fable-codex-loop`, HEAD `0e0a892` (seq-14 advance; pushed == origin). Tree clean.
- **Bootstrap Gate 0:** PASS — primary cwd IS the worktree root; MCP-clean (no `mcp__*` tools);
  origin + marker files match the handoff profile.
- **Authority:** owner successor prompt this session — "proceed through the unit sequence to the
  M0-T096 golden run". Campaign seq-14 NEXT = M0-T105 (recorded in the campaign record at
  `0e0a892`). Authorization of recorded work; no new requirement.
- **Directive-reference coverage:** `evaluate_task_refs` at HEAD `0e0a892` → ok=true,
  applicable = D-024-R154/R155/R173, cited via `D-024:ALL` (3/3, missing 0).
- **Dependencies:** `M0-T104` **accepted** (commit 44a4c6c; the native runtime adapter unit D
  builds its event ingestion on). Verified in the ledger.
- **Scope + overlap note:** allowed_paths = `tools/agent_supervisor`, `.claude/hooks`,
  `tools/test_agent_supervisor_event_bus.py`, `project-control/reports/M0-T105-event-integration.md`.
  `.claude/hooks` is shared with the backlog task **M0-T109** (readonly-guard hardening) — M0-T109
  is NOT claimed, so there is no concurrent writer; unit D adds NEW event-recorder hook scripts and
  MUST NOT touch `readonly_agent_guard.py` (M0-T108/T109 territory). Any `.claude/settings.json`
  hook registration is a SEPARATE reviewed change (forbidden_paths includes settings.json).
- **Machine identity + carried preconditions:** installed claude 2.1.247 (measured-at-use). Unit D
  carries forward from the accepted M0-T102 matrix + M0-T104: source/confidence labels on every
  usage number (R042), whole-run vs final-request accounting (R043), never poll the transcript
  where a structured event exists, statusLine sidecar stays primary if the stream feed is
  absent/malformed (R154), UTF-8 subprocess decoding (native_runtime lesson), command hooks
  preferred over HTTP hooks (G5 unit-D precondition).
- **Modularity boundary:** responsibility = native event ingestion (hook records, stream-JSON
  subagent events, dedup, redaction, replay, drift). Placement = NEW focused modules under
  `tools/agent_supervisor/` reusing the accepted telemetry sidecar/journal/redaction subsystem
  (M0-T088/T089/T099) — not grown into `cli.py`/`policy.py` (symbol-ceiling warnings). Boundary
  tests = `tools/test_agent_supervisor_event_bus.py`. Modularity CI must pass before submission.
- **Required gates:** G0/G2/G3/G4/G5 with reviewers ≠ producer (producer = orchestrator session).
