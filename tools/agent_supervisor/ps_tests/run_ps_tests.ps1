# run_ps_tests.ps1 - run every ps_tests\test_*.ps1 in its own real
# powershell.exe -File process (M0-T136 C-B5; D-024-R586, R589).
#
# Each test runs exactly the way an operator script runs: a fresh
# powershell.exe -NoProfile -ExecutionPolicy Bypass -File process, whose exit
# code is read raw from $LASTEXITCODE immediately after the unpiped call.
# The runner is fail-fast and fail-closed: no tests found is a failure, the
# first failing test ends the run with that test's RAW exit code, and the
# script always ends with an explicit exit statement (the exact discipline
# mutant_tee_no_exit.ps1 proves is load-bearing).
$tests = @(Get-ChildItem -Path $PSScriptRoot -Filter 'test_*.ps1' | Sort-Object Name)
if ($tests.Count -eq 0) {
    Write-Output 'run_ps_tests: NO test_*.ps1 found (fail closed)'
    exit 1
}
foreach ($test in $tests) {
    Write-Output "--- $($test.Name)"
    $global:LASTEXITCODE = $null
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $test.FullName
    if ($null -eq $LASTEXITCODE) {
        Write-Output "FAIL $($test.Name): no exit code observed (fail closed)"
        exit 1
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Output "FAIL $($test.Name): exit $LASTEXITCODE"
        exit $LASTEXITCODE
    }
    Write-Output "PASS $($test.Name)"
}
Write-Output "run_ps_tests: $($tests.Count) test file(s) passed"
exit $LASTEXITCODE
