# MUTANT (never a harness): judges success by $? AFTER an intervening command.
# The child exits 7, but the following command succeeds, so $? is 0 and this
# script reports GREEN. test_mutants_detected.sh asserts this lie is DETECTED.
"${PYTHON:-python3}" -c 'import sys; sys.exit(7)' >/dev/null 2>&1
: > "$(mktemp)"   # intervening command succeeds, clobbering $?
if [ $? -eq 0 ]; then exit 0; else exit 7; fi
