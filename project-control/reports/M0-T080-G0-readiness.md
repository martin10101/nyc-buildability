# M0-T080 G0 readiness — session/model turnover + owner-approved model routing

Administrative readiness recorded by the orchestrator at campaign identity `c52613f`
(includes merged M0-T079 bounded-mode machinery, currently awaiting_gate).

- **Directive binding:** in-regime, `D-023:ALL`. Governing rows: D-023-R013 (deliverable),
  R023, campaign conduct rows.
- **AD-093 qualifying evidence (supervisor-freeze §3):** (a) requirement explicitly listed in
  owner directive D-023 (Appendix A item 3); (b) reproduced defects: rotation invents a
  supervisor-internal session id (`rotation.py:833-838`, `sup-{uuid4}`) while
  `RunnerConfig.resume_session_id` (claude_runner.py:319) has NO production assigner — a
  completed rotation launches an unresumed fresh session; hard-coded model chain
  `config.py:82-84` (claude-fable-5 → claude-opus-4-8 → claude-opus-4-7) and turnover's pinned
  successor `turnover_adapters.py:32-33` (claude-opus-4-8@xhigh) + CLI defaults cli.py:2498/2616
  — none live-probed, violating the owner's approved-live-probed-IDs-only requirement.
- **Dependency:** M0-T079 (merged at campaign identity; awaiting_gate — claim proceeds only if
  the CLI's dependency rule permits, else deferred to T079 acceptance).
- **Freeze-baseline duty:** suite >= 1707/0 must be re-established after the change.
- **Worktree:** wt-m0t080 on task/M0-T080-session-model-turnover (to be created at claim).

G0 result: **PASS** — ready subject to the CLI dependency rule.
