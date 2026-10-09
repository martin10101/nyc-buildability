#!/usr/bin/env bash
# test_doc_check.sh - the living launcher carries its pinned fail-closed guards,
# and a mutated copy that drops one is DETECTED (M0-T166, D-091 T2; analog of
# ps_tests/test_doc_check.ps1: living docs pass the tooth, a weakened copy fails).
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$(cd "$HERE/.." && pwd)/launch.sh"
failures=0

# The launcher's load-bearing fail-closed guard tokens. README.md documents the
# same contract; this tooth proves none can be silently removed.
GUARDS=(
    "LAUNCH_REFUSE_BINARY"
    "LAUNCH_REFUSE_ENV"
    "LAUNCH_REFUSE_GATE"
    "DISABLE_AUTOUPDATER=1"
    "the start gate refused"
)

contract_ok() {  # file -> 0 if every guard present, 1 otherwise
    local f="$1" g
    for g in "${GUARDS[@]}"; do
        grep -qF -- "$g" "$f" || return 1
    done
    return 0
}

# 1. The living launcher passes the tooth (every pinned guard present).
if contract_ok "$LAUNCHER"; then
    echo "ok: the living launcher carries every pinned fail-closed guard"
else
    echo "ASSERT-FAIL: the living launch.sh is missing a pinned guard"
    failures=$((failures + 1))
fi

# 2. Mutation: drop one pinned guard from a temp copy; the tooth must FAIL -
#    a launcher cannot pass with a weakened fail-closed guard.
mutated="$(mktemp)"
grep -vF -- "the start gate refused" "$LAUNCHER" > "$mutated"
if contract_ok "$mutated"; then
    echo "ASSERT-FAIL: a launcher without the start-gate refusal still passed the tooth"
    failures=$((failures + 1))
else
    echo "DETECTED: a launcher with the start-gate refusal removed FAILS the tooth"
fi
rm -f "$mutated"

if [ "$failures" -gt 0 ]; then
    echo "test_doc_check: $failures assertion failure(s)"
    exit 1
fi
echo "test_doc_check: living launcher passes, mutation detected"
exit 0
