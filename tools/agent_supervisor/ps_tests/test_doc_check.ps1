# test_doc_check.ps1 - the living launch docs pass the command-document tooth,
# and a mutated copy FAILS it (M0-T136 C-B5; D-024-R585, R586, R589).
. (Join-Path $PSScriptRoot 'harness.ps1')

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$docCheck = Join-Path $repoRoot 'tools\supervisor_command_doc_check.py'
$runbook = Join-Path $repoRoot 'docs\MRL_LAUNCH_RUNBOOK.md'
$canary = Join-Path $repoRoot 'project-control\reports\M0-T136-canary-package.md'
$failures = 0

# 1. The MRL launch runbook passes the tooth (exit 0).
$r = Invoke-RawExit -FilePath python -ArgumentList @($docCheck, '--doc', $runbook)
if ($r.exit_code -ne 0) {
    Write-Output "ASSERT-FAIL: doc-check on the runbook expected 0, got '$($r.exit_code)'"
    Get-Content -Path $r.stdout | Select-Object -Last 5 | Write-Output
    $failures = $failures + 1
}

# 2. The owner-run canary package passes the tooth (exit 0).
$r = Invoke-RawExit -FilePath python -ArgumentList @($docCheck, '--doc', $canary)
if ($r.exit_code -ne 0) {
    Write-Output "ASSERT-FAIL: doc-check on the canary package expected 0, got '$($r.exit_code)'"
    Get-Content -Path $r.stdout | Select-Object -Last 5 | Write-Output
    $failures = $failures + 1
}

# 3. Mutation: drop the pinned --checkout continuation lines from a temp copy of
#    the runbook; the presented start then omits a pinned flag and the tooth
#    must FAIL (exit 1) - the doc cannot pass with a weakened launch command.
$mutated = Join-Path $env:TEMP 'm0t136_mutated_runbook.md'
Get-Content -Path $runbook | Where-Object { $_ -notmatch '^\s*--checkout ' } |
    Set-Content -Path $mutated -Encoding ascii
$r = Invoke-RawExit -FilePath python -ArgumentList @($docCheck, '--doc', $mutated)
if ($r.exit_code -eq 1) {
    Write-Output 'DETECTED: the mutated runbook (no pinned --checkout) fails the tooth'
} else {
    Write-Output "ASSERT-FAIL: doc-check on the mutated copy expected 1, got '$($r.exit_code)'"
    $failures = $failures + 1
}
Remove-Item -Path $mutated -ErrorAction SilentlyContinue

if ($failures -gt 0) {
    Write-Output "test_doc_check: $failures assertion failure(s)"
    exit 1
}
Write-Output 'test_doc_check: living docs pass, mutation detected'
exit 0
