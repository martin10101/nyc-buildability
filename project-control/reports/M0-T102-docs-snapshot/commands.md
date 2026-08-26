# Snapshot: Claude Code — Slash commands

- Source URL: https://code.claude.com/docs/en/commands
- Fetched: 2026-08-26
- Purpose: D-024 amendment-3 capability re-baseline (requirement D-024-R147)

Capture method: WebFetch; structured summary as returned by the fetch, command descriptions preserved. Commands are recognized only at the start of a message and can accept arguments. Up to six skills can be chained in a single invocation (as of v2.1.199).

## Session management

- `/background [prompt]` — Detach the current session to run as a background agent and free the terminal. Pass an optional prompt to send one more instruction before detaching. Monitor with `claude agents`. Alias: `/bg`. (No version gate stated.)
- `/resume` — Return to an earlier conversation. Works across sessions.
- `/fork [prompt]` — Copy the current conversation into a new background session while keeping the current one running. Pass an optional prompt for the copy to start working immediately. Requires Claude Code v2.1.212+; earlier versions run a forked subagent instead.
- `/branch [name]` — Create a branching point in the current conversation to try a different direction without losing the original. Switch into the branch; return to original with `/resume`.
- `/clear [name]` — Start a new conversation with empty context while keeping project memory. Pass a name to label the previous conversation in the `/resume` picker. Aliases: `/reset`, `/new`.
- `/cd <path>` — Move the session to a new working directory, keeping conversation and prompt cache. Requires Claude Code v2.1.169+.
- `/rewind` — Roll code and conversation back to a checkpoint, or summarize part of the conversation.
- `/exit` / `/quit` — Exit CLI. In an attached background session, detaches; the session keeps running.

## Agents and subagents

- `/agents` — (v2.1.198+) Prints a reminder to ask Claude to create or manage subagents, or edit `.claude/agents/` / `~/.claude/agents/` directly. Earlier versions opened an interactive interface.
- `/list-agents` — List subagents, agent team teammates, and other sessions Claude can message. Requires v2.1.224+; teammate rows and own session name require v2.1.239+.
- `/subtask` — Hand a side task to a subagent that reports back into this conversation.
- `/tasks` — List current session's background work including finished subagents (runs immediately).

## Review and diagnostics

- `/code-review [low|medium|high|xhigh|max|ultra] [--fix] [--comment] [pr#|branch|path]` — [Skill] Review the current diff or target; `--fix` applies findings; `--comment` posts as GitHub PR comments; `ultra` runs a deep cloud review. Alias: `/review`.
- `/security-review` — Check the current diff for security vulnerabilities.
- `/diff` — Interactive diff viewer: uncommitted changes and per-turn diffs.
- `/debug [description]` — [Skill] Enable debug logging and troubleshoot via the session debug log.
- `/doctor` — [Skill] Setup checkup: install health, unused skills/MCP servers, slow hooks, version updates; can trim bloated CLAUDE.md (trim requires v2.1.206+; before v2.1.205, read-only screen).
- `/bug [report]` / `/share` — Report bug or share conversation (before v2.1.232 queued until turn end; before v2.1.212 aliases of `/feedback`). `/feedback [report]` — product feedback.
- `/heapdump` — Heap snapshot + memory breakdown (hidden from menu; `.heapsnapshot` contains full conversation and credentials).

## Model and reasoning

- `/model [model]` — Switch model (saved as default for new sessions; `s` switches for current session only). In `-p` mode requires a model argument, applies to current session only (v2.1.205+).
- `/effort [level|auto|status]` — `low`–`xhigh`, `max`, `ultracode`, or `auto`; `max` and `ultracode` session-only. Works in `-p`.
- `/advisor [model|off]` — Advisor tool; accepts `fable`, `opus`, `sonnet`, or full model ID; `fable` requires Fable 5 access.
- `/fast [on|off]` — Toggle fast mode. Limited in `-p` mode. (v2.1.205+)

## Context and memory

- `/compact [instructions]` — Summarize conversation to free context.
- `/context [all]` — Visualize context usage.
- `/memory` — Edit CLAUDE.md files, manage auto memory.
- `/autocompact [auto|<tokens>]` — Set auto-compact window (e.g. `500k`). Saves to user settings, applies to current session. (v2.1.221+)

## Workflow

