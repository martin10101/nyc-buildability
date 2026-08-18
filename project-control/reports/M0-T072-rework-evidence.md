# M0-T072 rework evidence — round 1 (base ec8bc58 → be3a599)

Consolidates how each round-1 review's blocking items were closed, with the
frozen verification identity for re-review.

## Blocking items and their closures

| Source | Finding | Closure at be3a599 | Proof |
|---|---|---|---|
| G3-1 / DCV-R052 / G5-A | 14 pre-existing supervisor tests fail (broker/loop/model_chain/start_reentry assert the pre-repair contract) | four fixture modules updated to the new fail-closed contract (each start fixture records a bound manifest; broker expects verify-controller to fail closed bare); ContainmentGateTests genuinely reach the containment gate again; packet allowed_paths amended to admit the four modules | full battery **1845 passed, 2 skipped, 0 failures** (freeze floor ≥1165/0) |
| G3-2 / DCV-R052 | producer's "1813 passed, 0 failures" claim false (measured on the wrong cwd / ctl17 tree) | evidence-map R052 + before-after-evidence + this file corrected to 1845/0 at be3a599 with the root-cause note | `pytest tools/ -q` at be3a599 |
| G4-C1 / G5 SEC-MAJOR | manifest `patterns: []` coverage-downgrade bypass | `manifest_patterns_mismatch` production check + `patterns` folded into the recorded digest | `test_patterns_mismatch_fails_closed` |
| G4-C2 | record-manifest binds any file (e.g. model_selection.toml) as config.toml | refuses a source basename in EXCLUDED_NAMES | `test_record_manifest_refuses_excluded_source_names` |
| G3-3 | AS-1 start-leg + AS-8 dispatch-leg unproven | `test_as1_start_dispatches_with_verified_binding` (positive control: sentinel fires) + `test_as8_stale_manifest_refused_at_dispatch` | both in the new suite |
| G4-4 / G5 | record-manifest --out could overwrite the protected config | refuses out==config and config/selection basenames; verifies before writing | `cmd_record_manifest` |
| G3-4 / C4 | runbook `<the stamp…>` placeholder + fitted AS-9 tests | rollback uses newest-backup autodetect; `test_no_unresolved_executable_placeholders` now a generic in-fence `<…>` scan; probe test de-hollowed | `RunbookHygieneTests` |
| G3-6/9/10, G5 minors | uniform verify-controller JSON schema; doctor --live gated on manifest; start manifest read fail-closed; README/help/runbook doc drift | all applied | new suite 32 passed |

## Frozen verification identity
- Reviewed head for re-review: **be3a599** (branch `task/M0-T072-manifest-config-binding`).
- New regression suite: `tools/test_agent_supervisor_manifest_binding.py` — 32 passed.
- Full `tools/` battery: 1845 passed, 2 skipped, 0 failures.
- Not changed: protected config (SHA `6aef12a9…`), model_selection.toml, forbidden paths.
