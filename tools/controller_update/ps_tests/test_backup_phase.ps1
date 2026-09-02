# test_backup_phase.ps1 - the -Phase backup transaction step (M0-T139;
# D-024-R624..R630, R634): positive proof, uniqueness, per-copy raw exit
# codes, fail-closed source checks, and cache exclusion. Every case runs the
# REAL operator script in a fresh powershell.exe process; raw exit codes only.
. (Join-Path $PSScriptRoot 'fixtures.ps1')

$script:failures = 0
$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'update_controller_from_candidate.ps1'
$work = New-FixtureWork
$fix = New-FixtureRepo -Root $work

function Assert-True {
    param([bool]$Condition, [string]$Label)
    if ($Condition) {
        Write-Output ("PASS " + $Label)
    } else {
        Write-Output ("ASSERT-FAIL " + $Label)
        $script:failures = $script:failures + 1
    }
}

function Assert-Refused {
    param([hashtable]$Result, [string]$Code, [string]$Label)
    $refused = ($Result.exit_code -ne 0) -and ($Result.stdout -match ('REFUSED ' + $Code))
    if (-not $refused) {
        Write-Output ("  got exit " + $Result.exit_code + "; stdout: " + $Result.stdout.Trim())
    }
    Assert-True -Condition $refused -Label ($Label + ' -> REFUSED ' + $Code)
}

function New-CaseBinding {
    param([string]$Name, [hashtable]$Extra = @{})
    $values = @{
        repo = $fix.repo
        commit_sha = $fix.shaB
        commit_tree_sha = $fix.treeB
        subtree_tree_sha = $fix.subtreeB
        source_worktree = (Join-Path $work ('wt-' + $Name))
        destination = (Join-Path $work ('dest-' + $Name))
        controller_manifest = (Join-Path $work ('manifest-' + $Name + '.json'))
        evidence_out = (Join-Path $work ('evidence-' + $Name + '.json'))
    }
    foreach ($k in $Extra.Keys) { $values[$k] = $Extra[$k] }
    $path = Join-Path $work ('binding-' + $Name + '.json')
    New-BindingFile -Path $path -Values $values | Out-Null
    return @{ path = $path; values = $values }
}

# ---- B1: positive backup - evidence bound, both raw codes, digests (R629/R630)
$b1 = New-CaseBinding -Name 'b1'
Initialize-TxSources -BindingPath $b1.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b1.path
if ($r.exit_code -ne 0) { Write-Output ("  stdout: " + $r.stdout.Trim() + " stderr: " + $r.stderr.Trim()) }
Assert-True -Condition ($r.exit_code -eq 0) -Label 'B1 backup exits 0'
Assert-True -Condition ($r.stdout -match 'BACKUP VERIFIED run ') -Label 'B1 success marker names the run id'
$evidencePath = $b1.values.destination + '-backup-evidence.json'
Assert-True -Condition (Test-Path -LiteralPath $evidencePath) -Label 'B1 wrote controller_backup_evidence.json'
$ev = Get-Content -LiteralPath $evidencePath -Raw | ConvertFrom-Json
Assert-True -Condition ($ev.schema -eq 'controller_backup_evidence/v1') -Label 'B1 evidence schema'
Assert-True -Condition ($ev.verdict -eq 'PASS') -Label 'B1 verdict PASS only after verification'
Assert-True -Condition ($ev.run_id -match '^\d{8}-\d{9}-[0-9a-f]{8}$') -Label 'B1 run id carries timestamp + unique suffix'
Assert-True -Condition ($ev.robocopy_exit_codes.controller_tree -in 0..3 -and $ev.robocopy_exit_codes.runtime_a1 -in 0..3) -Label 'B1 BOTH raw robocopy exit codes recorded (R626)'
Assert-True -Condition ($ev.pre_update_controller_identity.file_count -ge 3) -Label 'B1 pre-update controller identity carries digests'
Assert-True -Condition ($ev.runtime_a1_identity.file_count -ge 2) -Label 'B1 runtime-a1 identity carries digests'
$ctlBackup = [string]$ev.backup_paths.controller
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $ctlBackup 'legacy_module.py')) -Label 'B1 backup holds the old controller tree'
Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $ctlBackup '__pycache__'))) -Label 'B1 cache dirs never copied into the backup'
Assert-True -Condition (Test-Path -LiteralPath (Join-Path ([string]$ev.backup_paths.runtime_a1) 'journal.db')) -Label 'B1 runtime journal preserved'

