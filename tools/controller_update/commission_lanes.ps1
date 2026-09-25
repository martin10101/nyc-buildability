# commission_lanes.ps1 - the OWNER-RUN, fail-closed five-lane commissioning
# helper (M0-T161; D-088-R003/R004/R007). It turns the accepted
# M0-T159-recertification.md section 5 sequence - the B-026 owner-typed
# commissioning of the recertified controller - into a few one-line commands
# with every STOP check built in, extended to stand up and verify lanes 4 and 5.
#
# The producer of this file NEVER runs it. The OWNER runs it in the orchestrator
# session, one phase at a time, following project-control/reports/M0-T161-owner-guide.md.
#
# Phases (each maps to the recertification report's section 5):
#   -Phase check    read-only preconditions (5.1) + a plan of what update will do,
#                   including free disk space (D-088-R006). Writes nothing.
#   -Phase update   the recertification 5.2-5.10 verbatim (backup, install,
#                   record-manifest with the "147 55dc7135..." STOP, verify-manifest,
#                   propagation to lanes 2-5 with lanes 4-5 STOOD UP, verify-controller
#                   from all five copies + wt-controller-src, doctor, doctor --live,
#                   post-update checks). Touches config.toml / model_selection.toml /
#                   the activation manifest ONLY via the 5.4 record-manifest re-record.
#   -Phase lane     section 5.11 for ONE lane: status, clear-recovery only on
#                   PAUSED_RECOVERY, a fresh launch manifest, the "2.1.281 946eb509..."
#                   STOP, then a DETACHED start with --repin-cli-identity. Lane 1 is the
#                   supervised one-cycle canary (5.12).
#   -Phase approve  the canary's prompt-digest approval, then the re-start WITHOUT repin.
#   -Phase lanes    lanes 2-5 from an orchestrator-written plan file, VALIDATED first
#                   (claimed/in_progress packets, git worktrees, distinct lanes and
#                   worktrees, pairwise-disjoint allowed_paths), started >= 60 s apart.
#
# DESIGN (D-088; recertification section 5): PowerShell 5.1; Set-StrictMode +
# $ErrorActionPreference 'Stop'; every pinned path/digest/version/SHA is a named
# constant below; every external command runs through the ONE Invoke-Ext helper
# that checks $LASTEXITCODE (the offline tests stub it); no Invoke-Expression and
# no caller text interpolated into a command string; every STOP throws a
# plain-English line that names the step and the expected value and runs nothing
# further.

[CmdletBinding()]
param(
    # Validated in the dispatcher (not by [ValidateSet]) so the empty defaults used
    # when a phase-specific argument is omitted never trip binding-time validation.
    [string]$Phase = '',
    [string]$Lane = '',
    [string]$Worktree = '',
    [string]$PacketId = '',
    [string]$Mode = '',
    [string]$PromptDigest = '',
    [string]$PlanFile = '',
    # Test hook (offline ps_tests): dot-source the file to load its functions and
    # constants WITHOUT dispatching a phase, then stub Invoke-Ext / the tree and
    # launch helpers. Never used by the owner.
    [switch]$LoadOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ============================================================================
# Named constants - every pinned value from M0-T159-recertification.md section 5
# ============================================================================

# Paths (recertification 5.0-5.11; source_binding.json).
$script:PackRepo        = 'C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack'
$script:Ctl24           = 'C:\Users\MLFLL\Downloads\nyc-zoning\ctl24'
$script:UpdateScript    = Join-Path $script:Ctl24 'tools\controller_update\update_controller_from_candidate.ps1'
$script:SourceBinding   = Join-Path $script:Ctl24 'tools\controller_update\source_binding.json'
$script:SourceWorktree  = 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src'
$script:A1Checkout      = 'C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063'
$script:ConfigPath      = 'C:\Program Files\SupervisorConfig\config.toml'
$script:ModelSelection  = 'C:\SupervisorController\model_selection.toml'
$script:ManifestPath    = Join-Path $env:LOCALAPPDATA 'NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json'
$script:ClaudeExe       = 'C:\Users\MLFLL\.local\bin\claude.exe'
$script:CodexExe        = 'C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd'
$script:AutostartLogDir = Join-Path $env:LOCALAPPDATA 'NYCBuildabilitySupervisor\autostart-logs'
$script:Lane3Wrapper    = 'C:\SupervisorController3\autostart-launch.ps1'

# Pinned identities (recertification 5.0). Long hashes live here, never retyped.
$script:CandidateCommit    = 'a3f24ff3825c126c038f59b1ea6d2352f29d724a'
$script:CandidateTree      = '82432361540c3c2a11c55ffa3d6d485426cd45f7'
$script:CandidateSubtree   = '9c0b14eaa56ce32d241c77f789266035b584380c'
$script:WrongSubtree       = '11d43515656120caae473cca5d6a833a57e5ea35'   # cfc3d22c - the NOT-install-source (5.0)
$script:ManifestStop       = '147 55dc71350b9f6b0a57e8e4121c62a9d2a4fe8914eea8bcd1ca4acdddbcec74b9'   # 5.4 STOP
$script:ConfigRawHash      = '610ce9d5cdf50dbf0710424c232ecc7b600c688e419d71204cddcbb9055270e5'         # 5.1 Get-FileHash raw
$script:ConfigLfHash       = '34f4fe90a1ecc2f4544b4ca7ff33fd08af0923cdf3c96d8c462acb8fe7b2a62e'         # manifest-bound LF
$script:ChainCheckStop     = '2.1.281 946eb5098cc8a56a189b8f0e3f083b6a8569030431252c9bb0ab4203b23bfff1' # 5.11 STOP
$script:ClaudeVersion      = '2.1.281'
$script:InstalledFileCount = 204   # 5.3 "files 204 byte-identical"
$script:ManifestFileCount  = 147   # 5.4 manifest entries
$script:CoveredFileCount   = 146   # 5.5 "covered files 146"

# Lanes. Each lane has its OWN runtime identity via a distinct --checkout
# (D-088-R001/R003). Lanes 1-3 exist; lanes 4-5 are stood up by -Phase update.
$script:LaneCheckout = @{
    '1' = 'C:\SupervisorController'
    '2' = 'C:\SupervisorController2'
    '3' = 'C:\SupervisorController3'
    '4' = 'C:\SupervisorController4'
    '5' = 'C:\SupervisorController5'
}
$script:ExistingLanes = @('1', '2', '3')
$script:NewLanes      = @('4', '5')
$script:AllLanes      = @('1', '2', '3', '4', '5')

# Policy numbers.
$script:MinFreeGiB         = 1.0   # D-088-R006 floor: below this = machine contention STOP
$script:LaneSpacingSeconds = 60    # D-088-R004: lanes 2-5 at least 60 s apart

# ============================================================================
# The ONE external-command helper (the offline tests stub this).
# ============================================================================

function Invoke-Ext {
    # Run one external command by RAW exit code, never a pipeline (so $LASTEXITCODE
    # is trustworthy on PowerShell 5.1). stdout/stderr are captured via temp files.
    # A command that never produces an exit code fails closed. Callers judge the
    # returned code/stdout against their step's expectation and STOP on a mismatch.
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ExtArgs = @(),
        [string]$WorkingDirectory = ''
    )
    # Function-scoped: native stderr must never become a terminating error before
    # the raw exit code is read (the update script uses the same discipline). The
    # exit code alone judges success; a missing one fails closed below.
    $ErrorActionPreference = 'Continue'
    $so = [System.IO.Path]::GetTempFileName()
    $se = [System.IO.Path]::GetTempFileName()
    $global:LASTEXITCODE = $null
    $invocationError = ''
    $pushed = $false
    try {
        if ($WorkingDirectory -ne '') { Push-Location -LiteralPath $WorkingDirectory; $pushed = $true }
        & $FilePath @ExtArgs 1>$so 2>$se
    } catch {
        $invocationError = $_.Exception.Message
    } finally {
        if ($pushed) { Pop-Location }
    }
    $code = $global:LASTEXITCODE
    $stdout = ''
    $stderr = ''
    if (Test-Path -LiteralPath $so) { $stdout = ([System.IO.File]::ReadAllText($so)).Trim() }
    if (Test-Path -LiteralPath $se) { $stderr = ([System.IO.File]::ReadAllText($se)).Trim() }
    Remove-Item -LiteralPath $so, $se -Force -ErrorAction SilentlyContinue
    if ($null -eq $code) {
        throw ("STOP: the command '" + $FilePath + ' ' + ($ExtArgs -join ' ') +
            "' produced no exit code (fail closed). " + $invocationError)
    }
    return @{ code = [int]$code; stdout = $stdout; stderr = $stderr }
}

