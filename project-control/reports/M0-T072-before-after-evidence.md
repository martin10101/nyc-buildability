# M0-T072 before/after evidence — external-config manifest binding

Before = main@`026e7cb` (defect identity, line refs in `M0-T072-defect-evidence.md`).
After = this branch. Each row is proven by a named test in
`tools/test_agent_supervisor_manifest_binding.py` (27 passed).

| # | Behavior | Before | After | Proof (test) |
|---|---|---|---|---|
| 1 | Matching external config | unverifiable: no CLI path passed extra_files; a bound manifest would FAIL as `missing` | passes on all three paths (doctor check, verify-controller, start) | AS-1: `test_as1_matching_external_config_passes`, `test_doctor_verifies_the_external_config_binding`, `test_verify_controller_passes_with_bound_manifest_and_config` |
| 2 | One-byte config change | undetected (config never verified) | fails: `changed: ['config.toml']` | AS-2: `test_as2_one_byte_config_change_fails`, `test_doctor_fails_on_config_drift`, `test_verify_controller_detects_config_drift` |
| 3 | Missing config | undetected | fails: `missing` / `config_path_missing` | AS-3: `test_as3_missing_config_fails`, `test_as3_no_config_path_fails_closed` |
| 4 | Manifest omitting config.toml at dispatch | dispatched (`controller_manifest: True`) | refused: `manifest_missing_config`, dispatched=false, provider_calls_made=0, exit 1 | AS-4: `test_as4_manifest_without_config_entry_fails`, `test_as4_start_refuses_manifest_without_config_binding` |
| 5 | Wrong config path | undetected | fails: digest mismatch on the logical entry | AS-5: `test_as5_wrong_config_path_fails` |
| 6 | model_selection.toml change | never invalidates (correct) | unchanged: never invalidates | AS-6: `test_as6_model_selection_change_never_invalidates` |
| 7 | Provider call after failed verification | possible (verification skippable) | impossible: sentinel-provider never invoked; stop precedes contact | AS-7: `test_as7_no_provider_call_on_config_drift`, `test_start_without_manifest_is_a_missing_required_input` |
| 8 | Stale manifest (version/edited) | accepted (no staleness check existed) | refused: `manifest_stale` | AS-8: `test_as8_wrong_controller_version_is_stale`, `test_as8_edited_manifest_is_stale` |
| 9 | Runbook hygiene | CMD carets, placeholders, config-coverage claim false | PowerShell-native, resolved paths, doctor --live only probe | AS-9: 4 `RunbookHygieneTests` |
| + | Absolute path leak into manifest | n/a (never recorded) | logical name only; private directory name never serialized | `test_as1_absolute_config_path_never_leaks_into_the_manifest`, `test_record_manifest_round_trip` |
| + | In-package config.toml duplicate | silently shadowed the walk | refused: `config_duplicated_in_package` (both verify and record-manifest) | `test_in_package_config_duplicate_is_refused` |
| + | verify-controller without --manifest | `ok: true` having verified NOTHING | exit 1, fail-closed message | `test_verify_controller_without_manifest_fails_closed` |
| + | start without --manifest | silently `controller_manifest: True` | `--manifest` in missing_inputs; manifest_binding `not_established`; no dispatch | `test_start_without_manifest_is_a_missing_required_input` |

Suite baseline after the change: **1813 passed, 2 skipped, 0 failures** (full
`tools/` battery), vs the M0-T039 freeze floor of ≥1165/0.
