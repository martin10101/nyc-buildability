# MUTANT (never a harness): routes the native call through a grep pipe. Without
# pipefail the pipeline's exit is the LAST stage's (grep), so the raw 7 is
# destroyed: grep selects no line from the empty output and exits 1.
# test_mutants_detected.sh asserts this is DETECTED (exit 1, not 7).
"${PYTHON:-python3}" -c 'import sys; sys.exit(7)' | grep -v xyzzy
exit $?
