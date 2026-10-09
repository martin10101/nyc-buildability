# test_null_exit.ps1 - a native command that never launches must fail closed
# with the typed native_no_exit_code refusal, never a null-propagated pass
# (M0-T139; D-024-R625/R634). The install phase's first native call is git;
# with git unresolvable on PATH the invocation throws, no exit code exists,
# and the script must refuse - under real PowerShell 5.1 raw-exit semantics.
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

$values = @{
    repo = $fix.repo
    commit_sha = $fix.shaB
    commit_tree_sha = $fix.treeB
    subtree_tree_sha = $fix.subtreeB
    source_worktree = (Join-Path $work 'wt-nullexit')
    destination = (Join-Path $work 'dest-nullexit')
    controller_manifest = (Join-Path $work 'manifest-nullexit.json')
    evidence_out = (Join-Path $work 'evidence-nullexit.json')
}
$bindingPath = Join-Path $work 'binding-nullexit.json'
New-BindingFile -Path $bindingPath -Values $values | Out-Null

$powershellExe = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$oldPath = $env:PATH
try {
    # a PATH with no git: the & git invocation throws, LASTEXITCODE stays null
    $env:PATH = (Join-Path $env:SystemRoot 'System32') + ';' + $env:SystemRoot
    $global:LASTEXITCODE = $null
    $out = & $powershellExe -NoProfile -ExecutionPolicy Bypass -File $scriptPath -Phase install -BindingFile $bindingPath 2>&1 | Out-String
    $code = $global:LASTEXITCODE
} finally {
    $env:PATH = $oldPath
}
Assert-True -Condition ($code -eq 1) -Label 'null-exit install exits with raw 1'
Assert-True -Condition ($out -match 'REFUSED native_no_exit_code') -Label 'typed native_no_exit_code refusal printed'
if (($code -ne 1) -or ($out -notmatch 'REFUSED native_no_exit_code')) {
    Write-Output ("  got exit " + $code + "; output: " + $out.Trim())
}

if ($script:failures -gt 0) {
    Write-Output ("test_null_exit: " + $script:failures + " assertion failure(s)")
    exit 1
}
Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Output 'test_null_exit: missing-launch fails closed with the typed refusal'
exit 0
