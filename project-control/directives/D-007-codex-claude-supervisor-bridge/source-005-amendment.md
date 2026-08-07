# D-007 amendment 4 — owner message (verbatim capture)

- Captured: 2026-08-04T06:50:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch 307b7c6
- Amends: source-004-amendment.md

## The owner message

Controller pulled --ff-only to bc83092. Before run 5, two things: (1) enumerate the 17 diagnostics the fixer surfaced in the 2 files — file plus one line each — and confirm none touch the session-close path or the watchdog; (2) report CI status on bc83092 (R554 makes CI-green a packet precondition, so I want it on record now). Then launch run 5: shadow mode only, forward nothing, owner-touch budget unchanged, runtime evidence verbatim to runtime-run5, and report the full cycle — checkpoint validation, the Codex review outcome, the ShadowPlan, and the shadow_observation_complete record at the acceptance gate.

## Orchestrator reconciliation notes (not owner text)

- "run 5" in this message = the NEXT pilot run (the ledger's run 6; runs 1–5 already recorded).
  `runtime-run5/` already holds committed run-5 evidence; the new run's evidence goes to
  `runtime-run6/` to preserve prior evidence verbatim rather than overwrite it.
- "the 17 diagnostics ... the 2 files" = the Pyright diagnostics surfaced on the session-close
  (F-3) fixer worktree: 7 in tools/agent_supervisor/claude_runner.py + 10 in
  tools/test_agent_supervisor_runner.py.
- bc83092 predates 307b7c6 (F-6/F-7 codex-schema fix); the controller needs one further
  --ff-only pull before the launched run can pass the Codex review stage.
