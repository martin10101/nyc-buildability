"""Stdlib regression test for the operational read-only guard
(.claude/hooks/readonly_agent_guard.py).

Focus of this suite (owner directive, session 18): prove that a governed
read-only reviewer role is DENIED when it issues a repo-mutating `git` command
through a quoted / backslash-escaped `-C <path>` whose path contains a space —
the HIGH bypass caused by the regex consuming the `-C` value with `\\S+`. Uses a
SYNTHETIC spaced path in the command text, so the result does not depend on the
checkout directory (CI runners rarely have a space in the path). Also proves the
fix removed NO existing denial and NO existing allow, that non-governed
lead/producer/orchestrator calls still pass through, and that malformed payloads
fail closed.

Run: python tools/test_readonly_agent_guard.py
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / ".claude" / "hooks" / "readonly_agent_guard.py"

# A synthetic absolute path containing a space, in each quoting variant the
# runtime (Git Bash / PowerShell) supports. The guard inspects the command text
# only, so the path need not exist.
DQ = '"/srv/nyc zoning/repo"'          # double-quoted
SQ = "'/srv/nyc zoning/repo'"          # single-quoted
BS = "/srv/nyc\\ zoning/repo"          # backslash-escaped space (unquoted)

SIX_ROLES = [
    "progress-auditor",
    "code-reviewer",
    "security-reviewer",
    "data-contract-verifier",
    "ci-evidence-verifier",
    "control-plane-verifier",
]

FAILURES = []


def run_guard(payload_obj) -> subprocess.CompletedProcess:
    text = payload_obj if isinstance(payload_obj, str) else json.dumps(payload_obj)
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=text,
        capture_output=True,
        text=True,
        timeout=30,
    )


def decision(payload_obj):
    """Return 'DENY' or 'ALLOW' for a payload. Deny == exit 0 with a
    permissionDecision:deny JSON body (the guard's contract)."""
    r = run_guard(payload_obj)
    denied = '"permissionDecision": "deny"' in r.stdout
    return "DENY" if denied else "ALLOW", r


def bash_payload(agent, command):
    p = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
         "tool_input": {"command": command}}
    if agent is not None:
        p["agent_type"] = agent
    return p


def tool_payload(agent, tool):
    p = {"hook_event_name": "PreToolUse", "tool_name": tool,
         "tool_input": {"file_path": "x", "content": "y"}}
    if agent is not None:
        p["agent_type"] = agent
    return p


def check(name, expect, payload_obj):
    got, r = decision(payload_obj)
    ok = got == expect
    print(f"{'PASS' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  [expect={expect} got={got} rc={r.returncode}]"))
    if not ok:
        FAILURES.append(name)


def main() -> int:
    R = "code-reviewer"  # representative governed reviewer

    # 1. THE FIX — governed reviewer DENIED on spaced -C mutations (owner's list),
    #    across double-quote, single-quote, and backslash-escaped variants.
    for verb, tail in [("push", "origin HEAD"), ("reset", "--hard origin/main"),
                       ("commit", "-m x"), ("tag", "zzz"), ("checkout", "main")]:
        for qname, q in [("dq", DQ), ("sq", SQ), ("bs", BS)]:
            check(f"deny git -C <spaced:{qname}> {verb}", "DENY",
                  bash_payload(R, f"git -C {q} {verb} {tail}"))

    # 1b. Nuanced mutating sub-commands through a spaced -C.
    check("deny git -C <spaced> branch -D", "DENY",
          bash_payload(R, f"git -C {DQ} branch -D feature"))
    check("deny git -C <spaced> config set", "DENY",
          bash_payload(R, f"git -C {DQ} config user.email a@b.com"))
    check("deny git -C <spaced> remote add", "DENY",
          bash_payload(R, f"git -C {DQ} remote add origin url"))
    check("deny git -C <spaced> worktree add", "DENY",
          bash_payload(R, f"git -C {DQ} worktree add ../wt"))
    check("deny git -C <spaced> stash", "DENY",
          bash_payload(R, f"git -C {DQ} stash"))
    check("deny chained: status && -C <spaced> push", "DENY",
          bash_payload(R, f"git status && git -C {DQ} push"))

    # 2. NO OVER-DENIAL — read-only git through the same spaced -C stays ALLOWED.
    for verb in ["status", "diff", "log --oneline -5", "show HEAD",
                 "config --get user.email", "branch --list", "remote -v",
                 "worktree list"]:
        check(f"allow git -C <spaced> {verb.split()[0]}", "ALLOW",
              bash_payload(R, f"git -C {DQ} {verb}"))
    check("allow -C <spaced> log piped to grep", "ALLOW",
          bash_payload(R, f"git -C {DQ} log | grep fix"))

    # 3. EXISTING DENIALS PRESERVED (governed reviewer).
    check("deny Write tool", "DENY", tool_payload(R, "Write"))
    check("deny Edit tool", "DENY", tool_payload(R, "Edit"))
    check("deny MultiEdit tool", "DENY", tool_payload(R, "MultiEdit"))
    check("deny git commit (no -C)", "DENY", bash_payload(R, "git commit -m x"))
    check("deny git -C /srv/repo commit (no space)", "DENY",
          bash_payload(R, "git -C /srv/repo commit -m x"))
    check("deny gh pr create", "DENY",
          bash_payload(R, "gh pr create --title t --body b"))
    check("deny project_control accept", "DENY",
          bash_payload(R, "python tools/project_control.py accept M0-T019"))
    check("deny rm -rf", "DENY", bash_payload(R, "rm -rf build"))
    check("deny redirect to file", "DENY", bash_payload(R, "echo x > out.txt"))
    check("deny npm install", "DENY", bash_payload(R, "npm install left-pad"))

    # 4. EXISTING ALLOWS PRESERVED (governed reviewer).
    check("allow git status", "ALLOW", bash_payload(R, "git status"))
    check("allow git log", "ALLOW", bash_payload(R, "git log --oneline -20"))
    check("allow git diff", "ALLOW", bash_payload(R, "git diff HEAD~1"))
    check("allow pytest run", "ALLOW", bash_payload(R, "python -m pytest tools/"))
    check("allow node --test", "ALLOW",
          bash_payload(R, "node --test apps/web/scripts/tests/*.test.mjs"))
    check("allow redirect to /dev/null", "ALLOW",
          bash_payload(R, "git status 2>/dev/null"))
    check("allow gh pr view (read)", "ALLOW",
          bash_payload(R, "gh pr view 64 --json headRefOid"))

    # 5. ALL SIX governed roles are enforced (spaced -C push denied for each);
    #    a non-governed role passes through.
    for role in SIX_ROLES:
        check(f"role governed: {role} deny spaced push", "DENY",
              bash_payload(role, f"git -C {DQ} push"))
    check("non-governed lead (no agent_type) push allowed", "ALLOW",
          bash_payload(None, f"git -C {DQ} push"))
    check("non-governed producer (frontend-engineer) push allowed", "ALLOW",
          bash_payload("frontend-engineer", f"git -C {DQ} push"))
    check("non-governed orchestrator push allowed", "ALLOW",
          bash_payload("orchestrator", f"git -C {DQ} push"))

    # 6. FAIL CLOSED on malformed payloads.
    check("fail-closed: non-JSON payload", "DENY", "this is not json")
    check("fail-closed: JSON non-object (array)", "DENY", "[1,2,3]")

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): " + ", ".join(FAILURES))
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