# ============================================================================
# Small helpers (each is separately stubbable in the offline tests).
# ============================================================================

function Get-FileSha256Raw {
    # Get-FileHash raw-byte SHA-256, lower-cased for comparison.
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-FreeGiB {
    # Free space on the drive holding $Path, in GiB (read-only).
    param([string]$Path)
    $root = [System.IO.Path]::GetPathRoot([System.IO.Path]::GetFullPath($Path))
    $drive = New-Object System.IO.DriveInfo($root)
    return [math]::Round($drive.AvailableFreeSpace / 1GB, 2)
}

function Get-BoundCommit {
    # The commit the checked-in source binding pins (M0-T160 re-pinned it to the
    # recertified candidate). A read-only precondition: it must equal the candidate.
    if (-not (Test-Path -LiteralPath $script:SourceBinding)) {
        throw ("STOP [check]: the source binding is missing at '" + $script:SourceBinding + "'")
    }
    $binding = Get-Content -LiteralPath $script:SourceBinding -Raw | ConvertFrom-Json
    if ($null -eq $binding.PSObject.Properties['commit_sha']) {
        throw 'STOP [check]: the source binding has no commit_sha'
    }
    return [string]$binding.commit_sha
}

function Get-RuntimeDirFor {
    # The controller's OWN runtime directory function, invoked through python from
    # wt-controller-src - never re-implemented here (D-066-R001).
    param([string]$Checkout)
    $py = ("from tools.agent_supervisor.durable_state import runtime_dir_for; " +
        "print(runtime_dir_for(r'" + $Checkout + "'))")
    $r = Invoke-Ext -FilePath 'python' -ExtArgs @('-c', $py) -WorkingDirectory $script:SourceWorktree
    if ($r.code -ne 0 -or $r.stdout -eq '') {
        throw ("STOP [check]: could not compute the runtime directory for '" + $Checkout +
            "' (python exit " + $r.code + "): " + $r.stderr)
    }
    return $r.stdout.Trim()
}

function Get-CheckoutKey {
    # The controller's OWN checkout_key, invoked through python from
    # wt-controller-src - never re-implemented (D-066-R001). Returns the 64-hex key.
    param([string]$Checkout)
    $py = ("from tools.agent_supervisor.durable_state import checkout_key; " +
        "print(checkout_key(r'" + $Checkout + "'))")
    $r = Invoke-Ext -FilePath 'python' -ExtArgs @('-c', $py) -WorkingDirectory $script:SourceWorktree
    $key = $r.stdout.Trim()
    if ($r.code -ne 0 -or $key -notmatch '^[0-9a-f]{64}$') {
        throw ("STOP [update 5.6]: could not compute the checkout key for '" + $Checkout +
            "' (python exit " + $r.code + "): " + $r.stderr)
    }
    return $key
}

function Assert-SameTree {
    # Byte-identical tree proof (recertification 5.2/5.6): every file under
    # $Candidate must match $Reference by raw SHA-256, ignoring cache dirs. STOP on
    # any mismatch. The offline tests stub this (they prove the STOP wiring, not
    # the file walk, which the update script's own ps_tests already prove).
    param([string]$Reference, [string]$Candidate, [string]$Step)
    $ref = @(Get-TreeHashList -Root $Reference)
    $cand = @(Get-TreeHashList -Root $Candidate)
    if ($ref.Count -eq 0 -or $cand.Count -eq 0) {
        throw ("STOP [" + $Step + "]: empty tree comparing '" + $Reference + "' and '" + $Candidate + "'")
    }
    $diff = @(Compare-Object -ReferenceObject $ref -DifferenceObject $cand)
    if ($diff.Count -gt 0) {
        throw ("STOP [" + $Step + "]: BYTE MISMATCH - '" + $Candidate +
            "' is not byte-identical to '" + $Reference + "' (" + $diff.Count + " difference(s))")
    }
    Write-Output ("  " + $Candidate + ": " + $cand.Count + " files byte-identical to " + $Reference)
}

function Get-TreeHashList {
    param([string]$Root)
    $r = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
    return @(Get-ChildItem -LiteralPath $r -Recurse -File -Force |
        Where-Object { $_.FullName -notmatch '\\(__pycache__|\.pytest_cache)\\' } |
        ForEach-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash + '  ' + $_.FullName.Substring($r.Length + 1) } |
        Sort-Object)
}

