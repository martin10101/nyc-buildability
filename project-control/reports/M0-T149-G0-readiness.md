# M0-T149 G0 readiness (administrative, orchestrator)

- **Task:** M0-T149 — enforce a non-mutating program profile for supervisor-executed
  documented test commands (G3 LOW-1 follow-up to accepted M0-T148).
- **Qualifying evidence (AD-093 §2):** demonstrated security risk — the independent G3
  review of accepted commit `53d642a1` confirmed `validate_documented_test_commands`
  admits mutating single-segment commands (e.g. `git push origin b`, `rm -rf tools`)
  that `run_command` would execute; today only orchestrator-only task-packet authorship
  prevents it (convention, not guard). Report: `M0-T148-G3-code-review.md` LOW-1.
- **Packet completeness:** objective + business reason recorded at creation; allowed_paths
  (6 files, supervisor lane + reports); documented_test_commands (2 focused suites +
  ruff + modularity); reviewers code-reviewer / security-reviewer /
  directive-compliance-verifier (all ≠ producer); gates G0/G2/G3/G5 per the
  supervisor-freeze rule; in-regime `D-032:ALL` (registry validator exit 0).
- **Dispatch context:** queued as task 2 of the D-032 product-queue v3 for the
  supervised loop (R754 closure run: multi-task queue proving acceptance-class
  auto-advance). Producer worktree `wt-m0t149` at candidate HEAD.
- **Result:** PASS — contractible; the loop worker may claim.
