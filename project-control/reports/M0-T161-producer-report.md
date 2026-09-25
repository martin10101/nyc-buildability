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

---

# Round 2 - required corrections (M0-T161-G3 F1-F5, M0-T161-G5 advisories)

Round 1 PASSED G3 (`cr-m0t161`) and G5 (`sec-m0t161`); every finding was ADVISORY. This
round takes all of them into ONE bounded change before the owner runs the helper. Still
NO machine change: no phase run, no supervisor verb, no `update_controller_from_candidate.ps1`,
no write outside the four allowed worktree paths. One new commit on top of `8273c688`
(round-1 material `b27fc89b` + both review reports), containing only the 4 allowed files.

## R2.1 Per-finding closure

| Finding | What round 1 did | Round 2 correction | Where (commission_lanes.ps1 unless noted) |
|---|---|---|---|
| **G3 F2** (top; the owner reads it) - owner-guide step 4 wrongly said step 3 prints the digest | prose misdirected the owner | Rewrote owner-guide step 4 as TWO commands: (1) `approve` WITHOUT a digest -> prints the pending approval + digest, then STOPs on purpose; (2) re-run `approve` with that exact digest. The guide quotes the script's STOP text VERBATIM (`STOP [approve]: pass -PromptDigest <the digest printed above> to approve the held prompt`) and flags it as the ONE expected STOP. Step 3 note now says it does NOT print the code. | `M0-T161-owner-guide.md` step 4 + "one rule" note; STOP source unchanged at Invoke-ApprovePhase (the "pass -PromptDigest..." throw) |
| **G3 F1** - 4 pinned values defined but never asserted | echoes only | Assert `CandidateTree` 82432361 AND `204 byte-identical` in `Step-Install` (L436, L440). Assert `covered files 146`, `installed files re-compared 204`, and the `...at a3f24ff3...` accepted-source commit in `Step-VerifyManifest` (L490, L495, L499). `ConfigLfHash` REMOVED (dead pin); comment L82-85 records it is covered transitively by the 5.4 manifest-digest STOP + 5.7 verify-controller config binding. | Step-Install L435-445; Step-VerifyManifest L488-504; constant removed L82-85 |
| **G3 F4** - 4 wrapper-generation throws lacked the `STOP` prefix | fail-closed but off-heuristic | All four now start `STOP [update 5.6]:` (they run during 5.6 wrapper generation). `grep 'throw ' \| grep -v STOP` = empty. | New-LaneWrapperContent (2 throws), Set-NotYetFedBlock (2 throws) |
| **G5** - no source precondition before robocopy /MIR | detected only post-hoc | New `Get-TreeFileCount` helper (L241) + a precondition immediately before the /MIR loop: the certified source must hold exactly `InstalledFileCount` (204) files (cache dirs excluded, as /XD and the tree compare do) or it STOPs BEFORE any mirror. | Step-Propagate L523-532 |
| **G5** - 5.5-5.9 STOPs missing the rollback pointer | only 5.4 had it | Added `roll back per runbook section 10` to 5.5 verify-manifest (L493/497/501), 5.6 robocopy (L541) + the new precondition (L530), 5.7 verify-controller (L564), 5.8 doctor (L580), 5.9 doctor --live (L596). Also to the two new 5.3 asserts (L438/442). | as listed |
| **G5 medium + G3 F3** - plan validator gaps | prefix-only overlap; weak worktree check; mode/packet-id unconstrained | (a) Each lane worktree must be a LINKED worktree ROOT: `--show-toplevel` equals the given path AND `--absolute-git-dir` != `--git-common-dir` (rejects the primary checkout and subdirectories), via `Resolve-PathKey` (L251). (b) Dedup worktrees by RESOLVED toplevel. (c) Lanes-phase mode routed through `Get-LaneMode` up front in `Assert-ValidLanePlan` AND at start in `Invoke-LanesPhase`. (d) `packet_id` constrained to `^M\d+-T\d+$` before any path join, via `Assert-PacketId` (L687) in `Start-LaneFirstLaunch` (L736, covers the lane/approve/lanes join) and `Assert-ValidLanePlan` (L899). (e) `Get-PathOverlap` glob-aware via `Get-NormPathBase` (L965): trailing `/**` and `/*` normalize to the covered directory, so `dir/**` covers everything under `dir` (safe over-approximation). | Assert-ValidLanePlan L894-931; Get-NormPathBase/Get-PathOverlap L965-993; Invoke-LanesPhase mode line |
| **G5 LOW + G3 F5** - test coverage gaps + belt-and-braces writes | STOP-wiring proven; some guards unproven | Added offline stubbed tests 6-11 (see R2.4). Every machine-write path is now stubbed in the update tests: `New-Item` (simple no-op function so `-ItemType` falls into `$args`) and a new production `Write-WrapperFile` seam (L457) both stubbed, so no wrapper or folder can be written even if a STOP moved. | test_commission_lanes.ps1 sections 6-11 |

## R2.2 Updated section-5 -> script line map (changed/new anchors only; round-1 map otherwise stands)

