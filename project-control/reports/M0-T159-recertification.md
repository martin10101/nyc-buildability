# M0-T159 — 2.1.281 admission + one recertification at the frozen candidate (B-026 remedy)

Producer: `backend-engineer`, in the isolation worktree `wt-m0t159` (branch
`task/M0-T159-cli-2-1-281-admission`), cut from the CERTIFIED controller commit
`a5886dab`. B-026 remedy per `docs/CONTROLLER_UPDATE_RUNBOOK.md` section 13 (R287 ordered
admission) and the M0-T132 (2.1.251->2.1.252) precedent. All commands recorded with an
explicit cwd. The stored activation-manifest overwrite, the controller re-point to the
admitted commit, and the per-lane `--repin-cli-identity` stay OWNER-TYPED commissioning
steps (section 5 below) — presented, never run.

## 1. The frozen candidate identity
| Anchor | Value |
|---|---|
| Material commit (THE admitted candidate) | [CORRECTED per M0-T159-G3 F1] commit **`a3f24ff3825c126c038f59b1ea6d2352f29d724a`** (parent `a5886dab9ad94629a4984199d0766b16dd49e85b`; branch `task/M0-T159-cli-2-1-281-admission`), commit_tree **`82432361540c3c2a11c55ffa3d6d485426cd45f7`**, `tools/agent_supervisor` subtree **`9c0b14eaa56ce32d241c77f789266035b584380c`** (204 tracked files). The integrated ledger commit `cfc3d22c` is NOT this candidate and must NOT be the install source (section 5.0) |
| Provider CLI (ADMITTED) | Claude Code **2.1.281**, executable digest **`92af58066c9cad103ff93c0b8dcf0599e96e26feea5bee45561d06ba579f4a2c`** (`sha256_head+size`), on-disk size **240,767,648 B**, at `C:\Users\MLFLL\.local\bin\claude.exe`; old **`e713c5a6…` (2.1.252)** retired |
| Codex CLI | **codex-cli 0.153.4 UNCHANGED** (the D-032 admission carries; only claude moved) |
| `tools/agent_supervisor` manifest | **147 files**, digest **`55dc71350b9f6b0a57e8e4121c62a9d2a4fe8914eea8bcd1ca4acdddbcec74b9`** (from the TEMP-recorded candidate manifest); the ONE manifest-tracked change is `event_drift.py` (digest `e85c775c3aa7769680d908bfbe8110cf87e20859556038507b9d655e4eb1f30d`, the catalog re-point) — [CORRECTED per M0-T159-G3 F7] the four fixtures are INSIDE the manifest root (`tools/agent_supervisor/fixtures/`) but are not matched by its covered patterns (`*.py`, `schemas/*.json`, `prompts/*.md`, `config.toml`, `config.example.toml`, `launchers/*.cmd`, `launchers/*.ps1`, `README.md`); the `tools/test_*.py` files are outside the root |
| External config bound | `config.toml` LF-normalized digest **`34f4fe90a1ecc2f4544b4ca7ff33fd08af0923cdf3c96d8c462acb8fe7b2a62e`** (the CURRENT B-025-edited config at `C:\Program Files\SupervisorConfig\config.toml`; its `[approved_models]` now lists `claude-opus-5-5`) |

## 2. Test evidence at the frozen candidate (one process, worktree root)
| Pack | Result |
|---|---|
| Golden certification pack (`test_agent_supervisor_golden_run.py`) | **42 passed** (159.88s) |
| Four re-pointed packs (event_bus, capability_probe, native_adapter, routing_probe) | **150 passed** (45.23s) |
| WHOLE supervisor suite (`python -m pytest tools/test_agent_supervisor_*.py -q`, one process, cwd = worktree root) | **3,662 passed, 2 skipped, 0 failed** (3,664 collected; 1,194.97s) |

