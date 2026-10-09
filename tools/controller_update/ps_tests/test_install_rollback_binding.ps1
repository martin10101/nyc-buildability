# test_install_rollback_binding.ps1 - the install/rollback halves of the
# transaction (M0-T139; D-024-R631..R635): install is bound to the verified
# backup evidence (never "newest"), rollback restores exactly the bound backup
# and removes partial-install residue, and every adversarial case in R634
# fails closed. Real script, fresh powershell.exe, raw exit codes.
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
    param([string]$Name)
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
    $path = Join-Path $work ('binding-' + $Name + '.json')
    New-BindingFile -Path $path -Values $values | Out-Null
    return @{ path = $path; values = $values }
}

# ---- I1: install WITHOUT backup evidence refuses (R631) ---------------------
$i1 = New-CaseBinding -Name 'i1'
Initialize-TxSources -BindingPath $i1.path | Out-Null
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
Assert-Refused -Result $r -Code 'backup_evidence_missing' -Label 'I1 install without a verified backup'
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $i1.values.destination 'legacy_module.py')) -Label 'I1 nothing was mirrored'

# ---- I2: tampered backup refuses the install (R634) -------------------------
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $i1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I2 backup exits 0'
Add-Content -Path (Join-Path ($i1.values.destination + '-backups') '*\agent_supervisor\cli.py') -Value '# tampered'
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
Assert-Refused -Result $r -Code 'backup_tampered' -Label 'I2 tampered backup blocks the install'

# ---- I3: a MISSING file in the backup refuses (R634) ------------------------
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $i1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I3 fresh backup exits 0'
# the LATEST backup is the bound one; deleting from every run dir keeps it simple
Get-ChildItem -Path (Join-Path ($i1.values.destination + '-backups') '*\agent_supervisor\legacy_module.py') -ErrorAction SilentlyContinue | Remove-Item -Force
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
Assert-Refused -Result $r -Code 'backup_tampered' -Label 'I3 missing backup file blocks the install'

# ---- I4: an EXTRA file in the backup refuses (R634) -------------------------
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $i1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I4 fresh backup exits 0'
$latest = (Get-Content -LiteralPath ($i1.values.destination + '-backup-evidence.json') -Raw | ConvertFrom-Json)
Set-Content -LiteralPath (Join-Path ([string]$latest.backup_paths.controller) 'smuggled.py') -Value 'print("extra")' -Encoding ascii
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
Assert-Refused -Result $r -Code 'backup_tampered' -Label 'I4 extra backup file blocks the install'

# ---- I5: destination drift after backup refuses (backup_stale, R631) --------
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $i1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I5 fresh backup exits 0'
Add-Content -LiteralPath (Join-Path $i1.values.destination 'cli.py') -Value '# drift after backup'
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
Assert-Refused -Result $r -Code 'backup_stale' -Label 'I5 live controller changed after the backup'

# ---- I6: WRONG evidence file (from another case) refuses (R634) -------------
$other = New-CaseBinding -Name 'i6other'
Initialize-TxSources -BindingPath $other.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $other.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I6 other-case backup exits 0'
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $i1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I6 own backup exits 0 (heals I5 drift)'
Copy-Item -LiteralPath ($other.values.destination + '-backup-evidence.json') -Destination ($i1.values.destination + '-backup-evidence.json') -Force
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
Assert-Refused -Result $r -Code 'evidence_binding_mismatch' -Label 'I6 evidence describing a different controller'

