# test_mutants_detected.ps1 - the source-binding checks are load-bearing
# (M0-T138; D-024-R589/R613 paired mutations). Each mutant disables exactly one
# guard in a COPY of the real operator script; the corresponding rejection
# fixture must then WRONGLY PASS (exit 0) where the real script refused - which
# is exactly how the negative tests would catch (kill) such a mutation. The
# generator fails closed if a mutation pattern no longer matches exactly once.
. (Join-Path $PSScriptRoot 'fixtures.ps1')

$script:failures = 0
$scriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'update_controller_from_candidate.ps1'
$scriptText = [System.IO.File]::ReadAllText($scriptPath)
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

function New-Mutant {
    param([string]$Name, [string]$Pattern)
    $count = ([regex]::Matches($scriptText, [regex]::Escape($Pattern))).Count
    if ($count -ne 1) {
        Write-Output ("ASSERT-FAIL mutant " + $Name + ": pattern matched " + $count + " time(s), expected exactly 1 (fail closed)")
        $script:failures = $script:failures + 1
        return ''
    }
    $mutantPath = Join-Path $work ('mutant_' + $Name + '.ps1')
    [System.IO.File]::WriteAllText($mutantPath, $scriptText.Replace($Pattern, 'if ($false) {'))
    return $mutantPath
}

function New-CaseBinding {
    param([string]$Name, [string]$Sha, [string]$Tree, [string]$Subtree)
    $values = @{
        repo = $fix.repo
        commit_sha = $Sha
        commit_tree_sha = $Tree
        subtree_tree_sha = $Subtree
        source_worktree = (Join-Path $work ('wt-' + $Name))
        destination = (Join-Path $work ('dest-' + $Name))
        controller_manifest = (Join-Path $work ('manifest-' + $Name + '.json'))
        evidence_out = (Join-Path $work ('evidence-' + $Name + '.json'))
    }
    $path = Join-Path $work ('binding-' + $Name + '.json')
    New-BindingFile -Path $path -Values $values | Out-Null
    return @{ path = $path; values = $values }
}

# ---- m_tree: accepted-tree comparison disabled -> wrong commit installs -----
$mutant = New-Mutant -Name 'tree' -Pattern 'if ($treeProbe.stdout -ne $binding.commit_tree_sha) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mtree-real' -Sha $fix.shaC -Tree $fix.treeB -Subtree $fix.subtreeB
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -ne 0) -Label 'control: real script refuses the wrong commit'
    $b = New-CaseBinding -Name 'mtree-mut' -Sha $fix.shaC -Tree $fix.treeB -Subtree $fix.subtreeB
    Initialize-TxSources -BindingPath $b.path | Out-Null
    Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path | Out-Null
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: tree-check mutant wrongly passes the wrong commit'
}

# ---- m_module: required-module gate disabled -> Tranche-B gap installs ------
$mutant = New-Mutant -Name 'module' -Pattern 'if ($moduleProbe.code -ne 0) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mmod-real' -Sha $fix.shaA -Tree $fix.treeA -Subtree $fix.subtreeA
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -ne 0) -Label 'control: real script refuses the module-less commit'
    $b = New-CaseBinding -Name 'mmod-mut' -Sha $fix.shaA -Tree $fix.treeA -Subtree $fix.subtreeA
    Initialize-TxSources -BindingPath $b.path | Out-Null
    Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path | Out-Null
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: module-check mutant wrongly passes without mrl_launch_draft.py'
}

# ---- shared good install for the manifest/content mutants -------------------
$shared = New-CaseBinding -Name 'mshared' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
Initialize-TxSources -BindingPath $shared.path | Out-Null
Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $shared.path | Out-Null
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $shared.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'shared fixture install exits 0'
$crafter = Write-CraftManifestScript -Path (Join-Path $work 'craft_manifest.py')
$sourceSubtree = Join-Path $shared.values.source_worktree 'tools\agent_supervisor'
$global:LASTEXITCODE = $null
& python $crafter $sourceSubtree $shared.values.controller_manifest 1>$null 2>$null
Assert-True -Condition ($LASTEXITCODE -eq 0) -Label 'shared fixture manifest crafted'

