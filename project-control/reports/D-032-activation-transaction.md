# D-032 activation transaction — evidence log + runbook (2026-09-06)

Authority: D-032 (owner 2026-09-05, source-001) + D-024 Amendment 54 (source-054-amendment.md).
Orchestrator-executed under the owner's activation directive; the two remaining steps below were
stopped by the machine's own permission layer and are handed to the owner exactly as the original
R772/R780 design prescribed.

## 1. Completed and verified (durable evidence)

| Step | Evidence |
|---|---|
| D-032 captured + validated (18 reqs) + D-024 Amendment 54 | commit `fdf29543`; `validate_directive_compliance.py` exit 0 |
| Codex CLI updated 0.146.0 → **0.153.4** (owner-ordered, D-032-R004) | `codex --version` = codex-cli 0.153.4; npm publish date 2026-09-04 |
| **gpt-6-astra @ high LIVE-CONFIRMED** on the owner's account | `codex exec -m gpt-6-astra -c model_reasoning_effort=high` banner: `model: gpt-6-astra`, `reasoning effort: high`; correct "OK" reply; 4,502 tokens |
| CLI-admission fixture recaptured (M0-T132 pattern) | `capability_probe_live_2026-09-06_d032_codex_0_153_4.json` + drift-teeth re-baseline; 19/19 focused, ruff clean; commit `e0dd4a3a` |
| **R247 suite recert at the certified candidate** | full `test_agent_supervisor_*` suite at `e0dd4a3a` content: **3633 passed / 2 skipped / 0 failed** (348s) |
| `source_binding.json` re-pinned to certified candidate | commit `8dd4ce86`: commit_sha `e0dd4a3a…`, tree `7ec34b7b…`, subtree `b67fe058…` |
| Source worktree detached-clean at pinned commit | `wt-controller-src` HEAD = `e0dd4a3a`, status clean |
| Controller **backup phase VERIFIED** | run `20260906-004458677-33c07573`: 199 controller + 3 runtime files → `C:\SupervisorBackup\20260906-004458677-33c07573`; evidence json written |
| Runtime effort config set | `C:\SupervisorController\model_selection.toml` → `review_reasoning_effort = "high"` (valid only once the new controller code is installed; old code fails closed on the key, which is safe) |
| Loop queue claimed + G0-passed + worktrees created | M0-T145 (`wt-m0t145` @ e0dd4a3a) + M0-T025 (`wt-m0t025` @ e0dd4a3a); queue file `project-control/campaigns/D-032-first-loop-queue.json` |

## 2. The two owner steps (in order; both are single commands)

**(a) Install the certified controller code** (the Claude permission layer denied the orchestrator
this exact call twice; run from any PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1" -Phase install
```

Then (recommended) the digest cross-check:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1" -Phase verify-manifest
```

**(b) Allowlist gpt-6-astra** (file is admin-locked by design; right-click → Run as administrator,
or from an elevated PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\owner_allow_astra.ps1"
```

## 3. After (a)+(b): switch + start (orchestrator does this on your reply; commands here so you can also run them yourself)

```powershell
Set-Location C:\Users\MLFLL\Downloads\nyc-zoning\ctl24
python -m tools.agent_supervisor set-codex-model gpt-6-astra --checkout C:\SupervisorController --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection C:\SupervisorController\model_selection.toml
python -m tools.agent_supervisor start `
  --mode limited-auto --owner-enable-bounded-auto `
  --checkout C:\SupervisorController `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe `
  --codex-executable C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
  --packet-queue C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\campaigns\D-032-first-loop-queue.json `
  --max-tasks 2 --max-cycles 6 `
  --run-id persistent-local-01
```

Live view (second window): `Get-Content -Wait "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\<runtime>\audit.jsonl"`.
Controls: `python -m tools.agent_supervisor status|pause|resume|graceful-stop --checkout C:\SupervisorController`.

Reviewer chain once (b) lands: **gpt-6-astra@high → gpt-6-astra@medium → gpt-5.6-terra@medium**
(M0-T146 ladder; each downgrade emits a notify). If (b) is skipped, the loop still runs at
**gpt-5.6-sol@high** — the model can be hot-swapped at a checkpoint boundary later via
`set-codex-model gpt-6-astra --at-checkpoint`.

## 4. Still pending after the run (orchestrator actions)

- `verify-controller` + `doctor` against the new install; DCV re-attest of D-024 rows R772/R780
  (recert=DONE above, reinstall=(a), live-confirm=DONE for astra@high) at final HEAD; then
  **accept M0-T146**; M0-T109 acceptance follows the successful first live limited-auto run (R754).
- Nothing here pushes, merges, deploys, touches PR #241, publishes legal rules, changes GitHub
  visibility, activates R595/Option-A, or decides R603–R605.
