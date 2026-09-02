# test_source_binding.ps1 - positive control + the six typed rejection classes
# of the controller-update source binding (M0-T138; D-024-R609/R610/R611/R613).
# Every case runs the REAL operator script in a fresh powershell.exe process
# against a real fixture git repository; raw exit codes only.
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

# ---- positive control: backup then install from the accepted candidate ------
# (M0-T139: install is transactional - it refuses without the verified backup.)
$p1 = New-CaseBinding -Name 'p1' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
Initialize-TxSources -BindingPath $p1.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $p1.path
if ($r.exit_code -ne 0) { Write-Output ("  backup stdout: " + $r.stdout.Trim() + " stderr: " + $r.stderr.Trim()) }
Assert-True -Condition ($r.exit_code -eq 0) -Label 'P1 backup of the old controller exits 0'
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $p1.path
if ($r.exit_code -ne 0) { Write-Output ("  install stdout: " + $r.stdout.Trim() + " stderr: " + $r.stderr.Trim()) }
Assert-True -Condition ($r.exit_code -eq 0) -Label 'P1 install from accepted fixture commit exits 0'
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $p1.values.destination 'mrl_launch_draft.py')) -Label 'P1 installed mrl_launch_draft.py'
Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $p1.values.destination 'legacy_module.py'))) -Label 'P1 mirror removed the old-tree module'
Assert-True -Condition (Test-Path -LiteralPath $p1.values.evidence_out) -Label 'P1 wrote controller_update_evidence.json'
$evidence = Get-Content -LiteralPath $p1.values.evidence_out -Raw | ConvertFrom-Json
Assert-True -Condition ($evidence.commit_sha -eq $fix.shaB) -Label 'P1 evidence binds the immutable commit SHA'
Assert-True -Condition ($evidence.commit_tree_sha -eq $fix.treeB) -Label 'P1 evidence binds the accepted commit tree'
Assert-True -Condition ($evidence.installed_file_count -ge 9) -Label 'P1 evidence carries per-file digests'
Assert-True -Condition ($null -ne $evidence.backup_binding -and $evidence.backup_binding.reverified -eq 'PASS') -Label 'P1 evidence records the verified backup identity (R631)'
$backupEvidence = Get-Content -LiteralPath ($p1.values.destination + '-backup-evidence.json') -Raw | ConvertFrom-Json
Assert-True -Condition ($evidence.backup_binding.run_id -eq $backupEvidence.run_id) -Label 'P1 install bound the exact backup run id'

# ---- rejection a: a mutable ref can never be the source (R613a) -------------
$na = New-CaseBinding -Name 'na' -Sha 'origin/main' -Tree $fix.treeB -Subtree $fix.subtreeB
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $na.path
Assert-Refused -Result $r -Code 'not_a_full_sha' -Label 'a) origin/main as source'
Assert-True -Condition (-not (Test-Path -LiteralPath $na.values.destination)) -Label 'a) nothing was installed'

# ---- rejection b: internally self-consistent wrong commit (R613b/R613d) -----
$nb = New-CaseBinding -Name 'nb' -Sha $fix.shaC -Tree $fix.treeB -Subtree $fix.subtreeB
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $nb.path
Assert-Refused -Result $r -Code 'tree_mismatch' -Label 'b) wrong self-consistent commit vs accepted tree'
Assert-True -Condition (-not (Test-Path -LiteralPath $nb.values.destination)) -Label 'b) nothing was installed'

# ---- rejection d: accepted subtree mismatch (R613d) -------------------------
$nd = New-CaseBinding -Name 'nd' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeA
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $nd.path
Assert-Refused -Result $r -Code 'subtree_mismatch' -Label 'd) accepted subtree-tree mismatch'

# ---- rejection c: missing Tranche-B module (R613c) --------------------------
$nc = New-CaseBinding -Name 'nc' -Sha $fix.shaA -Tree $fix.treeA -Subtree $fix.subtreeA
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $nc.path
Assert-Refused -Result $r -Code 'missing_module' -Label 'c) commit lacking mrl_launch_draft.py'