- `/batch <instruction>` — [Skill] Orchestrate large-scale changes: decomposes into 5–30 units, spawns one background subagent per unit in an isolated git worktree. Requires a git repository.
- `/deep-research <question>` — [Workflow] Fan out web searches, synthesize a cited report.
- `/plan [description]` — Enter plan mode.
- `/loop [interval] [prompt]` — [Skill] Run a prompt repeatedly while the session stays open. Alias: `/proactive`.
- `/goal [condition|clear]` — Set a goal; Claude works across turns until met.
- `/autofix-pr [prompt]` — Spawn a cloud session watching the current branch's PR, pushing fixes on CI failure or reviewer comments. Requires `gh` CLI and web access.
- `/verify` — [Skill] Runs only when invoked (before v2.1.215 Claude could run it autonomously).

## Setup and configuration

- `/init` — Initialize project with CLAUDE.md.
- `/permissions` — Manage allow/ask/deny rules; opens immediately mid-response (v2.1.234+).
- `/mcp [reconnect <server>|enable|disable [<server>|all]]` — Manage MCP servers; `-p` text summary requires v2.1.205+.
- `/config [key=value ...]` — Settings interface or direct set (v2.1.181+); works in `-p` and via Remote Control. Alias: `/settings`.
- `/add-dir <path>` — Add working directory; usable while Claude is working (v2.1.234+).
- `/theme` / `/color` — Prompt bar color; works in `-p` (v2.1.205+).
- `/import [codex|gemini] [--dry-run] [--yes]` — Import configuration from other agents (v2.1.213+; unavailable on Bedrock/GCP/Foundry/AWS platforms or without feature-flag fetching).
- `/auto-mode-setup` — Draft `autoMode.environment` entries (Pro/Max/Team, v2.1.228+; native Windows requires v2.1.233+).
- `/keybindings`, `/install-github-app`, `/install-slack-app`, `/login`, `/logout`, `/privacy-settings`, `/plugin [list|install|enable|disable]`, `/reload-plugins`.

## Utility

- `/btw [question]` — Side question without adding to history (before v2.1.212 required a question).
- `/status` — Session status (runs immediately). `/usage` (alias `/cost`) — token usage and cost.
- `/copy [N]` — Copy last (or Nth-latest) assistant response; `w` writes to file (useful over SSH).
- `/export [filename]` — Export conversation as plain text.
- `/focus` — Toggle focus view (fullscreen rendering only; persists via `viewMode` setting).
- `/help`, `/powerup`, `/passes`, `/radio` (unavailable on Bedrock/GCP/Foundry/AWS), `/rate-limit-options` (hidden; v2.1.234+ for wait-and-continue rows), `/upgrade` (not shown on Enterprise).

## Remote, IDE, desktop

- `/desktop` / `/app` — Continue in the desktop app (macOS or x64 Windows, Claude subscription).
- `/ide`, `/chrome`, `/mobile` / `/ios` / `/android`.
- `/teleport` — Pull a web session into this terminal. `/dr-remote-control` — continue a local session from another device.

## Other skills

- `/dataviz [request]` (v2.1.198+), `/design-sync [hint]` + `/design-login` (unavailable on Bedrock/GCP/Foundry/AWS), `/claude-api [migrate|upgrade|managed-agents-onboard|prompt-audit]` (prompt-audit v2.1.221+; upgrade v2.1.236+), `/fewer-permission-prompts`.
- `/pr-comments [PR]` — Removed in v2.1.91.

## Version gates and platform notes (as listed on the page)

- v2.1.234+: `/add-dir`, `/theme`, `/permissions` open immediately in fullscreen rendering instead of queuing.
- v2.1.212+: `/fork` background-session behavior; earlier versions run a forked subagent.
- v2.1.205+: `/config key=value`, `/fast`, `/mcp` text summary in `-p` mode.
- v2.1.198+: `/agents` prints reminder (earlier interactive); `/dataviz` added.
- v2.1.191+: `/clear` restores from rewind menu's previous-session entry.
- v2.1.169+: `/cd` added.
- Native Windows: `/auto-mode-setup` requires v2.1.233+.
- Unavailable on Amazon Bedrock, Google Cloud Agent Platform, Microsoft Foundry, Claude Platform on AWS: e.g. `/design-sync`, `/import`, `/radio`.

Custom commands are added via skills (prompts handed to Claude; up to six chained per invocation).
