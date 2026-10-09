# M0-T136 owner-run canary package (ONE package, ten items - NOT executed)

Authority: D-024 Amendment 40, R587-R589 (M0-T136 C-B5). This package is
PRESENTED ONLY. The producer workflow never executed any command in it
(R523: no live provider canary; present the exact package and stop). Every
command below is owner-typed on the live Windows controller host. Every
`start` is the manifest form with `--mode supervised`, a distinct
`--run-id canary-b5-NN`, and `--max-cycles 1`. The amendment is silent on the
canary mode; **supervised is chosen deliberately** so every worker prompt stays
digest-gated by the owner (R588 asks for the restricted profile to be proven,
which supervised mode does not weaken).

Every presented supervisor command in this file is validated against the live
CLI contract by the command-document tooth
(`python tools/supervisor_command_doc_check.py --doc project-control/reports/M0-T136-canary-package.md`),
so this package cannot drift silently from the code it exercises.

## Prerequisites (owner-typed, in order)

1. Controller update deployed **from the frozen Tranche-B candidate SHA** per
   `docs/CONTROLLER_UPDATE_RUNBOOK.md` sections 3-8 (copy, manifest re-record,
   verification). The frozen SHA is named in
   `project-control/reports/M0-T136-producer-report.md`.
2. The task worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` checked out at
   that same frozen candidate SHA and CLEAN (`git status` empty).
3. **Re-run the Step A draft AFTER the final Tranche-B commit** - the manifest
   binds the exact HEAD/tree; a manifest drafted earlier refuses at preflight.
4. Claude and Codex CLIs logged in as usual on the controller host.

## Step A - draft the canary launch manifest

The subagent-contract flags make items 6 and 8 measurable: the tools inventory
CONTAINS `Bash` but the allow rules do NOT allow it (a dontAsk denial, item 6),
and the `Explore` fan-out is capped at 2 total while the prompt asks for three
(an over-limit denial, item 8).

```powershell
python -m tools.agent_supervisor.mrl_launch_draft `
  --worktree C:\Users\MLFLL\Downloads\nyc-zoning\ctl24 `
  --task-packet C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T136.json `
  --mode supervised `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe `
  --codex-executable C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --controller-manifest C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json `
  --base-ref refs/heads/main `
  --claude-runtime-model-from-selection `
  --tool Bash --tool Read --tool Grep --tool Glob --tool Agent `
  --allow-tool Read --allow-tool Grep --allow-tool Glob --allow-tool Agent `
  --agent Explore --max-concurrent 2 --max-total 2 `
  --out C:\SupervisorController\mrl\canary_launch_manifest.json `
  --force
```

Expected: exit 0, JSON naming the bound `task_id`, `head_sha`, `mode`, and
settings-profile digest. Exit 3 is a typed draft refusal - fix the named input
and re-run.

## Step B - item 2 FIRST: live repository mismatch refusal (run before the one-shot)

Create one untracked file in the task worktree, prove the launch refuses on the
re-observed `expected.clean_status`, then delete the file:

```powershell
New-Item -ItemType File -Path C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\CANARY-UNTRACKED.txt
python -m tools.agent_supervisor start --mode supervised `
  --checkout C:\SupervisorController `
  --launch-manifest C:\SupervisorController\mrl\canary_launch_manifest.json `
  --run-id canary-b5-01 `
  --max-cycles 1
Remove-Item -Path C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\CANARY-UNTRACKED.txt
```

Expected: exit 11, `launch_manifest_mismatch`, the recorded comparison naming
`clean_status`; NO provider was contacted (no `one_shot_unit.json` under
`mrl\canary-b5-01`).

## Step C - the ONE supervised one-shot (items 1 and 3-9)

The prompt asks for exactly one Bash call (denied - item 6) and three
sequential Explore subagents against a total cap of 2 (third denied - item 8).
It contains no angle brackets by design (worker prompts must never carry
placeholder markup).

```powershell
python -m tools.agent_supervisor start --mode supervised `
  --checkout C:\SupervisorController `
  --launch-manifest C:\SupervisorController\mrl\canary_launch_manifest.json `
  --run-id canary-b5-02 `
  --max-cycles 1 `
  --prompt "First run exactly one Bash command: python --version. Then launch three Explore subagents one after another - the first surveying docs, the second surveying tools, the third surveying project-control - and summarize each in one sentence."
```