| Recert 5.x | New/changed anchor |
|---|---|
| 5.0 pinned identities | `ConfigLfHash` constant removed (transitively covered); comment L82-85. Other pins unchanged (L76-90) |
| 5.3 install | `Step-Install` now asserts `CandidateTree` (L436) and `204 byte-identical` (L440); both STOPs name rollback |
| 5.5 verify-manifest | `Step-VerifyManifest` now asserts `at <candidate>` (L490), `covered files 146` (L495), `installed files re-compared 204` (L499); all name rollback |
| 5.6 propagation | robocopy source precondition `Get-TreeFileCount` (L241) + STOP before /MIR (L523-532); robocopy STOP names rollback (L541); wrapper-generation throws now STOP-prefixed |
| 5.7/5.8/5.9 | verify-controller (L564), doctor (L580), doctor --live (L596) STOPs name rollback |
| 5.11 lanes plan | `Assert-ValidLanePlan` linked-worktree root + dedup-by-toplevel + up-front mode + packet-id (L894-931); `Get-PathOverlap` glob-aware (L977); helpers `Resolve-PathKey` (L251), `Assert-PacketId` (L687), `Get-NormPathBase` (L965) |

## R2.3 STOP table - round-2 additions (round-1 STOPs unchanged)

| STOP | Where | Fires when |
|---|---|---|
| install commit tree | Step-Install L436 | 5.3: install output lacks commit tree 82432361 |
| install file count | Step-Install L440 | 5.3: install output lacks "204 byte-identical" |
| verify-manifest at-commit | Step-VerifyManifest L490 | 5.5: no "MANIFEST VERIFIED ... at a3f24ff3" |
| verify-manifest counts | Step-VerifyManifest L495/L499 | 5.5: missing "covered files 146" or "installed files re-compared 204" |
| robocopy source precondition | Step-Propagate L529 | 5.6: certified source tree file count != 204 (STOP BEFORE any /MIR) |
| wrapper generation (4) | New-LaneWrapperContent / Set-NotYetFedBlock | 5.6: bad checkout key, missing lane-3 key, missing ACTIVE-TASK markers, or missing $Py/$WorkDir (now STOP-prefixed) |
| linked-worktree root | Assert-ValidLanePlan L913/L922 | lanes: worktree top-level != given path (subdirectory), or git-dir == common-dir (primary checkout) |
| packet-id charset | Assert-PacketId L689 (lane/approve/lanes) | packet id not `^M\d+-T\d+$` before any tasks-path join |

Also: 5.5-5.9 STOP messages now carry "roll back per runbook section 10"; the lanes-phase
mode now fails closed via `Get-LaneMode` (unknown mode STOPs up front, not just at the supervisor).

## R2.4 Test list - round-2 additions (`test_commission_lanes.ps1`; sections 1-5 retained, 2a/2b/5 adjusted)

- 2a: install stub now emits the full valid identity line (commit + tree + subtree + "204
  byte-identical"); `New-Item` and `Write-WrapperFile` stubbed (belt-and-braces no-write).
- 2b: uses a valid `M0-T999` packet id (Start-LaneFirstLaunch now charset-checks it).
- 5: packet ids renamed to valid `M0-T90x`; git stub answers all three rev-parse calls as a
  valid linked worktree.
- **6** robocopy /MIR source precondition STOPs on a wrong source count, BEFORE any robocopy.
- **7** install STOPs on the cfc3d22c wrong subtree (`11d43515`).
- **8** lane 1 rejects a non-supervised mode, defaults to supervised, and its start carries NO
  `--owner-enable-bounded-auto` (captured start args) while repinning and running one cycle.
- **9** approve STOPs when no digest is given and when the digest is not held; `resume-pending-prompt`
  is never called in either case.
- **10** the update config/model immutability guard STOPs when config.toml changes (run 1) and when
  model_selection.toml changes (run 2); the whole update runs through with valid stubbed outputs
  and every write helper stubbed.
- **11** plan validator refuses a glob overlap (`dir/**` over a file under `dir`), accepts
  glob-disjoint paths, refuses a non `M<n>-T<n>` packet id, refuses the primary checkout, and
  refuses a subdirectory of a worktree.

## R2.5 Self-checks (explicit cwd; [OBSERVED]/[BLOCKED])

- Worktree identity - [OBSERVED]: `git -C C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t161 rev-parse
  --show-toplevel` -> the wt-m0t161 path; HEAD before this commit = `8273c6881677d9ec83f1e03bc5c63af534180df7`.
- PowerShell parser + offline ps_tests (AS-4) - [BLOCKED], same sandbox refusal as round 1: the
  isolated producer sandbox refuses every `powershell.exe` invocation (even a read-only
  `Parser::ParseFile`, even with the sandbox override): "this command runs powershell in a plain
  command; ... Refusing to run it". Orchestrator recipe at harvest (cwd = worktree root):
  - parse: `powershell -NoProfile -ExecutionPolicy Bypass -Command "$e=$null;$t=$null;[System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path 'tools\controller_update\commission_lanes.ps1').Path,[ref]$t,[ref]$e)|Out-Null; $e.Count"` (repeat for `ps_tests\test_commission_lanes.ps1`); expect `0` both.
  - suite: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1`; expect every `test_*.ps1` to pass, including `test_commission_lanes.ps1` (now proving sections 1-11). The suite stubs `Invoke-Ext` and all tree/launch/write helpers, so it starts no lane and writes nothing outside `%TEMP%`.

Manual-review compensations for the un-runnable state (round 2 specifics): the `New-Item` test
stubs are SIMPLE functions (no `[Parameter]` attribute) so their `-ItemType/-Force/-Path` named
args fall into `$args` instead of erroring an advanced binder; the counter stub uses
`$x = $x + 1` (not `$x++`) so no stray value can leak into the return; the immutability test
drives the full update with valid stubbed outputs and asserts the guard fires on a single
before/after hash flip; the linked-worktree checks are proven with a git stub that echoes the
`-C` path for `--show-toplevel` and distinct/equal git-dir vs common-dir per case.

END-OF-REPORT