# ---- B2: a second backup creates a DIFFERENT previously nonexistent dir (R627)
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'B2 second backup exits 0'
$ev2 = Get-Content -LiteralPath $evidencePath -Raw | ConvertFrom-Json
Assert-True -Condition ($ev2.run_id -ne $ev.run_id -and $ev2.backup_dir -ne $ev.backup_dir) -Label 'B2 unique fresh backup directory per run'
Assert-True -Condition (Test-Path -LiteralPath $ev.backup_dir) -Label 'B2 earlier backup untouched (non-destructive)'

# ---- B3: first-copy failure refuses BEFORE the second copy (R625/R626) ------
$b3 = New-CaseBinding -Name 'b3'
Initialize-TxSources -BindingPath $b3.path | Out-Null
$locked = [System.IO.File]::Open((Join-Path $b3.values.destination 'cli.py'), 'Open', 'Read', 'None')
try {
    $r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b3.path
    Assert-Refused -Result $r -Code 'copy_failed' -Label 'B3 locked source file fails the first copy'
    Assert-True -Condition ($r.stdout -match 'second copy was NOT attempted') -Label 'B3 refusal states the second copy never ran'
    $runtimeCopies = @(Get-ChildItem -Path (Join-Path ($b3.values.destination + '-backups') '*\runtime-a1') -ErrorAction SilentlyContinue)
    Assert-True -Condition ($runtimeCopies.Count -eq 0) -Label 'B3 no runtime-a1 copy exists (first failure never masked)'
    Assert-True -Condition (-not (Test-Path -LiteralPath ($b3.values.destination + '-backup-evidence.json'))) -Label 'B3 no evidence written for a failed backup'
} finally {
    $locked.Dispose()
}

# ---- B4: missing sources refuse before anything is created (R628/R634) ------
$b4 = New-CaseBinding -Name 'b4'
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b4.path
Assert-Refused -Result $r -Code 'backup_source_missing' -Label 'B4 missing controller source'
Assert-True -Condition (-not (Test-Path -LiteralPath ($b4.values.destination + '-backups'))) -Label 'B4 no backup dir created'

# ---- B5: runtime key not 64-hex refuses (R636 machine validation) -----------
$b5 = New-CaseBinding -Name 'b5' -Extra @{ a1_runtime_dir = (Join-Path $work 'NYCBuildabilitySupervisor\not-a-hex-key') }
Initialize-TxSources -BindingPath $b5.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b5.path
Assert-Refused -Result $r -Code 'runtime_key_invalid' -Label 'B5 malformed runtime journal key'

# ---- B6: v1 binding (missing transaction keys) refuses ----------------------
$b6 = New-CaseBinding -Name 'b6'
$bindingJson = Get-Content -LiteralPath $b6.path -Raw | ConvertFrom-Json
$bindingJson.schema = 'controller_update_source_binding/v1'
$bindingJson | ConvertTo-Json -Depth 5 | Out-File -FilePath $b6.path -Encoding utf8
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b6.path
Assert-Refused -Result $r -Code 'binding_schema_unsupported' -Label 'B6 v1 binding schema'

if ($script:failures -gt 0) {
    Write-Output ("test_backup_phase: " + $script:failures + " assertion failure(s); fixtures kept at " + $work)
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_backup_phase: backup transaction step verified'
exit 0