function Start-Detached {
    # Launch a supervisor start DETACHED so it survives the owner's session, hidden,
    # with stdout/stderr to named logs under the autostart-logs directory. Returns
    # the PID and the two log paths. The offline tests stub this (no real launch).
    param([string]$LaneNumber, [string[]]$StartArgs, [string]$WorkingDirectory)
    if (-not (Test-Path -LiteralPath $script:AutostartLogDir)) {
        New-Item -ItemType Directory -Force -Path $script:AutostartLogDir | Out-Null
    }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $out = Join-Path $script:AutostartLogDir ("commission-lane" + $LaneNumber + "-" + $stamp + ".out.txt")
    $err = Join-Path $script:AutostartLogDir ("commission-lane" + $LaneNumber + "-" + $stamp + ".err.txt")
    $proc = Start-Process -FilePath 'python' -ArgumentList $StartArgs -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
    return @{ pid = $proc.Id; out = $out; err = $err }
}

function Start-LaneSpacing {
    # Enforce the >= 60 s gap between lane starts (D-088-R004). The offline tests
    # stub this so no real sleep runs.
    param([int]$Seconds)
    Start-Sleep -Seconds $Seconds
}

# ============================================================================
# Phase: check (read-only preconditions 5.1 + the update plan). No writes.
# ============================================================================

function Invoke-CheckPhase {
    Write-Output '== commission check (read-only preconditions, recertification 5.1) =='

    # The install source must already be re-pinned to the recertified candidate.
    $bound = Get-BoundCommit
    if ($bound -ne $script:CandidateCommit) {
        throw ("STOP [check]: the source binding pins '" + $bound + "', not the recertified candidate '" +
            $script:CandidateCommit + "' - the M0-T160 re-pin is not in place")
    }
    Write-Output ("  source binding pins the recertified candidate " + $script:CandidateCommit)

    # Every existing lane must be STOPPED (no supervisor.lock): 5.3 removes and
    # re-creates wt-controller-src, from which every lane runs its code.
    foreach ($lane in $script:ExistingLanes) {
        $checkout = $script:LaneCheckout[$lane]
        $runtimeDir = Get-RuntimeDirFor -Checkout $checkout
        $lock = Join-Path $runtimeDir 'supervisor.lock'
        if (Test-Path -LiteralPath $lock) {
            throw ("STOP [check 5.1]: lane " + $lane + " (" + $checkout +
                ") still holds a supervisor.lock at '" + $lock + "' - stop it before commissioning")
        }
        Write-Output ("  lane " + $lane + " (" + $checkout + "): no supervisor.lock - stopped")
    }

    # Journal status (5.1): informational (the controller journal may read
    # PAUSED_RECOVERY per B-026; 5.11 clears it). Surfaced, not a STOP.
    $ctrlStatus = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', 'status') `
        -WorkingDirectory 'C:\SupervisorController'
    Write-Output ('  controller journal status (informational): ' + ($ctrlStatus.stdout -replace '\s+', ' '))
    $a1Status = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', 'status', '--checkout', $script:A1Checkout) `
        -WorkingDirectory 'C:\SupervisorController'
    Write-Output ('  A1 journal status (expect PREFLIGHT, 0 pending): ' + ($a1Status.stdout -replace '\s+', ' '))

    # Protected config identity (5.1): any other value is a STOP.
    $rawHash = Get-FileSha256Raw -Path $script:ConfigPath
    if ($rawHash -ne $script:ConfigRawHash) {
        throw ("STOP [check 5.1]: protected config.toml raw SHA-256 is '" + $rawHash +
            "', expected '" + $script:ConfigRawHash + "' - do not proceed")
    }
    Write-Output ('  protected config.toml raw SHA-256 matches the expected B-025-edited value')

    # Free disk space (D-088-R006): report; below the floor is machine contention -> STOP.
    $freeGiB = Get-FreeGiB -Path 'C:\SupervisorController'
    Write-Output ('  free space on C: ' + $freeGiB + ' GiB (five lanes add roughly 0.5 GiB plus logs)')
    if ($freeGiB -lt $script:MinFreeGiB) {
        throw ("STOP [check]: only " + $freeGiB + " GiB free on C: (floor " + $script:MinFreeGiB +
            " GiB) - this is machine contention (D-088-R006/R001); reduce the lane count and tell the owner")
    }

    Write-Output ''
    Write-Output 'PLAN - what -Phase update will do (recertification 5.2-5.10):'
    Write-Output '  5.2 verified backup of the live controller + prove lanes 2/3 equal it'
    Write-Output ('  5.3 install the recertified candidate ' + $script:CandidateCommit + ' (handles source_worktree_exists)')
    Write-Output ('  5.4 record the activation manifest; STOP unless it reads "' + $script:ManifestStop + '"')
    Write-Output '  5.5 prove the manifest matches the accepted source'
    Write-Output '  5.6 propagate the certified tree to lanes 2-5 (STAND UP lanes 4 and 5) + prove all five'
    Write-Output '  5.7 verify-controller from all five copies + wt-controller-src'
    Write-Output '  5.8 full doctor; 5.9 doctor --live; 5.10 post-update state checks'
    Write-Output ''
    Write-Output 'CHECK PASSED - preconditions met. Next: run -Phase update.'
}

# ============================================================================
# Phase: update (recertification 5.2-5.10 + lanes 4-5 stand-up).
# ============================================================================

