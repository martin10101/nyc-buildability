# Snapshot: Claude Code CLI Reference

- Source URL: https://code.claude.com/docs/en/cli-reference
- Fetched: 2026-08-26
- Purpose: D-024 amendment-3 capability re-baseline (requirement D-024-R147)

Capture method: WebFetch (page rendered to markdown; content reproduced by the fetch tool's
extraction model, verbatim where quoted). Known conversion gap: the page's own table row for
`--worktree`/`-w` is truncated in the rendered markdown; a labeled supplement from
https://code.claude.com/docs/en/worktrees (fetched the same day) covers that flag at the end.

## CLI commands

| Command | Description | Example |
|---------|-------------|---------|
| `claude` | Start interactive session | `claude` |
| `claude "query"` | Start interactive session with initial prompt | `claude "explain this project"` |
| `claude -p "query"` | Query via SDK, then exit | `claude -p "explain this function"` |
| `cat file \| claude -p "query"` | Process piped content | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | Continue most recent conversation in current directory | `claude -c` |
| `claude -c -p "query"` | Continue via SDK | `claude -c -p "Check for type errors"` |
| `claude -r "<session>" "query"` | Resume session by ID or name | `claude -r "auth-refactor" "Finish this PR"` |
| `claude update` | Update to latest version | `claude update` |
| `claude gateway` | Start the self-hosted Claude apps gateway server, for administrators deploying SSO and policy in front of Claude Code on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry. Requires `--config` pointing at a `gateway.yaml`. Available in Claude Code v2.1.195 and later. | `claude gateway --config gateway.yaml` |
| `claude install [version]` | Install or reinstall the native binary. Accepts a version like `2.1.118`, or `stable` or `latest`. | `claude install stable` |
| `claude auth login` | Sign in to your Anthropic account. Use `--email` to pre-fill your email address, `--sso` to force SSO authentication, and `--console` to sign in with Anthropic Console for API usage billing instead of a Claude subscription | `claude auth login --console` |
| `claude auth logout` | Log out from your Anthropic account | `claude auth logout` |
| `claude auth status` | Show authentication status as JSON. Use `--text` for human-readable output. Exits with code 0 if logged in, 1 if not | `claude auth status` |
| `claude agents` | Open agent view to monitor and dispatch parallel background sessions. Use `--cwd <path>` to show only sessions started under that directory, or `--json` to print active sessions as a JSON array for scripting (`--json --all` also includes completed background sessions). Pass `--permission-mode`, `--model`, `--effort`, or `--agent` to set defaults for dispatched sessions. Accepts `--settings`, `--add-dir`, `--plugin-dir`, and `--mcp-config` like the top-level `claude` command. Opening agent view requires an interactive terminal | `claude agents --json` |
| `claude attach <id>` | Attach to a background session in this terminal | `claude attach 7c5dcf5d` |
| `claude auto-mode defaults` | Print the built-in auto mode classifier rules as JSON. Use `claude auto-mode config` to see your effective config with settings applied. `--label <prefix>` prints only the rules whose label starts with that prefix, matched case-insensitively. Requires Claude Code v2.1.208 or later | `claude auto-mode defaults --label 'Git Destructive'` |
| `claude auto-mode reset` | Restore the default auto mode configuration by removing the `autoMode` section from your user settings file. Prompts for confirmation before writing; pass `-y`/`--yes` to skip the prompt. Rules from managed settings or the `--settings` flag still apply. Requires Claude Code v2.1.212 or later. | `claude auto-mode reset --yes` |
| `claude daemon status` | Print the background-session supervisor's state, version, socket directory, and worker count for diagnostics. Exits 1 if the supervisor isn't running | `claude daemon status` |
| `claude daemon stop --any` | Stop the background-session supervisor and the sessions it hosts. Pass `--keep-workers` to leave background sessions running so the next supervisor reconnects to them. `--any` confirms stopping an on-demand supervisor, which is the default. Use this to recover from an unresponsive supervisor | `claude daemon stop --any --keep-workers` |
| `claude doctor` | Print read-only installation and settings diagnostics from the terminal without starting a session, including install health, settings-file validation errors, and Remote Control eligibility. For the in-session setup checkup that can also apply fixes, run `/doctor` | `claude doctor` |
| `claude import [codex\|gemini]` | Start an interactive session that runs `/import` to bring configuration from other coding agents into Claude Code. Accepts the same `--dry-run` and `--yes` options as the command. Not available on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or Claude Platform on AWS. Also unavailable when you turn off feature-flag fetching. Requires Claude Code v2.1.213 or later | `claude import codex --dry-run` |
| `claude logs <id>` | Print recent output from a background session | `claude logs 7c5dcf5d` |
| `claude mcp` | Configure Model Context Protocol (MCP) servers | See the Claude Code MCP documentation |
| `claude mcp login <name>` | Run a configured MCP server's OAuth flow without opening the interactive `/mcp` panel. Works for HTTP, SSE, and claude.ai connector servers. Add `--no-browser` over SSH to print the authorization URL instead of opening a browser, then paste the redirect URL back at the prompt. Requires Claude Code v2.1.186 or later. | `claude mcp login sentry` |
| `claude mcp logout <name>` | Clear stored OAuth credentials for an MCP server. Requires Claude Code v2.1.186 or later | `claude mcp logout sentry` |
| `claude plugin` | Manage Claude Code plugins. Alias: `claude plugins`. See plugin reference for subcommands | `claude plugin install code-review@claude-plugins-official` |
| `claude project purge [path]` | Delete all local Claude Code state for a project: transcripts, task lists, debug logs, file-edit history, prompt history lines, and the project's entry in `~/.claude.json`. Omit `[path]` to pick from an interactive list. Flags: `--dry-run` to preview, `-y`/`--yes` to skip confirmation, `-i`/`--interactive` to confirm each item, `--all` for every project. | `claude project purge <path> --dry-run` |
| `claude remote-control` | Start a Remote Control server to control Claude Code from Claude.ai or the Claude app. Runs in server mode (no local interactive session). After you stop the server, you can bring back the sessions it was serving. | `claude remote-control --name "My Project"` |
| `claude respawn <id>` | Restart a background session, running or stopped, with its conversation intact. Use `--all` to restart every running session, e.g. to pick up an updated Claude Code binary | `claude respawn 7c5dcf5d` |
| `claude rm <id>` | Remove a background session from the list. The conversation transcript stays on your local machine, available through `claude --resume` | `claude rm 7c5dcf5d` |
| `claude self-hosted-runner` | Start a runner process that registers this machine or container with a self-hosted environment and hosts Claude Code cloud sessions on your infrastructure. Run `claude self-hosted-runner setup` for a guided operator walkthrough, `claude self-hosted-runner doctor` to diagnose a deployed runner, and `claude self-hosted-runner orchestrator` to spawn on-demand runners. Requires Claude Code v2.1.224 or later | `claude self-hosted-runner setup` |
| `claude setup-token` | Generate a long-lived OAuth token for CI and scripts. Prints the token to the terminal without saving it. Requires a Claude subscription. | `claude setup-token` |
| `claude stop <id>` | Stop a background session. Also accepts `claude kill` | `claude stop 7c5dcf5d` |
| `claude ultrareview [target]` | Run ultrareview non-interactively. Prints findings to stdout and exits 0 on success or 1 on failure. Use `--json` for the raw payload and `--timeout <minutes>` to override the 30-minute default. Use `--post` on a `github.com` pull request target to post the finished findings to the PR as one plain comment from your GitHub account. `--no-post` is the default. Requires Claude Code v2.1.227 or later. | `claude ultrareview 1234 --json` |

