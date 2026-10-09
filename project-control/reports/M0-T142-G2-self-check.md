# M0-T142 G2 producer self-check (orchestrator, 2026-09-02)

| Check | Result | Evidence |
|---|---|---|
| Scope: only allowed paths touched | PASS | `git show --stat 65e43491` + `8c604681` — every path in allowed_paths (packet amended pre-submit to include the two launch modules; the hazardous default template WAS the R692 enforcement surface); forbidden paths untouched (empty diffs on schemas/, mrl_worker_result.py, mrl_provider_schema.py, mrl_transport.py, model_selection.py) |
| AS-SI-1 canary shape settles | PASS | `test_canary_b5_02r1_aggregate_settles_when_the_transcript_proves_the_pin` + module-level `test_canary_b5_02r1_shape_verifies` |
| AS-SI-2 [1m] tier explicit | PASS | `test_pinned_context_tier_turn_settles_and_is_recorded` + `test_tier_suffix_on_a_different_model_refuses` + `test_model_matches_pin_is_exact` |
| AS-SI-3 six refusal shapes | PASS | missing/uncorrelated/no-turns/divergent/pin-absent/empty-aggregate tests, all typed ContractError, no checkpoint |
| AS-SI-4 binding proven | PASS | `test_project_key_matches_the_real_observed_directory` (real canary dir name) + foreign-session + foreign-cwd refusals (module and runner level) |
| AS-PB-1 explicit restriction load-bearing | PASS | `test_bash_bare_deny_is_load_bearing` (deny → permissions.deny + --disallowedTools) + `test_unpinned_inventory_tool_refuses` (profile) + `test_unpinned_inventory_tool_refuses_at_the_draft` |
| AS-ER-1 reader corrections documented | PASS | producer report s3 (rows 3/4/6/8 criteria bound to unit-record fields; script regenerated post-acceptance) |
| AS-CX-1 Codex review after settlement | PASS | `test_agent_supervisor_mrl_one_shot_review.py` green on the shared transcript-fixture harness |
| AS-FZ-1 freeze + ONE suite run | PASS | supervisor suite 3591 passed / 2 skipped (single run, R696); binding/runbook/ps_test agree on 65e43491; controller_update harness 7/7 |
| AS-MD-1 owner script duties | DEFERRED BY DESIGN | generated after acceptance (R697/R699); criteria recorded in packet + producer report |
| R685 one bounded package / one task | PASS | only M0-T142 created; no accepted task reopened; no repo-wide audit; zero provider calls |
| R694 proven surfaces preserved | PASS | forbidden-path diffs empty; transport/schema-hotfix/containment/updater untouched |
| R699 exact model id discipline | PASS | no model_selection change made; `claude-fable-5` appears only in the owner-script plan + a refusal fixture; no `fable` alias, no `claude-fable-5-1` anywhere in production code |

Verdict: PASS — submit for independent G3/G4/DCV review (producer ≠ reviewer).
