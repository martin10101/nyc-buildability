# test_commission_lanes.ps1 - offline proof of commission_lanes.ps1 (M0-T161;
# D-088-R003/R004). Everything runs offline: the file is dot-sourced with
# -LoadOnly (functions + constants loaded, no phase dispatched), and the ONE
# external-command helper Invoke-Ext plus the tree/launch/write helpers are stubbed,
# so NO supervisor verb and NO machine change ever run. It proves:
#   1. both .ps1 files parse clean under Windows PowerShell 5.1;
#   2. each STOP throws a plain-English line and halts everything after it
#      (update 5.4 manifest STOP; lane 5.11 chain STOP that prevents the start;
#      check 5.1 config-hash STOP);
#   3. -Phase check performs no write;
#   4. the generated lane-4 wrapper differs from lane 3's ONLY in lane-specific
#      values + the ACTIVE-TASK block, which is marked "not yet fed";
#   5. the plan-file validator refuses overlapping allowed_paths, duplicate lane
#      numbers, duplicate worktrees, and unclaimed packets, and accepts a clean plan;
#   6. the robocopy /MIR source precondition STOPs before any mirror (round 2, G5);
#   7. the install cfc3d22c WRONG-subtree refusal (round 2, G5/G3);
#   8. lane-1 supervised-canary mode enforcement + no bounded-auto (round 2, G5);
#   9. the approve "digest missing / not held" STOPs, resume never called (round 2);
#  10. the update config/model immutability guard STOPs on any change (round 2);
#  11. the linked-worktree (primary + subdirectory) refusals, glob-aware overlap
#      refusal + disjoint accept, and the packet-id charset refusal (round 2).
# Rounds 6-11 add the M0-T161-G3/G5 required-corrections coverage. Every write path
# (New-Item, the wrapper WriteAllText seam) is stubbed too (belt-and-braces).

$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'commission_lanes.ps1'

$script:failures = 0
function Assert-True {
    param([bool]$Condition, [string]$Label)
    if ($Condition) { Write-Output ("PASS " + $Label) }
    else { Write-Output ("ASSERT-FAIL " + $Label); $script:failures = $script:failures + 1 }
}

# ---- 1. parse both .ps1 files clean --------------------------------------------
foreach ($p in @($scriptPath, (Join-Path (Split-Path $PSScriptRoot -Parent) 'update_controller_from_candidate.ps1'))) {
    $parseErrors = $null
    $tokens = $null
    [System.Management.Automation.Language.Parser]::ParseFile($p, [ref]$tokens, [ref]$parseErrors) | Out-Null
    $errCount = @($parseErrors).Count
    Assert-True -Condition ($errCount -eq 0) -Label ("parses clean: " + (Split-Path -Leaf $p))
    if ($errCount -gt 0) { $parseErrors | ForEach-Object { Write-Output ("  " + $_.Message) } }
}

# ---- load the functions + constants (no dispatch) ------------------------------
. $scriptPath -LoadOnly

# The dot-source turned StrictMode on and ErrorActionPreference to Stop; keep the
# harness resilient so one stray error cannot abort the whole file.
$ErrorActionPreference = 'Continue'

