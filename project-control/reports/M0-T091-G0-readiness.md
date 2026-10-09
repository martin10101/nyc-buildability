# M0-T091 — G0 readiness (administrative)

**Task:** D-024 C2: invisible runtime supervision (health bands, no-progress, extension gate, landing)
**Recorded by:** orchestrator (administrative gate class) · 2026-08-26 UTC
**Session:** `session_01HfptKuEs3RDxaxsSHJjc7t`, branch `control/D-024-fable-codex-loop`

## Bootstrap Gate 0 (D-024-R125–R128)

- Verified THIS session before any write: primary cwd IS this worktree root
  (`git rev-parse --show-toplevel` == `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`); branch
  `control/D-024-fable-codex-loop`; HEAD `1d8d53f` == origin tip; working tree clean; MCP roster
  empty (no `mcp__*` tools present in the session).

## Authorization chain

- Campaign `D-024-fable-codex-loop` seq 6 **NEXT = M0-T091** (machine-validated record, frozen
  `2fba87f`), confirmed live via `campaign_continuity --status`.
- The D-028 seam handoff (`docs/SESSION_HANDOFF.md` §10) names this exact action; resume prompt
  adds no new requirement beyond the captured campaign state (no new directive capture owed).
- Supervisor-freeze qualifying evidence: **D-024-R101** (Phase C) — cited in the packet objective;
  commits will cite it (freeze rule §3).

## Packet readiness

- Dependencies `M0-T089` and `M0-T090` both **accepted**. Task `backlog`, no producer, no blockers.
- `evaluate_task_refs`: ok=true; applicable == cited == 46 requirement ids (D-024:ALL resolution);
  `missing_ids: []`, `invalid_refs: []`, `unresolved: []` — no selective citation.
- Scope: `tools/agent_supervisor`, `tools/test_agent_supervisor_runtime_supervision.py`,
  `project-control/reports/M0-T091-runtime-supervision.md`. Forbidden paths intact. NOTE:
  `tools/test_agent_supervisor_bounded_contracts.py` is OUTSIDE this packet's scope — correction
  regression tests live in the new runtime pack; existing bounded-contracts tests must stay green
  under the corrected guards without edits.
- **Carried PRE-ACTIVATION CORRECTION BUNDLE** (canonical text in campaign seq 6 next_action;
  this unit owns the runtime graduation of these guards): G3 MAJOR-1 / G5 M2 (envelope-leak guard
  word-boundary/vocabulary-token match — bare `observe`/`land` substrings false-positive), G3
  MAJOR-2 + MINOR-3 + G5 M1 (quota/leak guards cover `70 %`, spelled `percent`, conserve synonyms
  save/economical/frugal), G3 MINOR-4 (root `/` lease normalizes to empty and dodges overlap), G3
  MINOR-5 (size-class error-code consistency), G5 M3 (lease paths: normalize dot-segments, reject
  absolute/traversal), G5 M4 (document + implement `assert_grantable` snapshot-vs-lock: runtime
  serializes grants and folds each grant into the active set), G5 N1 (`worker_text_fields` fail
  closed on unscannable field types), G4 ADV-1 (non-omittable s13 packet categories), DCV R063
  (add the "likely evidence sources" clause to `DEFAULT_EXTENSION_PROTOCOL`).
- Gates: G0 (this record) → G2 → independent G3 (code-reviewer) + G4 (qa-engineer) +
  G5 (security-reviewer) + DCV at the frozen identity → accept → advance the campaign record.
- Standing restrictions honored: NO worker-facing token quota/countdown/conserve-tokens pressure
  ever (D-024-R045); supervisor stays SHADOW-ONLY — nothing spawns, resumes, stops, or messages a
  live agent (R595/D-024 §18); never merge PR #241; no maxTurns/budget caps as routine sizing
  (catastrophic ceiling only, private, with partial-state recovery tested); suite-baseline duty
  applies (supervisor tree WILL change → re-establish the 2653/3/0 baseline).

**G0 verdict: PASS — packet ready to claim.**
