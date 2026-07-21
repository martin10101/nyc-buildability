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

# --- Quoting- and separator-aware git-mutation detection (additive) --------
# The _MUTATING regex consumes a `-C <path>` / `-c <cfg>` argument with `\S+`,
# which cannot span a space; because this repo's path contains a space and
# absolute `-C` is the encouraged idiom, `git -C "<spaced path>" <verb>` slipped
# past it. Rather than another whitespace-fragile regex, we split the command
# into segments on UNQUOTED shell separators (`; | & ( ) { } < > newline`,
# backtick, and `$(`) — so a git call hidden after ANY operator, glued or
# spaced, is isolated into its own segment — then shlex-tokenize each segment
# (resolving single/double quotes and backslash-escaped spaces to real argv) and
# inspect the git sub-command. Quoted separators are preserved, so a read-only
# `git log --grep "a;b|c"` is never mis-split. This pass is ADDITIVE (OR-ed with
# the regexes) and mirrors the regex's config/remote/worktree/branch nuances
# exactly, so no existing denial is removed and no read-only form is newly denied.
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
# The subset of value-options that point git at a DIFFERENT working tree/repo.
# A cross-tree git call whose sub-command cannot be positively classified as
# read-only (a dynamic `$…`/backtick verb, a verb produced by a split-off `$(…)`,
# or an absent verb) is failed closed — that is exactly the spaced-`-C` mutation
# pattern this guard exists to stop.
_GIT_TARGET_OPTS = frozenset({"-C", "--git-dir", "--work-tree"})
# Unquoted single-char shell separators that begin a new command (`$(` handled
# separately). Each isolates whatever follows into its own segment.
_SEGMENT_CHARS = ";\n|&(){}<>`"


def _is_git(token):
    base = token.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
    return base in ("git", "git.exe")


def _git_sub_mutates(sub, rest):
    """Classify a git sub-command as mutating, mirroring the _MUTATING regex's
    nuances for config/remote/worktree/branch so their read-only forms
    (config --get*/--list/-l, remote -v/show, worktree list, branch --list) stay
    allowed and nothing beyond the regex baseline is newly denied."""
    if sub in _GIT_MUTATING_SUBCMDS:
        return True
    if sub == "config":
        first = rest[0] if rest else None
        return not (first is not None
                    and (first.startswith("--get") or first in ("--list", "-l")))
    if sub == "remote":
        return any(r in ("add", "remove", "rename", "set-url", "prune") for r in rest)
    if sub == "worktree":
        return any(r in ("add", "remove", "move", "prune", "lock", "unlock") for r in rest)
    if sub == "branch":
        return any(r in ("-d", "-D", "-m", "-M", "--delete", "--move", "--force")
                   for r in rest)
    return False


def _split_command_segments(cmd):
    """Split a command line into candidate command segments on UNQUOTED shell
    separators (_SEGMENT_CHARS plus `$(`), preserving quoted separators and
    backslash escapes so a read-only command's quoted metacharacters are never
    mis-split. A git call hidden after any operator lands in its own segment."""
    segments, buf = [], []
    quote = None
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if quote is not None:
            buf.append(c)
            if c == "\\" and quote == '"' and i + 1 < n:
                buf.append(cmd[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in ("'", '"'):
            quote = c
            buf.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            if cmd[i + 1] in "\r\n":
                # backslash-newline = shell line continuation: join (drop both,
                # plus any run of CR/LF) so `git -C "x y" \<nl>push` cannot hide
                # the verb by gluing the newline onto it.
                i += 1
                while i < n and cmd[i] in "\r\n":
                    i += 1
                continue
            buf.append(c)
            buf.append(cmd[i + 1])
            i += 2
            continue
        if c == "$" and i + 1 < n and cmd[i + 1] == "(":
            segments.append("".join(buf))
            buf = []
            i += 2
            continue
        if c in _SEGMENT_CHARS:
            segments.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    segments.append("".join(buf))
    return segments


def _git_argv_mutates(cmd):
    """True if any command segment invokes a repo-mutating git, with quotes and
    separators resolved so nothing static can hide the git verb. Each segment is
    shlex-tokenized (blank/newline tokens dropped, closing backslash line
    continuations) and EVERY `git` token is inspected wherever it sits — so a
    leading assignment (`VAR=v git …`), a command wrapper (`env`/`sudo`/`nice`/
    `command`/`exec`/…), or a case-variant binary (`GIT`) cannot make the guard
    miss it. For each git token we skip global options, tracking whether it
    targets another tree (`-C`/`--git-dir`/`--work-tree`), then classify the
    sub-command: a known mutating verb -> deny; a cross-tree git whose verb is
    dynamic (`$…`/backtick), split off (`$(…)`), or absent -> deny (fail closed);
    otherwise allow. NOTE (documented residual, unchanged from the base regex):
    a verb hidden in a shell variable WITHOUT a tree target (`c=push; git "$c"`)
    still runs against the current dir and is not statically resolvable here — the
    same limitation the `_MUTATING` regex has for `git "$c"`; it is covered by the
    read-only role + orchestrator-only integration, not by this static pass."""
    for seg in _split_command_segments(cmd):
        seg = seg.strip()
        if not seg:
            continue
        try:
            words = shlex.split(seg, posix=True)
        except ValueError:
            # Malformed quoting (only if the original command is itself
            # unbalanced): fail closed when the segment invokes git.
            if re.search(r"(?i)(?:^|\s)git(?:\.exe)?(?:\s|$)", seg):
                return True
            continue
        words = [w for w in words if w.strip()]  # drop stray blank/newline tokens
        for gi, w in enumerate(words):
            if not _is_git(w):
                continue
            has_target = False
            sub = None
            j = gi + 1
            while j < len(words):
                t = words[j]
                if t.startswith("-"):
                    base = t.split("=", 1)[0]
                    if base in _GIT_TARGET_OPTS:
                        has_target = True
                    if "=" in t:
                        j += 1
                        continue
                    if t in _GIT_VALUE_OPTS:
                        j += 2
                        continue
                    j += 1
                    continue
                sub = t
                break
            if sub is None:
                if has_target:  # `git -C <tree>` with no resolvable verb
                    return True
                continue
            if "$" in sub or "`" in sub:  # verb hidden in a variable/substitution
                if has_target:
                    return True
                continue
            if _git_sub_mutates(sub, words[j + 1:]):
                return True
            # known read-only sub-command for this git token; keep scanning
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