$work = Join-Path $env:TEMP ('ctl24-m0t161-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $work | Out-Null

# A git stub that answers the plan validator's three rev-parse calls per worktree.
# $Kind: 'linked' (a real linked worktree root), 'primary' (the primary checkout:
# git-dir == common-dir), or 'subdir' (show-toplevel != the given path).
function Resolve-GitStub {
    param([string[]]$ExtArgs, [string]$Kind)
    $a = ($ExtArgs -join ' ')
    $cpath = ''
    for ($k = 0; $k -lt $ExtArgs.Count - 1; $k++) { if ($ExtArgs[$k] -eq '-C') { $cpath = $ExtArgs[$k + 1]; break } }
    if ($a -match '--show-toplevel') {
        if ($Kind -eq 'subdir') { return @{ code = 0; stdout = (Split-Path $cpath -Parent); stderr = '' } }
        return @{ code = 0; stdout = $cpath; stderr = '' }
    }
    if ($a -match '--absolute-git-dir') {
        if ($Kind -eq 'primary') { return @{ code = 0; stdout = (Join-Path $cpath '.git'); stderr = '' } }
        return @{ code = 0; stdout = (Join-Path (Join-Path $cpath '.git\worktrees') (Split-Path $cpath -Leaf)); stderr = '' }
    }
    if ($a -match '--git-common-dir') { return @{ code = 0; stdout = (Join-Path $cpath '.git'); stderr = '' } }
    return @{ code = 0; stdout = ''; stderr = '' }
}

# A full, valid -Phase install stdout (all pinned identities present, no wrong subtree).
function Get-GoodInstallStdout {
    return ("INSTALLED from immutable commit " + $script:CandidateCommit + " commit tree " + $script:CandidateTree +
        " subtree " + $script:CandidateSubtree + " files " + $script:InstalledFileCount + " byte-identical source-to-destination")
}

# ---- 2a. update 5.4 manifest STOP halts everything after it --------------------
# New-Item + Write-WrapperFile are stubbed too, so no machine write is possible even
# if the 5.4 STOP were removed (belt-and-braces).
$script:calls = @()
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    $script:calls += ($FilePath + ' ' + $a)
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase backup') {
        return @{ code = 0; stdout = 'BACKUP VERIFIED run T'; stderr = '' }
    }
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase install') {
        return @{ code = 0; stdout = (Get-GoodInstallStdout); stderr = '' }
    }
    if ($a -match 'print\(len\(m') {
        return @{ code = 0; stdout = '146 deadbeefdeadbeef'; stderr = '' }   # WRONG readback -> 5.4 STOP
    }
    return @{ code = 0; stdout = ''; stderr = '' }
}
function Get-FileSha256Raw { param([string]$Path) return 'stub-hash' }
function Assert-SameTree { param([string]$Reference, [string]$Candidate, [string]$Step) $script:calls += ('same-tree ' + $Candidate) }
function Ensure-ActivationDir { $script:calls += 'ensure-activation-dir' }   # no real machine write
# A SIMPLE function (no [Parameter] attribute) so its named args (-ItemType/-Force/
# -Path) fall harmlessly into $args instead of erroring an advanced binder.
function New-Item { $script:calls += 'new-item(stub)' }
function Write-WrapperFile { param([string]$Path, [string]$Content) $script:calls += 'write-wrapper(stub)' }
$threw = $false
$msg = ''
try { Invoke-UpdatePhase | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'update 5.4' -and $msg -match 'expected') -Label 'update 5.4 manifest mismatch throws a plain-English STOP'
Assert-True -Condition (($script:calls -join '|') -match 'record-manifest') -Label 'update ran through 5.4 (record-manifest called)'
Assert-True -Condition (($script:calls -join '|') -notmatch 'verify-manifest') -Label 'update 5.5 verify-manifest NEVER ran after the 5.4 STOP'
Assert-True -Condition (($script:calls -join '|') -notmatch 'verify-controller') -Label 'update 5.7 verify-controller NEVER ran after the 5.4 STOP'
Assert-True -Condition (($script:calls -join '|') -notmatch 'robocopy') -Label 'update 5.6 propagation NEVER ran after the 5.4 STOP'
Assert-True -Condition (($script:calls -join '|') -notmatch 'doctor') -Label 'update 5.8/5.9 doctor NEVER ran after the 5.4 STOP'
Remove-Item Function:New-Item -ErrorAction SilentlyContinue

# ---- 2b. lane 5.11 chain STOP prevents the detached start ----------------------
$script:launched = $false
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    if ($a -match 'status --checkout') { return @{ code = 0; stdout = 'PREFLIGHT'; stderr = '' } }
    if ($a -match 'mrl_launch_draft') { return @{ code = 0; stdout = ''; stderr = '' } }
    if ($a -match "claude_chain_sha256") { return @{ code = 0; stdout = '2.1.252 wrongchainvalue'; stderr = '' } }  # WRONG -> STOP
    return @{ code = 0; stdout = ''; stderr = '' }
}
function Start-Detached { param([string]$LaneNumber, [string[]]$StartArgs, [string]$WorkingDirectory) $script:launched = $true; return @{ pid = 1; out = 'o'; err = 'e' } }
$threw = $false
$msg = ''
try { Start-LaneFirstLaunch -LaneNumber '2' -Checkout 'C:\SupervisorController2' -LaneWorktree 'C:\wt-x' -LanePacketId 'M0-T999' -Mode 'limited-auto' -Repin $true | Out-Null }
catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'lane 5.11' -and $msg -match 'expected') -Label 'lane 5.11 chain mismatch throws a plain-English STOP'
Assert-True -Condition (-not $script:launched) -Label 'lane 5.11 STOP prevented the detached start (no launch)'

