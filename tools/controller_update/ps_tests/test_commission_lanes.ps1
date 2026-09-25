# test_commission_lanes.ps1 - offline proof of commission_lanes.ps1 (M0-T161;
# D-088-R003/R004). Everything runs offline: the file is dot-sourced with
# -LoadOnly (functions + constants loaded, no phase dispatched), and the ONE
# external-command helper Invoke-Ext plus the tree/launch helpers are stubbed, so
# NO supervisor verb and NO machine change ever run. It proves:
#   1. both .ps1 files parse clean under Windows PowerShell 5.1;
#   2. each STOP throws a plain-English line and halts everything after it
#      (update 5.4 manifest STOP; lane 5.11 chain STOP that prevents the start;
#      check 5.1 config-hash STOP);
#   3. -Phase check performs no write;
#   4. the generated lane-4 wrapper differs from lane 3's ONLY in lane-specific
#      values (checkout path, checkout key, log names, labels) + the ACTIVE-TASK
#      block, which is marked "not yet fed";
#   5. the plan-file validator refuses overlapping allowed_paths, duplicate lane
#      numbers, duplicate worktrees, and unclaimed packets, and accepts a clean plan.

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

# ---- 2a. update 5.4 manifest STOP halts everything after it --------------------
$script:calls = @()
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    $a = ($ExtArgs -join ' ')
    $script:calls += ($FilePath + ' ' + $a)
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase backup') {
        return @{ code = 0; stdout = 'BACKUP VERIFIED run T'; stderr = '' }
    }
    if ($FilePath -eq 'powershell.exe' -and $a -match 'Phase install') {
        return @{ code = 0; stdout = ('INSTALLED from immutable commit ' + $script:CandidateCommit + ' subtree ' + $script:CandidateSubtree + ' files 204'); stderr = '' }
    }
    if ($FilePath -eq 'python' -and $a -match 'print\(len\(m') {
        return @{ code = 0; stdout = '146 deadbeefdeadbeef'; stderr = '' }   # WRONG readback -> 5.4 STOP
    }
    return @{ code = 0; stdout = ''; stderr = '' }
}
function Get-FileSha256Raw { param([string]$Path) return 'stub-hash' }
function Assert-SameTree { param([string]$Reference, [string]$Candidate, [string]$Step) $script:calls += ('same-tree ' + $Candidate) }
function Ensure-ActivationDir { $script:calls += 'ensure-activation-dir' }   # no real machine write
$threw = $false
$msg = ''
try { Invoke-UpdatePhase | Out-Null } catch { $threw = $true; $msg = $_.Exception.Message }
Assert-True -Condition ($threw -and $msg -match 'update 5.4' -and $msg -match 'expected') -Label 'update 5.4 manifest mismatch throws a plain-English STOP'
Assert-True -Condition (($script:calls -join '|') -match 'record-manifest') -Label 'update ran through 5.4 (record-manifest called)'
Assert-True -Condition (($script:calls -join '|') -notmatch 'verify-manifest') -Label 'update 5.5 verify-manifest NEVER ran after the 5.4 STOP'
Assert-True -Condition (($script:calls -join '|') -notmatch 'verify-controller') -Label 'update 5.7 verify-controller NEVER ran after the 5.4 STOP'
Assert-True -Condition (($script:calls -join '|') -notmatch 'robocopy') -Label 'update 5.6 propagation NEVER ran after the 5.4 STOP'
Assert-True -Condition (($script:calls -join '|') -notmatch 'doctor') -Label 'update 5.8/5.9 doctor NEVER ran after the 5.4 STOP'

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
try { Start-LaneFirstLaunch -LaneNumber '2' -Checkout 'C:\SupervisorController2' -LaneWorktree 'C:\wt-x' -LanePacketId 'M0-TX' -Mode 'limited-auto' -Repin $true | Out-Null }
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

# ---- 5. plan-file validator ----------------------------------------------------
$script:Ctl24 = $work   # redirect packet lookups into the sandbox
$tasksDir = Join-Path $work 'project-control\tasks'
New-Item -ItemType Directory -Force -Path $tasksDir | Out-Null
function Write-Packet { param([string]$Id, [string]$Status, [string[]]$Paths)
    $obj = [ordered]@{ task_id = $Id; status = $Status; allowed_paths = $Paths }
    $obj | ConvertTo-Json -Depth 5 | Out-File -FilePath (Join-Path $tasksDir ($Id + '.json')) -Encoding utf8
}
Write-Packet -Id 'M0-PA' -Status 'claimed'    -Paths @('services/api/app/a.py')
Write-Packet -Id 'M0-PB' -Status 'in_progress' -Paths @('apps/web/b.tsx')
Write-Packet -Id 'M0-PC' -Status 'claimed'    -Paths @('services/api/app/a.py')     # overlaps PA
Write-Packet -Id 'M0-PD' -Status 'backlog'    -Paths @('packages/d.py')             # unclaimed
function Invoke-Ext {
    param([string]$FilePath, [string[]]$ExtArgs = @(), [string]$WorkingDirectory = '')
    if (($ExtArgs -join ' ') -match 'rev-parse --show-toplevel') { return @{ code = 0; stdout = 'C:\some\worktree'; stderr = '' } }
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
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-PA'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-b'; packet_id = 'M0-PB'; mode = 'limited-auto' })
$overlapPlan = Write-Plan -Name 'overlap' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-PA'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-c'; packet_id = 'M0-PC'; mode = 'limited-auto' })
$dupLanePlan = Write-Plan -Name 'duplane' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-PA'; mode = 'limited-auto' },
    @{ lane = 2; worktree = 'C:\wt-b'; packet_id = 'M0-PB'; mode = 'limited-auto' })
$dupWtPlan = Write-Plan -Name 'dupwt' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-PA'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-a'; packet_id = 'M0-PB'; mode = 'limited-auto' })
$unclaimedPlan = Write-Plan -Name 'unclaimed' -Lanes @(
    @{ lane = 2; worktree = 'C:\wt-a'; packet_id = 'M0-PA'; mode = 'limited-auto' },
    @{ lane = 3; worktree = 'C:\wt-b'; packet_id = 'M0-PD'; mode = 'limited-auto' })

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

# ---- done ----------------------------------------------------------------------
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
if ($script:failures -gt 0) {
    Write-Output ("test_commission_lanes: " + $script:failures + " assertion failure(s)")
    exit 1
}
Write-Output 'test_commission_lanes: all offline STOP, no-write, wrapper-diff and plan-validator checks passed'
exit 0
