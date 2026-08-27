"""PreToolUse guard enforcing OPERATIONAL read-only for spawned agents.

Wired in tracked `.claude/settings.json` as a PreToolUse hook on
`Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`. Observed payload reality (M0-T028
primary evidence, project-control/reports/M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md):
the lead/main session carries NO agent identity key at all (no `agent_type`,
`agentType`, or `agent_id`); an UNNAMED spawn carries its `.claude/agents/`
role in `agent_type`; a NAMED spawn carries the runtime SPAWN NAME in
`agent_type`, and the role is then unrecoverable from any payload field
(B-015: named reviewer teammates resolved to "ungoverned" and fell through
the roster check).

Fail-closed identity resolution (B-015 fix):
- No identity key at all (`agent_type`/`agentType`/`agent_id` all absent or
  empty) -> pass through (lead/main session; unchanged).
- Identity in READ_ONLY_AGENTS -> enforce the read-only rules (unchanged).
- Identity equal to another KNOWN `.claude/agents/` roster definition -> pass
  through (write-authorized producer/specialist, e.g. backend-engineer). The
  roster is listed at runtime from the agents directory resolved RELATIVE to
  this file, never a hardcoded machine path; if it cannot be read, the roster
  is EMPTY and every spawned identity fails closed.
- Identity present but NOT a known roster definition (any arbitrary spawn
  name, harness built-in agent types) -> enforce the read-only rules (fail
  closed). An unidentifiable spawned agent must never mutate; writing
  producers must be spawned UNNAMED so their roster identity resolves.

Enforcement (2.1.x PreToolUse blocking contract):
- Any file-mutation tool (Write/Edit/MultiEdit/NotebookEdit) -> DENY.
- Bash commands that mutate the repo/GitHub/control-plane/lockfiles or write files
  -> DENY. Git mutations are matched both by the regex AND by a quoting-aware
  shlex/argv pass (`_git_argv_mutates`), so a quoted or backslash-escaped
  `-C <path>` containing spaces cannot hide the sub-command from the guard.
- PowerShell commands (M0-T108, G5 M0-T102 MEDIUM: the harness exposes a
  PowerShell tool on Windows that previously reached the filesystem with no
  deny): the SAME text passes run on a backtick-normalized command (PowerShell
  escapes with a backtick, which could otherwise split a git verb), PLUS a
  PowerShell-specific mutation denylist (`_PS_MUTATING`: write cmdlets and
  their aliases, `[IO.File]::Write*`-class .NET calls, `-OutFile`, mutating
  web methods, registry/task/ACL writers, `Add-Type`, nested/encoded shells,
  and the dynamic call operator `& $var`), and a PowerShell redirect rule that
  allows only `$null` targets and stream merges (`2>&1`).
- Redirect detection is QUOTE-AWARE (M0-T108 false-positive fix): a `>` inside
  a quoted string (`python -c "1 if x>0 else 2"`, `grep 'a->b'`) is literal
  text in every real shell and no longer denies; an UNQUOTED redirect to a
  real path still does.
- Best-effort scripting-write pass (both shells): command text that invokes an
  inline-write idiom (`open(..., 'w'|'a'|'x'|'+')`, `.write_text/.write_bytes`,
  `os.remove/rename/makedirs/...`, `shutil.*`, `fs.write*`) is DENIED even
  though quoted. Mode-less/`'r'` opens stay allowed (pure reads).
- Read-only git inspection, gh reads, and test execution -> ALLOW (silent).
Deny is emitted as exit 0 with hookSpecificOutput.permissionDecision == "deny".
An unparseable / non-object payload fails CLOSED (deny) — real harness payloads are
always valid JSON objects, so this never affects the main session in practice while
guaranteeing a malformed event can never slip a mutation through.

Documented residuals (honest, unchanged in kind): a scripting-language write
composed dynamically at runtime (string-built mode, exec of assembled source)
is not statically resolvable — the pass above catches the direct idioms only;
a PowerShell verb assembled by string concatenation is likewise dynamic, but
its execution vectors (`Invoke-Expression`/`iex`, `& $var`, encoded commands,
nested shells) are themselves denied. The remaining residual is covered by
(a) the removed Write/Edit tools and (b) the orchestrator-only integration
model: only the lead commits/pushes/merges, so a reviewer's local scratch
never reaches a branch, a PR, or the ledger. See
`.claude/ORCHESTRATION_POLICY.md`.
"""
import json
import re
import shlex
import sys
from pathlib import Path