# ---- 2c. check 5.1 config-hash STOP -------------------------------------------
function Get-BoundCommit { return $script:CandidateCommit }
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    if ($a -match 'runtime_dir_for') { return @{ code = 0; stdout = (Join-Path $work 'rt-nolock'); stderr = '' } }
    if ($a -match 'status') { return @{ code = 0; stdout = 'PREFLIGHT'; stderr = '' } }
    return @{ code = 0; stdout = ''; stderr = '' }
}
New-Item -ItemType Directory -Force -Path (Join-Path $work 'rt-nolock') | Out-Null
function Get-FileSha256Raw { param([string]$Path) return 'not-the-expected-config-hash' }
function Get-FreeGiB { param([string]$Path) return 500 }
$threw = $false
$msg = ''
try { Invoke-CheckPhase | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'check 5.1' -and $msg -match 'config') -Label 'check 5.1 config-hash mismatch throws a plain-English STOP'

# ---- 3. check performs no write -----------------------------------------------
$sandbox = Join-Path $work 'check-nowrite'
New-Item -ItemType Directory -Force -Path $sandbox | Out-Null
foreach ($n in @('rt1', 'rt2', 'rt3')) { New-Item -ItemType Directory -Force -Path (Join-Path $sandbox $n) | Out-Null }
Set-Content -LiteralPath (Join-Path $sandbox 'seed.txt') -Value 'seed' -Encoding ascii
function Get-BoundCommit { return $script:CandidateCommit }
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    if ($a -match 'SupervisorController2') { return @{ code = 0; stdout = (Join-Path $sandbox 'rt2'); stderr = '' } }
    if ($a -match 'SupervisorController3') { return @{ code = 0; stdout = (Join-Path $sandbox 'rt3'); stderr = '' } }
    if ($a -match 'runtime_dir_for') { return @{ code = 0; stdout = (Join-Path $sandbox 'rt1'); stderr = '' } }
    if ($a -match 'status') { return @{ code = 0; stdout = 'PREFLIGHT'; stderr = '' } }
    return @{ code = 0; stdout = ''; stderr = '' }
}
function Get-FileSha256Raw { param([string]$Path) return $script:ConfigRawHash }
function Get-FreeGiB { param([string]$Path) return 500 }
function Snapshot-Tree { param([string]$Root)
    return @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
        ForEach-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash + '  ' + $_.FullName } | Sort-Object)
}
$before = @(Snapshot-Tree -Root $sandbox)
$checkThrew = $false
try { Invoke-CheckPhase | Out-Null } catch { $checkThrew = $true; Write-Output ("  check threw: " + $_.Exception.Message) }
$after = @(Snapshot-Tree -Root $sandbox)
Assert-True -Condition (-not $checkThrew) -Label 'check with healthy stubs passes'
$diff = @(Compare-Object -ReferenceObject $before -DifferenceObject $after)
Assert-True -Condition ($diff.Count -eq 0) -Label 'check performed NO write (sandbox unchanged before/after)'

# ---- 4. lane-4 wrapper differs from lane 3 only in lane-specific values --------
$lane3Key = '9df5e3ba' + ('0' * 56)
$lane4Key = ('4' * 64)
$lane3Text = @'
# NYC Buildability Supervisor - INSTANCE 3 launcher wrapper (fixture)
# Third parallel loop instance. Runtime state is keyed by THIS checkout path.

$ErrorActionPreference = 'Stop'

$CheckoutKey = 'LANE3KEYPLACEHOLDER'
$LockPath    = Join-Path $env:LOCALAPPDATA "NYCBuildabilitySupervisor\$CheckoutKey\supervisor.lock"

function Test-SupervisorAlive {
    if (-not (Test-Path $LockPath)) { return $false }
    return $true
}
if (Test-SupervisorAlive) { Write-Output "supervisor-3 already running"; exit 0 }

# ---- ACTIVE-TASK block (orchestrator-maintained) --------------------------
# 2026-09-22 seq-125: M5-T070 run 14 - fixture active task note line one.
# fixture active task note line two.
$Py        = 'C:\Users\MLFLL\AppData\Local\Programs\Python\Python311\python.exe'
$WorkDir   = 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src'
$TaskPacket= 'C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M5-T079.json'
$Repo      = 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t079'
$Branch    = 'task/M5-T079-max-surface-hardening'
$RunId     = 'persistent3-local-19-m5t079'
# ---------------------------------------------------------------------------