## CLI flags

### Essential

- `--print`, `-p` — Print response without interactive mode (see Agent SDK documentation for programmatic usage details).
- `--continue`, `-c` — Load the most recent conversation in the current directory, skipping background sessions, sessions created with `claude -p` or the Agent SDK, and sessions whose first prompt was `/loop`. `claude -p --continue` includes `-p`, SDK, and `/loop` sessions. Includes sessions that added this directory with `/add-dir`.
- `--resume`, `-r` — Resume a specific session by ID or name, or show an interactive picker to choose a session. The picker and name search include sessions that added this directory with `/add-dir`. When you pass a session ID, Claude Code searches the current project directory and its git worktrees, then every other project on this machine. Before v2.1.223, the ID search covered only the current project directory and its git worktrees. Background sessions appear in the picker marked with `bg`.
- `--name`, `-n` — Set a display name for the session, shown in `/resume` and the terminal title. You can resume a named session with `claude --resume <name>`. In an interactive session, if another live session on this machine already uses the name, Claude Code applies a variant of it instead. `/rename` changes the name mid-session and also shows it on the prompt bar.
- `--session-id` — Use a specific session ID for the conversation (must be a valid UUID).
- `--fork-session` — When resuming, create a new session ID instead of reusing the original (use with `--resume` or `--continue`).