# ---- m_manifest: digest cross-check disabled -> wrong-tree manifest passes --
$mutant = New-Mutant -Name 'manifest' -Pattern 'if ($manifestDigestFailures.Count -gt 0) {'
if ($mutant -ne '') {
    $goodManifestText = Get-Content -LiteralPath $shared.values.controller_manifest -Raw
    $flipped = $goodManifestText | ConvertFrom-Json
    $firstName = @($flipped.files.PSObject.Properties)[0].Name
    $flipped.files.PSObject.Properties[$firstName].Value = ('0' * 64)
    $flipped | ConvertTo-Json -Depth 5 | Out-File -FilePath $shared.values.controller_manifest -Encoding utf8
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase verify-manifest -BindingFile $shared.path
    Assert-True -Condition ($r.exit_code -ne 0) -Label 'control: real script refuses the wrong-tree manifest'
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase verify-manifest -BindingFile $shared.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: manifest-check mutant wrongly passes a wrong-tree manifest'
    [System.IO.File]::WriteAllText($shared.values.controller_manifest, $goodManifestText)
}

# ---- m_content: installed-tree comparison disabled -> tampered dest passes --
$mutant = New-Mutant -Name 'content' -Pattern 'if ($comparisonFailures.Count -gt 0) {'
if ($mutant -ne '') {
    Add-Content -LiteralPath (Join-Path $shared.values.destination 'cli.py') -Value '# tampered'
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase verify-manifest -BindingFile $shared.path
    Assert-True -Condition ($r.exit_code -ne 0) -Label 'control: real script refuses the tampered installation'
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase verify-manifest -BindingFile $shared.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: content-check mutant wrongly passes a tampered installation'
}

# ============ M0-T139 transaction mutants (D-024-R638) =======================

# ---- m_tamper: install's backup-tamper gate disabled -> tampered backup ----
# wrongly installs (clean kill: real refuses backup_tampered, mutant exits 0).
$mutant = New-Mutant -Name 'tamper' -Pattern 'if ($backupTamperFailures.Count -gt 0) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mtamper' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
    Initialize-TxSources -BindingPath $b.path | Out-Null
    Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path | Out-Null
    $backupCli = Join-Path ($b.values.destination + '-backups') '*\agent_supervisor\cli.py'
    Add-Content -Path $backupCli -Value '# backup tampered'
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $b.path
    Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED backup_tampered')) -Label 'control: real script refuses the tampered backup'
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: tamper-gate mutant wrongly installs over a tampered backup'
}

# ---- m_stale: install's backup-currency gate disabled -> a controller -------
# changed after backup wrongly installs (clean kill).
$mutant = New-Mutant -Name 'stale' -Pattern 'if ($backupStaleFailures.Count -gt 0) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mstale' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
    Initialize-TxSources -BindingPath $b.path | Out-Null
    Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path | Out-Null
    Add-Content -LiteralPath (Join-Path $b.values.destination 'cli.py') -Value '# post-backup drift'
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $b.path
    Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED backup_stale')) -Label 'control: real script refuses the stale backup'
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: currency-gate mutant wrongly installs over a stale backup'
}

# ---- m_reparse: tree reparse scan disabled -> robocopy silently copies ------
# THROUGH the planted junction (layered defense, measured on this host:
# robocopy /E follows the junction while the PS 5.1 digest walk does not, so
# the bidirectional proof refuses the leaked content with a DIFFERENT code and
# only AFTER junction bytes reached the backup - the changed refusal identity
# plus the leak is the detection; the typed early reparse refusal is the
# guard's own work).
$mutant = New-Mutant -Name 'reparse' -Pattern 'if ($null -ne $reparseHit) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mreparse' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
    Initialize-TxSources -BindingPath $b.path | Out-Null
    $junctionTarget = Join-Path $work 'mreparse-target'
    New-Item -ItemType Directory -Force -Path $junctionTarget | Out-Null
    Set-Content -LiteralPath (Join-Path $junctionTarget 'lured.py') -Value 'print("outside")' -Encoding ascii
    $junction = Join-Path $b.values.destination 'junction_dir'
    New-Item -ItemType Junction -Path $junction -Target $junctionTarget | Out-Null
    $r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path
    Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED reparse_point_detected')) -Label 'control: real script refuses the planted junction BEFORE any copy'
    $backupRoot = $b.values.destination + '-backups'
    Assert-True -Condition (-not (Test-Path -LiteralPath $backupRoot)) -Label 'control: reparse refusal created no backup directory'
    $r = Invoke-BackupPhase -ScriptPath $mutant -BindingFile $b.path
    Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED backup_verify_failed')) -Label 'DETECTED: reparse-scan mutant loses the typed refusal (deeper digest layer fires instead)'
    $leaked = @(Get-ChildItem -Path (Join-Path $backupRoot '*\agent_supervisor\junction_dir\lured.py') -ErrorAction SilentlyContinue)
    Assert-True -Condition ($leaked.Count -gt 0) -Label 'DETECTED: reparse-scan mutant let junction bytes reach the backup'
    (Get-Item -LiteralPath $junction).Delete()
}

