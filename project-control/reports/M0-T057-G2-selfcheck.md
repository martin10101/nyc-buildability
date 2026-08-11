# M0-T057 — G2 producer self-check — VERDICT: PASS

Recorded by `orchestrator` (role self_check). Independently confirmed by the G3 code-review and the
control-plane-verifier review at the acceptance head `8221419` / identity `6525ddfb`.

## Deliverable → evidence
- **c17 empty-identity guard** (`tools/validate_directive_compliance.py`): an in-regime task whose
  `allowed_paths` resolve to ZERO tracked files is REFUSED, unless it validly opts in path-free
  (`path_free_governance:true` + justification) or is grandfathered. Wired into the shared
  `_task_git_identity` so submit/gate/accept fail closed, plus the CI validator's c17 check.

## Test evidence (reproduced this session at HEAD 8221419)
- `python tools/test_project_control.py` → all 23 project-control test groups pass, including
  "S12 empty-identity guard (prose + malformed opt-in fail closed; real path stamps real identity)".
- `python tools/test_directive_compliance.py` → guard test group passes (`test_empty_identity_guard`,
  `test_grandfathered_task_is_not_flagged`, path-free opt-in permit/malformed-refuse).
- `python tools/validate_directive_compliance.py --check` → exit 0 with the guard active and M0-T055 drained.
- `python -m py_compile tools/validate_directive_compliance.py` → OK.

## Session-16 changes (self-checked)
- M0-T055 drained from `_EMPTY_IDENTITY_GRANDFATHERED` (now accepted at real identity f3a6a363 → resolves
  non-empty → never reaches c17); remaining 8 grandfathered packets still fail closed; validate exit 0.
- Three dead locals removed (Pyright hints) — zero behavior change.

## Verdict
The guard is implemented, fail-closed, and covered; the session-16 drain/cleanup is behavior-neutral.
**PASS** (self_check; independent confirmation is G3 + control-plane review).
