# M0-T050 — G2 self-check (producer self-checks + orchestrator reproduction)

Recorded by the orchestrator 2026-08-08 at frozen identity `60acbeb` (code head `b1817ff`).

- **Diff shape verified twice:** Invoke-Step parameter rename ($Args -> $CommandArgs, both uses,
  collision comment) + completion-wording branch (if ($DryRun) "dry run complete. NO changes
  were made..." else the original apply text) + 6 new tests + report. Nothing else.
- **Root cause proven mechanically:** under WinPS 5.1 the automatic $args shadows a parameter
  named $Args inside the function; the live demonstration is codified as the permanent
  RED-on-defective test against merged blob ca3811cd (emits "[dry-run] icacls.exe" with no
  arguments) while the fix emits the complete vector.
- **Call sites:** all FOURTEEN Invoke-Step call sites AST-enumerated (packet said 12 - producer
  corrected honestly) and retention-proven; the six apply-path vectors statically pinned AND
  live-replayed with every path, /F, /A, /inheritance:r, /grant:r, and every principal asserted.
- **Suites:** os_acl 38 passed (+6); full supervisor suite **1387 passed / 2 skipped**
  (producer + orchestrator reproductions). Parse test still green (parse_errors=0 on the new
  content).
- **Out-of-scope flag carried:** -Rollback completion wording still unconditional (would misread
  under -Rollback -DryRun); bounded out per R194, surfaced to the owner as candidate follow-up.
- **Boundaries:** config untouched (R184), no activation, no broadening, model_selection
  untouched.

Self-check PASS; ready for independent G3 + G5 delta review (R191).