# ---- m_rc1: first-copy raw-exit gate disabled -> the first robocopy ---------
# failure is masked and the SECOND copy runs (layered defense: the digest
# proof still refuses, but with a DIFFERENT code and after the masked copy -
# the behavioral difference is the detection).
$mutant = New-Mutant -Name 'rc1' -Pattern 'if ($rcControllerCopy -lt 0 -or $rcControllerCopy -ge 4) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mrc1' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
    Initialize-TxSources -BindingPath $b.path | Out-Null
    $locked = [System.IO.File]::Open((Join-Path $b.values.destination 'cli.py'), 'Open', 'Read', 'None')
    try {
        $r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path
        Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED copy_failed')) -Label 'control: real script refuses the failed first copy'
        $backupRoot = $b.values.destination + '-backups'
        $runtimeCopies = @(Get-ChildItem -Path (Join-Path $backupRoot '*\runtime-a1') -ErrorAction SilentlyContinue)
        Assert-True -Condition ($runtimeCopies.Count -eq 0) -Label 'control: the second copy never ran after the first failure'
        $r = Invoke-BackupPhase -ScriptPath $mutant -BindingFile $b.path
        $runtimeCopies = @(Get-ChildItem -Path (Join-Path $backupRoot '*\runtime-a1') -ErrorAction SilentlyContinue)
        Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -notmatch 'REFUSED copy_failed')) -Label 'DETECTED: rc1 mutant masks the first-copy failure (refusal identity changed)'
        Assert-True -Condition ($runtimeCopies.Count -gt 0) -Label 'DETECTED: rc1 mutant let the second copy run over a failed first copy'
    } finally {
        $locked.Dispose()
    }
}

# ---- m_rbtamper: rollback's tamper gate disabled -> the tampered backup -----
# is RESTORED; the post-restore digest proof still refuses (layered defense:
# changed refusal identity + the tampered bytes reached the destination).
$mutant = New-Mutant -Name 'rbtamper' -Pattern 'if ($rollbackTamperFailures.Count -gt 0) {'
if ($mutant -ne '') {
    $b = New-CaseBinding -Name 'mrbt' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
    Initialize-TxSources -BindingPath $b.path | Out-Null
    Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $b.path | Out-Null
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'mrbt fixture install exits 0'
    $backupCli = Join-Path ($b.values.destination + '-backups') '*\agent_supervisor\cli.py'
    Add-Content -Path $backupCli -Value '# rollback backup tampered'
    $r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase rollback -BindingFile $b.path
    Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED backup_tampered')) -Label 'control: real rollback refuses the tampered backup BEFORE restoring'
    Assert-True -Condition (Test-Path -LiteralPath (Join-Path $b.values.destination 'mrl_launch_draft.py')) -Label 'control: refused rollback left the destination untouched'
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase rollback -BindingFile $b.path
    Assert-True -Condition (($r.exit_code -ne 0) -and ($r.stdout -match 'REFUSED rollback_verify_failed')) -Label 'DETECTED: rbtamper mutant restores first and only the post-restore proof refuses'
    $destCli = Get-Content -LiteralPath (Join-Path $b.values.destination 'cli.py') -Raw
    Assert-True -Condition ($destCli -match 'rollback backup tampered') -Label 'DETECTED: rbtamper mutant let tampered bytes reach the destination'
}

if ($script:failures -gt 0) {
    Write-Output ("test_mutants_detected: " + $script:failures + " assertion failure(s); fixtures kept at " + $work)
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_mutants_detected: every source-binding and transaction mutation detected'
exit 0
