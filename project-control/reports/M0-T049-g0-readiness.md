# M0-T049 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-08.

- **Directive binding:** D-010 source-019 captured verbatim (R173–R183), validator green; refs
  stamped on the packet at creation. Owner authorization: "Treat it as a narrowly bounded
  pre-activation defect fix" (source-019).
- **Scope is tight and known:** four defective interpolations at
  `tools/agent_supervisor/harden_controller_config.ps1:130,132,154,165` (`"$UnelevatedUser:(M)"`
  / `"$UnelevatedUser:(RX)"` → `"${UnelevatedUser}:(M)"` / `"${UnelevatedUser}:(RX)"`), plus ONE
  new regression test that parses the whole script under Windows PowerShell 5.1 semantics via the
  PS parser API (exit codes proven insufficient — a parse failure masquerades as the unelevated
  refusal). No other change permitted (R183).
- **Evidence baseline on file:** R175 honest ACL posture inspection committed
  (`M0-T049-acl-posture-inspection.md`): relocated file NOT protected (moved descriptor), parent
  protected, contents SHA intact `29eb765e…da1cb`.
- **Environment ready:** orch worktree available; PS 5.1 present on the host (Windows 11); the
  supervisor OS-ACL test suite (`test_agent_supervisor_os_acl.py`) runs locally.
- **Gates:** G0 (this record), G2 self-check, G3 code review + G5 security review (owner-required
  delta reviewers, R179), DCV at accept. G4 not contracted (the parse test IS the QA artifact;
  bounded scope per R183).
- **Holds honored:** no activation, no config move/content change, model_selection untouched
  (R173/R182); old blob 0f01d649 barred from elevation (R180).

READY.