$startArgs = @(
    '-m','tools.agent_supervisor','start',
    '--mode','limited-auto','--owner-enable-bounded-auto',
    '--checkout','C:\SupervisorController3',
    '--config','"C:\Program Files\SupervisorConfig\config.toml"',
    '--model-selection','C:\SupervisorController\model_selection.toml',
    '--manifest','C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json',
    '--repo',$Repo,'--worktree',$Repo,'--branch',$Branch,
    '--max-tasks','1','--max-cycles','10','--run-id',$RunId
)
$logDir = Join-Path $env:LOCALAPPDATA "NYCBuildabilitySupervisor\autostart-logs"
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss')
$out = Join-Path $logDir "autostart3-$stamp.out.txt"
$err = Join-Path $logDir "autostart3-$stamp.err.txt"
Start-Process -FilePath $Py -ArgumentList $startArgs -WorkingDirectory $WorkDir -RedirectStandardOutput $out -RedirectStandardError $err | Out-Null
Write-Output "supervisor-3 launched and holding lock"
'@
$lane3Text = $lane3Text.Replace('LANE3KEYPLACEHOLDER', $lane3Key)

$lane4Text = New-LaneWrapperContent -Lane3Content $lane3Text -LaneNumber '4' -CheckoutKey $lane4Key