function Invoke-UpdatePhase {
    Write-Output '== commission update (recertification 5.2-5.10) =='

    # Immutability guard (DESIGN): update must not change config.toml or
    # model_selection.toml at all, nor the activation manifest except via 5.4.
    $configBefore = Get-FileSha256Raw -Path $script:ConfigPath
    $modelBefore  = Get-FileSha256Raw -Path $script:ModelSelection

    Step-Backup            # 5.2
    Step-Install           # 5.3
    Step-RecordManifest    # 5.4
    Step-VerifyManifest    # 5.5
    Step-Propagate         # 5.6 (lanes 2-5; lanes 4-5 stood up)
    Step-VerifyController   # 5.7
    Step-Doctor            # 5.8
    Step-DoctorLive        # 5.9
    Step-PostChecks        # 5.10

    $configAfter = Get-FileSha256Raw -Path $script:ConfigPath
    $modelAfter  = Get-FileSha256Raw -Path $script:ModelSelection
    if ($configAfter -ne $configBefore) {
        throw 'STOP [update guard]: config.toml changed during update - it must never be modified'
    }
    if ($modelAfter -ne $modelBefore) {
        throw 'STOP [update guard]: model_selection.toml changed during update - it must never be modified'
    }
    Write-Output ''
    Write-Output 'UPDATE PASSED - controller recertified and propagated to all five lanes.'
    Write-Output 'Next: run -Phase lane -Lane 1 (the supervised canary).'
}