**Baseline reconciliation (freeze rule, exact).** The a5886dab tree's OWN count, measured
first (installed CLI already at 2.1.281, fixtures still at 2.1.252): **3 failed, 3659
passed, 2 skipped (3664 collected), 939.62s**. The 3 failures were EXACTLY the CLI-drift
live teeth stuck on `'2.1.281 (Claude Code)' == '2.1.252 (Claude Code)'`:
`capability_probe::test_live_reprobe_claude_version_matches_fixture`,
`event_bus::test_s8_live_version_matches_catalog_fixture`,
`native_adapter::test_live_detection_matches_committed_fixture`. **This admission RESOLVES
all three**: 3659 + 3 = **3,662** passed, 0 failed, same 3664 collected, 2 skipped. No
test removed; the capability current-fixture test was repurposed in place (net 0 nodes).

## 3. R282-style admission pass-list (2.1.281)
| Item | Evidence |
|---|---|
| Fixtures | Four measured 2.1.281 fixtures — `capability_probe_live_2026-09-24_m0t159_2_1_281.json`, `hook_event_catalog_2_1_281.json` (33 events, docs re-fetched 2026-09-24, no drift), `native_runtime_detection_2026-09-24_m0t159.json`, `shell_routing_2026-09-24_m0t159_2_1_281.json`; the 2_1_252 / m0t132 / d032 pack kept append-only |
| Drift teeth | The version teeth **GREEN at 2.1.281** and removal-sensitive (section 4); S8/capability/native live teeth match the installed 2.1.281 |
| Live probes | capability + native probes measured live (bounded `--version`/`--help`, no provider); **shell-routing measured live at digest `92af5806…` on the approved worker model `claude-opus-5-5`** — verdict `native_preferred`, 3 native / 0 shell, 0 worker file write, 3 provider calls, deny-everything handler |
| Golden suites | **42 passed** (159.88s) at this identity |
| Manifest binding | 147-file manifest `55dc71350b…` recorded to a TEMP path, external `config.toml` bound, round-trip verified; **`verify-controller` PASS**; **non-live `doctor` overall PASS (41 checks, 0 failed)** |
| Admission scope | ONLY `event_drift.py` (catalog re-point) is manifest-tracked; [CORRECTED per M0-T159-G3 F7] the four fixtures sit inside the manifest root but match none of its covered patterns, and the four fixture-consuming test files are outside the root |

**ADMITTED (candidate): Claude Code `2.1.281` (executable digest `92af5806…`; codex-cli
0.153.4 unchanged).** The one-time `--repin-cli-identity` on the next certified start
completes the admission at the journal level (a per-launch owner act, deferred — section 5).

## 4. Removal-sensitivity (AS-3), recorded
The baseline run above IS a recorded removal-sensitivity demonstration: with the pointers at
2.1.252 and the installed CLI at 2.1.281, the 3 version teeth are RED. Additionally, an
explicit focused run pointed the catalog tooth back at `hook_event_catalog_2_1_252.json`
and ran the two S8 teeth:
```
FAILED tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture
FAILED tools/test_agent_supervisor_event_bus.py::test_s8_catalog_fixture_valid_and_masked
2 failed in 0.85s
```
(the second on `assert 'M0-T132' == 'M0-T159'`). The pointer was restored to
`hook_event_catalog_2_1_281.json`; the same two teeth then passed (`2 passed in 0.25s`).

## 5. Deferred commissioning — the complete ordered sequence (NOT done here)
[CORRECTED per M0-T159-G3 F1, F2, F3, F4 and condition (6)] These steps act on the LIVE
controller and the three lanes; none was run in this unit. They follow
`docs/CONTROLLER_UPDATE_RUNBOOK.md` sections 2, 3, 4, 5, 5a, 6, 7, 8, 9 and 13 (step 4), then
`docs/MRL_LAUNCH_RUNBOOK.md` sections 1, 2 and 5, in that order (the M0-T132 section-5
precedent, completed). Every step fails closed. A **STOP** below means: run nothing further,
launch no lane, report the printed line. Use ONE PowerShell window throughout (5.2 defines two
helper functions that 5.6 reuses).

