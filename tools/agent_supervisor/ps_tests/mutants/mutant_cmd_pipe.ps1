# MUTANT (never a harness): routes the native call through a cmd.exe pipe.
# cmd's pipe replaces the exit code with the LAST stage's code (findstr -> 1),
# so the raw 7 is destroyed. test_mutants_detected.ps1 asserts this is DETECTED.
& cmd /c 'python -c "import sys; sys.exit(7)" | findstr /v xyzzy'
exit $LASTEXITCODE