function Invoke-UpdateScriptPhase {
    # Run one -Phase of the checked-in update transaction script through Invoke-Ext.
    param([string]$UpdatePhase)
    return Invoke-Ext -FilePath 'powershell.exe' `
        -ExtArgs @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $script:UpdateScript, '-Phase', $UpdatePhase)
}

function Step-Backup {
    Write-Output '-- 5.2 verified backup'
    $r = Invoke-UpdateScriptPhase -UpdatePhase 'backup'
    if ($r.code -ne 0 -or $r.stdout -notmatch 'BACKUP VERIFIED') {
        throw ("STOP [update 5.2]: -Phase backup did not report BACKUP VERIFIED (exit " + $r.code + "): " +
            (($r.stdout + ' ' + $r.stderr).Trim()))
    }
    Write-Output ('  ' + (($r.stdout -split "`n")[0]).Trim())
    foreach ($lane in @('2', '3')) {
        Assert-SameTree -Reference (Join-Path 'C:\SupervisorController' 'tools\agent_supervisor') `
            -Candidate (Join-Path $script:LaneCheckout[$lane] 'tools\agent_supervisor') -Step 'update 5.2'
    }
}

function Step-Install {
    Write-Output '-- 5.3 install the recertified candidate'
    $r = Invoke-UpdateScriptPhase -UpdatePhase 'install'
    if ($r.code -ne 0 -and $r.stdout -match 'REFUSED source_worktree_exists') {
        # Documented handling (recertification 5.3 / runbook section 4): remove the
        # stale source worktree, then re-run the same install.
        Write-Output '  install refused source_worktree_exists - removing the stale source worktree and retrying'
        $rm = Invoke-Ext -FilePath 'git' -ExtArgs @('-C', $script:PackRepo, 'worktree', 'remove', '--force', $script:SourceWorktree)
        if ($rm.code -ne 0) {
            throw ('STOP [update 5.3]: could not remove the stale source worktree: ' + $rm.stderr)
        }
        $r = Invoke-UpdateScriptPhase -UpdatePhase 'install'
    }
    if ($r.code -ne 0 -or $r.stdout -notmatch 'INSTALLED from immutable commit') {
        throw ("STOP [update 5.3]: -Phase install did not report INSTALLED (exit " + $r.code + "): " +
            (($r.stdout + ' ' + $r.stderr).Trim()))
    }
    # Identity guard (5.3): the printed commit/tree/subtree must be the candidate,
    # never the cfc3d22c subtree.
    if ($r.stdout -notmatch [regex]::Escape($script:CandidateCommit)) {
        throw ('STOP [update 5.3]: install did not report the candidate commit ' + $script:CandidateCommit)
    }
    if ($r.stdout -notmatch [regex]::Escape($script:CandidateSubtree)) {
        throw ('STOP [update 5.3]: install did not report the candidate subtree ' + $script:CandidateSubtree)
    }
    if ($r.stdout -match [regex]::Escape($script:WrongSubtree)) {
        throw ('STOP [update 5.3]: install reported the WRONG subtree ' + $script:WrongSubtree + ' (cfc3d22c) - not the certified candidate')
    }
    Write-Output ('  installed candidate ' + $script:CandidateCommit + ', subtree ' + $script:CandidateSubtree)
}

function Ensure-ActivationDir {
    # Create the certified activation directory if absent (runbook section 5). A
    # write, but a legitimate part of the update phase; the offline tests stub it.
    $dir = Split-Path -Parent $script:ManifestPath
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

function Step-RecordManifest {
    Write-Output '-- 5.4 record the activation manifest'
    Ensure-ActivationDir
    $rec = Invoke-Ext -FilePath 'python' `
        -ExtArgs @('-m', 'tools.agent_supervisor', 'record-manifest', '--config', $script:ConfigPath, '--out', $script:ManifestPath) `
        -WorkingDirectory 'C:\SupervisorController'
    if ($rec.code -ne 0) {
        throw ('STOP [update 5.4]: record-manifest failed (exit ' + $rec.code + '): ' + $rec.stderr)
    }
    # record-manifest prints only 16 hex digits, so read the file back (5.4).
    $readback = ("import json,os; m=json.load(open(os.path.expandvars(r'" + $script:ManifestPath +
        "'))); print(len(m['files']), m['manifest_digest'])")
    $r = Invoke-Ext -FilePath 'python' -ExtArgs @('-c', $readback) -WorkingDirectory 'C:\SupervisorController'
    $got = $r.stdout.Trim()
    if ($r.code -ne 0 -or $got -ne $script:ManifestStop) {
        throw ("STOP [update 5.4]: the manifest reads '" + $got + "', expected '" + $script:ManifestStop +
            "' - wrong tree installed or the config changed; roll back per runbook section 10")
    }
    Write-Output ('  manifest recorded: ' + $got)
}

function Step-VerifyManifest {
    Write-Output '-- 5.5 prove the manifest matches the accepted source'
    $r = Invoke-UpdateScriptPhase -UpdatePhase 'verify-manifest'
    if ($r.code -ne 0 -or $r.stdout -notmatch 'MANIFEST VERIFIED against the accepted source') {
        throw ("STOP [update 5.5]: verify-manifest did not report MANIFEST VERIFIED (exit " + $r.code + "): " +
            (($r.stdout + ' ' + $r.stderr).Trim()))
    }
    Write-Output ('  ' + (($r.stdout -split "`n")[0]).Trim())
}

function Step-Propagate {
    Write-Output '-- 5.6 propagate the certified tree to lanes 2-5 (stand up lanes 4 and 5)'
    $certifiedTree = Join-Path 'C:\SupervisorController' 'tools\agent_supervisor'

    # Stand up lanes 4 and 5: folder, mrl folder, and a wrapper derived from lane 3.
    $lane3Content = Get-Content -LiteralPath $script:Lane3Wrapper -Raw
    foreach ($lane in $script:NewLanes) {
        $checkout = $script:LaneCheckout[$lane]
        New-Item -ItemType Directory -Force -Path (Join-Path $checkout 'tools\agent_supervisor') | Out-Null
        New-Item -ItemType Directory -Force -Path (Join-Path $checkout 'mrl') | Out-Null
        $key = Get-CheckoutKey -Checkout $checkout
        $wrapperText = New-LaneWrapperContent -Lane3Content $lane3Content -LaneNumber $lane -CheckoutKey $key
        [System.IO.File]::WriteAllText((Join-Path $checkout 'autostart-launch.ps1'), $wrapperText)
        Write-Output ('  lane ' + $lane + ' stood up at ' + $checkout + ' (checkout key ' + $key.Substring(0, 12) + '..., ACTIVE-TASK block: not yet fed)')
    }

    # Mirror the certified tree into lanes 2-5.
    foreach ($lane in @('2', '3', '4', '5')) {
        $dst = Join-Path $script:LaneCheckout[$lane] 'tools\agent_supervisor'
        $rc = Invoke-Ext -FilePath 'robocopy' -ExtArgs @($certifiedTree, $dst, '/MIR',
            '/XD', '__pycache__', '.pytest_cache', '/R:0', '/W:0', '/NP', '/NFL', '/NDL')
        if ($rc.code -ge 8) {
            throw ('STOP [update 5.6]: robocopy into ' + $dst + ' failed, raw exit ' + $rc.code)
        }
        Write-Output ('  ' + $dst + ': robocopy raw exit ' + $rc.code)
    }

    # Prove every copy that runs code is byte-identical to wt-controller-src.
    $srcTree = Join-Path $script:SourceWorktree 'tools\agent_supervisor'
    foreach ($lane in $script:AllLanes) {
        Assert-SameTree -Reference $srcTree -Candidate (Join-Path $script:LaneCheckout[$lane] 'tools\agent_supervisor') -Step 'update 5.6'
    }
}

function Step-VerifyController {
    Write-Output '-- 5.7 verify-controller from every copy that runs code'
    $dirs = @()
    foreach ($lane in $script:AllLanes) { $dirs += $script:LaneCheckout[$lane] }
    $dirs += $script:SourceWorktree
    foreach ($dir in $dirs) {
        $r = Invoke-Ext -FilePath 'python' `
            -ExtArgs @('-m', 'tools.agent_supervisor', 'verify-controller', '--manifest', $script:ManifestPath, '--config', $script:ConfigPath) `
            -WorkingDirectory $dir
        if ($r.code -ne 0 -or $r.stdout -notmatch 'controller verified, including the external config.toml binding') {
            throw ("STOP [update 5.7]: verify-controller FAILED from " + $dir + " (exit " + $r.code + "): " +
                (($r.stdout + ' ' + $r.stderr).Trim()))
        }
        Write-Output ('  verified from ' + $dir)
    }
}

function Step-Doctor {
    Write-Output '-- 5.8 full doctor'
    $r = Invoke-Ext -FilePath 'python' -ExtArgs @(
        '-m', 'tools.agent_supervisor', 'doctor',
        '--checkout', $script:A1Checkout,
        '--config', $script:ConfigPath,
        '--model-selection', $script:ModelSelection,
        '--manifest', $script:ManifestPath) -WorkingDirectory 'C:\SupervisorController'
    if ($r.code -ne 0 -or $r.stdout -notmatch 'PASS') {
        throw ("STOP [update 5.8]: doctor did not report overall PASS (exit " + $r.code + "): " +
            (($r.stdout + ' ' + $r.stderr).Trim()))
    }
    Write-Output '  doctor overall PASS'
}

function Step-DoctorLive {
    Write-Output '-- 5.9 bounded live probe (doctor --live)'
    $r = Invoke-Ext -FilePath 'python' -ExtArgs @(
        '-m', 'tools.agent_supervisor', 'doctor', '--live',
        '--checkout', $script:A1Checkout,
        '--config', $script:ConfigPath,
        '--model-selection', $script:ModelSelection,
        '--manifest', $script:ManifestPath,
        '--claude-executable', $script:ClaudeExe) -WorkingDirectory 'C:\SupervisorController'
    if ($r.code -ne 0 -or $r.stdout -notmatch 'VERIFIED') {
        throw ("STOP [update 5.9]: doctor --live did not record VERIFIED (exit " + $r.code + "): " +
            (($r.stdout + ' ' + $r.stderr).Trim()))
    }
    Write-Output '  doctor --live VERIFIED'
}

function Step-PostChecks {
    Write-Output '-- 5.10 post-update state checks (informational)'
    foreach ($verb in @('status', 'recovery-status', 'pending-approvals')) {
        $r = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', $verb, '--checkout', $script:A1Checkout) `
            -WorkingDirectory 'C:\SupervisorController'
        Write-Output ('  ' + $verb + ': ' + ($r.stdout -replace '\s+', ' '))
    }
}

# ============================================================================
# Lane wrapper generation for lanes 4 and 5 (derived from lane 3; only
# lane-specific values + the ACTIVE-TASK block change).
# ============================================================================

function New-LaneWrapperContent {
    param(
        [Parameter(Mandatory = $true)][string]$Lane3Content,
        [ValidateSet('4', '5')][string]$LaneNumber,
        [Parameter(Mandatory = $true)][string]$CheckoutKey
    )
    if ($CheckoutKey -notmatch '^[0-9a-f]{64}$') {
        throw ("lane " + $LaneNumber + " checkout key is not a 64-hex value: '" + $CheckoutKey + "'")
    }
    if ($Lane3Content -match "(?m)^\`$CheckoutKey\s*=\s*'([0-9a-f]{64})'") {
        $lane3Key = $Matches[1]
    } else {
        throw 'could not find lane 3 checkout key assignment in the reference wrapper'
    }
    $out = $Lane3Content
    # Lane-specific values ONLY: checkout key, checkout path, log names, labels.
    $out = $out.Replace($lane3Key, $CheckoutKey)
    $out = $out.Replace('SupervisorController3', ('SupervisorController' + $LaneNumber))
    $out = $out.Replace('autostart3-', ('autostart' + $LaneNumber + '-'))
    $out = $out.Replace('supervisor-3', ('supervisor-' + $LaneNumber))
    $out = $out.Replace('INSTANCE 3', ('INSTANCE ' + $LaneNumber))
    # The ACTIVE-TASK block: marked "not yet fed" (task inputs blanked, so an
    # accidental launch fails closed rather than reusing lane 3's task).
    $out = Set-NotYetFedBlock -Content $out -LaneNumber $LaneNumber
    return $out
}

function Set-NotYetFedBlock {
    param([string]$Content, [string]$LaneNumber)
    $lines = $Content -split "`r?`n"
    $startIdx = -1
    $endIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($startIdx -lt 0 -and $lines[$i] -match '^# ---- ACTIVE-TASK block') { $startIdx = $i; continue }
        if ($startIdx -ge 0 -and $lines[$i] -match '^# -{10,}\s*$') { $endIdx = $i; break }
    }
    if ($startIdx -lt 0 -or $endIdx -lt 0) {
        throw 'could not locate the ACTIVE-TASK block markers in the reference wrapper'
    }
    $py = ''
    $workdir = ''
    for ($i = $startIdx; $i -le $endIdx; $i++) {
        if ($lines[$i] -match "^\`$Py\s*=\s*'(.+)'") { $py = $Matches[1] }
        if ($lines[$i] -match "^\`$WorkDir\s*=\s*'(.+)'") { $workdir = $Matches[1] }
    }
    if ($py -eq '' -or $workdir -eq '') {
        throw 'could not extract $Py / $WorkDir from the reference ACTIVE-TASK block'
    }
    $block = @(
        '# ---- ACTIVE-TASK block (orchestrator-maintained) --------------------------',
        ('# NOT YET FED - lane ' + $LaneNumber + ' stood up by the M0-T161 commissioning. The'),
        '# orchestrator fills in the task packet, repo/worktree, branch and run-id',
        '# before this lane is launched; until then it dispatches nothing.',
        ('$Py        = ' + "'" + $py + "'"),
        ('$WorkDir   = ' + "'" + $workdir + "'"),
        "`$TaskPacket= 'NOT-YET-FED'",
        "`$Repo      = 'NOT-YET-FED'",
        "`$Branch    = 'NOT-YET-FED'",
        ('$RunId     = ' + "'NOT-YET-FED-lane" + $LaneNumber + "'"),
        '# ---------------------------------------------------------------------------'
    )
    $new = @()
    if ($startIdx -gt 0) { $new += $lines[0..($startIdx - 1)] }
    $new += $block
    if ($endIdx -lt ($lines.Count - 1)) { $new += $lines[($endIdx + 1)..($lines.Count - 1)] }
    return ($new -join "`r`n")
}