### Background sessions and agent view

- `--bg`, `--background` — Start the session as a background agent and return immediately. Prints the session ID and management commands. Combine with `--exec` to run a shell command as a background job instead of a Claude session, or with `--agent` to run a specific subagent. Cannot be combined with `-p`/`--print`. Example: `claude --bg "investigate the flaky test"`.
- Background-session management subcommands: `claude agents` (incl. `--json`, `--json --all`), `claude attach <id>`, `claude logs <id>`, `claude stop <id>` (alias `claude kill`), `claude respawn <id>` (`--all`), `claude rm <id>`, `claude daemon status`, `claude daemon stop --any [--keep-workers]` — full text in the commands table above.

### Output formatting

- `--output-format` — Specify output format for print mode (options: `text`, `json`, `stream-json`). Example: `claude -p "query" --output-format json`.
- `--input-format` — Specify input format for print mode (options: `text`, `stream-json`).
- `--include-partial-messages` — Include partial streaming events in output. Requires `--print` and `--output-format stream-json`.
- `--include-hook-events` — Include hook lifecycle events in the output stream. `SessionStart` and `Setup` hook events are always included and don't need this flag. Some hook events, such as `Notification`, `SessionEnd`, `PreCompact`, and `PostCompact`, never produce a `hook_started` event, even with this flag. For those events, Claude Code still emits `hook_progress` while a command hook that runs for more than a second produces output, and emits `hook_response` only when a hook that runs in the background finishes. Requires `--output-format stream-json`.
- `--forward-subagent-text` — Emit subagent text and thinking blocks in the output stream as `assistant` and `user` messages with `parent_tool_use_id` set, so you can reconstruct each subagent's transcript. Without this flag, Claude Code emits only subagent `tool_use` and `tool_result` blocks. Requires `--print` and `--output-format stream-json`. Claude Code also forwards messages from nested subagents, setting `parent_tool_use_id` to the ID of the Agent tool call that spawned each one; this requires Claude Code v2.1.219 or later. The `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` environment variable enables the same behavior. Requires Claude Code v2.1.211 or later.
- `--prompt-suggestions` — Emit a `prompt_suggestion` message with a predicted next user prompt after each turn that generates one; very short conversations can produce none. Requires `--print`, `--output-format stream-json`, and `--verbose`.
- `--replay-user-messages` — Re-emit user messages from stdin back on stdout for acknowledgment. Requires `--input-format stream-json` and `--output-format stream-json`.

### Model and effort

- `--model` — Sets the model for the current session with an alias for the latest model (`sonnet`, `opus`, `haiku`, or `fable`) or a model's full name. Overrides the `model` setting and `ANTHROPIC_MODEL`.
- `--effort` — Set the effort level for the current session. Options: `low`, `medium`, `high`, `xhigh`, `max`, or `ultracode`. Available levels depend on the model. `ultracode` starts the session at `xhigh` effort with ultracode turned on, and requires Claude Code v2.1.203 or later. Overrides the `effortLevel` setting for this session and does not persist.
- `--advisor <model>` — Enable the server-side advisor tool for this session with a model alias, `fable`, `opus`, or `sonnet`, or a full model ID. Takes precedence over the `advisorModel` setting for the session. `fable` requires Fable 5 access.
- `--autocompact <auto|tokens>` — Set the auto-compact window for this session without changing your saved settings. Accepts the same values as `/autocompact`. Requires Claude Code v2.1.221 or later.
- `--fallback-model` — Enable automatic fallback to the specified model(s) when the primary model is overloaded or not available, for example a retired model. Accepts a comma-separated list tried in order. To persist a chain across sessions, use the `fallbackModel` setting, which this flag overrides.

