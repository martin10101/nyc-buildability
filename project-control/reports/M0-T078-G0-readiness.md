# M0-T078 G0 readiness — engineering-reliability standard + skill router

Administrative readiness recorded by the orchestrator at campaign identity `6b9ae32`
(control/D-023-autonomy-campaign; base origin/main `d8b3899f`, zero drift at reconciliation).

- **Directive binding:** in-regime, `D-023:ALL` (capture validated, DCV PASS at `6b9ae32`).
  Governing rows: D-023-R015 (deliverable), R038/R005/R006 (no third-party/downloaded code),
  R023 (no unmeasured claims), plus campaign-wide conduct rows.
- **Scope check:** allowed_paths cover the two new deliverables
  (`docs/ENGINEERING_RELIABILITY_STANDARD.md`, `.claude/skills/engineering-reliability/SKILL.md`),
  optional discovery pointers (`CLAUDE.md`, `AGENTS.md`), and the producer report. No overlap
  with any nonterminal task's scope (verified: no nonterminal task owns these paths).
- **Dependencies:** none. Independent of the supervisor tasks; may run in parallel with M0-T079
  (disjoint file scope, separate worktree per ORCHESTRATION policy).
- **Inputs available:** vetted principles list (campaign packet Section 4, derived from the
  reviewed handoff), existing policy corpus for the non-duplication comparison (CLAUDE.md,
  .claude/ORCHESTRATION_POLICY.md, docs/GATES_AND_CHECKPOINTS.md,
  docs/ACCEPTANCE_SCENARIO_STANDARD.md, docs/CODE_MODULARITY_POLICY.md,
  docs/DEPENDENCY_SECURITY_POLICY.md, docs/LEAN_OPERATING_PROCESS.md,
  docs/ENGINEERING_RELIABILITY* — none exists yet).
- **Acceptance harness:** context-budget validator must remain green; skill must be a short
  discriminating router (no scripts/assets); standard adds only non-duplicative principles;
  G3 code/content review + G5 security/control-plane review required before acceptance.
- **Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t078` on
  `task/M0-T078-reliability-standard` at `6b9ae32` (clean).

G0 result: **PASS** — task is ready to claim.
