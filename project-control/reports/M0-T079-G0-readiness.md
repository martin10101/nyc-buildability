# M0-T079 G0 readiness — bounded mode, budgets, breakers, recovery probes, refusals

Administrative readiness recorded by the orchestrator at campaign identity `6b9ae32`
(control/D-023-autonomy-campaign; base origin/main `d8b3899f`).

- **Directive binding:** in-regime, `D-023:ALL`. Governing rows: D-023-R011 (bounded mode
  deliverable), **R037 (owner amendment: NO hardcoded maximum run length; duration
  owner-controlled, unlimited allowed)**, R033 (activation hold), R023 (no unmeasured claims),
  campaign-wide conduct rows.
- **AD-093 qualifying evidence (supervisor-freeze lane, cited per §3):**
  (a) requirement explicitly listed in owner directive D-023 (Appendix A item 1 + amendment);
  (b) reproduced defect: `start --mode limited-auto` refuses via `LimitedAutoRefused` at
  `LoopConfig` construction (loop.py:222,263) and surfaces to the operator as a traceback,
  not a structured machine-meaningful refusal (campaign packet proof ledger, reproduced on
  the frozen identity);
  (c) measured gap: `LoopConfig(max_cycles=1_000_000)` accepted (no durable run-budget layer);
  breakers module header records that wiring counters to real event sites is incomplete
  (circuit_breakers.py:26-28 "Phase 1 scope note"), and `cmd_start` recovery facts are
  constant-true synthetic (packet must-fix 7).
- **Scope check:** `tools/agent_supervisor/**`, supervisor test files, two new test modules,
  producer report. No nonterminal task overlap (campaign supervisor tasks are strictly
  sequential; T079 is first).
- **Dependencies:** none within the campaign (root of the supervisor chain).
- **Freeze-baseline duty:** change must re-establish the supervisor suite baseline
  (>= 1165 tests, 0 failures on Windows) per `.claude/rules/supervisor-freeze.md` §4; the
  supervisor remains SHADOW-ONLY and R595 activation prerequisites are untouched.
- **Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t079` on `task/M0-T079-bounded-mode`
  at `6b9ae32` (clean).

G0 result: **PASS** — task is ready to claim.
