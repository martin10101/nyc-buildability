# run_ps_tests.ps1 - run every controller_update ps_tests\test_*.ps1 in its own
# real powershell.exe -File process (M0-T138; D-024-R612/R613, mirroring the
# accepted tools/agent_supervisor/ps_tests runner discipline).
#
# Fail-fast and fail-closed: no tests found is a failure, the first failing
# test ends the run with that test's RAW exit code, and the script always ends
# with an explicit exit statement.
$tests = @(Get-ChildItem -Path $PSScriptRoot -Filter 'test_*.ps1' | Sort-Object Name)
if ($tests.Count -eq 0) {
    Write-Output 'run_ps_tests(controller_update): NO test_*.ps1 found (fail closed)'
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
Write-Output "run_ps_tests(controller_update): $($tests.Count) test file(s) passed"
exit $LASTEXITCODE
