# MRL Launch Runbook - the ONE operator launch path

Authority: M0-T136 C-B5 (D-024-R585, R586). This document is the single operator
launch path for the minimal-real-loop (MRL) supervisor. It supersedes
`docs/CONTROLLER_UPDATE_RUNBOOK.md` section 11, which is OBSOLETE and presents no
`start` command any more. Every command below is validated against the live CLI
contract by `tools/supervisor_command_doc_check.py --doc docs/MRL_LAUNCH_RUNBOOK.md`
(the command-document tooth), so this page cannot drift silently.

Prerequisites: an owner-typed controller update completed and verified per
`docs/CONTROLLER_UPDATE_RUNBOOK.md` sections 3-8, and a claimed task packet whose
worktree is clean at the commit you intend to dispatch. Both steps below run from
`C:\SupervisorController`.

## 1. Draft the launch manifest

The draft tool observes the task worktree and binds every dispatch input - the
executables and their hashed chains, the task packet and its digest, the config,
model selection, controller manifest, repo/worktree/branch/HEAD identity, bounds,
and the subagent contract - into ONE reviewed `launch_manifest.json`:

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
  --out C:\SupervisorController\mrl\launch_manifest.json `
  --force
```

Substitute the task's own `--worktree` and `--task-packet` for the unit being
launched; everything else is the standing controller identity. The tool prints
the bound `task_id`, `head_sha`, `mode` and settings-profile digest and exits 0;
a typed refusal (unclean worktree, unreadable packet, missing executable, an
`--allow-tool` rule outside the tool inventory, bad limits) prints the reason and
exits 3 with nothing written. `--force` overwrites an existing out-file. Re-run
the draft after ANY new commit in the worktree: the manifest binds the exact
HEAD, and a stale one refuses at start time rather than launching the wrong code.

## 2. Start the run

