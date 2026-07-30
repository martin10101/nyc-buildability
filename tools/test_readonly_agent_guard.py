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

M0-T028 (B-015) additions - fail-closed identity resolution, tested against
the OBSERVED payload shapes (project-control/reports/
M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md): a NAMED spawn's agent_type carries the
SPAWN NAME (not the role) plus a name-derived agent_id and must fail CLOSED;
an agent_id-only payload is spawned-unknown (fail closed); a roster producer
identity (backend-engineer) passes through entirely; the lead (no identity
keys at all) passes through; an unreadable roster fails closed (proven by
running a byte-identical copy of the guard from a temp tree with no ../agents
directory); and the D-004-R100 ride-along - every hook command in
.claude/settings.json keeps its project-path reference double-quoted so a
repository path containing a space still resolves to ONE script-path token.

Run: python tools/test_readonly_agent_guard.py
"""
import json
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / ".claude" / "hooks" / "readonly_agent_guard.py"

# A synthetic absolute path containing a space, in each quoting variant the
# runtime (Git Bash / PowerShell) supports. The guard inspects the command text
# only, so the path need not exist.
DQ = '"/srv/nyc zoning/repo"'          # double-quoted
SQ = "'/srv/nyc zoning/repo'"          # single-quoted
BS = "/srv/nyc\\ zoning/repo"          # backslash-escaped space (unquoted)
NL = chr(10)                            # explicit newline (avoid \\n f-string ambiguity)

GOVERNED_ROLES = [
    "progress-auditor",
    "code-reviewer",
    "security-reviewer",
    "data-contract-verifier",
    "ci-evidence-verifier",
    "control-plane-verifier",
    "directive-compliance-verifier",
]

FAILURES = []


def run_guard(payload_obj, guard_path=None) -> subprocess.CompletedProcess:
    text = payload_obj if isinstance(payload_obj, str) else json.dumps(payload_obj)
    return subprocess.run(
        [sys.executable, str(guard_path or GUARD)],
        input=text,
        capture_output=True,
        text=True,
        timeout=30,
    )


def decision(payload_obj, guard_path=None):
    """Return 'DENY' or 'ALLOW' for a payload. Deny == exit 0 with a
    permissionDecision:deny JSON body (the guard's contract)."""
    r = run_guard(payload_obj, guard_path)
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


def check(name, expect, payload_obj, guard_path=None):
    got, r = decision(payload_obj, guard_path)
    ok = got == expect
    print(f"{'PASS' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  [expect={expect} got={got} rc={r.returncode}]"))
    if not ok:
        FAILURES.append(name)


def check_static(name, ok):
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        FAILURES.append(name)


