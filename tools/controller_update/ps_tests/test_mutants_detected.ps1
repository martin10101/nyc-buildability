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
    $r = Invoke-UpdateScript -ScriptPath $mutant -Phase install -BindingFile $b.path
    Assert-True -Condition ($r.exit_code -eq 0) -Label 'DETECTED: module-check mutant wrongly passes without mrl_launch_draft.py'
}

# ---- shared good install for the manifest/content mutants -------------------
$shared = New-CaseBinding -Name 'mshared' -Sha $fix.shaB -Tree $fix.treeB -Subtree $fix.subtreeB
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

if ($script:failures -gt 0) {
    Write-Output ("test_mutants_detected: " + $script:failures + " assertion failure(s); fixtures kept at " + $work)
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_mutants_detected: every source-binding mutation detected'
exit 0