READ_ONLY_AGENTS = frozenset(
    {
        "progress-auditor",
        "code-reviewer",
        "security-reviewer",
        "data-contract-verifier",
        "ci-evidence-verifier",
        "control-plane-verifier",
        "directive-compliance-verifier",
    }
)

WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})

# Shell tools whose command text is scanned by the mutation passes. The matcher
# in .claude/settings.json must list every one of these (M0-T108).
SHELL_TOOLS = frozenset({"Bash", "PowerShell"})


def _known_roster_agents():
    """The `.claude/agents/` roster (file stems), listed at runtime from the
    agents directory resolved RELATIVE to this hook file - never a hardcoded
    machine path - so every checkout/worktree resolves its own roster. Any
    read failure (missing dir, OSError) returns an EMPTY roster: spawned
    identities then fail CLOSED, never open."""
    try:
        agents_dir = Path(__file__).resolve().parent.parent / "agents"
        return {p.stem for p in agents_dir.iterdir()
                if p.is_file() and p.suffix == ".md"}
    except OSError:
        return set()


def _identity(payload, key):
    """String form of a payload identity field ('' when absent/None). A
    non-string truthy value is coerced to str so a malformed identity still
    resolves to spawned-unknown (fail closed) instead of crashing the hook
    (a crashed hook is a non-blocking error, i.e. fails OPEN)."""
    value = payload.get(key)
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ""
    return str(value).strip()

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

# Redirect targets that never write a repo file. Bash: /dev/null|stderr|stdout
# and fd duplications (`>&2`, `2>&1`). PowerShell: `$null` and stream merges
# (`2>&1`, `*>&1`). A leading fd/stream digit (1>, 2>, *>, or none) still counts
# as a file write unless the target is one of those — so `1>out.txt` is DENIED
# while `2>/dev/null`, `2>&1`, and `> $null` are allowed. Detection itself is
# quote-aware (`_unquoted_redirect`), replacing the former raw-text _REDIRECT
# regex that denied literal `>` inside quoted strings (M0-T108 false-positive
# fix: `python -c "1 if x>0 else 2"` is a pure read).
_BASH_REDIRECT_TARGET_OK = re.compile(r"^(?:&|/dev/(?:null|stderr|stdout)\b)")
_PS_REDIRECT_TARGET_OK = re.compile(r"(?i)^(?:&\d|\$null\b)")