### Permissions and security

- `--permission-mode` — Begin in a specified permission mode. Accepts `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`, or `manual` as an alias for `default`. The `manual` alias requires Claude Code v2.1.200 or later; `claude --help` lists it in place of `default`, and both values work. Overrides `defaultMode` from settings files. For `-p`, the default start mode is `default` when nothing is configured.
- `--dangerously-skip-permissions` — Skip permission prompts. Equivalent to `--permission-mode bypassPermissions`. For sessions started with `--bg`, the mode persists when the supervisor restarts the session.
- `--allow-dangerously-skip-permissions` — Add `bypassPermissions` to the `Shift+Tab` mode cycle without starting in it.
- `--permission-prompt-tool` — Specify an MCP tool to handle permission prompts in non-interactive mode. Claude Code waits for that tool's MCP server to connect before running the first turn, up to the `MCP_TIMEOUT` startup timeout, 30 seconds by default. The prompt tool can't approve an MCP tool marked as requiring user interaction: Claude Code converts an `allow` result for one to a deny. This restriction requires Claude Code v2.1.199 or later.

### Tools and MCP

- `--allowedTools`, `--allowed-tools` — Tools that execute without prompting for permission. To restrict which tools are available, use `--tools` instead. If you name one of the task-tracking tools here, Claude Code also opts the session in.
- `--disallowedTools`, `--disallowed-tools` — Deny rules. A bare tool name removes the matching tools from Claude's context: `"Edit"` removes Edit, `"*"` removes every tool, and `"mcp__*"` removes every MCP tool. A scoped rule such as `Bash(rm *)` leaves the tool available and denies only matching calls. A rule naming `EndConversation` can't remove it while any other tool remains.
- `--tools` — Restrict which built-in tools Claude can use. Use `""` to disable all, `"default"` for all, or tool names like `"Bash,Edit,Read"`.
- `--mcp-config` — Load MCP servers from JSON files or strings (space-separated). When you pass this flag with `-p`, Claude Code waits for still-pending servers to connect before running the first turn, up to the `MCP_TIMEOUT` startup timeout, 30 seconds by default; a server with a cached tool list skips the wait and connects on first use. The wait requires Claude Code v2.1.221 or later.
- `--strict-mcp-config` — Only use MCP servers from `--mcp-config`, ignoring all other MCP configurations.

### System prompts and configuration

- `--system-prompt` / `--system-prompt-file` — Replace the entire system prompt with custom text / from a file.
- `--append-system-prompt` / `--append-system-prompt-file` — Append custom text to the end of the default system prompt.
- `--append-subagent-system-prompt` — Append custom text to the end of every subagent's system prompt, nested subagents included, apart from a forked subagent, which reuses the conversation's own prompt. Only applies in non-interactive mode with `-p`. Requires Claude Code v2.1.205 or later.
- `--exclude-dynamic-system-prompt-sections` — Move per-machine sections from the system prompt (working directory, environment info, memory paths, git-repo flag) into the first user message. Improves prompt-cache reuse across different users and machines running the same task. Only applies with the default system prompt. Use with `-p` for scripted, multi-user workloads.
- `--settings` — Path to a settings JSON file or an inline JSON string; overrides same keys for this session; file must be a regular file no larger than 2 MiB.
- `--setting-sources` — Comma-separated list of setting sources to load (`user`, `project`, `local`).

### Plugins, directories, cloud