# contains-checks: lane-specific tokens flipped, ACTIVE-TASK block blanked.
Assert-True -Condition ($lane4Text -match 'SupervisorController4' -and $lane4Text -notmatch 'SupervisorController3') -Label 'wrapper: checkout path 3 -> 4'
Assert-True -Condition ($lane4Text -match [regex]::Escape($lane4Key) -and $lane4Text -notmatch [regex]::Escape($lane3Key)) -Label 'wrapper: checkout key replaced'
Assert-True -Condition ($lane4Text -match 'autostart4-' -and $lane4Text -notmatch 'autostart3-') -Label 'wrapper: log names 3 -> 4'
Assert-True -Condition ($lane4Text -match 'supervisor-4' -and $lane4Text -notmatch 'supervisor-3') -Label 'wrapper: labels 3 -> 4'
Assert-True -Condition ($lane4Text -match 'INSTANCE 4' -and $lane4Text -notmatch 'INSTANCE 3') -Label 'wrapper: INSTANCE header 3 -> 4'
Assert-True -Condition ($lane4Text -match 'NOT-YET-FED' -and $lane4Text -match 'NOT YET FED - lane 4') -Label 'wrapper: ACTIVE-TASK block marked not yet fed'
Assert-True -Condition ($lane4Text -notmatch 'M5-T079') -Label 'wrapper: lane 3 task inputs removed'
# certified/shared lines byte-identical
Assert-True -Condition ($lane4Text -match [regex]::Escape("'--config','`"C:\Program Files\SupervisorConfig\config.toml`"'")) -Label 'wrapper: config path unchanged'
Assert-True -Condition ($lane4Text -match [regex]::Escape("'--model-selection','C:\SupervisorController\model_selection.toml'")) -Label 'wrapper: model-selection path unchanged'
Assert-True -Condition ($lane4Text -match [regex]::Escape("'--mode','limited-auto'")) -Label 'wrapper: mode flags unchanged'
Assert-True -Condition ($lane4Text -match [regex]::Escape('$WorkDir   = ''C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src''')) -Label 'wrapper: shared WorkDir preserved'

# strong region diff: outside the ACTIVE-TASK block, every differing line is lane-specific.
function Find-BlockRange { param([string[]]$Lines)
    $s = -1; $e = -1
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($s -lt 0 -and $Lines[$i] -match '^# ---- ACTIVE-TASK block') { $s = $i; continue }
        if ($s -ge 0 -and $Lines[$i] -match '^# -{10,}\s*$') { $e = $i; break }
    }
    return @($s, $e)
}
$l3 = $lane3Text -split "`r?`n"
$l4 = $lane4Text -split "`r?`n"
$r3 = Find-BlockRange -Lines $l3
$r4 = Find-BlockRange -Lines $l4
$laneToken = '(SupervisorController3|SupervisorController4|autostart3|autostart4|supervisor-3|supervisor-4|INSTANCE 3|INSTANCE 4|' + $lane3Key + '|' + $lane4Key + ')'
$unexpected = 0
# pre-block region (same start index in both)
for ($i = 0; $i -lt $r3[0]; $i++) {
    if ($l3[$i] -ne $l4[$i]) {
        if (($l3[$i] + $l4[$i]) -notmatch $laneToken) { $unexpected++; Write-Output ("  UNEXPECTED pre-block diff: " + $l3[$i] + ' => ' + $l4[$i]) }
    }
}
# post-block region (tails should align 1:1)
$tail3 = @(); $tail4 = @()
if ($r3[1] + 1 -le $l3.Count - 1) { $tail3 = $l3[($r3[1] + 1)..($l3.Count - 1)] }
if ($r4[1] + 1 -le $l4.Count - 1) { $tail4 = $l4[($r4[1] + 1)..($l4.Count - 1)] }
Assert-True -Condition ($tail3.Count -eq $tail4.Count) -Label 'wrapper: post-block region has the same line count'
for ($i = 0; $i -lt [math]::Min($tail3.Count, $tail4.Count); $i++) {
    if ($tail3[$i] -ne $tail4[$i]) {
        if (($tail3[$i] + $tail4[$i]) -notmatch $laneToken) { $unexpected++; Write-Output ("  UNEXPECTED post-block diff: " + $tail3[$i] + ' => ' + $tail4[$i]) }
    }
}
Assert-True -Condition ($unexpected -eq 0) -Label 'wrapper: outside the ACTIVE-TASK block, every diff is a lane-specific value'

# a real lane-3 fixture file for the Step-Propagate tests (rounds 6 and 10).
$lane3Fixture = Join-Path $work 'lane3-fixture.ps1'
Set-Content -LiteralPath $lane3Fixture -Value $lane3Text -Encoding utf8

# ---- 5. plan-file validator ----------------------------------------------------
$script:Ctl24 = $work   # redirect packet lookups into the sandbox
$tasksDir = Join-Path $work 'project-control\tasks'
New-Item -ItemType Directory -Force -Path $tasksDir | Out-Null
function Write-Packet { param([string]$Id, [string]$Status, [string[]]$Paths)
    $obj = [ordered]@{ task_id = $Id; status = $Status; allowed_paths = $Paths }
    $obj | ConvertTo-Json -Depth 5 | Out-File -FilePath (Join-Path $tasksDir ($Id + '.json')) -Encoding utf8
}
Write-Packet -Id 'M0-T901' -Status 'claimed'     -Paths @('services/api/app/a.py')
Write-Packet -Id 'M0-T902' -Status 'in_progress' -Paths @('apps/web/b.tsx')
Write-Packet -Id 'M0-T903' -Status 'claimed'     -Paths @('services/api/app/a.py')   # overlaps 901
Write-Packet -Id 'M0-T904' -Status 'backlog'     -Paths @('packages/d.py')           # unclaimed
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    if ($FilePath -eq 'git') { return Resolve-GitStub -ExtArgs $ExtArgs -Kind 'linked' }
    return @{ code = 0; stdout = ''; stderr = '' }
}
function Write-Plan { param([string]$Name, $Lanes)
    $p = Join-Path $work ($Name + '.json')
    ([ordered]@{ schema = 'commission_lanes_plan/v1'; lanes = $Lanes }) | ConvertTo-Json -Depth 6 | Out-File -FilePath $p -Encoding utf8
    return $p
}
function Test-Plan { param([string]$Path)
    try { $plan = Read-LanePlan -Path $Path; Assert-ValidLanePlan -Plan $plan | Out-Null; return @{ ok = $true; msg = '' } }
    catch { return @{ ok = $false; msg = $_.Exception.Message } }
}
$cleanPlan = Write-Plan -Name 'clean' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T901'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-b'; packet_id = 'M0-T902'; mode = 'limited-auto' })
$overlapPlan = Write-Plan -Name 'overlap' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T901'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-c'; packet_id = 'M0-T903'; mode = 'limited-auto' })
$dupLanePlan = Write-Plan -Name 'duplane' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T901'; mode = 'limited-auto' },
    @{ lane = 2; worktree = 'C:\wt-b'; packet_id = 'M0-T902'; mode = 'limited-auto' })
$dupWtPlan = Write-Plan -Name 'dupwt' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T901'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-a'; packet_id = 'M0-T902'; mode = 'limited-auto' })
$unclaimedPlan = Write-Plan -Name 'unclaimed' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T901'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-b'; packet_id = 'M0-T904'; mode = 'limited-auto' })

$rc = Test-Plan -Path $cleanPlan
Assert-True -Condition ($rc.ok) -Label 'plan validator ACCEPTS a clean, disjoint, claimed plan'
$ro = Test-Plan -Path $overlapPlan
Assert-True -Condition (-not $ro.ok -and $ro.msg -match 'overlapping allowed_paths') -Label 'plan validator REFUSES overlapping allowed_paths'
$rdl = Test-Plan -Path $dupLanePlan
Assert-True -Condition (-not $rdl.ok -and $rdl.msg -match 'more than once') -Label 'plan validator REFUSES a duplicate lane number'
$rdw = Test-Plan -Path $dupWtPlan
Assert-True -Condition (-not $rdw.ok -and $rdw.msg -match 'shared by two lanes') -Label 'plan validator REFUSES a shared worktree'
$ru = Test-Plan -Path $unclaimedPlan
Assert-True -Condition (-not $ru.ok -and $ru.msg -match 'not claimed/in_progress') -Label 'plan validator REFUSES an unclaimed packet'

# ---- 6. robocopy /MIR source precondition (round 2, G5) ------------------------
# Step-Propagate must STOP before any /MIR when the certified source has the wrong
# file count. Every write helper is stubbed so nothing touches the machine.
$script:calls = @()
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $script:calls += ($FilePath + ' ' + ($ExtArgs -join ' '))
    return @{ code = 0; stdout = ''; stderr = '' }
}
function New-Item { $script:calls += 'new-item(stub)' }
function Write-WrapperFile { param([string]$Path, [string]$Content) $script:calls += 'write-wrapper(stub)' }
function Get-CheckoutKey { param([string]$Checkout) return ('a' * 64) }
function Assert-SameTree { param([string]$Reference, [string]$Candidate, [string]$Step) $script:calls += 'same-tree' }
function Get-TreeFileCount { param([string]$Root) return 3 }   # WRONG count -> precondition STOP
$script:Lane3Wrapper = $lane3Fixture
$threw = $false; $msg = ''
try { Step-Propagate | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'update 5.6' -and $msg -match ('expected ' + $script:InstalledFileCount)) -Label 'robocopy precondition STOPs on a wrong source count'
Assert-True -Condition (($script:calls -join '|') -notmatch 'robocopy') -Label 'robocopy precondition STOP fired BEFORE any /MIR'
Remove-Item Function:New-Item -ErrorAction SilentlyContinue
Remove-Item Function:Get-TreeFileCount -ErrorAction SilentlyContinue

# ---- 7. install cfc3d22c WRONG-subtree refusal (round 2, G5/G3) ----------------
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase install') {
        # An install output that carries the candidate identities AND leaks the
        # cfc3d22c subtree - the explicit wrong-subtree guard must catch it.
        return @{ code = 0; stdout = ((Get-GoodInstallStdout) + ' but also ' + $script:WrongSubtree); stderr = '' }
    }
    return @{ code = 0; stdout = ''; stderr = '' }
}
$threw = $false; $msg = ''
try { Step-Install | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'update 5.3' -and $msg -match 'WRONG subtree' -and $msg -match 'cfc3d22c') -Label 'install STOPs on the cfc3d22c wrong subtree'

# ---- 8. lane-1 supervised canary: mode enforcement + no bounded-auto -----------
$threw = $false; $msg = ''
try { Get-LaneMode -LaneNumber '1' -RequestedMode 'limited-auto' | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'supervised one-cycle canary') -Label 'lane 1 rejects a non-supervised mode'
$m1 = Get-LaneMode -LaneNumber '1' -RequestedMode ''
Assert-True -Condition ($m1 -eq 'supervised') -Label 'lane 1 defaults to supervised'
$script:capturedArgs = @()
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    if ($a -match 'status --checkout') { return @{ code = 0; stdout = 'PREFLIGHT'; stderr = '' } }
    if ($a -match 'mrl_launch_draft') { return @{ code = 0; stdout = ''; stderr = '' } }
    if ($a -match 'claude_chain_sha256') { return @{ code = 0; stdout = $script:ChainCheckStop; stderr = '' } }
    return @{ code = 0; stdout = ''; stderr = '' }
}
function Start-Detached { param([string]$LaneNumber, [string[]]$StartArgs, [string]$WorkingDirectory) $script:capturedArgs = $StartArgs; return @{ pid = 7; out = 'o'; err = 'e' } }
Start-LaneFirstLaunch -LaneNumber '1' -Checkout 'C:\SupervisorController' -LaneWorktree 'C:\wt-can' -LanePacketId 'M0-T555' -Mode 'supervised' -Repin $true | Out-Null
$capJoined = ($script:capturedArgs -join ' ')
Assert-True -Condition ($capJoined -match '--mode supervised') -Label 'canary start uses --mode supervised'
Assert-True -Condition ($capJoined -notmatch 'owner-enable-bounded-auto') -Label 'canary start carries NO --owner-enable-bounded-auto'
Assert-True -Condition ($capJoined -match 'max-cycles 1') -Label 'canary start is one cycle'
Assert-True -Condition ($capJoined -match 'repin-cli-identity') -Label 'canary first start repins'

# ---- 9. approve digest missing / not held (round 2) ---------------------------
$script:calls = @()
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    $script:calls += ($FilePath + ' ' + $a)
    if ($a -match 'pending-approvals') { return @{ code = 0; stdout = 'held prompt digest aaaabbbbccccdddd'; stderr = '' } }
    return @{ code = 0; stdout = ''; stderr = '' }
}
$threw = $false; $msg = ''
try { Invoke-ApprovePhase -LaneNumber '1' -LaneWorktree 'C:\wt-can' -LanePacketId 'M0-T555' -RequestedMode '' -Digest '' | Out-Null }
catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'pass -PromptDigest') -Label 'approve STOPs when no digest is given'
Assert-True -Condition (($script:calls -join '|') -notmatch 'resume-pending-prompt') -Label 'approve did NOT resume when no digest given'
$script:calls = @()
$threw = $false; $msg = ''
try { Invoke-ApprovePhase -LaneNumber '1' -LaneWorktree 'C:\wt-can' -LanePacketId 'M0-T555' -RequestedMode '' -Digest 'deadbeefdeadbeef' | Out-Null }
catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'not among the held prompts') -Label 'approve STOPs when the digest is not held'
Assert-True -Condition (($script:calls -join '|') -notmatch 'resume-pending-prompt') -Label 'approve did NOT resume a digest that is not held'

# ---- 10. update config/model immutability guard (round 2) ----------------------
# Run the whole update with valid stubbed outputs, then flip config (run 1) or model
# (run 2) between the before/after snapshots. Every write helper is stubbed.
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase backup') { return @{ code = 0; stdout = 'BACKUP VERIFIED run T controller 200 file(s)'; stderr = '' } }
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase install') { return @{ code = 0; stdout = (Get-GoodInstallStdout); stderr = '' } }
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase verify-manifest') {
        return @{ code = 0; stdout = ("MANIFEST VERIFIED against the accepted source at " + $script:CandidateCommit +
            "`n  covered files " + $script:CoveredFileCount + "; installed files re-compared " + $script:InstalledFileCount); stderr = '' }
    }
    if ($a -match 'print\(len\(m') { return @{ code = 0; stdout = $script:ManifestStop; stderr = '' } }
    if ($a -match 'record-manifest') { return @{ code = 0; stdout = 'recorded'; stderr = '' } }
    if ($a -match 'verify-controller') { return @{ code = 0; stdout = 'controller verified, including the external config.toml binding.'; stderr = '' } }
    if ($a -match 'doctor --live') { return @{ code = 0; stdout = 'live probe VERIFIED'; stderr = '' } }
    if ($a -match 'doctor') { return @{ code = 0; stdout = 'doctor overall PASS'; stderr = '' } }
    if ($FilePath -eq 'robocopy') { return @{ code = 1; stdout = ''; stderr = '' } }   # < 8 = ok
    return @{ code = 0; stdout = ''; stderr = '' }
}
function New-Item { }
function Write-WrapperFile { param([string]$Path, [string]$Content) }
function Ensure-ActivationDir { }
function Assert-SameTree { param([string]$Reference, [string]$Candidate, [string]$Step) }
function Get-CheckoutKey { param([string]$Checkout) return ('a' * 64) }
function Get-TreeFileCount { param([string]$Root) return $script:InstalledFileCount }
$script:Lane3Wrapper = $lane3Fixture
# run 1: config.toml raw hash changes between before (call 1) and after (call 3).
$script:hc = 0
function Get-FileSha256Raw { param([string]$Path) $script:hc = $script:hc + 1; switch ($script:hc) { 1 { 'cfg1' } 2 { 'mdl1' } 3 { 'cfg2' } default { 'mdl1' } } }
$threw = $false; $msg = ''
try { Invoke-UpdatePhase | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'update guard' -and $msg -match 'config.toml changed') -Label 'update guard STOPs when config.toml changes'
# run 2: model_selection.toml raw hash changes between before (call 2) and after (call 4).
$script:hc = 0
function Get-FileSha256Raw { param([string]$Path) $script:hc = $script:hc + 1; switch ($script:hc) { 1 { 'cfg1' } 2 { 'mdl1' } 3 { 'cfg1' } default { 'mdl2' } } }
$threw = $false; $msg = ''
try { Invoke-UpdatePhase | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'update guard' -and $msg -match 'model_selection.toml changed') -Label 'update guard STOPs when model_selection.toml changes'
Remove-Item Function:New-Item -ErrorAction SilentlyContinue
Remove-Item Function:Get-TreeFileCount -ErrorAction SilentlyContinue

