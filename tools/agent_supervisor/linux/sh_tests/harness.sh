# harness.sh - raw-exit-code invocation harness for the Linux loop launch path
# (M0-T166, D-091 T2; the bash analog of ps_tests/harness.ps1).
#
# The operator launch path runs on bash, where the ONLY honest carrier of a
# child's exit code is $? read IMMEDIATELY after an UNPIPED invocation. Measured
# bash facts this harness is built on (proven by test_mutants_detected.sh against
# mutants/):
#   - an UNPIPED call with file redirection sets $? to the RAW child exit code;
#   - "child | tee file" leaves $? = tee's code (0), NOT the child's, unless you
#     read ${PIPESTATUS[0]}; a script whose LAST statement is such a pipeline
#     reports 0 to its caller even though the child exited nonzero;
#   - judging success by $? AFTER an intervening command greens a failed child;
#   - "child | grep ..." replaces $? with the LAST pipe stage's code (grep);
#   - a command that does not resolve never launches, so the harness checks the
#     program resolves FIRST and FAILS CLOSED (no verdict) when it does not -
#     never treating a non-launch as success (bash would otherwise return 127).
#
# Source this file, then call invoke_raw_exit <program> [args...]. It sets the
# globals RAWEXIT_CODE (empty when the command never launched), RAWEXIT_OK
# ("true"/"false"), RAWEXIT_REASON, RAWEXIT_ERROR, RAWEXIT_STDOUT, RAWEXIT_STDERR.
# Never pipe the invocation, never judge by a later $?, and always end runner
# scripts with an explicit exit.

invoke_raw_exit() {
    local program="${1:-}"
    shift || true
    RAWEXIT_STDOUT="$(mktemp)"
    RAWEXIT_STDERR="$(mktemp)"
    RAWEXIT_CODE=""
    RAWEXIT_OK="false"
    RAWEXIT_REASON=""
    RAWEXIT_ERROR=""
    # Fail closed: a program that cannot be resolved never launches, so it has NO
    # verdict and is NEVER ok (the bash analog of a CommandNotFoundException that
    # leaves $LASTEXITCODE unset in PowerShell).
    if ! { [ -n "$program" ] && { command -v "$program" >/dev/null 2>&1 || [ -x "$program" ]; }; }; then
        RAWEXIT_REASON="no_exit_code_fail_closed"
        RAWEXIT_ERROR="command not found: $program"
        return 0
    fi
    # Unpiped invocation; stdout/stderr go to FILES via redirection (redirection
    # is not a pipeline and does not disturb $?).
    "$program" "$@" >"$RAWEXIT_STDOUT" 2>"$RAWEXIT_STDERR"
    RAWEXIT_CODE=$?
    RAWEXIT_REASON="raw_exit_status"
    if [ "$RAWEXIT_CODE" -eq 0 ]; then
        RAWEXIT_OK="true"
    else
        RAWEXIT_OK="false"
    fi
    return 0
}