### 5.0 The admitted candidate, named exactly [CORRECTED per M0-T159-G3 F1]
| Anchor | Value (each re-verified with git in the correction pass) |
|---|---|
| commit | `a3f24ff3825c126c038f59b1ea6d2352f29d724a` (parent `a5886dab9ad94629a4984199d0766b16dd49e85b`) |
| commit_tree | `82432361540c3c2a11c55ffa3d6d485426cd45f7` |
| `tools/agent_supervisor` subtree | `9c0b14eaa56ce32d241c77f789266035b584380c` (204 files) |
| activation manifest after 5.4 | **147 files**, digest **`55dc71350b9f6b0a57e8e4121c62a9d2a4fe8914eea8bcd1ca4acdddbcec74b9`** (binds `config.toml` LF `34f4fe90…`) |
| claude chain a fresh launch manifest must bind (5.11) | `claude_version` `2.1.281`, `claude_chain_sha256` `946eb5098cc8a56a189b8f0e3f083b6a8569030431252c9bb0ab4203b23bfff1` |

- **NOT the install source: `cfc3d22c711930539a18e9a90e492a1116e34ab8`** (the integrated ledger
  commit). It is this unit cherry-picked onto a later base (parent `33662211`); its
  `tools/agent_supervisor` subtree `11d43515656120caae473cca5d6a833a57e5ea35` also carries the
  UNCERTIFIED M0-T149/M0-T152 supervisor changes (`cli.py`, `evidence.py`, `policy.py`, new
  `gate_wave.py`; `git diff --stat a3f24ff3 cfc3d22c -- tools/agent_supervisor` = 4 files,
  +1280/-8). The installer checks only that the binding is self-consistent, and
  record-manifest, verify-manifest and verify-controller would all pass on a wrong install, so
  the identity checks in 5.3 and 5.4 are the guard.
- **Re-pin BEFORE step 5.2 (orchestrator, in a reviewed commit):** set ctl24's
  `tools/controller_update/source_binding.json` (the file the section 3/4 script reads; today it
  pins `a5886dab` / `65036d3f…` / `850841ab…`) to the `commit_sha`, `commit_tree_sha` and
  `subtree_tree_sha` above. Checked for the re-pin: `a3f24ff3` exists in the bound
  `source_repo` (this worktree shares its object store), is on `origin`
  (`origin/task/M0-T159-cli-2-1-281-admission`), `origin` equals the bound
  `expected_origin_url`, and all 12 `required_modules` exist at it.

### 5.1 Preconditions (runbook section 2, read-only) [CORRECTED per M0-T159-G3 F2]
- All three lanes STOPPED: no `supervisor.lock` in runtime dirs `9aca7075…`, `cfdedc11…`,
  `9df5e3ba…` (none was present at the 2026-09-24 read). Required because every lane runs its
  code from `wt-controller-src` (5.6), which 5.3 removes and re-creates.
