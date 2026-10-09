#!/usr/bin/env bash
# test_mutants_detected.sh - piping / $?-after-a-command / grep-pipes CANNOT green
# a failure (M0-T166, D-091 T2; analog of ps_tests/test_mutants_detected.ps1).
# Each mutant in mutants/ is a broken harness discipline; every child in them
# really exits 7. This test runs each mutant exactly the way the runner runs tests
# (a fresh `bash <file>`) and asserts the mutant LOSES or FAKES the raw 7 - proving
# the real harness rules are load-bearing, not stylistic.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./harness.sh
. "$HERE/harness.sh"
MUTANTS="$HERE/mutants"
PY="${PYTHON:-python3}"
failures=0

run_mutant() {  # name -> echoes the mutant's raw exit code
    bash "$MUTANTS/$1" >/dev/null 2>&1
    echo $?
}

# 1. A pipeline through tee with no explicit exit reports 0 to the caller even
#    though the child exited 7.
code=$(run_mutant mutant_pipe_tee.sh)
if [ "$code" = "0" ]; then
    echo "DETECTED: mutant_pipe_tee reports 0 (green) for a child that exited 7"
else
    echo "ASSERT-FAIL: mutant_pipe_tee expected 0, got '$code'"
    failures=$((failures + 1))
fi

# 2. Judging by $? after an intervening (successful) command greens a child that
#    exited 7.
code=$(run_mutant mutant_dollar_q.sh)
if [ "$code" = "0" ]; then
    echo "DETECTED: mutant_dollar_q reports 0 (green) for a child that exited 7"
else
    echo "ASSERT-FAIL: mutant_dollar_q expected 0, got '$code'"
    failures=$((failures + 1))
fi

# 3. A grep pipe replaces the raw 7 with the last pipe stage's code (grep -> 1).
code=$(run_mutant mutant_grep_pipe.sh)
if [ "$code" = "1" ]; then
    echo "DETECTED: mutant_grep_pipe reports 1 (grep), the raw 7 is destroyed"
else
    echo "ASSERT-FAIL: mutant_grep_pipe expected 1, got '$code'"
    failures=$((failures + 1))
fi

# 4. Control: the REAL harness, over the same child, keeps the raw 7.
invoke_raw_exit "$PY" -c 'import sys; sys.exit(7)'
if [ "$RAWEXIT_CODE" = "7" ]; then
    echo "CONTROL: invoke_raw_exit preserves the raw 7 the mutants lost"
else
    echo "ASSERT-FAIL: control harness expected 7, got '$RAWEXIT_CODE'"
    failures=$((failures + 1))
fi

if [ "$failures" -gt 0 ]; then
    echo "test_mutants_detected: $failures assertion failure(s)"
    exit 1
fi
echo "test_mutants_detected: every mutation detected"
exit 0
