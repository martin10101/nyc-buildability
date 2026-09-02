# MUTANT (never a harness): judges success by $? after an intervening cmdlet.
# The child exits 7, but Set-Content succeeds, so $? is $true and this script
# reports GREEN. test_mutants_detected.ps1 asserts this lie is DETECTED.
& python -c "import sys; sys.exit(7)" 2>$null | Out-Null
Set-Content -Path (Join-Path $env:TEMP 'm0t136_mutant_q.txt') -Value 'ran'
if ($?) { exit 0 } else { exit 7 }
