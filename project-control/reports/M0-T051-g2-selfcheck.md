# M0-T051 — G2 self-check (producer self-checks + orchestrator reproduction)

Recorded by the orchestrator 2026-08-08 at the frozen submit identity (code head bbdfb76).

- Diff verified twice: /reset inserted before /inheritance:r on BOTH targets (one extra icacls
  flag each) + root-cause/ordering comments; APPLY_VECTORS 6->8 + A2/B1 updated; new
  HardenExplicitAceStripTests (5 tests); hashlib import present (line 34; Pyright stale-diagnostic
  checked). Nothing else.
- Mechanism: deterministic BY CONSTRUCTION (reset -> inheritance:r -> three grant:r = exactly
  three ACEs regardless of prior explicit ACEs); ordering reasoned (back-to-back in one elevated
  session; dir /reset non-recursive).
- Adversarial fixture: poisoned explicit Authenticated Users:(M) stripped; DACL == exactly the
  intended three ACEs; evaluate_acl_entries PROTECTED; RED on blob 9625514e (all three property
  assertions fail on the old sequence); idempotent; byte-preserving; read retained. All 5 RAN.
- Honest proof boundary documented: takeown ownership-transfer sub-property (owner-elevation
  check + denied write probe) provable only by the owner's real elevated run + unelevated doctor.
- Suites: os_acl 43 passed; FULL suite 1392 passed / 2 skipped (producer + orchestrator).
- Boundaries: config untouched; no manual ACL repair; no activation; rollback untouched;
  model_selection untouched.

Self-check PASS; ready for independent G3 + G5 (R206).
