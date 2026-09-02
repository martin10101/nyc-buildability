# test_mutants_detected.ps1 - piping / $? / cmd-pipes CANNOT green a failure
# (M0-T136 C-B5; D-024-R586, R589 paired mutations). Each mutant in mutants/
# is a broken harness discipline; every child in them really exits 7. This
# test runs each mutant exactly the way the runner runs tests
# (powershell.exe -NoProfile -ExecutionPolicy Bypass -File) and asserts the
# mutant LOSES or FAKES the raw 7 - proving the real harness rules are
# load-bearing, not stylistic.
$failures = 0
$mutants = Join-Path $PSScriptRoot 'mutants'

function Invoke-MutantFile {
    param([string]$Name)
    $global:LASTEXITCODE = $null
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $mutants $Name) 1>$null 2>$null
    return $global:LASTEXITCODE
}

# 1. $? after an intervening cmdlet greens a child that exited 7.
$code = Invoke-MutantFile 'mutant_dollar_q.ps1'
if ($code -eq 0) {
    Write-Output 'DETECTED: mutant_dollar_q reports 0 (green) for a child that exited 7'
} else {
    Write-Output "ASSERT-FAIL: mutant_dollar_q expected 0, got '$code'"
    $failures = $failures + 1
}

# 2. A -File script ending "native | Tee-Object" without an explicit exit
#    reports 0 to its caller even though the child exited 7.
$code = Invoke-MutantFile 'mutant_tee_no_exit.ps1'
if ($code -eq 0) {
    Write-Output 'DETECTED: mutant_tee_no_exit reports 0 (green) for a child that exited 7'
} else {
    Write-Output "ASSERT-FAIL: mutant_tee_no_exit expected 0, got '$code'"
    $failures = $failures + 1
}

# 3. A cmd.exe pipe replaces the raw 7 with the last pipe stage's code (1).
$code = Invoke-MutantFile 'mutant_cmd_pipe.ps1'
if ($code -eq 1) {
    Write-Output 'DETECTED: mutant_cmd_pipe reports 1 (findstr), the raw 7 is destroyed'
} else {
    Write-Output "ASSERT-FAIL: mutant_cmd_pipe expected 1, got '$code'"
    $failures = $failures + 1
}

# 4. Control: the REAL harness, over the same child, keeps the raw 7.
. (Join-Path $PSScriptRoot 'harness.ps1')
$r = Invoke-RawExit -FilePath python -ArgumentList @('-c', 'import sys; sys.exit(7)')
if ($r.exit_code -eq 7) {
    Write-Output 'CONTROL: Invoke-RawExit preserves the raw 7 the mutants lost'
} else {
    Write-Output "ASSERT-FAIL: control harness expected 7, got '$($r.exit_code)'"
    $failures = $failures + 1
}

if ($failures -gt 0) {
    Write-Output "test_mutants_detected: $failures assertion failure(s)"
    exit 1
}
Write-Output 'test_mutants_detected: every mutation detected'
exit 0