# ---- I7: the happy transactional install (R631) -----------------------------
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $i1.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I7 fresh backup exits 0'
$boundEvidence = Get-Content -LiteralPath ($i1.values.destination + '-backup-evidence.json') -Raw | ConvertFrom-Json
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $i1.path
if ($r.exit_code -ne 0) { Write-Output ("  stdout: " + $r.stdout.Trim()) }
Assert-True -Condition ($r.exit_code -eq 0) -Label 'I7 transactional install exits 0'
$updateEvidence = Get-Content -LiteralPath $i1.values.evidence_out -Raw | ConvertFrom-Json
Assert-True -Condition ($updateEvidence.backup_binding.run_id -eq $boundEvidence.run_id) -Label 'I7 install recorded the exact bound backup run'
Assert-True -Condition ($updateEvidence.robocopy_exit_codes.install_mirror -in 0..7) -Label 'I7 raw mirror exit code recorded'
Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $i1.values.destination '__pycache__'))) -Label 'I7 stale cache residue removed from the destination'

# ---- R1: rollback restores the BOUND backup, not a decoy newest (R632) ------
# plant a decoy directory that sorts and dates NEWER than every real backup
$decoy = Join-Path ($i1.values.destination + '-backups') 'zzzz-99999999-decoy'
New-Item -ItemType Directory -Force -Path (Join-Path $decoy 'agent_supervisor') | Out-Null
Set-Content -LiteralPath (Join-Path $decoy 'agent_supervisor\evil.py') -Value 'print("decoy")' -Encoding ascii
# plant partial-install residue + drift at the destination (a failed update)
Set-Content -LiteralPath (Join-Path $i1.values.destination 'half_installed_module.py') -Value 'print("partial")' -Encoding ascii
Add-Content -LiteralPath (Join-Path $i1.values.destination 'cli.py') -Value '# corrupted by failed update'
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase rollback -BindingFile $i1.path
if ($r.exit_code -ne 0) { Write-Output ("  stdout: " + $r.stdout.Trim()) }
Assert-True -Condition ($r.exit_code -eq 0) -Label 'R1 rollback exits 0'
Assert-True -Condition ($r.stdout -match ('ROLLBACK VERIFIED to backup run ' + [regex]::Escape($boundEvidence.run_id))) -Label 'R1 restored the BOUND run, not the decoy'
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $decoy 'agent_supervisor\evil.py')) -Label 'R1 decoy untouched'
Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $i1.values.destination 'half_installed_module.py'))) -Label 'R1 partial-install residue removed (R633)'
Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $i1.values.destination 'evil.py'))) -Label 'R1 nothing from the decoy was restored'
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $i1.values.destination 'legacy_module.py')) -Label 'R1 pre-update controller content restored'
# independent digest re-check of one restored file against the bound evidence
$restoredHash = (Get-FileHash -LiteralPath (Join-Path $i1.values.destination 'cli.py') -Algorithm SHA256).Hash.ToLowerInvariant()
$expectedHash = [string]$boundEvidence.pre_update_controller_identity.files_sha256.'cli.py'
Assert-True -Condition ($restoredHash -eq $expectedHash) -Label 'R1 restored cli.py digest equals the bound evidence'
Assert-True -Condition (-not (Test-Path -LiteralPath $i1.values.evidence_out)) -Label 'R1 stale install evidence removed with checked result'
$rollbackEvidence = Get-Content -LiteralPath ($i1.values.destination + '-rollback-evidence.json') -Raw | ConvertFrom-Json
Assert-True -Condition ($rollbackEvidence.verdict -eq 'PASS' -and $rollbackEvidence.restored_from.run_id -eq $boundEvidence.run_id) -Label 'R1 rollback evidence binds the restored run'

# ---- R2: rollback with MISSING evidence refuses (R632) ----------------------
Remove-Item -LiteralPath ($i1.values.destination + '-backup-evidence.json') -Force
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase rollback -BindingFile $i1.path
Assert-Refused -Result $r -Code 'backup_evidence_missing' -Label 'R2 rollback without evidence never guesses a backup'

if ($script:failures -gt 0) {
    Write-Output ("test_install_rollback_binding: " + $script:failures + " assertion failure(s); fixtures kept at " + $work)
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_install_rollback_binding: transactional install + bound rollback verified'
exit 0