# ---- 11. linked-worktree / glob-overlap / packet-id refusals (round 2) ---------
Write-Packet -Id 'M0-T910' -Status 'claimed' -Paths @('services/api/**')
Write-Packet -Id 'M0-T911' -Status 'claimed' -Paths @('services/api/app/x.py')   # under the T910 glob
Write-Packet -Id 'M0-T912' -Status 'claimed' -Paths @('apps/web/**')             # disjoint from T910

$globOverlapPlan = Write-Plan -Name 'globoverlap' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T910'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-b'; packet_id = 'M0-T911'; mode = 'limited-auto' })
$globDisjointPlan = Write-Plan -Name 'globdisjoint' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T910'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-b'; packet_id = 'M0-T912'; mode = 'limited-auto' })
$primaryPlan = Write-Plan -Name 'primary' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T910'; mode = 'limited-auto' })
$subdirPlan = Write-Plan -Name 'subdir' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-T910'; mode = 'limited-auto' })
$badPacketPlan = Write-Plan -Name 'badpacket' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'bad-id'; mode = 'limited-auto' })

function Invoke-Ext { param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    if ($FilePath -eq 'git') { return Resolve-GitStub -ExtArgs $ExtArgs -Kind 'linked' }
    return @{ code = 0; stdout = ''; stderr = '' } }
