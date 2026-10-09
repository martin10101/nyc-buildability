# M0-T110 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T110 (unit K: persistent same-terminal Codex-only discussion channel `/loop-codex`;
D-024 Amendment 8, rows R231–R240/R246/R248/R249).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-28, campaign seq 23.
Supervisor-freeze qualifying evidence: **D-024-R232/R234** (packet-named, Amendment 8).

1. **Bootstrap Gate 0 (R125–R128):** passed at session start — primary cwd IS the worktree
   root (`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`), branch
   `control/D-024-fable-codex-loop`, clean tree, local == origin at `1b5513f`; NO MCP tools
   attached (session toolset carries zero `mcp__*` entries).
2. **Dependencies:** M0-T096 (unit I) is `accepted` (ledger; verification entry at reviewed
   head `9f93587`, manifest `0d999749`); campaign seq 23 names M0-T110 as the authorized
   NEXT (M0-T111 → M0-T112 follow; M0-T107 trails non-blocking).
3. **Packet integrity:** outputs/allowed/forbidden paths present; directive_refs
   `D-024:ALL`; `evaluate_task_refs` resolves ok=true, **13 applicable ids**
   (R231–R240, R246, R248, R249), no missing/invalid/unresolved (selective-citation guard
   satisfied at claim). Acceptance scenarios follow the unit-I precedent: executable
   prove-first pack (`tools/test_agent_supervisor_codex_channel.py`) rather than packet
   JSON rows.
4. **Owner resume prompt (2026-08-28) classification:** citation-only restatement of the
   captured seq-23 NEXT + Amendment 8 + standing holds (R187/R595, PR #241, R125–R128,
   shadow-only, Amendment-3/7 restrictions). Every prompt item maps to an existing
   requirement (channel surface → R234; interception + honest limits → R233/R235; bounded
   per-turn context → R236/R237/R238; closed dispositions + owner-gated promotion →
   R239/R240; sequencing before activation-package presentation → R232/R247; prohibitions →
   R248). No new atomic requirement beyond D-024 R001–R249 → no new directive record
   (per /directive-compliance §0). Amendment 8 itself was captured at seq 23 with validator
   EXIT=0; the R249 first-report was delivered at capture
   (`project-control/reports/D-024-amendment-8-owner-report.md`).
5. **Scope sanity:** allowed_paths cover `tools/agent_supervisor` (channel modules),
   `tools/test_agent_supervisor_codex_channel.py`, `.claude/skills/loop-codex` (user-only
   skill, `disable-model-invocation: true`), `.claude/hooks/loop_command_interceptor.py`
   (the EXISTING unit-G UserPromptSubmit interceptor being extended — it is packet-named and
   G5-review is a required gate; the untouchable guards `agent_dispatch_guard.py` /
   `readonly_agent_guard.py` sit in forbidden_paths and stay untouched), and the report
   `project-control/reports/M0-T110-codex-channel.md`. No settings, no new MCP servers, no
   new dependencies (stdlib/existing machinery only per the reuse plan — any dependency
   would trigger the full admission policy instead).
6. **Honesty + reuse discipline staged:** never claim /btw-equivalence without a measured
   installed-version fixture (R233 — ordinary commands queue until the turn ends; the second
   terminal stays the real-time path); intercepted commands blocked+erased pre-model with
   zero-context proof on the installed version or the truthful documented fallback (R235);
   reuse of the unit-G skill+interceptor architecture, codex_reviewer read-only contract,
   evidence-packet/redaction/token-budget machinery, durable_state CAS threads (R236/R237);
   stable refs over bare line numbers (R238); closed dispositions with no automatic
   Fable-instruction change and owner-gated promotion (R239/R240). Continuous mode stays
   disabled (R187/R232 hold); supervisor SHADOW-ONLY.

Verdict: **PASS** (administrative readiness; independent review comes at G3/G4/G5 + DCV).