Exactly one launch form exists. The manifest supplies every dispatch input;
`start` takes only what the manifest cannot carry - `--checkout` (the runtime
journal is addressed by `sha256(checkout)`), `--mode` (must EQUAL the manifest's
authorized mode; the parser's default would refuse at preflight), and
`--max-cycles 1` (a manifest binds exactly one task to one fresh process for one
cycle):

```powershell
python -m tools.agent_supervisor start --mode supervised `
  --checkout C:\SupervisorController `
  --launch-manifest C:\SupervisorController\mrl\launch_manifest.json `
  --max-cycles 1
```

The manifest is never proof. Before any provider launches, preflight re-observes
the repo root, normalized origin, task id, packet digest, worktree, branch, HEAD,
tree, clean status, allowed paths, settings-profile identity and mode, and hashes
the full Claude and Codex executable chains (wrapper -> runtime -> entrypoint)
with streaming SHA-256; any disagreement refuses at exit 11 with a typed reason
below. A typed flag that disagrees with the manifest is a
`launch_manifest_conflict`, never silently preferred.

After a DELIBERATE Claude CLI admission event (an intentional upgrade per
CONTROLLER_UPDATE_RUNBOOK section 13), a `claude_version_mismatch` refusal is
expected until the identity is re-pinned: the owner adds `--repin-cli-identity`
to the same start command, once, to accept the new certified identity. It is
never a default and never answers an UNEXPECTED version drift.

## 3. Refusals (exit 11 unless noted)

| Reason code | Meaning | Operator action |
|---|---|---|
| `launch_manifest_invalid` | manifest missing, not a file, relative path, bad JSON, or a structural contract violation | re-run the Step 1 draft |
| `launch_manifest_base_ref_missing` | `dispatch.base_ref` absent, empty, or an unfilled draft placeholder - the reviewer's decision is never bound to a guessed ref | draft with an explicit `--base-ref` |
| `launch_manifest_conflict` | a typed flag disagrees with the manifest (every conflict is listed) | drop the flag or re-draft |
| `launch_manifest_single_task` | `--max-tasks>1`, `--packet-queue`, or `--max-cycles` other than 1 with a manifest | one task, one cycle |
| `launch_manifest_mismatch` | a preflight re-observation (mode, branch, HEAD, tree, clean status, packet digest, model, ...) disagrees with `expected.*` | fix the worktree or re-draft at the real state |
| `launch_manifest_unobservable` | a fact the manifest pins could not be observed at preflight | investigate the named probe, then retry |
| `cwd_primary_checkout` | the launch would run against the primary checkout instead of the bound task worktree | launch against the packet's worktree |
| `cwd_mismatch` | the process working directory disagrees with the bound checkout | start from `C:\SupervisorController` |
| `codex_model_mismatch` / `codex_version_mismatch` | the live Codex CLI identity disagrees with the manifest | investigate drift; re-draft only if the change was deliberate |
| `claude_version_mismatch` | the live Claude CLI identity disagrees with the certified pin | see the `--repin-cli-identity` prose above |
| `illegal_transition` (exit 13) | the journal is parked in a blocking state (e.g. `WAIT_FOR_OWNER`); `start` never leaves one | leave the state explicitly - section 5 |

A RUNTIME-reported model mismatch (the child announces a different model than
the manifest's `claude_runtime_model`) is not a preflight refusal: it is
recorded in the run's `one_shot_unit.json` as `model_mismatch` with the observed
models, and the unit is not trusted as a success.

## 4. Exit codes

| Code | Meaning |
|---|---|
| 0 | the command did what it was asked; for `start`, the one-shot run dispatched and settled |
| 1 | legacy generic failure: failed controller-manifest verification (M0-T072 security halt), `verify-controller`, `doctor` FAIL |
| 2 | argparse rejected the command line (unknown flag / missing required argument) |
| 3 | `mrl_launch_draft` typed refusal - nothing written |
| 10 | HALTED - terminal; only an explicit owner act reopens the run |
| 11 | UNSAFE - integrity, authority, identity, repository, toolchain, auth, or policy no longer matches |
| 12 | UNSUPPORTED_PLATFORM - this host cannot provide a required precondition |
| 13 | STALE_STATE - durable state and the world disagree, or a required fact is missing |
| 14 | APPROVAL_REQUIRED - a human decision is required before anything else happens |
| 15 | BUDGET_EXHAUSTED - the owner-set run budget is spent |
| 16 | REFUSED_MODE - the named mode is not enabled for this launch |

## 5. Leaving WAIT_FOR_OWNER

In supervised mode every unit prompt parks the run in `WAIT_FOR_OWNER` until the
owner approves the exact prompt digest (CONTROLLER_UPDATE_RUNBOOK section 9a).
List the held prompt and its digest:

```powershell
python -m tools.agent_supervisor pending-approvals --checkout C:\SupervisorController
```

then approve it - replace the digest below with the one actually printed for the
held prompt (the example value is the SHA-256 of an empty string and will match
nothing real):

```powershell
python -m tools.agent_supervisor resume-pending-prompt `
  --checkout C:\SupervisorController `
  --approve-prompt-digest e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

and run the Step 2 start again (a fresh start re-runs the full preflight gate; a
digest-bound approval is never replaced by directive text).

## 6. Where the run wrote its records

The runtime directory is addressed by `sha256(checkout)`; print it with:

```powershell
python -c "from tools.agent_supervisor.durable_state import runtime_dir_for; print(runtime_dir_for(r'C:\SupervisorController'))"
```

Under it, `mrl\<run_id>\` holds `launch_verification.json` (every preflight
comparison), `one_shot_unit.json` (session id, schema-bound result, observed
models, permission denials, timings), `codex_decision.json` (the reviewer's
decision bound to the observed base ref), `subagent_ledger.json` (issued/denied
subagents and the process accounting), and the profile directory; the audit
trail is the sibling `audit.jsonl`. Journal state at a glance:

```powershell
python -m tools.agent_supervisor status --checkout C:\SupervisorController --json
```

## 7. Health probe

`doctor --live` is the ONLY live probe - it verifies the config, model
selection, controller manifest and provider CLIs without dispatching anything:

```powershell
python -m tools.agent_supervisor doctor --live `
  --checkout C:\SupervisorController `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe
```

## 8. PowerShell exit-code tests (ps_tests)

`tools/agent_supervisor/ps_tests/` proves, on real PowerShell 5.1, that the
operator path preserves raw exit codes (`$LASTEXITCODE`) and that piping or
`Tee-Object` cannot fake a green - plus that this runbook and the canary package
pass the command-document tooth. Run from the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\agent_supervisor\ps_tests\run_ps_tests.ps1
```

The runner executes every `ps_tests\test_*.ps1` in its own process and exits
nonzero if any test (or any asserted mutation detection) fails. The
command-document tooth alone can be run directly:

```powershell
python tools\supervisor_command_doc_check.py --doc docs\MRL_LAUNCH_RUNBOOK.md
python tools\supervisor_command_doc_check.py --doc project-control\reports\M0-T136-canary-package.md
```