# PowerShell-specific mutation surface (M0-T108; G5 M0-T102 MEDIUM). Matched on
# the backtick-normalized command text, ADDITIVE to the shell-agnostic
# _MUTATING pass (which already catches `git add`, `gh pr create`, `rm`, `mv`,
# `cp`, `tee`, `npm install`, ... appearing in PowerShell command text).
# Same quoted-text posture as _MUTATING: a mutating token inside a quoted
# string still denies (fail closed).
_PS_MUTATING = re.compile(
    r"""(?ix)
    (?:^|[\s;&|({`])
    (?:
        (?:Set|Add|Clear)-Content\b
      | Out-File\b
      | (?:New|Remove|Move|Copy|Rename|Set)-Item(?:Property)?\b
      | Tee-Object\b
      | Export-(?:Csv|Clixml|FormatData|PSSession|ModuleMember)\b
      | (?:Compress|Expand)-Archive\b
      | Set-(?:Acl|ExecutionPolicy)\b
      | Add-Type\b
      | Start-Process\b
      | Invoke-(?:Expression|Item)\b
      | iex\b
      | Invoke-(?:WebRequest|RestMethod)\b[^;|]*?(?:-OutFile\b|-Method\s+(?:POST|PUT|PATCH|DELETE)\b)
      | New-Object\s+(?:System\.)?IO\.(?:StreamWriter|FileStream|BinaryWriter)\b
      | \[(?:System\.)?IO\.(?:File|Directory)\]::
            (?!Exists|ReadAll|ReadLines|OpenRead|OpenText|GetAttributes|
               GetLastWrite|GetCreationTime|GetFiles|GetDirectories|
               GetFileSystemEntries)\w+
      | \[(?:System\.)?IO\.Path\]::GetTempFileName\b
      | reg\s+(?:add|delete|import|copy|restore|load|unload)\b
      | schtasks\b[^;|]*/(?:create|delete|change|run|end)\b
      | icacls\b[^;|]*/(?:grant|deny|remove|reset|setowner)\b
      | (?:powershell|pwsh|cmd)(?:\.exe)?\s   # nested shell: laundering vector
      | (?:sc|ni|ri|rd|del|erase|md|cpi|rni|ren|move|copy)\s  # write aliases
      | &\s*\$                                # call operator on a variable
    )
    """
)
# A `-OutFile` anywhere (outside the Invoke-* form above) writes a file.
_PS_OUTFILE = re.compile(r"(?i)(?:^|\s)-OutFile\b")
# powershell/pwsh encoded command: base64-hidden payload; never needed read-only.
_PS_ENCODED = re.compile(r"(?i)(?:^|\s)-e(?:c|nc\w*)\b")

# Best-effort inline scripting-write idioms (both shells; M0-T108 objective iii).
# Deliberately mode-gated: `open(f)` / `open(f,'r')` / `open(f,'rb')` are pure
# reads and stay ALLOWED (the observed M0-T102 reviewer false-positive class);
# any `w`/`a`/`x`/`+` in a positional mode string denies.
_SCRIPT_WRITE = re.compile(
    r"""(?ix)
    (?:
        \bopen\s*\([^()]*,\s*['\"][^'\"]*[wax+][^'\"]*['\"]
      | \.write_(?:text|bytes)\s*\(
      | \bos\.(?:remove|unlink|rename|replace|makedirs|mkdir|rmdir|removedirs|
                truncate|chmod|chown)\b
      | \bshutil\.(?:copy\w*|move|rmtree|make_archive)\b
      | \.unlink\s*\(
      | \bfs\.(?:write|append|unlink|rm|mkdir|rename|copy)\w*\s*\(
    )
    """
)

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


def _ps_normalize(cmd):
    """Resolve PowerShell backtick escapes so a mutating verb cannot hide
    behind them (`git pu`+backtick+`sh` executes `git push`). Backtick+newline
    is a line continuation (both dropped, plus any CR/LF run); backtick+char
    resolves to the char. Single-quoted spans are literal in PowerShell, so
    backticks inside them are preserved. Backslash is NOT an escape character
    in PowerShell (it is the path separator) and is left untouched."""
    out = []
    in_single = False
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if in_single:
            out.append(c)
            if c == "'":
                in_single = False
            i += 1
            continue
        if c == "'":
            in_single = True
            out.append(c)
            i += 1
            continue
        if c == "`" and i + 1 < n:
            nxt = cmd[i + 1]
            if nxt in "\r\n":
                i += 2
                while i < n and cmd[i] in "\r\n":
                    i += 1
                continue
            out.append(nxt)
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _unquoted_redirect(cmd, powershell=False):
    """True if the command contains an UNQUOTED `>`/`>>` whose target is a real
    path (not /dev/null|stderr|stdout / fd-dup for Bash; not $null / stream
    merge for PowerShell). Quote-aware replacement for the former raw-text
    _REDIRECT regex (M0-T108): a `>` inside a quoted string is literal text in
    every real shell and must not deny a pure read. For Bash, a backslash
    escapes the next character outside single quotes (an escaped `\\>` is
    literal); for PowerShell the caller passes backtick-normalized text and
    backslash is a path character."""
    target_ok = _PS_REDIRECT_TARGET_OK if powershell else _BASH_REDIRECT_TARGET_OK
    quote = None
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if quote is not None:
            if not powershell and c == "\\" and quote == '"' and i + 1 < n:
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in ("'", '"'):
            quote = c
            i += 1
            continue
        if not powershell and c == "\\" and i + 1 < n:
            i += 2
            continue
        if c == "<":
            # heredoc/herestring/process-substitution reads: `<`, `<<`, `<<<`
            i += 1
            continue
        if c == ">":
            j = i + 1
            if j < n and cmd[j] == ">":
                j += 1
            while j < n and cmd[j] in " \t":
                j += 1
            if not target_ok.match(cmd[j:]):
                return True
            i = j if j > i else i + 1
            continue
        i += 1
    return False


