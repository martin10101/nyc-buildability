# M0-T108 G0 readiness (administrative; orchestrator)

- **Recorded:** 2026-08-27 UTC, session `session_01HfptKuEs3RDxaxsSHJjc7t` (statusline session id
  masked per convention), branch `control/D-024-fable-codex-loop`, HEAD at recording `24aa061`
  (R162-discharge landing, pushed == origin tip). Tree clean; registry validator EXIT=0 at this
  identity.
- **Bootstrap Gate 0:** PASS — the session's primary cwd IS the worktree root
  (`git rev-parse --show-toplevel` == primary working directory); MCP-clean: no `mcp__*` tools
  exposed in the session tool list at session start or since; no `.mcp.json`, no `mcpServers`
  block, `.claude/settings.json` untouched since the M0-T103 G5 diff proof.
- **Authority:** owner instruction this session (2026-08-27, verbatim in conversation): "Continue
  D-024 from durable campaign sequence 12. Claim M0-T108 only. Complete and independently verify
  its required G0/G2/G3/G4/G5 gates at one frozen identity… Do not begin unit C–I reviewer
  dispatches until M0-T108 is accepted." — matches the recorded campaign seq-12 NEXT verbatim
  (authorization of recorded work; no new requirement → no amendment). Task origin: G5 M0-T102
  MEDIUM advisory (readonly-guard PowerShell write gap), packet `project-control/tasks/M0-T108.json`.
- **Directive-reference coverage (pre-claim):** `evaluate_task_refs` at HEAD `24aa061` returns
  `ok: true` with **empty applicable set** across all 28 active directives (no requirement row
  binds M0-T108 by task id, task type, milestone, or path); cited refs `D-024:ALL` valid. The
  accept-time verification will carry the explicit empty-set task row for D-024.
- **Dependencies:** none in the packet. Sequencing honored: M0-T108 lands BEFORE any unit C–I
  reviewer dispatch (owner instruction + G5 M0-T102 recommendation); no unit C–I task claimed.
- **Machine identity note:** installed claude binary 2.1.247 (auto-updated during the seq-12
  discharge; recorded in `M0-T103-R162-discharge-2.1.247.md`). M0-T108 touches only the repo's
  guard hook, settings matcher, tests, and its report — no supervisor runtime, no binary
  dependency; the drift-tooth RED (capability fixture 2.1.246 vs live 2.1.247) is unrelated to
  this task's scope and carried to unit C.
- **Reviewer-dispatch mitigation while the gap is open:** M0-T108's own G3/G4/G5 reviewers are
  read-only roster spawns; until this task lands, the recorded procedural stopgap applies —
  reviewer prompts explicitly forbid PowerShell/scripting mutations and the orchestrator stages
  exact paths only (no broad `git add`).
- **Scope:** allowed_paths = `.claude/hooks`, `.claude/settings.json`,
  `tools/test_readonly_agent_guard_powershell.py`, `project-control/reports/M0-T108-guard-powershell-fix.md`.