- Runbook section 2, verbatim:
```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor status                # controller checkout journal: COMPLETE, no children
python -m tools.agent_supervisor status `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063   # A1 journal: PREFLIGHT, 0 pending
Get-FileHash "C:\Program Files\SupervisorConfig\config.toml" -Algorithm SHA256
Get-FileHash C:\SupervisorController\model_selection.toml -Algorithm SHA256
```
- Expected deviation: the first `status` addresses the `C:\SupervisorController` journal, which
  is also lane 1's (`9aca7075…`). It will show `PAUSED_RECOVERY` (B-026), not the runbook's
  `COMPLETE`. That is acceptable only with no live children; 5.11 clears it.
- Config hash: runbook section 1's expected values (`A1F99501…` raw / `4c67875b…` LF) predate
  the B-025 edit. Today the file reads raw
  `610ce9d5cdf50dbf0710424c232ecc7b600c688e419d71204cddcbb9055270e5` (`Get-FileHash` prints it
  in upper case), LF `34f4fe90…` (the value the 147-file manifest binds). Any other value:
  **STOP**.

### 5.2 Verified backup (runbook section 3) [CORRECTED per M0-T159-G3 F2]
Required: the install refuses without backup evidence that matches the CURRENT live controller
(`update_controller_from_candidate.ps1:620-643`: `backup_evidence_missing` / `backup_stale`).
The bound evidence today is run `20260906-161802039-7230a5a0` (2026-09-06), taken before the
`a5886dab` install; the live controller differs from it in 3 files (`codex_reviewer.py`,
`evidence.py`, `loop.py`), so the install WOULD refuse `backup_stale`.
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase backup
```
Expect `BACKUP VERIFIED run <id>` with `controller 200 file(s)`. Then define the byte-compare
helpers and prove instances 2 and 3 equal instance 1, so this backup also covers them (F3; on
2026-09-24 all three were raw-byte identical, 200 files each):
```powershell
function Get-TreeHashList([string]$Root) {
    $r = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
    Get-ChildItem -LiteralPath $r -Recurse -File -Force |
        Where-Object { $_.FullName -notmatch '\\(__pycache__|\.pytest_cache)\\' } |
        ForEach-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash + '  ' + $_.FullName.Substring($r.Length + 1) } |
        Sort-Object
}
function Assert-SameTree([string]$Reference, [string]$Candidate) {
    $a = @(Get-TreeHashList $Reference); $b = @(Get-TreeHashList $Candidate)
    if ($a.Count -eq 0 -or $b.Count -eq 0) { throw ('EMPTY TREE: ' + $Reference + ' / ' + $Candidate) }
    $d = @(Compare-Object -ReferenceObject $a -DifferenceObject $b)
    if ($d.Count -gt 0) { $d | Format-Table -AutoSize | Out-Host; throw ('BYTE MISMATCH: ' + $Candidate) }
    Write-Output ($Candidate + ': ' + $b.Count + ' files byte-identical to ' + $Reference)
}
foreach ($inst in @('C:\SupervisorController2', 'C:\SupervisorController3')) {
    Assert-SameTree 'C:\SupervisorController\tools\agent_supervisor' (Join-Path $inst 'tools\agent_supervisor')
}
```
Expect two lines ending `200 files byte-identical to C:\SupervisorController\tools\agent_supervisor`.
Any `BYTE MISMATCH`: **STOP**.

### 5.3 Install from the admitted candidate (runbook section 4) [CORRECTED per M0-T159-G3 F1/F2]
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase install
```
`wt-controller-src` exists today (detached at `a5886dab`), so this first run refuses
`source_worktree_exists` (`ps1:645-648`). Runbook section 4: "If it refuses
`source_worktree_exists`, remove the stale source worktree and re-run:"
```powershell
git -C C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack worktree remove --force C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src
```
then run the same `-Phase install` command again. Expect `INSTALLED from immutable commit
a3f24ff3825c126c038f59b1ea6d2352f29d724a`, `commit tree 82432361540c3c2a11c55ffa3d6d485426cd45f7`,
`subtree tree 9c0b14eaa56ce32d241c77f789266035b584380c`, `files 204 byte-identical`. Any other
identity (above all subtree `11d43515…` = `cfc3d22c`): **STOP**.

### 5.4 Record the activation manifest (runbook section 5) + STOP condition [CORRECTED per M0-T159-G3 F1]
```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor record-manifest `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --out "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"
python -c "import json,os; m=json.load(open(os.path.expandvars(r'%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json'))); print(len(m['files']), m['manifest_digest'])"
```
record-manifest prints only 16 hex digits, so the second line reads the file back. It must
print exactly `147 55dc71350b9f6b0a57e8e4121c62a9d2a4fe8914eea8bcd1ca4acdddbcec74b9`. Anything
else: **STOP** (wrong tree installed, or the config changed); roll back per runbook section 10.