- `--plugin-dir` — Load a plugin from a directory or `.zip` archive for this session only; repeat per plugin.
- `--plugin-url` — Fetch a plugin `.zip` archive from a URL for this session only.
- `--add-dir` — Add additional working directories for Claude to read and edit files. Grants file access; most `.claude/` configuration is not discovered from these directories. To persist, set `permissions.additionalDirectories` in settings.
- `--cloud` — With a task description, create a new web session on claude.ai. With a session ID (`session_...` or `cse_...`) or a claude.ai/code URL, target that existing session instead: `-p` queues the message into it, and no `-p` attaches your terminal.
- `--remote` — Deprecated alias for `--cloud`, including the existing-session form.
- `--remote-control`, `--rc` — Start an interactive session with Remote Control enabled; optionally pass a name.
- `--remote-control-session-name-prefix <prefix>` — Prefix for auto-generated Remote Control session names; defaults to the machine hostname. `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` has the same effect.
- `--teleport` — Resume a web session in your local terminal.
- `--from-pr` — Open the session picker filtered to sessions linked to a specific pull request (PR number, GitHub/GHE PR URL, GitLab MR URL, Bitbucket PR URL). Sessions are linked automatically when Claude creates the pull request.
- `--environment <environment-id>` — Create a new cloud session on the self-hosted environment with the given ID (IDs start with `ccpool_`). Requires Claude Code v2.1.224 or later.
- `--ref <branch>` — With `--environment`, base the new session's checkout on a named ref instead of local `HEAD`.
- `--channels` — (Research preview) MCP servers whose channel notifications Claude should listen for; `plugin:<name>@<marketplace>` entries.
- `--dangerously-load-development-channels` — Enable channels not on the approved allowlist, for local development; prompts for confirmation.

### Subagents

- `--agent` — Specify an agent for the current session (overrides the `agent` setting).
- `--agents` — Define custom subagents dynamically via JSON. Example: `claude --agents '{"reviewer":{"description":"Reviews code","prompt":"You are a code reviewer"}}'`.

### Display, integration, process control

- `--ax-screen-reader` — Screen-reader friendly output; forces the classic renderer; attached background sessions still render fullscreen. Requires Claude Code v2.1.181 or later.
- `--teammate-mode` — How agent team teammates display: `in-process` (default), `auto`, `tmux`, or `iterm2` (added in v2.1.186).
- `--chrome` / `--no-chrome` — Enable/disable Chrome browser integration for this session.
- `--tmux` — Create a tmux session for the worktree. Requires `--worktree`. Uses iTerm2 native panes when available; pass `--tmux=classic` for traditional tmux. Example: `claude -w feature-auth --tmux`.
- `--exec` — Run a shell command as a PTY-backed background job instead of starting a Claude session. Use with `--bg` to launch from the shell. Example: `claude --bg --exec 'pytest -x'`.
- `--init` — Run Setup hooks with the `init` matcher before the session (print mode only).
- `--init-only` — Run Setup and `SessionStart` hooks, then exit without starting a conversation.
- `--maintenance` — Run Setup hooks with the `maintenance` matcher before the session (print mode only).
- `--max-budget-usd` — Maximum dollar amount to spend on API calls before stopping (print mode only). Spend from subagents counts toward the cap. Once spend reaches the cap, spawning another subagent fails with `Budget limit reached`, and Claude Code stops background subagents that are still running; the cap-enforcement behaviors require Claude Code v2.1.217 or later.
- `--max-turns` — Limit the number of agentic turns (print mode only). Exits with an error when the limit is reached. No limit by default. With `--input-format stream-json`, a message sent while Claude is working stays queued and runs as its own turn, with its own limit, when the limit ends the current one.
- `--json-schema` — Get validated JSON output matching a JSON Schema after the agent completes its workflow (print mode only).
- `--no-session-persistence` — Disable session persistence so sessions are not saved to disk and cannot be resumed. Print mode only. The `CLAUDE_CODE_SKIP_PROMPT_HISTORY` environment variable does the same in any mode.
- `--bare` — Minimal mode: skip auto-discovery of hooks, skills, custom commands, subagents, plugins, MCP servers, auto memory, and CLAUDE.md so scripted calls start faster. Skills in a directory passed with `--add-dir` still load. Claude has access to Bash, file read, and file edit tools. Sets `CLAUDE_CODE_SIMPLE`.
- `--safe-mode` — Start with all customizations disabled to troubleshoot a broken configuration. Managed settings policy still applies. Sets `CLAUDE_CODE_SAFE_MODE`.
- `--ide` — Automatically connect to IDE on startup if exactly one valid IDE is available.
- `--betas` — Beta headers to include in API requests (API key users only).
- `--debug` — Enable debug mode with optional category filtering, such as `--debug='mcp,startup'` or `--debug='!1p'`. The filter binds only in the `=` form.
- `--debug-file <path>` — Write debug logs to a specific file path. Implicitly enables debug mode. Takes precedence over `CLAUDE_CODE_DEBUG_LOGS_DIR`.
- `--disable-slash-commands` — Disable all skills and commands for this session.
- `--verbose` — referenced in the page's output-format examples but has no standalone entry in the fetched flags list.

