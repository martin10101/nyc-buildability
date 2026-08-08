# M0-T050 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-08.

- Directive binding: D-010 source-020 captured verbatim (R184–R195), validator green; refs stamped.
- Scope known precisely: Invoke-Step `param([string]$Exe, [string[]]$Args)` collides with the
  automatic `$args` (live elevated -DryRun printed six executable-only lines); fix = rename to
  `$CommandArgs` in the param block, `$shown`, and the splat; correct the unconditional
  "apply complete" wording for dry runs; add the full-vector dry-run regression test (RED on
  merged blob ca3811cd). Elevation-refusal ordering must NOT change (line 105 precedes DryRun) —
  the test proves the mechanism via AST extraction + call-site verification, unelevated.
- Environment ready: orch worktree repointable to main (1e649a8); WinPS 5.1 present; os_acl suite local.
- Gates: G0 (this), G2, G3+G5 (owner-required, R191), DCV at accept. Owner dry-run inspection
  (R193/R195) follows merge and precedes any real apply.
- Holds honored: R184 (config untouched), no activation, no broadening (R194).

READY.