# ---- stale source worktree refuses (fail-closed rerun) ----------------------
# (needs a valid backup first: the worktree check follows the backup gates)
$nw = New-CaseBinding -Name 'nw' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
Initialize-TxSources -BindingPath $nw.path | Out-Null
$r = Invoke-BackupPhase -ScriptPath $scriptPath -BindingFile $nw.path
Assert-True -Condition ($r.exit_code -eq 0) -Label 'nw backup exits 0'
New-Item -ItemType Directory -Force -Path $nw.values.source_worktree | Out-Null
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase install -BindingFile $nw.path
Assert-Refused -Result $r -Code 'source_worktree_exists' -Label 'stale source-worktree path'

# ---- positive verify-manifest: manifest crafted independently (python) ------
$crafter = Write-CraftManifestScript -Path (Join-Path $work 'craft_manifest.py')
$sourceSubtree = Join-Path $p1.values.source_worktree 'tools\agent_supervisor'
$global:LASTEXITCODE = $null
& python $crafter $sourceSubtree $p1.values.controller_manifest 1>$null 2>$null
Assert-True -Condition ($LASTEXITCODE -eq 0) -Label 'P2 fixture manifest crafted via python hashlib'
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase verify-manifest -BindingFile $p1.path
if ($r.exit_code -ne 0) { Write-Output ("  verify stdout: " + $r.stdout.Trim()) }
Assert-True -Condition ($r.exit_code -eq 0) -Label 'P2 verify-manifest exits 0 on the accepted installation'
$evidence = Get-Content -LiteralPath $p1.values.evidence_out -Raw | ConvertFrom-Json
Assert-True -Condition ($evidence.manifest_binding.verdict -eq 'PASS') -Label 'P2 evidence binds the manifest verdict'

# ---- rejection f: manifest recorded from the wrong installed tree (R613f) ---
$good = Get-Content -LiteralPath $p1.values.controller_manifest -Raw | ConvertFrom-Json
$flipped = Get-Content -LiteralPath $p1.values.controller_manifest -Raw | ConvertFrom-Json
$firstName = @($flipped.files.PSObject.Properties)[0].Name
$flipped.files.PSObject.Properties[$firstName].Value = ('0' * 64)
$flipped | ConvertTo-Json -Depth 5 | Out-File -FilePath $p1.values.controller_manifest -Encoding utf8
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase verify-manifest -BindingFile $p1.path
Assert-Refused -Result $r -Code 'manifest_digest_mismatch' -Label 'f) manifest digest from a wrong installed tree'

$extra = $good
$extra.files | Add-Member -NotePropertyName 'extra.py' -NotePropertyValue ('1' * 64) -Force
$extra | ConvertTo-Json -Depth 5 | Out-File -FilePath $p1.values.controller_manifest -Encoding utf8
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase verify-manifest -BindingFile $p1.path
Assert-Refused -Result $r -Code 'manifest_key_set_mismatch' -Label 'f) manifest covering a file the accepted source lacks'

# restore the good manifest for the final case
& python $crafter $sourceSubtree $p1.values.controller_manifest 1>$null 2>$null
Assert-True -Condition ($LASTEXITCODE -eq 0) -Label 'good manifest restored'

# ---- rejection e: destination changed after copying (R613e) -----------------
Add-Content -LiteralPath (Join-Path $p1.values.destination 'cli.py') -Value '# tampered after install'
$r = Invoke-UpdateScript -ScriptPath $scriptPath -Phase verify-manifest -BindingFile $p1.path
Assert-Refused -Result $r -Code 'content_mismatch' -Label 'e) destination file changed after copying'

if ($script:failures -gt 0) {
    Write-Output ("test_source_binding: " + $script:failures + " assertion failure(s); fixtures kept at " + $work)
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_source_binding: positive control + all rejection classes verified'
exit 0
