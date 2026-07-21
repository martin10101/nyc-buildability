"""PreToolUse guard enforcing OPERATIONAL read-only for the reviewer/auditor roles.

Wired in tracked `.claude/settings.json` as a PreToolUse hook on
`Bash|Write|Edit|MultiEdit|NotebookEdit`. It enforces ONLY when the invoking
subagent's `agent_type` is one of the six read-only roles, so it never affects the
main orchestrator or the isolated-worktree producers (they retain full write/git
authority). The `agent_type` field is present in the PreToolUse payload for
subagent tool calls (Claude Code 2.1.x).

Enforcement (2.1.x PreToolUse blocking contract):
- Any file-mutation tool (Write/Edit/MultiEdit/NotebookEdit) -> DENY.
- Bash commands that mutate the repo/GitHub/control-plane/lockfiles or write files
  -> DENY.
- Read-only git inspection, gh reads, and test execution -> ALLOW (silent).
Deny is emitted as exit 0 with hookSpecificOutput.permissionDecision == "deny".
An unparseable payload from a read-only role fails CLOSED (deny); a payload with no
read-only agent_type is allowed (it is the main session or a producer).

This does NOT sandbox a scripting-language file write (e.g. `python -c` opening a
file for writing) — that is inseparable from allowing test execution. The residual
is covered by (a) the removed Write/Edit tools and (b) the orchestrator-only
integration model: only the lead commits/pushes/merges, so a reviewer's local
scratch never reaches a branch, a PR, or the ledger. See
`.claude/ORCHESTRATION_POLICY.md`.
"""
import json
import re
import sys

READ_ONLY_AGENTS = frozenset(
    {
        "progress-auditor",
        "code-reviewer",
        "security-reviewer",
        "data-contract-verifier",
        "ci-evidence-verifier",
        "control-plane-verifier",
    }
)

WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})

# Repository / GitHub / control-plane / filesystem mutation. Read-only git
# (status/log/show/diff/rev-parse/ls-*/cat-file/blame/branch --list/worktree list/
# config --get) and test runners (pytest/node --test/npm test) are NOT matched.
_MUTATING = re.compile(
    r"""(?ix)
    (?:^|[\s;&|(`{])
    (?:
        git\s+(?:(?:-c|-C)\s+\S+\s+)*
            (?:add|commit|push|pull|fetch|merge|rebase|reset|revert|restore|
               checkout|switch|rm|mv|clean|stash|tag|apply|am|cherry-pick|
               update-ref|update-index|write-tree|commit-tree|gc|prune|
               config(?!\s+(?:--get|--list|-l)) |
               remote\s+(?:add|remove|rename|set-url|prune)|
               worktree\s+(?:add|remove|move|prune|lock|unlock)|
               branch\s+(?:-[dDmM]|--delete|--move|--force)|
               notes|replace|filter-branch|submodule|fast-import)
      | gh\s+(?:pr|issue|release|repo|run|api|workflow|label|gist|secret|
               variable|ruleset|cache|project|codespace)\b
            [^;&|]*?\b(?:create|edit|close|reopen|merge|comment|review|delete|
               rename|transfer|rerun|cancel|disable|enable|sync|lock|unlock|
               ready|develop|approve|pin|unpin|set-default|add|remove|restore)\b
      | gh\s+api\b[^;&|]*?(?:--method\s*(?:POST|PUT|PATCH|DELETE)|-X\s*(?:POST|PUT|PATCH|DELETE)|--field\b|-f\s)
      | (?:python[0-9.]*\s+)?(?:tools/)?project_control\.py\s+
            (?:new-task|claim|progress|submit|gate|accept|checkpoint|unlock|
               new-milestone|depend|set-\S+)
      | (?:rm|rmdir|shred|truncate|dd|mkfifo|ln)\s
      | (?:mv|cp|install|chmod|chown|chgrp)\s
      | (?:sed|perl)\s+[^;&|]*-i
      | tee\s
      | (?:npm|pnpm|yarn)\s+(?:install|ci|i|add|remove|uninstall|update|publish|link|exec)\b
      | npx\s
      | (?:pip[0-9.]*|uv)\s+(?:install|add|sync|uninstall|remove)\b
      | (?:python[0-9.]*\s+-m\s+pip)\s+(?:install|uninstall)\b
    )
    """
)

# A redirection writing to a real path (not /dev/null|/dev/stderr|/dev/stdout or an
# fd duplication like >&2 / 2>&1). `2>/dev/null` is fine (digit before '>' excluded).
_REDIRECT = re.compile(r"(?<![0-9&>])>>?\s*(?!\s*(?:/dev/null|/dev/stderr|/dev/stdout|&))")


def _deny(reason):
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        payload = None
    agent = ""
    if isinstance(payload, dict):
        agent = (payload.get("agent_type") or payload.get("agentType") or "").strip()
    # Only govern the six read-only roles. Main session / producers pass through.
    if agent not in READ_ONLY_AGENTS:
        return 0
    if payload is None:
        _deny(f"read-only guard for '{agent}': unparseable PreToolUse payload (fail-closed)")
        return 0
    tool = payload.get("tool_name") or ""
    if tool in WRITE_TOOLS:
        _deny(f"'{agent}' is operationally read-only and may not use {tool}.")
        return 0
    if tool == "Bash":
        cmd = (payload.get("tool_input") or {}).get("command") or ""
        if _MUTATING.search(cmd) or _REDIRECT.search(cmd):
            _deny(
                f"'{agent}' is operationally read-only: repository/GitHub/control-plane "
                "mutation and shell file-writes are blocked. Read-only git inspection, "
                "gh reads, and test execution are allowed; return findings via SendMessage."
            )
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
