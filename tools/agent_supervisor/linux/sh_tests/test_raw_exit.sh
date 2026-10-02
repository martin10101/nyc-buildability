#!/usr/bin/env bash
# test_raw_exit.sh - the harness preserves the raw child exit code and fails
# closed when a command never launches (M0-T166, D-091 T2; analog of
# ps_tests/test_raw_exit.ps1).
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./harness.sh
. "$HERE/harness.sh"

failures=0
PY="${PYTHON:-python3}"

assert_eq() {  # actual expected message
    if [ "$1" != "$2" ]; then
        echo "ASSERT-FAIL: $3 (got '$1', expected '$2')"
        failures=$((failures + 1))
    fi
}
assert_file_contains() {  # file needle message
    if ! grep -qF -- "$2" "$1" 2>/dev/null; then
        echo "ASSERT-FAIL: $3 (file '$1' missing '$2')"
        failures=$((failures + 1))
    fi
}

# 1. Raw nonzero code preserved exactly (7 stays 7, never collapsed to 1/0).
invoke_raw_exit "$PY" -c 'import sys; sys.exit(7)'
assert_eq "$RAWEXIT_CODE" "7" "raw exit 7 preserved"
assert_eq "$RAWEXIT_OK" "false" "exit 7 must not be ok"
assert_eq "$RAWEXIT_REASON" "raw_exit_status" "reason is raw_exit_status"

# 2. Success is exit 0, from the same unpiped read.
invoke_raw_exit "$PY" -c 'import sys; sys.exit(0)'
assert_eq "$RAWEXIT_CODE" "0" "raw exit 0"
assert_eq "$RAWEXIT_OK" "true" "exit 0 must be ok"

# 3. A command that never launches FAILS CLOSED: no exit code, never ok.
invoke_raw_exit "no-such-executable-m0t166-xyzzy"
assert_eq "$RAWEXIT_CODE" "" "not-found has no exit code"
assert_eq "$RAWEXIT_OK" "false" "a command with no exit code is never ok"
assert_eq "$RAWEXIT_REASON" "no_exit_code_fail_closed" "not-found fails closed"

# 4. Captured stdout/stderr land in the named files, and the raw code (5) rides
#    along.
invoke_raw_exit "$PY" -c 'import sys; sys.stdout.write("OUT-MARK"); sys.stderr.write("ERR-MARK"); sys.exit(5)'
assert_eq "$RAWEXIT_CODE" "5" "raw exit 5"
assert_file_contains "$RAWEXIT_STDOUT" "OUT-MARK" "stdout capture carries OUT-MARK"
assert_file_contains "$RAWEXIT_STDERR" "ERR-MARK" "stderr capture carries ERR-MARK"

if [ "$failures" -gt 0 ]; then
    echo "test_raw_exit: $failures assertion failure(s)"
    exit 1
fi
echo "test_raw_exit: all assertions passed"
exit 0
