#!/usr/bin/env bash
# launch.sh - the Linux loop launcher (M0-T166, D-091 T2; owner directive D-091).
#
# The Linux analog of the owner's Windows launch path (docs/MRL_LAUNCH_RUNBOOK.md
# + tools/agent_supervisor/ps_tests). It is a THIN, FAIL-CLOSED wrapper that:
#   1. carries the Linux autoupdater belt (DISABLE_AUTOUPDATER=1) so a bare
#      `claude --version`/`--help` child launched with env=None inherits it
#      (M0-T165 process.bare_probe_env; D-091 T1, runbook section 13);
#   2. fails closed when the claude binary is missing or not executable;
#   3. fails closed when any declared required env var is unset or empty;
#   4. runs the START GATE and REFUSES to start when the gate refuses;
#   5. only on a passing gate hands the (already-gated) start to the controller.
#
# It NEVER pushes, NEVER merges, and NEVER starts a live run of its own: step 5
# execs the controller start command, which carries the owner/gate guards. The
# five fail-closed guards above are proven load-bearing by sh_tests/test_doc_check.sh.
#
# Installing or enabling the systemd unit (nyc-supervisor.service.template) and the
# live certified start are OWNER-TYPED commissioning steps (runbook section 12 /
# D-091 T8) - NEVER run by an agent.
#
# Everything is environment-driven so the harness can drive it with fakes and no
# live provider (tools/test_agent_supervisor_linux_launch.py):
#   NYC_SUP_CLAUDE_BIN   (required) path to the claude binary; must be executable.
#                        Empty falls back to `claude` on PATH.
#   NYC_SUP_GATE_CMD     (required) the start-gate command; a nonzero exit REFUSES.
#   NYC_SUP_START_CMD    (required) the controller start command, run ONLY when the
#                        gate passed. It must be the gated controller start; the
#                        launcher adds no push, merge, or live run of its own.
#   NYC_SUP_REQUIRED_ENV (optional) space-separated env var NAMES that must all be
#                        set and non-empty before the gate runs.
set -u

LAUNCH_REFUSE_BINARY=3
LAUNCH_REFUSE_ENV=4
LAUNCH_REFUSE_GATE=5
LAUNCH_MISCONFIG=6

# The Linux autoupdater belt (D-091 T1; runbook section 13). A child launched with
# env=None inherits it; the systemd unit sets the identical value.
export DISABLE_AUTOUPDATER=1

refuse() {  # code, message
    echo "launch.sh: REFUSE: $2" >&2
    exit "$1"
}

# --- required launcher configuration (fail closed on misconfiguration) ------
: "${NYC_SUP_GATE_CMD:=}"
: "${NYC_SUP_START_CMD:=}"
: "${NYC_SUP_CLAUDE_BIN:=}"
: "${NYC_SUP_REQUIRED_ENV:=}"
[ -n "$NYC_SUP_GATE_CMD" ] \
    || refuse "$LAUNCH_MISCONFIG" "NYC_SUP_GATE_CMD is not set (no start gate to consult)"
[ -n "$NYC_SUP_START_CMD" ] \
    || refuse "$LAUNCH_MISCONFIG" "NYC_SUP_START_CMD is not set (nothing to start)"

# --- 2. the claude binary must exist and be executable (fail closed) --------
if [ -z "$NYC_SUP_CLAUDE_BIN" ]; then
    NYC_SUP_CLAUDE_BIN="$(command -v claude 2>/dev/null || true)"
fi
{ [ -n "$NYC_SUP_CLAUDE_BIN" ] && [ -x "$NYC_SUP_CLAUDE_BIN" ]; } \
    || refuse "$LAUNCH_REFUSE_BINARY" \
       "claude binary missing or not executable (NYC_SUP_CLAUDE_BIN='$NYC_SUP_CLAUDE_BIN'); failing closed before any provider contact"

# --- 3. every declared required env var must be set and non-empty -----------
for name in $NYC_SUP_REQUIRED_ENV; do
    value="${!name:-}"
    [ -n "$value" ] \
        || refuse "$LAUNCH_REFUSE_ENV" \
           "required env '$name' is unset or empty; failing closed before any provider contact"
done

# --- 4. the start gate: REFUSE to start when it refuses ----------------------
# Unpiped invocation; $? is the gate's RAW exit code. Never piped, never judged by
# a later command's status (the shell-routing discipline sh_tests/harness.sh pins).
# shellcheck disable=SC2086
$NYC_SUP_GATE_CMD
gate_code=$?
if [ "$gate_code" -ne 0 ]; then
    refuse "$LAUNCH_REFUSE_GATE" "the start gate refused (exit $gate_code); the loop is NOT started"
fi

# --- 5. gate passed: hand the already-gated start to the controller ----------
# The launcher adds NO push, NO merge, and NO live run of its own; the controller
# start command below carries the owner/gate guards.
# shellcheck disable=SC2086
exec $NYC_SUP_START_CMD