# ============================================================================
# Phase: lane (recertification 5.11 for one lane; lane 1 = supervised canary).
# ============================================================================

function Get-LaneMode {
    param([string]$LaneNumber, [string]$RequestedMode)
    if ($LaneNumber -eq '1') {
        if ($RequestedMode -ne '' -and $RequestedMode -ne 'supervised') {
            throw ("STOP [lane]: lane 1 is the supervised one-cycle canary; -Mode '" + $RequestedMode + "' is not allowed")
        }
        return 'supervised'
    }
    if ($RequestedMode -eq '') {
        throw 'STOP [lane]: -Mode is required for lanes 2-5 (supervised or limited-auto)'
    }
    if ($RequestedMode -notin @('supervised', 'limited-auto')) {
        throw ("STOP [lane]: -Mode '" + $RequestedMode + "' is not valid (use supervised or limited-auto)")
    }
    return $RequestedMode
}

function Invoke-LanePhase {
    param([string]$LaneNumber, [string]$LaneWorktree, [string]$LanePacketId, [string]$RequestedMode)
    if ($LaneNumber -notin @('1', '2', '3', '4', '5')) {
        throw 'STOP [lane]: -Lane must be one of 1..5'
    }
    if ($LaneWorktree -eq '' -or $LanePacketId -eq '') {
        throw 'STOP [lane]: -Worktree and -PacketId are required for -Phase lane'
    }
    $mode = Get-LaneMode -LaneNumber $LaneNumber -RequestedMode $RequestedMode
    $checkout = $script:LaneCheckout[$LaneNumber]
    $canary = ''
    if ($LaneNumber -eq '1') { $canary = ' (supervised one-cycle CANARY)' }
    Write-Output ('== commission lane ' + $LaneNumber + $canary + ' - recertification 5.11 ==')

    Start-LaneFirstLaunch -LaneNumber $LaneNumber -Checkout $checkout -LaneWorktree $LaneWorktree `
        -LanePacketId $LanePacketId -Mode $mode -Repin $true | Out-Null
}

function Start-LaneFirstLaunch {
    # The per-lane 5.11 sequence: status, clear-recovery only on PAUSED_RECOVERY, a
    # fresh launch manifest, the "2.1.281 946eb509..." STOP, then a DETACHED start.
    param([string]$LaneNumber, [string]$Checkout, [string]$LaneWorktree, [string]$LanePacketId, [string]$Mode, [bool]$Repin)

    # (2) status
    $status = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', 'status', '--checkout', $Checkout) `
        -WorkingDirectory $Checkout
    if ($status.code -ne 0) {
        throw ('STOP [lane 5.11]: status failed for ' + $Checkout + ' (exit ' + $status.code + '): ' + $status.stderr)
    }
    Write-Output ('  status: ' + ($status.stdout -replace '\s+', ' '))

    # (3) clear-recovery ONLY if PAUSED_RECOVERY
    if ($status.stdout -match 'PAUSED_RECOVERY') {
        $cr = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', 'clear-recovery', '--checkout', $Checkout) `
            -WorkingDirectory $Checkout
        if ($cr.code -ne 0) {
            throw ('STOP [lane 5.11]: clear-recovery failed for ' + $Checkout + ' (exit ' + $cr.code + '): ' + $cr.stderr)
        }
        Write-Output '  PAUSED_RECOVERY cleared'
    }

    # (4) draft a fresh launch manifest and check the pinned chain
    $manifestOut = Join-Path $Checkout 'mrl\launch_manifest.json'
    $packet = Join-Path $script:Ctl24 ('project-control\tasks\' + $LanePacketId + '.json')
    $draft = Invoke-Ext -FilePath 'python' -ExtArgs @(
        '-m', 'tools.agent_supervisor.mrl_launch_draft',
        '--worktree', $LaneWorktree,
        '--task-packet', $packet,
        '--mode', $Mode,
        '--claude-executable', $script:ClaudeExe,
        '--codex-executable', $script:CodexExe,
        '--config', $script:ConfigPath,
        '--model-selection', $script:ModelSelection,
        '--controller-manifest', $script:ManifestPath,
        '--base-ref', 'refs/heads/main',
        '--claude-runtime-model-from-selection',
        '--out', $manifestOut,
        '--force') -WorkingDirectory $Checkout
    if ($draft.code -ne 0) {
        throw ('STOP [lane 5.11]: mrl_launch_draft failed for lane ' + $LaneNumber + ' (exit ' + $draft.code + '): ' + $draft.stderr)
    }

    $chk = ("import json; d=json.load(open(r'" + $manifestOut + "'))['dispatch']; print(d['claude_version'], d['claude_chain_sha256'])")
    $r = Invoke-Ext -FilePath 'python' -ExtArgs @('-c', $chk) -WorkingDirectory $Checkout
    $got = $r.stdout.Trim()
    if ($r.code -ne 0 -or $got -ne $script:ChainCheckStop) {
        throw ("STOP [lane 5.11]: the launch manifest chain reads '" + $got + "', expected '" +
            $script:ChainCheckStop + "' - do NOT start lane " + $LaneNumber)
    }
    Write-Output ('  launch manifest chain verified: ' + $got)

    # (5) start DETACHED, repin on the first start only
    $startArgs = @('-m', 'tools.agent_supervisor', 'start', '--mode', $Mode)
    if ($Mode -eq 'limited-auto') { $startArgs += '--owner-enable-bounded-auto' }
    $startArgs += @('--checkout', $Checkout, '--launch-manifest', $manifestOut, '--max-cycles', '1')
    if ($Repin) { $startArgs += '--repin-cli-identity' }
    $launch = Start-Detached -LaneNumber $LaneNumber -StartArgs $startArgs -WorkingDirectory $Checkout
    Write-Output ('  lane ' + $LaneNumber + ' started DETACHED (mode ' + $Mode + ', repin=' + $Repin +
        '), PID ' + $launch.pid)
    Write-Output ('    stdout log: ' + $launch.out)
    Write-Output ('    stderr log: ' + $launch.err)
    if ($LaneNumber -eq '1') {
        Write-Output '  CANARY: it will park in WAIT_FOR_OWNER. Run -Phase approve next, then watch the canary checks (5.12).'
    }
    return $launch
}

# ============================================================================
# Phase: approve (the canary's prompt-digest approval, then the re-start).
# ============================================================================

function Invoke-ApprovePhase {
    param([string]$LaneNumber, [string]$LaneWorktree, [string]$LanePacketId, [string]$RequestedMode, [string]$Digest)
    if ($LaneNumber -eq '') { $LaneNumber = '1' }
    if ($LaneNumber -notin @('1', '2', '3', '4', '5')) {
        throw 'STOP [approve]: -Lane must be one of 1..5'
    }
    $checkout = $script:LaneCheckout[$LaneNumber]
    Write-Output ('== commission approve lane ' + $LaneNumber + ' - the canary prompt-digest approval (5.11/5.12) ==')

    # List the held prompt (MRL runbook section 5).
    $pa = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', 'pending-approvals', '--checkout', $checkout) `
        -WorkingDirectory $checkout
    if ($pa.code -ne 0) {
        throw ('STOP [approve]: pending-approvals failed (exit ' + $pa.code + '): ' + $pa.stderr)
    }
    Write-Output ('  pending approvals: ' + ($pa.stdout -replace '\s+', ' '))
    if ($Digest -eq '') {
        throw 'STOP [approve]: pass -PromptDigest <the digest printed above> to approve the held prompt'
    }
    if ($pa.stdout -notmatch [regex]::Escape($Digest)) {
        throw ("STOP [approve]: the digest '" + $Digest + "' is not among the held prompts - approve only a digest that is really held")
    }

    # Approve the exact digest.
    $ap = Invoke-Ext -FilePath 'python' -ExtArgs @('-m', 'tools.agent_supervisor', 'resume-pending-prompt',
        '--checkout', $checkout, '--approve-prompt-digest', $Digest) -WorkingDirectory $checkout
    if ($ap.code -ne 0) {
        throw ('STOP [approve]: resume-pending-prompt failed (exit ' + $ap.code + '): ' + $ap.stderr)
    }
    Write-Output ('  approved prompt digest ' + $Digest)

    # Re-start WITHOUT --repin-cli-identity (the repin already landed on the first start).
    if ($LaneWorktree -eq '' -or $LanePacketId -eq '') {
        throw 'STOP [approve]: -Worktree and -PacketId are required so the re-start can re-draft the manifest'
    }
    $mode = Get-LaneMode -LaneNumber $LaneNumber -RequestedMode $RequestedMode
    Start-LaneFirstLaunch -LaneNumber $LaneNumber -Checkout $checkout -LaneWorktree $LaneWorktree `
        -LanePacketId $LanePacketId -Mode $mode -Repin $false | Out-Null
    Write-Output '  canary re-started. Watch the 5.12 canary checks; on any anomaly, stop and open a blocker.'
}

# ============================================================================
# Phase: lanes (lanes 2-5 from an orchestrator-written plan file, validated).
# ============================================================================

function Read-LanePlan {
    param([string]$Path)
    if ($Path -eq '' -or -not (Test-Path -LiteralPath $Path)) {
        throw ("STOP [lanes]: plan file not found: '" + $Path + "'")
    }
    try {
        $plan = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        throw ('STOP [lanes]: plan file is not valid JSON: ' + $_.Exception.Message)
    }
    return $plan
}

function Assert-ValidLanePlan {
    # Fail-closed plan validation (D-088-R004/R005): each lane 2-5 exactly once,
    # distinct worktrees, each a git worktree, each packet claimed/in_progress, and
    # pairwise-disjoint allowed_paths.
    param($Plan)
    if ($null -eq $Plan.PSObject.Properties['lanes']) {
        throw 'STOP [lanes]: the plan has no "lanes" array'
    }
    $lanes = @($Plan.lanes)
    if ($lanes.Count -eq 0) {
        throw 'STOP [lanes]: the plan lists no lanes'
    }
    $seenLane = @{}
    $seenWorktree = @{}
    $pathsByLane = @{}
    foreach ($entry in $lanes) {
        foreach ($field in @('lane', 'worktree', 'packet_id', 'mode')) {
            if ($null -eq $entry.PSObject.Properties[$field]) {
                throw ("STOP [lanes]: a plan entry is missing '" + $field + "'")
            }
        }
        $laneNo = [string]$entry.lane
        if ($laneNo -notin @('2', '3', '4', '5')) {
            throw ("STOP [lanes]: lane number '" + $laneNo + "' is out of range (lane 1 is the canary; the plan feeds 2-5)")
        }
        if ($seenLane.ContainsKey($laneNo)) {
            throw ("STOP [lanes]: lane " + $laneNo + " appears more than once in the plan")
        }
        $seenLane[$laneNo] = $true

        $wtKey = ([System.IO.Path]::GetFullPath([string]$entry.worktree)).TrimEnd('\').ToLowerInvariant()
        if ($seenWorktree.ContainsKey($wtKey)) {
            throw ("STOP [lanes]: worktree '" + $entry.worktree + "' is shared by two lanes")
        }
        $seenWorktree[$wtKey] = $true

        # The worktree must be a real git worktree.
        $top = Invoke-Ext -FilePath 'git' -ExtArgs @('-C', [string]$entry.worktree, 'rev-parse', '--show-toplevel')
        if ($top.code -ne 0) {
            throw ("STOP [lanes]: '" + $entry.worktree + "' is not a git worktree (lane " + $laneNo + ")")
        }

        # The packet must exist and be claimed / in_progress.
        $packetPath = Join-Path $script:Ctl24 ('project-control\tasks\' + [string]$entry.packet_id + '.json')
        if (-not (Test-Path -LiteralPath $packetPath)) {
            throw ("STOP [lanes]: packet file not found for lane " + $laneNo + ": " + $packetPath)
        }
        $packet = Get-Content -LiteralPath $packetPath -Raw | ConvertFrom-Json
        if ($null -eq $packet.PSObject.Properties['status'] -or [string]$packet.status -notin @('claimed', 'in_progress')) {
            $st = 'missing'
            if ($null -ne $packet.PSObject.Properties['status']) { $st = [string]$packet.status }
            throw ("STOP [lanes]: packet " + [string]$entry.packet_id + " for lane " + $laneNo +
                " is '" + $st + "', not claimed/in_progress")
        }
        if ($null -eq $packet.PSObject.Properties['allowed_paths']) {
            throw ("STOP [lanes]: packet " + [string]$entry.packet_id + " has no allowed_paths")
        }
        $pathsByLane[$laneNo] = @($packet.allowed_paths | ForEach-Object { (([string]$_).Replace('\', '/').Trim().TrimEnd('/')).ToLowerInvariant() })
    }

    # Pairwise-disjoint allowed_paths across all planned lanes.
    $laneKeys = @($pathsByLane.Keys | Sort-Object)
    for ($i = 0; $i -lt $laneKeys.Count; $i++) {
        for ($j = $i + 1; $j -lt $laneKeys.Count; $j++) {
            $overlap = Get-PathOverlap -PathsA $pathsByLane[$laneKeys[$i]] -PathsB $pathsByLane[$laneKeys[$j]]
            if ($overlap -ne '') {
                throw ("STOP [lanes]: lanes " + $laneKeys[$i] + " and " + $laneKeys[$j] +
                    " share overlapping allowed_paths ('" + $overlap + "') - lanes must be pairwise disjoint")
            }
        }
    }
    Write-Output ('  plan validated: ' + $laneKeys.Count + ' lane(s), pairwise-disjoint allowed_paths, all packets claimed/in_progress')
}

function Get-PathOverlap {
    # Returns the first overlapping path pair (equal, or one an ancestor of the
    # other), or '' if the two allowed-path sets are disjoint.
    param([string[]]$PathsA, [string[]]$PathsB)
    foreach ($a in $PathsA) {
        foreach ($b in $PathsB) {
            if ($a -eq $b) { return $a }
            if ($a.StartsWith($b + '/')) { return $a }
            if ($b.StartsWith($a + '/')) { return $b }
        }
    }
    return ''
}

function Invoke-LanesPhase {
    param([string]$Path)
    Write-Output '== commission lanes 2-5 from the orchestrator plan (5.11, spaced >= 60 s) =='
    $plan = Read-LanePlan -Path $Path
    Assert-ValidLanePlan -Plan $plan

    $entries = @($plan.lanes | Sort-Object { [int]$_.lane })
    $first = $true
    foreach ($entry in $entries) {
        if (-not $first) {
            Write-Output ('  spacing ' + $script:LaneSpacingSeconds + ' s before the next lane start (D-088-R004)')
            Start-LaneSpacing -Seconds $script:LaneSpacingSeconds
        }
        $first = $false
        $laneNo = [string]$entry.lane
        $checkout = $script:LaneCheckout[$laneNo]
        Start-LaneFirstLaunch -LaneNumber $laneNo -Checkout $checkout -LaneWorktree ([string]$entry.worktree) `
            -LanePacketId ([string]$entry.packet_id) -Mode ([string]$entry.mode) -Repin $true | Out-Null
    }
    Write-Output ''
    Write-Output 'LANES STARTED - each with its own runtime identity, worktree and fresh manifest.'
}

# ============================================================================
# Dispatch (skipped when dot-sourced for tests via -LoadOnly).
# ============================================================================

if ($LoadOnly) { return }

try {
    switch ($Phase) {
        'check'   { Invoke-CheckPhase }
        'update'  { Invoke-UpdatePhase }
        'lane'    { Invoke-LanePhase -LaneNumber $Lane -LaneWorktree $Worktree -LanePacketId $PacketId -RequestedMode $Mode }
        'approve' { Invoke-ApprovePhase -LaneNumber $Lane -LaneWorktree $Worktree -LanePacketId $PacketId -RequestedMode $Mode -Digest $PromptDigest }
        'lanes'   { Invoke-LanesPhase -Path $PlanFile }
        default   { throw "STOP: unknown -Phase '$Phase'. Use check | update | lane | approve | lanes." }
    }
    exit 0
} catch {
    Write-Output ($_.Exception.Message)
    exit 1
}