def check_settings_commands():
    """D-004-R100 (AS-5): every hook command in .claude/settings.json is the
    canonical single-string form with the ${CLAUDE_PROJECT_DIR} project-path
    reference DOUBLE-QUOTED. Proof: substitute a synthetic project root that
    CONTAINS A SPACE, shlex-split, and require the script path to survive as
    ONE token; then substitute the REAL repo root and require that token to
    be an existing hook file. Independent of the checkout path, so it proves
    resolution on any machine, including one whose repo path has a space."""
    data = json.loads(
        (REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    entries = []
    for matchers in (data.get("hooks") or {}).values():
        for matcher in matchers:
            for hook in matcher.get("hooks") or []:
                entries.append(hook)
    check_static("settings: hook entries present", len(entries) >= 1)
    spaced_root = "/srv/nyc zoning/repo"
    real_root = str(REPO).replace("\\", "/")
    for i, hook in enumerate(entries):
        cmd = hook.get("command") or ""
        label = f"settings hook #{i}"
        # The legacy {"command": "python", "args": [...]} split form is
        # retired; a leftover args list would defeat the quoting proof.
        check_static(f"{label}: no legacy args list", "args" not in hook)
        try:
            spaced = shlex.split(
                cmd.replace("${CLAUDE_PROJECT_DIR}", spaced_root), posix=True)
        except ValueError:
            spaced = []
        check_static(
            f"{label}: spaced-root script path survives as ONE token",
            len(spaced) == 2 and spaced[1].startswith(spaced_root + "/"))
        try:
            real = shlex.split(
                cmd.replace("${CLAUDE_PROJECT_DIR}", real_root), posix=True)
        except ValueError:
            real = []
        check_static(
            f"{label}: real-root token is an existing hook file",
            len(real) == 2 and Path(real[1]).is_file())


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

    # 1c. Operator-adjacency — a mutating git hidden after ANY shell separator
    #     (glued or spaced, incl. newline / subst / backtick / brace / redirect)
    #     must still be DENIED. These 8 vectors bypassed the first shlex-only
    #     implementation (found by the config-security-review wave, session 18).
    check("deny glued ; status;git -C push", "DENY",
          bash_payload(R, f"git status;git -C {DQ} push"))
    check("deny newline echo<LF>git -C push", "DENY",
          bash_payload(R, f"echo hi\ngit -C {DQ} push"))
    check("deny newline status<LF>git -C push", "DENY",
          bash_payload(R, f"git -C {DQ} status\ngit -C {DQ} push"))
    check("deny glued subshell (git -C push)", "DENY",
          bash_payload(R, f"(git -C {DQ} push)"))
    check("deny cmd-subst x=$(git -C push)", "DENY",
          bash_payload(R, f"x=$(git -C {DQ} push)"))
    check("deny backtick x=`git -C push`", "DENY",
          bash_payload(R, f"x=`git -C {DQ} push`"))
    check("deny glued pipe true|git -C push", "DENY",
          bash_payload(R, f"true|git -C {DQ} push"))
    check("deny brace group { git -C push; }", "DENY",
          bash_payload(R, f"{{ git -C {DQ} push; }}"))
    check("deny glued redirect push>log", "DENY",
          bash_payload(R, f"git -C {DQ} push>log"))

    # 1d. Quoted separators must NOT over-deny read-only git (regression guard).
    check("allow -C log --grep with ;| in quotes", "ALLOW",
          bash_payload(R, f'git -C {DQ} log --grep "fix;feat|bug"'))
    check("allow -C log --pretty parens in quotes", "ALLOW",
          bash_payload(R, f'git -C {DQ} log --pretty=format:"%h (%an)"'))
    check("allow subshell of read-only (git -C status)", "ALLOW",
          bash_payload(R, f"(git -C {DQ} status)"))

    # 1e. Prefix / wrapper / case / dynamic vectors — a spaced-`-C` mutation must
    #     DENY regardless of a leading assignment, command wrapper, binary case,
    #     backslash line-continuation, or a verb hidden in a variable/substitution
    #     (found by the wave-2 code + security reviewers, session 18).
    check("deny env-prefix VAR=v git -C push", "DENY",
          bash_payload(R, f"VAR=v git -C {DQ} push"))
    check("deny multi-assign A=1 B=2 git -C commit", "DENY",
          bash_payload(R, f"A=1 B=2 git -C {DQ} commit -m x"))
    check("deny wrapper env git -C push", "DENY",
          bash_payload(R, f"env git -C {DQ} push"))
    check("deny wrapper sudo git -C push", "DENY",
          bash_payload(R, f"sudo git -C {DQ} push"))
    check("deny wrapper command git -C push", "DENY",
          bash_payload(R, f"command git -C {DQ} push"))
    check("deny wrapper exec git -C reset", "DENY",
          bash_payload(R, f"exec git -C {DQ} reset --hard"))
    check("deny case-variant GIT -C push", "DENY",
          bash_payload(R, f"GIT -C {DQ} push"))
    check("deny case-variant Git.exe -C push", "DENY",
          bash_payload(R, f"Git.exe -C {DQ} push"))
    check("deny line-continuation (space) push", "DENY",
          bash_payload(R, f"git -C {DQ} \\{NL} push"))
    check("deny line-continuation (no-space) push", "DENY",
          bash_payload(R, f"git -C {DQ} \\{NL}push"))
    check("deny CRLF line-continuation push", "DENY",
          bash_payload(R, f"git -C {DQ} \\{chr(13)}{NL}push"))
    check("deny verb-in-variable git -C \"$c\"", "DENY",
          bash_payload(R, f'git -C {DQ} "$c"'))
    check("deny verb-in-subst git -C $(printf push)", "DENY",
          bash_payload(R, f"git -C {DQ} $(printf push)"))
    check("deny bare git -C <tree> (no verb)", "DENY",
          bash_payload(R, f"git -C {DQ}"))

    # 1f. The prefix / case forms must still ALLOW read-only sub-commands, and a
    #     dynamic -C VALUE with an explicit read-only verb must ALLOW.
    check("allow VAR=v git -C status", "ALLOW",
          bash_payload(R, f"VAR=v git -C {DQ} status"))
    check("allow env git -C log", "ALLOW",
          bash_payload(R, f"env git -C {DQ} log --oneline"))
    check("allow GIT -C diff (case, read-only)", "ALLOW",
          bash_payload(R, f"GIT -C {DQ} diff"))
    check("allow git -C \"$REPO\" status (dynamic tree, explicit read verb)", "ALLOW",
          bash_payload(R, 'git -C "$REPO" status'))

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

    # 5. ALL governed roles are enforced (spaced -C push denied for each);
    #    a non-governed role passes through.
    for role in GOVERNED_ROLES:
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

    # 7. B-015 FIX - the ACTUAL teammate payload shape (M0-T028 primary
    #    evidence): a NAMED spawn's agent_type carries the SPAWN NAME (not
    #    the role) plus a name-derived agent_id; the role appears in NO
    #    payload field. Such an identity is not a roster definition and must
    #    fail CLOSED: mutations denied, read-only inspection still allowed.
    TM_NAME = "m0t028-diag-probe"
    TM_ID = "am0t028-diag-probe-0f3a"

    def teammate_bash(command):
        p = bash_payload(TM_NAME, command)
        p["agent_id"] = TM_ID
        return p

    def teammate_tool(tool):
        p = tool_payload(TM_NAME, tool)
        p["agent_id"] = TM_ID
        return p

    for tool in ["Write", "Edit", "MultiEdit", "NotebookEdit"]:
        check(f"teammate shape: deny {tool}", "DENY", teammate_tool(tool))
    check("teammate shape: deny git commit", "DENY",
          teammate_bash("git commit -m x"))
    check("teammate shape: deny sentinel redirect", "DENY",
          teammate_bash("echo escaped > sentinel.txt"))
    check("teammate shape: deny rm -rf", "DENY", teammate_bash("rm -rf build"))
    check("teammate shape: deny project_control accept", "DENY",
          teammate_bash("python tools/project_control.py accept M0-T028"))
    check("teammate shape: deny spaced -C push", "DENY",
          teammate_bash(f"git -C {DQ} push"))
    check("teammate shape: allow pwd", "ALLOW", teammate_bash("pwd"))
    check("teammate shape: allow git status", "ALLOW",
          teammate_bash("git status"))
    check("teammate shape: allow git rev-parse HEAD", "ALLOW",
          teammate_bash("git rev-parse HEAD"))
    check("teammate shape: allow gh pr view (read)", "ALLOW",
          teammate_bash("gh pr view 64 --json headRefOid"))
    check("teammate shape: allow pytest run", "ALLOW",
          teammate_bash("python -m pytest tools/"))

    # 8. agent_id present WITHOUT agent_type/agentType = spawned-unknown:
    #    fail CLOSED on mutations, read-only still allowed.
    def id_only_bash(command):
        return {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                "agent_id": "a1b2c3d4e5f6",
                "tool_input": {"command": command}}

    check("id-only: deny git commit", "DENY", id_only_bash("git commit -m x"))
    check("id-only: deny redirect to file", "DENY",
          id_only_bash("echo x > out.txt"))
    check("id-only: deny Write tool", "DENY",
          {"hook_event_name": "PreToolUse", "tool_name": "Write",
           "agent_id": "a1b2c3d4e5f6",
           "tool_input": {"file_path": "x", "content": "y"}})
    check("id-only: allow git status", "ALLOW", id_only_bash("git status"))
    check("id-only: allow pwd", "ALLOW", id_only_bash("pwd"))

    # 9. Roster producer identity (an UNNAMED spawn carries its role in
    #    agent_type): NOT governed - passes through entirely, mutations
    #    included, exactly as before the fix.
    def producer_bash(command):
        p = bash_payload("backend-engineer", command)
        p["agent_id"] = "0e1f2a3b4c5d"  # runtime id is present for real spawns
        return p

    check("producer roster id: mutating git ALLOWED (not governed)", "ALLOW",
          producer_bash("git commit -m x"))
    check("producer roster id: spaced -C push ALLOWED (not governed)", "ALLOW",
          producer_bash(f"git -C {DQ} push"))
    producer_write = tool_payload("backend-engineer", "Write")
    producer_write["agent_id"] = "0e1f2a3b4c5d"
    check("producer roster id: Write tool ALLOWED (not governed)", "ALLOW",
          producer_write)

    # 9b. Harness built-in agent types are NOT roster definitions -> fail
    #     closed (intended under ADR-005: only roster identities may write).
    check("built-in type general-purpose: deny git commit", "DENY",
          bash_payload("general-purpose", "git commit -m x"))
    check("built-in type general-purpose: allow git log", "ALLOW",
          bash_payload("general-purpose", "git log --oneline -5"))

    # 10. Lead/main session payload carries NO identity key at all (observed
    #     baseline shape) -> passes through even for mutations.
    check("lead shape (no identity keys): mutation allowed", "ALLOW",
          {"hook_event_name": "PreToolUse", "tool_name": "Bash",
           "session_id": "s", "prompt_id": "p", "cwd": "/srv/repo",
           "tool_input": {"command": "git commit -m x"}})

    # 11. ROSTER-READ FAILURE fails CLOSED. The guard resolves the roster
    #     RELATIVE to its own file, so running a byte-identical COPY of the
    #     guard from a temp tree with no `../agents` directory exercises the
    #     real missing-roster path through this same subprocess harness (no
    #     monkeypatching or in-process import needed).
    with tempfile.TemporaryDirectory() as td:
        hooks_dir = Path(td) / "hooks"
        hooks_dir.mkdir()
        guard_copy = hooks_dir / "readonly_agent_guard.py"
        guard_copy.write_bytes(GUARD.read_bytes())
        check("roster-fail: producer id fails closed (deny commit)", "DENY",
              producer_bash("git commit -m x"), guard_path=guard_copy)
        check("roster-fail: producer id read-only still allowed", "ALLOW",
              producer_bash("git status"), guard_path=guard_copy)
        check("roster-fail: governed reviewer still denied", "DENY",
              bash_payload(R, "git commit -m x"), guard_path=guard_copy)
        check("roster-fail: lead (no identity) still passes", "ALLOW",
              bash_payload(None, "git commit -m x"), guard_path=guard_copy)

    # 12. D-004-R100 ride-along: settings.json hook commands are space-safe.
    check_settings_commands()

    # 13. G5 C3 - fail-closed exception envelope. Malformed tool_input shapes
    #     that survive identity resolution used to CRASH the hook (exit 1, no
    #     decision emitted = the harness proceeds = fail OPEN). With the
    #     envelope they must DENY. The lead (no identity keys) returns before
    #     tool handling, so it stays unaffected regardless of shape.
    p = bash_payload(R, "irrelevant")
    p["tool_input"] = "not-a-dict"
    check("C3: governed + tool_input as string -> deny", "DENY", p)
    p = bash_payload(R, "irrelevant")
    p["tool_input"] = ["not", "a", "dict"]
    check("C3: governed + tool_input as list -> deny", "DENY", p)
    p = bash_payload(R, "x")
    p["tool_input"] = {"command": 42}
    check("C3: governed + command as int -> deny", "DENY", p)
    p = bash_payload("m0t028-diag-probe", "irrelevant")
    p["agent_id"] = "am0t028-diag-probe-0f3a"
    p["tool_input"] = "not-a-dict"
    check("C3: named spawn + tool_input as string -> deny", "DENY", p)
    p = bash_payload(None, "irrelevant")
    p["tool_input"] = "not-a-dict"
    check("C3: lead (no identity) + odd tool_input -> allow (returns first)",
          "ALLOW", p)

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): " + ", ".join(FAILURES))
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
