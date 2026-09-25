# M0-T161 producer report - D-088 five-lane commissioning helper

Producer: `backend-engineer`, isolation task worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t161` (branch
`task/M0-T161-five-lane-commissioning`), from the claim seam
`110894295ec97c1d7cb87deb3421a628b526b66b`.

The producer changed NOTHING on the machine: no phase of the helper was run, no
`update_controller_from_candidate.ps1`, no supervisor verb, no write to
`C:\SupervisorController*`, `C:\SupervisorBackup`, `C:\Program Files\SupervisorConfig`,
`%LOCALAPPDATA%\NYCBuildabilitySupervisor` or `wt-controller-src`.
`C:\SupervisorController3\autostart-launch.ps1` was READ once as the wrapper structural
reference (allowed). All writes are the four allowed worktree paths.

## 1. What was built

- `tools/controller_update/commission_lanes.ps1` - the owner-run, fail-closed helper.
  Five phases (`-Phase check | update | lane | approve | lanes`), PowerShell 5.1,
  `Set-StrictMode -Version Latest` + `$ErrorActionPreference 'Stop'`, every pinned
  path/digest/version/SHA a named constant (lines 60-104), one external-command helper
  `Invoke-Ext` (line 110, checks `$LASTEXITCODE`, tests stub it), no `Invoke-Expression`
  and no caller text interpolated into a command string, every STOP a plain-English
  `throw`.
- `tools/controller_update/ps_tests/test_commission_lanes.ps1` - the offline proof.
  Dot-sources the helper with `-LoadOnly` (loads functions + constants, dispatches no
  phase) and stubs `Invoke-Ext` and the tree/launch helpers, so nothing touches the
  machine.
- `project-control/reports/M0-T161-owner-guide.md` - the plain-English owner guide.

Design note: the helper keeps STRICTMODE + EAP=Stop at script scope; `Invoke-Ext`
sets EAP=Continue function-scoped for the native call only (native stderr must not
become a terminating error before the raw exit code is read - the same discipline as
`update_controller_from_candidate.ps1`).

## 2. Section 5 -> script line map (AS-1)

Every command/argument/path/digest/STOP from M0-T159-recertification.md section 5 is a
named constant or a step function. `check` = 5.1; `update` = 5.2-5.10 + lanes 4-5
stand-up; `lane`/`approve` = 5.11/5.12; `lanes` = 5.11 for lanes 2-5 from a plan file.

| Recert 5.x | Helper location | Notes / justified deviation |
|---|---|---|
| 5.0 pinned identities | constants L76-L87 (`CandidateCommit` a3f24ff3, `CandidateTree` 82432361, `CandidateSubtree` 9c0b14ea, `WrongSubtree` 11d43515, `ManifestStop` "147 55dc7135...", `ConfigRawHash` 610ce9d5, `ConfigLfHash` 34f4fe90, `ChainCheckStop` "2.1.281 946eb509...") | long hashes live once, never retyped |
| 5.1 preconditions | `Invoke-CheckPhase` L265-L321 | lock check per existing lane via `runtime_dir_for` (L274-283); controller+A1 `status` informational (L287-292); config raw-hash STOP (L295-301); binding-pin precondition L265-270; free-disk added per D-088-R006 (L303-308) |
| 5.2 verified backup | `Step-Backup` L369-377 | runs update `-Phase backup`; STOP unless `BACKUP VERIFIED`; then `Assert-SameTree` lanes 2/3 vs live |
| 5.3 install | `Step-Install` L383-408 | documented `source_worktree_exists` handling (L382-391: `git worktree remove --force` then re-run); identity guard rejects the wrong subtree 11d43515 (L404-406) |
| 5.4 record-manifest + STOP | `Step-RecordManifest` L423-438 (`Ensure-ActivationDir` L414) | reads the manifest back; STOP unless exactly "147 55dc7135..." |
| 5.5 verify-manifest | `Step-VerifyManifest` L444-448 | runs update `-Phase verify-manifest`; STOP unless `MANIFEST VERIFIED against the accepted source` |
| 5.6 propagation 2-5 + STAND UP 4-5 | `Step-Propagate` L454-482 | creates C:\SupervisorController4/5 folder + `tools\agent_supervisor` mirror + `mrl\` folder + a wrapper from lane 3 (`New-LaneWrapperContent` L550) with the checkout key from the controller's own `checkout_key` (`Get-CheckoutKey` L195, run via python from wt-controller-src); robocopy /MIR into 2-5; `Assert-SameTree` all five vs wt-controller-src |
| 5.7 verify-controller | `Step-VerifyController` L488-499 | loops C:\SupervisorController,2,3,4,5 + wt-controller-src; STOP on any failure |
| 5.8 doctor | `Step-Doctor` L505-514 | STOP unless overall `PASS` |
| 5.9 doctor --live | `Step-DoctorLive` L520-530 | STOP unless `VERIFIED` |
| 5.10 post-update checks | `Step-PostChecks` L536-539 | status / recovery-status / pending-approvals (informational) |
| 5.11 per-lane relaunch | `Start-LaneFirstLaunch` L657-719 | (2) status; (3) clear-recovery only on `PAUSED_RECOVERY`; (4) fresh `mrl_launch_draft`, chain STOP unless "2.1.281 946eb509..."; (5) detached start, `--repin-cli-identity` on first start only, `--owner-enable-bounded-auto` for limited-auto |
| 5.11 lane 1 canary | `Invoke-LanePhase` L639-650 (mode forced supervised via `Get-LaneMode` L622) | lane 1 = supervised one-cycle canary |
| 5.11/5.12 approve | `Invoke-ApprovePhase` L730-764 | pending-approvals -> approve the exact digest -> re-start WITHOUT repin |
| 5.11 lanes 2-5 | `Invoke-LanesPhase` L876-892 + `Assert-ValidLanePlan` L788-855 | validate the plan, then start each lane >= 60 s apart |
| immutability guard | `Invoke-UpdatePhase` L332-352 | snapshots config.toml + model_selection.toml raw SHA before/after; STOP if either changed (the activation manifest is the only thing 5.4 re-records) |

Deviations, all justified: (a) update stands up lanes 4-5 (the recert's 5.6 only mirrors
to 2/3) - this is the packet's explicit extension (D-088-R003); (b) free-disk STOP in
`check` (D-088-R006) with a 1.0 GiB floor constant `MinFreeGiB` - reported as machine
contention, not in the recert text; (c) starts are detached (`Start-Detached` L238,
Start-Process hidden, logs under `autostart-logs`) per the packet DESIGN, whereas the
recert shows the foreground `start`. Nothing in section 5 is dropped or reordered.

## 3. STOP-condition table (AS-2)

| STOP | Where | Fires when |
|---|---|---|
| no exit code | L144 | any external command produces no exit code (fail closed) |
| binding not re-pinned | L271 | `check`: source binding != candidate a3f24ff3 |
| lane not stopped | L283 | `check` 5.1: an existing lane still holds `supervisor.lock` |
| config hash | L301 | `check` 5.1: config.toml raw SHA != 610ce9d5... |
| low disk | L310 | `check`: free space on C: below 1.0 GiB (D-088-R006/R001) |
| backup | L373 | `update` 5.2: no `BACKUP VERIFIED` |
| tree mismatch | L219/L223 | 5.2/5.6: `Assert-SameTree` BYTE MISMATCH / empty tree |
| install | L397 / L399-406 | 5.3: no `INSTALLED`, or wrong commit/subtree (incl. the 11d43515 cfc3d22c subtree) |
| manifest | L438 | 5.4: readback != "147 55dc7135..." |
| verify-manifest | L448 | 5.5: no `MANIFEST VERIFIED` |
| checkout key | L204 | 5.6: `checkout_key` did not return a 64-hex key |
| robocopy | L472 | 5.6: robocopy raw exit >= 8 |
| verify-controller | L498 | 5.7: any copy fails verify-controller |
| doctor | L514 | 5.8: not overall PASS |
| doctor --live | L530 | 5.9: not VERIFIED |
| update guard | L348/L351 | update changed config.toml or model_selection.toml |
| lane chain | L705 | 5.11: launch-manifest chain != "2.1.281 946eb509..." (start is NOT reached) |
| lane args / mode | L637/L641/L626/L634 | `lane`: bad -Lane, missing -Worktree/-PacketId, or bad -Mode |
| approve | L742/L750/L753 | `approve`: no digest given, digest not held, or resume failed |
| plan (5 checks) | L806/L811/L814/L820/L827/L833/L839/L854 | `lanes`: missing field, lane out of 2-5, duplicate lane, duplicate/absent git worktree, missing packet, packet not claimed/in_progress, missing allowed_paths, overlapping allowed_paths |

## 4. Test list (`test_commission_lanes.ps1`)

1. both `.ps1` files parse clean under PowerShell 5.1 (`Parser::ParseFile`, 0 errors).
2a. update 5.4 manifest STOP throws a plain-English line AND nothing after it runs
   (asserts verify-manifest / verify-controller / robocopy / doctor were NEVER called
   after the STOP; record-manifest WAS).
2b. lane 5.11 chain STOP throws AND the detached start never fired (stubbed
   `Start-Detached` was not called).
2c. check 5.1 config-hash STOP throws a plain-English line.
3. `check` performs NO write (a before/after snapshot of a sandbox is byte-identical;
   `Invoke-Ext`, `Get-FileSha256Raw`, `Get-FreeGiB`, `Get-BoundCommit` stubbed).
4. the generated lane-4 wrapper differs from a fixture lane-3 ONLY in lane-specific
   values (checkout path, checkout key, log names, labels) plus the ACTIVE-TASK block
   (now "not yet fed", lane 3's task inputs removed): contains-checks + a strong
   region diff asserting every differing line outside the block carries a lane token.
5. the plan validator ACCEPTS a clean disjoint claimed plan and REFUSES overlapping
   allowed_paths, a duplicate lane number, a shared worktree, and an unclaimed packet.

## 5. Self-checks (explicit cwd; [OBSERVED]/[BLOCKED])

- Worktree identity - [OBSERVED]
  - cwd: agent isolation worktree; `git -C C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t161 rev-parse --show-toplevel`
    -> `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t161`
  - `git -C ... rev-parse HEAD` -> `110894295ec97c1d7cb87deb3421a628b526b66b` (the claim seam).
- PowerShell parser (AS-4, script parses clean) - [BLOCKED]
  - The isolated producer sandbox refuses every `powershell.exe` invocation (even a
    read-only `Parser::ParseFile`, and even with the sandbox override): "this command
    runs powershell in a plain command; ... Refusing to run it". Recorded per the
    packet HARNESS note.
  - Recipe for the orchestrator at harvest (cwd = worktree root
    `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t161`):
    `powershell -NoProfile -ExecutionPolicy Bypass -Command "$e=$null;$t=$null;[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path 'tools\controller_update\commission_lanes.ps1').Path,[ref]$t,[ref]$e)|Out-Null; $e.Count"`
    (repeat for `ps_tests\test_commission_lanes.ps1`); expect `0` both times.
- Offline ps_tests suite (AS-4) - [BLOCKED], same sandbox refusal.
  - Recipe (cwd = worktree root):
    `powershell -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1`
  - `run_ps_tests.ps1` auto-discovers every `test_*.ps1` and exits nonzero on any
    failure; expect all test files (including the new `test_commission_lanes.ps1`) to
    pass. The new test is offline: it stubs `Invoke-Ext` and the tree/launch helpers,
    so it starts no lane and writes nothing outside `%TEMP%`.

Manual review compensations for the un-runnable state: params with empty defaults use
manual validation (no `[ValidateSet]` binding-time trap); `Invoke-Ext` sets EAP=Continue
function-scoped for the native call; the checkout-key extraction uses a positive
`-match`; the test avoids `$var` interpolation of undefined variables under StrictMode
(the `$WorkDir` assertion is single-quoted); the one activation-dir write is routed
through `Ensure-ActivationDir`, which the update-STOP test stubs so the suite makes no
machine write.

## 6. DISCOVERIES

- D-1 (harness/env): this producer sandbox blanket-refuses `powershell.exe` (any plain
  command, any cwd, even with the sandbox override) on worktree-isolation grounds, so
  PowerShell producers cannot self-run the parser or the ps_tests. All PS verification
  for such tasks must be harvested by the orchestrator. (Route to backlog if not
  already tracked; not fixed in-packet.)
- D-2 (wrapper cosmetic): the lane-4/5 wrapper keeps lane 3's header prose except the
  `INSTANCE N` label (e.g. the comment "Third parallel loop instance" is left as-is,
  byte-identical, so the wrapper-diff proof stays tight). It has no runtime effect; the
  orchestrator may polish the comment when it first feeds the lane. Not a defect.
- D-3 (lane 1-3 runtime keys): the recert lists the lanes' runtime keys only truncated
  (`9aca7075...`, `cfdedc11...`, `9df5e3ba...`). The helper never hardcodes them - it
  computes each lane's runtime dir / checkout key from the controller's own
  `durable_state.runtime_dir_for` / `checkout_key` at run time (D-066-R001), so no
  truncated value is ever needed.

END-OF-REPORT