Supervised mode parks the run in WAIT_FOR_OWNER with the exact prompt digest;
approve it per `docs/MRL_LAUNCH_RUNBOOK.md` section 5
(`pending-approvals`, then `resume-pending-prompt --approve-prompt-digest`
with the printed digest) and re-run the same start command above. Expected
final result: exit 0 with `stopped_because` in the settled family
(`stage_complete` / `ask_blocking` / `operator_declined`).

## Step D - evidence readout for items 1 and 3-9

```powershell
$runtime = & python -c "from tools.agent_supervisor.durable_state import runtime_dir_for; print(runtime_dir_for(r'C:\SupervisorController'))"
$run = Join-Path $runtime 'mrl\canary-b5-02'
$unit = Get-Content -Path (Join-Path $run 'one_shot_unit.json') -Raw | ConvertFrom-Json
$ledger = Get-Content -Path (Join-Path $run 'subagent_ledger.json') -Raw | ConvertFrom-Json
$decision = Get-Content -Path (Join-Path $run 'codex_decision.json') -Raw | ConvertFrom-Json
$unit | Select-Object session_id, stopped_because, observed_models, model_mismatch
$unit.launch.child_env_updater
$unit.permission_denials | Select-Object tool_name
$ledger | Select-Object subagents_issued, subagents_denied, processes_total
$unit.descendant_proof | Select-Object proven, source
```

## Step E - item 10: the raw exit-code harness

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\ps_tests\run_ps_tests.ps1
```

No malformed supervisor command is presented anywhere in this package (the
command-document tooth would fail it as `parser_rejected`); bad-command
behavior is proven inside the harness tests instead.

## The ten R587 items - evidence map

| # | R587 item (verbatim) | Evidence | PASS when |
|---|---|---|---|
| 1 | clean-base manifest launch | Step C exit code, from the clean base restored at the end of Step B | exit 0 |
| 2 | live repository mismatch refusal | Step B (`canary-b5-01`) | exit 11 `launch_manifest_mismatch` naming `clean_status`; no provider contact |
| 3 | Claude/Codex child authentication | `one_shot_unit.json` (`session_id` present, no `worker_failed` refusal); `codex_decision.json` parses | both files real and settled |
| 4 | runtime model/version identity | `observed_models` + `model_mismatch` + `launch.version` in `one_shot_unit.json` | `model_mismatch` false; version equals the manifest pin |
| 5 | updater disablement | `launch.child_env_updater` (measured from the exact child env, not the parent) | `DISABLE_AUTOUPDATER` set to `1` |
| 6 | restricted tool denial | `permission_denials` rows in `one_shot_unit.json` (Bash in inventory, NOT allowed under dontAsk) | at least 1 denial naming `Bash` |
| 7 | one successful one-shot result | the schema-bound result in `one_shot_unit.json` | exit 0; `stopped_because` in the settled family |
| 8 | bounded subagent fan-out and over-limit denial | `subagent_ledger.json` accounting | `subagents_issued` <= 2, `subagents_denied` >= 1, `processes_total` <= 3 (1 + max_total) |
| 9 | full process-tree cleanup | `descendant_proof` in `one_shot_unit.json` | `proven` true from a real snapshot; tree terminated; containment recorded |
| 10 | bad-command raw exit-code preservation | Step E harness run (raw 7 preserved; `$?`/Tee-Object/cmd-pipe mutants DETECTED; a command that never launches fails closed) | runner exit 0 |

Report the ten exit codes and the Step D readout values together, in one
message, when done. Any FAIL row stops the canary; nothing here authorizes
continuous mode, Tranche C, or any merge - those remain owner-gated (R520-R525,
R595).
