# MUTANT (never a harness): a script whose LAST statement is a native call piped
# through tee, with NO explicit exit and NO pipefail. $? INSIDE the pipeline would
# be 7 via ${PIPESTATUS[0]}, but the script reports 0 (tee's code) to its caller.
# test_mutants_detected.sh asserts this lie is DETECTED.
"${PYTHON:-python3}" -c 'import sys; sys.exit(7)' 2>/dev/null | tee "$(mktemp)" >/dev/null
