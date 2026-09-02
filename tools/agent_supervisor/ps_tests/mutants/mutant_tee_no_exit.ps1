# MUTANT (never a harness): a -File script whose LAST statement is a native
# call piped through Tee-Object, with NO explicit exit. $LASTEXITCODE inside
# is 7, but the outer powershell.exe -File reports 0 to its caller.
# test_mutants_detected.ps1 asserts this lie is DETECTED.
& python -c "import sys; sys.exit(7)" 2>$null | Tee-Object -FilePath (Join-Path $env:TEMP 'm0t136_mutant_tee.txt')