def _shell_command_mutates(cmd, powershell=False):
    """The full mutation decision for one shell command (M0-T108). The
    shell-agnostic _MUTATING regex and the quoting-aware git argv pass run for
    BOTH shells; PowerShell additionally normalizes backticks first and runs
    its own denylist; both shells run the quote-aware redirect scan and the
    best-effort inline scripting-write pass."""
    if powershell:
        cmd = _ps_normalize(cmd)
        if (_PS_MUTATING.search(cmd) or _PS_OUTFILE.search(cmd)
                or _PS_ENCODED.search(cmd)):
            return True
    return bool(
        _MUTATING.search(cmd)
        or _unquoted_redirect(cmd, powershell=powershell)
        or _git_argv_mutates(cmd)
        or _SCRIPT_WRITE.search(cmd)
    )


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


def _main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        payload = None
    if not isinstance(payload, dict):
        # Malformed / non-object event on a guarded tool: fail CLOSED.
        _deny("read-only guard: unparseable PreToolUse payload (fail-closed)")
        return 0
    # Fail-closed identity resolution (B-015 fix; see module docstring).
    agent = _identity(payload, "agent_type") or _identity(payload, "agentType")
    agent_id = _identity(payload, "agent_id")
    if not agent and not agent_id:
        # No agent identity key of any kind: the lead/main session (the only
        # payload shape observed without identity). Pass through.
        return 0
    if agent not in READ_ONLY_AGENTS:
        if agent and agent in _known_roster_agents():
            # A KNOWN roster definition outside READ_ONLY_AGENTS is a
            # write-authorized producer/specialist (unnamed spawn): pass through.
            return 0
        # Identity present but NOT a roster definition (a named spawn, a
        # harness built-in type, or an unreadable roster): FAIL CLOSED -
        # govern it below exactly like a read-only role. An unidentifiable
        # spawned agent must never mutate.
    who = agent or agent_id
    tool = payload.get("tool_name") or ""
    if tool in WRITE_TOOLS:
        _deny(f"'{who}' is operationally read-only and may not use {tool}.")
        return 0
    if tool in SHELL_TOOLS:
        cmd = (payload.get("tool_input") or {}).get("command") or ""
        if _shell_command_mutates(cmd, powershell=(tool == "PowerShell")):
            _deny(
                f"'{who}' is operationally read-only: repository/GitHub/control-plane "
                "mutation and shell file-writes are blocked (Bash and PowerShell). "
                "Read-only git inspection, gh reads, and test execution are allowed; "
                "return findings via SendMessage."
            )
            return 0
    return 0


def main():
    """Fail-closed envelope (G5 required correction C3): a crashed hook is a
    NON-BLOCKING error to the harness, i.e. it fails OPEN. Any unexpected
    exception in the decision path (e.g. a malformed tool_input shape that
    survives identity resolution) must therefore emit a deny instead of
    propagating."""
    try:
        return _main()
    except Exception:
        _deny("read-only guard: internal error (fail-closed)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