### 5.5 Prove the manifest matches the accepted source (runbook section 5a, R611) [CORRECTED per M0-T159-G3 F2]
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase verify-manifest
```
Expect `MANIFEST VERIFIED against the accepted source at a3f24ff3825c126c038f59b1ea6d2352f29d724a`
and `covered files 146; installed files re-compared 204` (146 + the bound `config.toml` = the
147 manifest entries). Runbook section 5a allows removing the source worktree once sections 6-8
pass: **do NOT remove it here.** It is the working directory all three lane launchers run from
(5.6); without it no lane can start.

### 5.6 Lanes 2 and 3: what they load, and the verified propagation [CORRECTED per M0-T159-G3 F3]
Read-only facts (2026-09-24):

| Lane | Launcher | Working dir | `--checkout` (journal key) | `--manifest` / `--model-selection` |
|---|---|---|---|---|
| 1 | `C:\SupervisorController\autostart-launch.ps1` | `C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src` | `C:\SupervisorController` (`9aca7075…`) | shared `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` / shared `C:\SupervisorController\model_selection.toml` |
| 2 | `C:\SupervisorController2\autostart-launch.ps1` | same | `C:\SupervisorController2` (`cfdedc11…`) | same / same |
| 3 | `C:\SupervisorController3\autostart-launch.ps1` | same | `C:\SupervisorController3` (`9df5e3ba…`) | same / same |

- All three launchers run `Start-Process … python -m tools.agent_supervisor start …
  -WorkingDirectory $WorkDir`, with `$WorkDir = C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src`,
  in the legacy explicit-flag form (`--mode limited-auto … --task-packet … --max-cycles 10`, no
  `--launch-manifest`). So `python -m` loads the package from
  `wt-controller-src\tools\agent_supervisor` (`PACKAGE_ROOT`, `cli.py:308`), not from any
  `C:\SupervisorController*` copy. Corroboration: every Python traceback in the autostart logs
  (all from lane 1's wrapper; the lane 2 and 3 logs contain none) names
  `…\wt-controller-src\tools\agent_supervisor\*.py`; `PYTHONPATH` is empty; no `.pth` file and
  no `tools` package in the launcher Python's site-packages points anywhere else. For lanes 2
  and 3 the evidence is their launcher source (same `$WorkDir`, same `Start-Process` line).
- Today `wt-controller-src` is detached at `a5886dab` with 200 files equal to that commit. Each
  `C:\SupervisorController{,2,3}\tools\agent_supervisor` holds the same 200 files (raw-byte
  identical to each other, LF-equal to `a5886dab`). `event_drift.py` has LF digest `f06fc856…`
  in all four (the candidate's is `e85c775c…`). None of the four has a
  `fixtures\shell_routing_*2_1_281*.json` (only the `2_1_251` / `2_1_252` pair). No reparse
  points in any instance tree.
- Consequence: once 5.3 re-creates `wt-controller-src` at `a3f24ff3`, all three launchers load
  the certified candidate, and the 2.1.281 routing fixture sits in the directory the routing
  tooth reads (`recovery_probes.py:600-601`). But `C:\SupervisorController2` / `3` stay at
  `a5886dab`, and any command run with THAT folder as the working directory (5.11 does so)
  would load the stale copy. So propagate, then prove:
```powershell
foreach ($inst in @('C:\SupervisorController2', 'C:\SupervisorController3')) {
    $dst = Join-Path $inst 'tools\agent_supervisor'
    robocopy 'C:\SupervisorController\tools\agent_supervisor' $dst /MIR /XD __pycache__ .pytest_cache /R:0 /W:0 /NP /NFL /NDL
    $rc = $LASTEXITCODE
    if ($rc -ge 8) { throw ('robocopy into ' + $dst + ' failed, raw exit ' + $rc) }
    Get-ChildItem -LiteralPath $dst -Recurse -Directory -Force |
        Where-Object { $_.Name -in @('__pycache__', '.pytest_cache') } |
        Remove-Item -Recurse -Force
    Write-Output ($dst + ': robocopy raw exit ' + $rc)
}
foreach ($inst in @('C:\SupervisorController', 'C:\SupervisorController2', 'C:\SupervisorController3')) {
    Assert-SameTree 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src\tools\agent_supervisor' (Join-Path $inst 'tools\agent_supervisor')
}
```
Expect three lines ending `204 files byte-identical to …\wt-controller-src\tools\agent_supervisor`.
A robocopy exit of 8 or more, or any `BYTE MISMATCH`: **STOP**. Rollback for instances 2 and 3:
runbook section 10 restores only `C:\SupervisorController`; afterwards re-run the robocopy loop
above from the restored copy and compare against it (5.2 proved all three equal before the
update).

### 5.7 Verify the controller from every copy that runs code (runbook section 6) [CORRECTED per M0-T159-G3 F2/F3]
```powershell
foreach ($dir in @('C:\SupervisorController', 'C:\SupervisorController2', 'C:\SupervisorController3', 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src')) {
    Set-Location $dir
    python -m tools.agent_supervisor verify-controller `
      --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
      --config "C:\Program Files\SupervisorConfig\config.toml"
    if ($LASTEXITCODE -ne 0) { throw ('verify-controller FAILED from ' + $dir) }
}
Set-Location C:\SupervisorController
```
Expect `controller verified, including the external config.toml binding.` four times. Any
failure: **STOP** and roll back (runbook section 10).

### 5.8 Full doctor (runbook section 7) [CORRECTED per M0-T159-G3 F2]
```powershell
python -m tools.agent_supervisor doctor `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"
```
Expect overall PASS: `controller_manifest` ok with the external `config.toml` binding, config
ACL protected, model selection accepted, journal integrity ok. Otherwise **STOP** and roll back.

### 5.9 Bounded live probe (runbook section 8): RUN it, do not skip [CORRECTED per M0-T159-G3 F2]
```powershell
python -m tools.agent_supervisor doctor --live `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe
```
Why run it: it is the runbook's only intentional live probe (one disclosed allow-and-deny
control-response round-trip, nothing forwarded to a task); it is the first live run of the
INSTALLED tree against 2.1.281 (this unit ran non-live `doctor` only); and runbook section 10
lists "the section 8 probe does not record VERIFIED" as a rollback trigger. Expect VERIFIED;
otherwise **STOP** and roll back.

### 5.10 Post-update state checks (runbook section 9)
```powershell
python -m tools.agent_supervisor status --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
python -m tools.agent_supervisor recovery-status --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
python -m tools.agent_supervisor pending-approvals --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
```
Expect A1 still PREFLIGHT, no live children, no open asks; the update changed no journal.

### 5.11 Relaunch the lanes: a fresh launch manifest each, repin LAST [CORRECTED per M0-T159-G3 F4]
(Runbook section 13 step 4; MRL runbook sections 1, 2 and 5.) Why a FRESH manifest per lane,
drafted only now, after 5.3-5.10: at launch `OneShotRunner` re-hashes the claude chain against
`dispatch.claude_chain_sha256` and compares `claude --version` with `dispatch.claude_version`
(`mrl_one_shot.py:249-254`). Every existing launch manifest
(`C:\SupervisorController{,2,3}\mrl\canary_launch_manifest.json` and
`journey_launch_manifest.json`) pins `2.1.252`, so it is refused `claude_version_mismatch`
whatever `--repin-cli-identity` says. The repin rewrites only the lane journal's executable pin
(`recovery_probes.py:358-384`, refusal code `provider_cli_drift`). Both are needed: the fresh
draft cures the manifest pin, the repin cures the journal pin.

Per-lane order: (1) `Set-Location` into the lane checkout; (2) `status`; (3) `clear-recovery`
only if `status` shows `PAUSED_RECOVERY` (lane 1 does, per B-026 and its 2026-09-24 03:48
autostart log; lanes 2 and 3 have not launched since D-085 and sit at `PREFLIGHT`); (4) draft
the fresh manifest and check it; (5) `start` with `--repin-cli-identity`, the LAST act. Lane 1
goes first as the canary (5.12). Lanes 2 and 3 go only after the canary passes, at least 60 s
apart.

Lane 1 (the canary). Replace the two `<…>` values first (see below):
```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor status --checkout C:\SupervisorController
python -m tools.agent_supervisor clear-recovery --checkout C:\SupervisorController
python -m tools.agent_supervisor.mrl_launch_draft `
  --worktree <LANE_WORKTREE> `
  --task-packet C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\<LANE_PACKET_ID>.json `
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
python -c "import json; d=json.load(open(r'C:\SupervisorController\mrl\launch_manifest.json'))['dispatch']; print(d['claude_version'], d['claude_chain_sha256'])"
python -m tools.agent_supervisor start --mode supervised `
  --checkout C:\SupervisorController `
  --launch-manifest C:\SupervisorController\mrl\launch_manifest.json `
  --max-cycles 1 `
  --repin-cli-identity
```
- The `clear-recovery` line runs only if `status` showed `PAUSED_RECOVERY`.
- The check line must print `2.1.281 946eb5098cc8a56a189b8f0e3f083b6a8569030431252c9bb0ab4203b23bfff1`;
  anything else: **STOP**, do not start.
- `<LANE_WORKTREE>` / `<LANE_PACKET_ID>`: the lane's fresh claimed packet (not yet
  contracted; B-026 workaround). MRL runbook section 1 says to substitute exactly these two
  values; everything else is literal. Re-draft after ANY new commit in that worktree.
- Lanes 2 and 3: the same commands with `C:\SupervisorController2` / `C:\SupervisorController3`
  in place of `C:\SupervisorController` in `Set-Location`, `--checkout`, `--out`, the check line
  and `--launch-manifest` (their `mrl\` folders exist). `--model-selection` and
  `--controller-manifest` stay the shared paths shown. Their mode is the one the orchestrator
  authorizes; the draft's `--mode` and the start's `--mode` must be equal, and a `limited-auto`
  start also needs `--owner-enable-bounded-auto` (`start_gate.py:72-73`), as the wrappers pass.
- Supervised mode parks the run in `WAIT_FOR_OWNER` until the prompt digest is approved (MRL
  runbook section 5: `pending-approvals`, then `resume-pending-prompt --approve-prompt-digest
  <printed digest>`, then the same `start` again). The repin is written to the lane journal at
  the first start's preflight (audit event `cli_identity_repinned`), so that re-start runs
  WITHOUT `--repin-cli-identity`.
- The `autostart-launch.ps1` wrappers use the legacy form: no launch manifest (`cli.py:2704-2705`
  builds the legacy `ClaudeRunner`, not `OneShotRunner`), so a fresh manifest does not apply to
  them, but the journal repin does. Do not use them for any lane's first launch (they run
  limited-auto for 10 cycles, not a one-cycle canary). A lane returned to its wrapper after its
  repinned start needs a new ACTIVE-TASK block and no `--repin-cli-identity`.

### 5.12 Residual risk and the supervised canary [CORRECTED per M0-T159-G3 condition (6)]
**Named residual risk (open).** The launch-manifest worker path runs the CLI with
`--restricted`, `--permission-mode dontAsk`, `--tools`, `--strict-mcp-config`, `--settings`,
`--agents`, `--allowedTools` / `--disallowedTools` (`mrl_subagent_contract.py:426-436`) and
`--json-schema` (`mrl_one_shot.py:268`). 2.1.281 `--help` lists all of them (producer report,
F5/F6 note), but none was exercised LIVE at 2.1.281. This unit's live measurements were the
bounded `--version` / `--help` probes and the shell-routing capture, which runs the legacy argv
(`-p --input-format stream-json --output-format stream-json --verbose --max-turns 1
--permission-mode manual --permission-prompt-tool stdio --model claude-opus-5-5`). The code
refuses any inventory tool with no explicit allow or deny rule
(`mrl_subagent_contract.py:381-394`), but it is unproven that 2.1.281 enforces `--restricted` and
`dontAsk` the way the 2.1.252-era canaries (M0-T140..M0-T142) measured.

**So the FIRST lane launch (lane 1, 5.11) is a supervised canary:** `--mode supervised`, ONE
cycle, owner prompt-digest approval. During and after the cycle:
- runtime dir (MRL runbook section 6):
  `python -c "from tools.agent_supervisor.durable_state import runtime_dir_for; print(runtime_dir_for(r'C:\SupervisorController'))"`;
- its `audit.jsonl`: exactly one `cli_identity_repinned`, then `mrl_one_shot_launched` and
  `mrl_one_shot_settled` with `policy_result` `OK`; any `mrl_one_shot_refused` is an anomaly;
- `mrl\<run_id>\one_shot_unit.json`: every tool in `main_tool_uses` must be in the launch
  manifest's `dispatch.subagents.tools_inventory` and allowed by its `allow_rules`. A tool the
  profile should deny (above all Bash, PowerShell or WebFetch when `--tools` does not name it)
  showing up in `main_tool_uses` instead of `permission_denials` is an anomaly. `model_mismatch`
  must be false and `observed_models` must show `claude-opus-5-5`;
- `mrl\<run_id>\subagent_ledger.json`: nothing issued outside the contract.

On ANY anomaly: stop (`python -m tools.agent_supervisor stop --checkout C:\SupervisorController`
if the run is still live), launch no further lane, and open a blocker. Follow-up requested of the
orchestrator (G3 condition 6): add these flags to the capability probe and re-measure the
M0-T140..M0-T142 canary facts at 2.1.281.

## 6. Preservation (safety)
Every lane journal is byte-untouched — before AND after all probes (size+mtime identical):
`9aca7075…`=17,080,320/1790236111, `cfdedc11…`=5,689,344/1790144402,
`9df5e3ba…`=3,526,656/1790143705. No supervisor verb was run against the live controller;
`record-manifest`/`doctor` wrote only under `%TEMP%\m0t159\` (doctor `--runtime-base` a temp
dir, so its fresh empty journal landed in temp, not `%LOCALAPPDATA%`). No write outside the
worktree allowed_paths and the temp dir. `C:\SupervisorController*`, `wt-controller-src`,
`C:\Program Files\SupervisorConfig`, and `%LOCALAPPDATA%\NYCBuildabilitySupervisor` were
read-only throughout.

[CORRECTED per M0-T159-G3 F1-F7] The correction pass (documentation only) only listed, hashed
and read those locations, the lane autostart logs and the lane launchers; it ran no supervisor
verb. The three lane journals still read `9aca7075…`=17,080,320/1790236111,
`cfdedc11…`=5,689,344/1790144402, `9df5e3ba…`=3,526,656/1790143705 afterwards. Nothing under
`tools/` changed: the candidate stays byte-identical at `a3f24ff3`.

## 7. Verdict
Recertification: **PASS at the one frozen candidate** ([CORRECTED per M0-T159-G3 F1] commit
`a3f24ff3825c126c038f59b1ea6d2352f29d724a`, subtree `9c0b14ea…`; manifest `55dc71350b…`; admitted CLI
`2.1.281`/`92af5806…`; config `34f4fe90…`), subject to the independent G3/G4 + DCV wave. Any
supervisor/operator-channel change after this point re-invalidates certification and
re-triggers the recert.
