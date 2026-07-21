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
  -> DENY. Git mutations are matched both by the regex AND by a quoting-aware
  shlex/argv pass (`_git_argv_mutates`), so a quoted or backslash-escaped
  `-C <path>` containing spaces cannot hide the sub-command from the guard.
- Read-only git inspection, gh reads, and test execution -> ALLOW (silent).
Deny is emitted as exit 0 with hookSpecificOutput.permissionDecision == "deny".
An unparseable / non-object payload fails CLOSED (deny) — real harness payloads are
always valid JSON objects, so this never affects the main session in practice while
guaranteeing a malformed event can never slip a mutation through.

This does NOT sandbox a scripting-language file write (e.g. `python -c` opening a
file for writing) — that is inseparable from allowing test execution. The residual
is covered by (a) the removed Write/Edit tools and (b) the orchestrator-only
integration model: only the lead commits/pushes/merges, so a reviewer's local
scratch never reaches a branch, a PR, or the ledger. See
`.claude/ORCHESTRATION_POLICY.md`.
"""
import json
import re
import shlex
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
# config --get/merge-base/show-branch) and test runners (pytest/node --test/npm
# test) are NOT matched. `(?![\w-])` after the git verb group prevents a mutating
# verb from matching a hyphenated read-only cousin (e.g. `merge` vs `merge-base`).
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
               notes|replace|filter-branch|submodule|fast-import)(?![\w-])
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

# A redirection writing to a real path. Allows only /dev/null|/dev/stderr|/dev/stdout
# and fd duplications (`>&2`, `2>&1`). A leading fd digit (1>, 2>, 9>, or none) still
# counts as a file write unless the target is one of those — so `1>out.txt` is DENIED
# while `2>/dev/null` and `2>&1` are allowed.
_REDIRECT = re.compile(r">>?\s*(?!\s*(?:/dev/(?:null|stderr|stdout)\b|&))")

# --- Quoting-aware git-mutation detection (additive backstop) --------------
# The _MUTATING regex consumes a `-C <path>` / `-c <cfg>` argument with `\S+`,
# which cannot span a space. Because this repo's path contains a space and
# absolute `-C` paths are the encouraged idiom here, `git -C "<spaced path>"
# <verb>` slipped past the regex (the mutating verb never realigned). Rather
# than swap in another whitespace-fragile regex, we ALSO tokenize the command
# with shlex — which resolves single quotes, double quotes, and backslash-escaped
# spaces into real argv — and inspect the git sub-command directly. This pass is
# ADDITIVE: it only ever ADDS a denial (OR-ed with the regexes below), so every
# existing regex/redirect denial and every existing allow is preserved. A parse
# failure returns False, leaving the regex as the primary matcher (no regression).
_GIT_MUTATING_SUBCMDS = frozenset(
    {
        "add", "commit", "push", "pull", "fetch", "merge", "rebase", "reset",
        "revert", "restore", "checkout", "switch", "rm", "mv", "clean", "stash",
        "tag", "apply", "am", "cherry-pick", "update-ref", "update-index",
        "write-tree", "commit-tree", "gc", "prune", "notes", "replace",
        "filter-branch", "submodule", "fast-import",
    }
)
# git global options that consume the FOLLOWING token as their value.
_GIT_VALUE_OPTS = frozenset(
    {
        "-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix",
        "--exec-path", "--config-env",
    }
)
_SHELL_OPS = frozenset({"&&", "||", "|", "&", ";", "(", ")", "{", "}", "\n"})


def _is_git(token):
    base = token.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return base in ("git", "git.exe")


def _git_sub_mutates(sub, rest):
    """Classify a git sub-command (with its trailing tokens) as mutating. Mirrors
    the regex nuances for config/remote/worktree/branch so read-only forms
    (config --get, remote -v, worktree list, branch --list) stay allowed."""
    if sub in _GIT_MUTATING_SUBCMDS:
        return True
    if sub == "config":
        return not any(
            r in ("--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l")
            for r in rest
        )
    if sub == "remote":
        return any(
            r in ("add", "remove", "rm", "rename", "set-url", "set-head",
                  "set-branches", "prune", "update")
            for r in rest
        )
    if sub == "worktree":
        return any(
            r in ("add", "remove", "move", "prune", "lock", "unlock", "repair")
            for r in rest
        )
    if sub == "branch":
        return any(
            r in ("-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy",
                  "-f", "--force")
            for r in rest
        )
    return False


def _git_argv_mutates(cmd):
    """True if any simple command in `cmd` is a repo-mutating git invocation,
    with quotes/escapes resolved so a spaced `-C`/`-c` value cannot hide the
    verb. Returns False on shlex parse failure (regex stays the primary matcher)."""
    try:
        tokens = shlex.split(cmd, posix=True)
    except ValueError:
        return False
    simple, cur = [], []
    for tok in tokens:
        if tok in _SHELL_OPS:
            if cur:
                simple.append(cur)
                cur = []
        else:
            cur.append(tok)
    if cur:
        simple.append(cur)
    for words in simple:
        if not words or not _is_git(words[0]):
            continue
        j = 1
        while j < len(words):
            t = words[j]
            if t.startswith("-"):
                if "=" in t:
                    j += 1
                    continue
                if t in _GIT_VALUE_OPTS:
                    j += 2
                    continue
                j += 1
                continue
            if _git_sub_mutates(t, words[j + 1:]):
                return True
            break
    return False


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
    if not isinstance(payload, dict):
        # Malformed / non-object event on a guarded tool: fail CLOSED.
        _deny("read-only guard: unparseable PreToolUse payload (fail-closed)")
        return 0
    agent = (payload.get("agent_type") or payload.get("agentType") or "").strip()
    # Only govern the six read-only roles. Main session / producers pass through.
    if agent not in READ_ONLY_AGENTS:
        return 0
    tool = payload.get("tool_name") or ""
    if tool in WRITE_TOOLS:
        _deny(f"'{agent}' is operationally read-only and may not use {tool}.")
        return 0
    if tool == "Bash":
        cmd = (payload.get("tool_input") or {}).get("command") or ""
        if _MUTATING.search(cmd) or _REDIRECT.search(cmd) or _git_argv_mutates(cmd):
            _deny(
                f"'{agent}' is operationally read-only: repository/GitHub/control-plane "
                "mutation and shell file-writes are blocked. Read-only git inspection, "
                "gh reads, and test execution are allowed; return findings via SendMessage."
            )
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
