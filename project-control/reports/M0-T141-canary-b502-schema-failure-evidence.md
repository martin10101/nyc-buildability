# M0-T141 — preserved evidence: failed canary-b5-02 run of 2026-09-02 (owner-typed)

Preserves the second live canary run's result (D-024 Amendment 44, R672). Nothing here is
a PASS claim for b5-02; the child exited 1 BEFORE provider contact. The b5-01 refusal
probe from the same script run PASSED and is REUSED, never rerun (R673).

## The reusable b5-01 PASS (controller audit record 17)

Owner-typed run of the Amendment-43 corrected script
(`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_m0t136_canaries.ps1`,
2026-09-02): with the deliberate untracked file present, `start --run-id canary-b5-01`
refused at the launch manifest exactly as intended:

- audit record 17, `2026-09-02T18:24:58.305Z`, `event_type` `launch_manifest_refused`,
  `policy_result` `REFUSED`, detail `mismatches` = one row
  `{field: clean_status, expected: true, observed: false}`, `reason` `mismatch`;
- no `one_shot_unit.json` exists under `mrl\canary-b5-01` (only
  `launch_verification.json` + the profile) — **no provider contact**;
- the untracked file was removed afterward; the task worktree is clean
  (`git status --porcelain` empty at capture).

This is the R587 item-2 refusal (`launch_manifest_mismatch` naming `clean_status`,
safety exit 11). The corrected continuation reuses THIS record as item-2 evidence.

## The failed b5-02 attempt (audit records 18–26; provider-contact count ZERO)

The same script then re-drafted the manifest against claimed M0-T140 at clean HEAD
`c3903878` (record 19 `launch_manifest_verified`), passed preflight (record 21), and
launched ONE fresh `claude -p` child (record 22, `mrl_one_shot_launched`,
`2026-09-02T18:25:00.958Z`). Durable unit record
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca707563cfe6e2cdeeee99e5d153951936dc46edac131889c37c2a9f713b6a\mrl\canary-b5-02\one_shot_unit.json`,
verbatim load-bearing fields:

- `returncode` **1**; `ok` false; `session_id` **""** (no session was ever created);
- `observed_models` **[]**; `model_mismatch` false; `result_source` "";
- `accounting.processes_total` **1** (the claude child only), `subagents_issued` 0;
- `checkpoint_error`:
  `malformed_output: stdout carried no JSON result object (exit 1); stderr tail:
  'Error: --json-schema is not a valid JSON Schema: no schema with key or ref
  "https://json-schema.org/draft/2020-12/schema"\n'`;
- `launch.argv` carries `--json-schema` whose serialized value declares
  `"$schema": "https://json-schema.org/draft/2020-12/schema"` (the canonical schema,
  serialized unprojected — the pre-fix expression);
- `launch.child_env_updater.DISABLE_AUTOUPDATER` = "1"; `launch.version` `2.1.252`;
- `descendant_proof.proven` true (`windows_toolhelp32`), `containment` `job_object`.

**Provider-contact count was zero**: the child exited before any provider request —
empty `session_id`, empty `observed_models`, no structured output, no result object;
the stderr is the CLI's local schema validation refusing the Draft 2020-12 dialect.

Aftermath (records 23–26): `mrl_one_shot_settled` REFUSED → S4.5 synchronous stop
`unsafe_condition` (record 25 carries the same stderr) → `owner_touch_recorded`
`no_valid_checkpoint` (record 26, `2026-09-02T18:25:02.138Z`, audit head). The durable
journal now reports **PAUSED_RECOVERY** (observed read-only this session: no emergency
stop, no manual pause, 0 surviving children, 0 pending effects, audit chain ok head 26,
transitions 14). Canonical exit remains runbook §9a `clear-recovery`, conditional on
`recovery-status` actually reporting PAUSED_RECOVERY.

## Root cause (R665)

Claude Code 2.1.252 validates `--json-schema` against Draft 7 and exits 1 on a schema
declaring `"$schema": "https://json-schema.org/draft/2020-12/schema"`. The canonical
`tools/agent_supervisor/schemas/worker_result.schema.json` declares exactly that
dialect, and pre-fix `mrl_one_shot.py` serialized it verbatim into the CLI argument.
Anthropic's structured-output documentation requires Draft 7;
anthropics/claude-code issue #80402 reproduces this exact error and documents Draft 7
(or removal of the top-level declaration) as the workaround. The M0-T141 repair projects
a deep-copied, explicitly Draft-7-declared provider schema at the CLI boundary
(`tools/agent_supervisor/mrl_provider_schema.py`) and leaves the canonical contract and
controller-side validation untouched; `test_guard_removed_would_reproduce_the_exact_
recorded_failure` proves the refused URI is byte-equal to what the pre-fix expression
emits.

Run directories `mrl\canary-b5-01` and `mrl\canary-b5-02` are preserved as-is; the
corrected continuation uses a NEW correlated run id for the single b5-02 successor
provider call so this evidence is never overwritten (R673).
