---
name: supervisor-mrl-canary-evidence
description: Where the agent_supervisor MRL canary durable artifacts live and how the ten R587 canary rows + live-proven items re-derive from them (used for D-024 M0-T140-class gates)
metadata:
  type: reference
---

Independent verification of a supervisor MRL canary/journey run reads DURABLE artifacts under the runtime dir (a hashed dir under `%LOCALAPPDATA%\NYCBuildabilitySupervisor\<hash>`, which equals `C:\SupervisorController`). Never re-run a provider canary (owner prohibition R715); verify from artifacts only.

Per-run dir `mrl\<run-id>\`:
- `one_shot_unit.json` (schema `mrl_one_shot_unit/v1`): `launch.argv` (--model, --allowedTools/--disallowedTools, --agents), `launch.version` (CLI pin), `launch.child_env_updater.DISABLE_AUTOUPDATER`, `runtime_identity.primary_model`/`auxiliary_models`/`context_tier_used`/`session_id`, `model_mismatch`, `main_tool_uses` (Bash absence check), `accounting` (subagents issued/denied/processes_total/live), `descendant_proof` (worker cleanup), `worker_result.outcome`, `permission_denials`, `result_source`, `returncode`, `ok`.
- `codex_decision.json` (schema `mrl_codex_decision_record/v1`): `decision.decision`/`verdict`, `legacy_decision.model_used` (gpt-5.6-sol), `reviewer_version`, `git.task_head_sha`/`observed_base_sha`, `reviewer_chain`, `descendant_proof` (reviewer cleanup).
- `subagent_ledger.json` (schema `mrl_subagent_ledger/v1`): `contract` (max_total/max_concurrent/agent_inventory), `issued`, `denials` (R567 over-limit, R575 out-of-inventory).
- `launch_verification.json` (schema `mrl_launch_verification/v1`): `checks[]` incl `clean_status` (a dirty tree gives `match:false`, `ok:false` = the "live repository mismatch refusal"; that run has NO `one_shot_unit.json` and NO `mrl_one_shot_launched` audit row).

Shared runtime files:
- `audit.jsonl`: hash-chained (`prev_digest`==previous `digest`, genesis all-zero); fields are `sequence`/`event_type`/`run_id`/`decision`/`state_from`/`state_to`/`detail`/`timestamp_utc` (NOT `seq`/`event`). Key events: `launch_manifest_verified`, `launch_manifest_refused`, `mrl_one_shot_launched` (count==1 per successful successor), `codex_review_decision` (detail has `model_used`/`returncode`/`mrl_decision`), `supervised_approval_answered` (decision `deny`).
- `supervisor_journal.sqlite3` (has -wal/-shm; copy all three to scratch and open read-only): `transitions` table (sequence/state_from/state_to/trigger/run_id); `state_kv` table — `run_budget/<run-id>` value JSON has `exit_reason` (`operator_declined` = owner clean close; `review_unavailable` = codex-unavailable ask).

Install evidence at `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_update_evidence.json` (UTF-8 BOM — open with `utf-8-sig`): `commit_sha`/`commit_tree_sha`/`subtree_tree_sha`/`subtree_path`(=tools/agent_supervisor)/`installed_file_count`. The launch manifest `C:\SupervisorController\mrl\canary_launch_manifest.json` pins `dispatch.claude_version`/`claude_model`/`claude_chain_sha256` (chain sha == the run's `launch.chain.combined_sha256`). Related: [[isolated-reviewer-git-diff-target]].