$rgo = Test-Plan -Path $globOverlapPlan
Assert-True -Condition (-not $rgo.ok -and $rgo.msg -match 'overlapping allowed_paths') -Label 'plan validator REFUSES a glob overlap (dir/** over a file under dir)'
$rgd = Test-Plan -Path $globDisjointPlan
Assert-True -Condition ($rgd.ok) -Label 'plan validator ACCEPTS glob-disjoint allowed_paths'
$rbp = Test-Plan -Path $badPacketPlan
Assert-True -Condition (-not $rbp.ok -and $rbp.msg -match 'not a valid M') -Label 'plan validator REFUSES a non M<n>-T<n> packet id'

function Invoke-Ext { param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    if ($FilePath -eq 'git') { return Resolve-GitStub -ExtArgs $ExtArgs -Kind 'primary' }
    return @{ code = 0; stdout = ''; stderr = '' } }
$rp = Test-Plan -Path $primaryPlan
Assert-True -Condition (-not $rp.ok -and $rp.msg -match 'primary checkout') -Label 'plan validator REFUSES the primary checkout (not a linked worktree)'

function Invoke-Ext { param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    if ($FilePath -eq 'git') { return Resolve-GitStub -ExtArgs $ExtArgs -Kind 'subdir' }
    return @{ code = 0; stdout = ''; stderr = '' } }
$rs = Test-Plan -Path $subdirPlan
Assert-True -Condition (-not $rs.ok -and $rs.msg -match 'not a worktree root') -Label 'plan validator REFUSES a subdirectory of a worktree'

# ---- done ----------------------------------------------------------------------
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
if ($script:failures -gt 0) {
    Write-Output ("test_commission_lanes: " + $script:failures + " assertion failure(s)")
    exit 1
}
Write-Output 'test_commission_lanes: all offline STOP, no-write, wrapper-diff, plan-validator, precondition, install-guard, canary-mode, approve, immutability and linked-worktree/glob/packet-id checks passed'
exit 0
