#!/usr/bin/env bash
# run_sh_tests.sh - run every sh_tests/test_*.sh in its own bash process
# (M0-T166, D-091 T2; the bash analog of ps_tests/run_ps_tests.ps1).
#
# Each test runs the way an operator script runs: a fresh `bash` process on the
# test file, whose exit code is read raw from $? immediately after the UNPIPED
# call. Fail-fast and fail-closed: no tests found is a failure, the first failing
# test ends the run with that test's RAW exit code, and the script always ends
# with an explicit exit (the discipline mutant_pipe_tee.sh proves is load-bearing).
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
shopt -s nullglob
tests=("$HERE"/test_*.sh)
if [ "${#tests[@]}" -eq 0 ]; then
    echo "run_sh_tests: NO test_*.sh found (fail closed)"
    exit 1
fi
for t in "${tests[@]}"; do
    echo "--- $(basename "$t")"
    bash "$t"
    code=$?
    if [ "$code" -ne 0 ]; then
        echo "FAIL $(basename "$t"): exit $code"
        exit "$code"
    fi
    echo "PASS $(basename "$t")"
done
echo "run_sh_tests: ${#tests[@]} test file(s) passed"
exit 0