## Page notes (verbatim points)

1. Subcommand routing with `--dangerously-skip-permissions`: as of v2.1.199, `claude --dangerously-skip-permissions daemon <subcommand>` runs the `daemon` subcommand. Earlier versions treated `daemon <subcommand>` as the prompt for a new interactive session. Only a leading `--dangerously-skip-permissions` or `--allow-dangerously-skip-permissions` routes to `daemon` this way.
2. Mistyped subcommands: Claude Code suggests the closest match and exits without starting a session (`claude udpate` prints `Did you mean claude update?`).
3. `claude --help` does not list every flag, so a flag's absence from `--help` does not mean it is unavailable.

## Supplement: `--worktree` / `-w` (from https://code.claude.com/docs/en/worktrees, fetched 2026-08-26; included because the cli-reference table row for this flag is truncated in page conversion)

- "Pass `--worktree` or `-w` with a name to create an isolated worktree and start Claude in it. By default, the worktree is created under `.claude/worktrees/<name>/` at your repository root, on a new branch named `worktree-<name>`." If you omit the name, Claude generates one such as `bright-running-fox`.
- Interactive runs require workspace trust; `--worktree` exits with an error if the directory was never trusted. Non-interactive runs with `-p` skip the trust check, so `claude -p --worktree` proceeds without it.
- New worktrees branch from the repository's default branch; set `worktree.baseRef` to `"head"` to branch from current local `HEAD`. It cannot be set to a branch name.
- PR/MR base: pass `"#<number>"`, a GitHub pull request URL, or a GitLab merge request URL; worktree is created at `.claude/worktrees/pr-<number>`. Before v2.1.233, only `#<number>` and GitHub-style PR URLs were accepted.
- Reusing a name whose directory already exists opens that existing worktree instead of creating a new one (fresh-base reset conditions apply; before v2.1.208 the old tip was always reopened).
- Resume: a session that was inside a worktree is returned to it (interactive, `-p` `--continue`/`--resume`, and Agent SDK). Before v2.1.212, a non-interactive resume stayed in the starting directory. `--fork-session` starts the fork in the launch directory, leaving the original session's worktree untouched. If the worktree directory no longer exists, the session resumes in the launch directory and the binding is cleared.
- Transcript relocation on worktree enter/exit requires Claude Code v2.1.198 or later.
- Isolation enforcement (file edits, command working directory, git redirects, command shape) applies to `--worktree` sessions, `EnterWorktree`, resumed worktree sessions, and every subagent they spawn, including background sessions.
- Subagent isolation: `isolation: worktree` frontmatter; a periodic sweep removes subagent/background-session worktrees older than `cleanupPeriodDays` but never removes worktrees you created with `--worktree`.
- Windows: removing a worktree doesn't delete files outside it; an NTFS junction or directory symlink inside is deleted as the link only. Before v2.1.205, removing a worktree with a link nested in a subdirectory could delete the folder it pointed to. Permission approvals granted in a worktree save to the main checkout's `.claude/settings.local.json`, except on Windows (and other cases where the local file stays in the starting directory), where the rule stays with that worktree.
