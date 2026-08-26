# Snapshot: Claude Code — Manage sessions

- Source URL: https://code.claude.com/docs/en/sessions
- Fetched: 2026-08-26
- Purpose: D-024 amendment-3 capability re-baseline (requirement D-024-R147)

Capture method: WebFetch; body below reproduced as returned (verbatim where quoted).

> Name, resume, branch, and switch between Claude Code conversations. Covers `--continue`, `--resume`, `--from-pr`, the `/resume` picker, session naming, exporting transcripts, and where transcripts are stored.

A session is a saved conversation tied to a project directory. Claude Code stores it locally as you work, so you can resume where you left off, branch to try a different approach, or switch between tasks. The desktop app, Claude Code on the web, and the VS Code extension each maintain their own session history. This page covers the CLI.

## Resume a session

| Command | What it does |
|---|---|
| `claude --continue` | Resumes the most recent interactive session in the current directory |
| `claude --resume` | Opens the session picker |
| `claude --resume <name>` | Resumes the named session directly |
| `claude --from-pr <number>` | Opens the session picker filtered to sessions linked to that pull request |
| `/resume` | Switches to a different conversation from inside an active session |

Claude Code leaves sessions created with `claude -p` or the Agent SDK out of the session picker and out of `claude --continue`. You can still resume one by passing its session ID to `claude --resume <session-id>`. With `claude --continue`, Claude Code also skips background sessions and sessions whose first prompt was `/loop`. When you run `claude -p --continue`, Claude Code includes `-p`, SDK, and `/loop` sessions and still skips background sessions.

You can run `claude --resume <session-id>` from any directory: Claude Code looks for the ID in the current project directory and its git worktrees first, then in every other project on this machine, so it finds a session that started elsewhere or moved with `/cd`. The cross-project search resolves the ID only when exactly one other project holds a transcript with messages for it, so a hand-copied duplicate makes Claude Code report not-found rather than resume an arbitrary copy. If no stored session matches the ID, Claude Code reports `No conversation found with session ID: <session-id>`. Before v2.1.223, the lookup stopped at the current project directory and its git worktrees.

### What a resumed session restores

- Conversation history: the full history, including tool calls and results.
- Model: the session continues on the model it was using, with exceptions (retired model, `availableModels` restriction, a `--model` flag or `ANTHROPIC_MODEL`-family env var at launch, provider-specific deployment IDs on Bedrock / Google Cloud's Agent Platform / Microsoft Foundry).
- Agent: a session started with `--agent` or the `agent` setting continues as that agent, keeping its system prompt, tool restrictions, and model. Pass `--agent` when resuming to pick a different one. Claude Code looks for the agent in the session's original directory (if that workspace is trusted), then the directory you resume from. If not found, the session resumes with the default tools and system prompt and shows a warning naming the agent.
- Permission mode: the mode the session was in, except: `plan` and `bypassPermissions` are never restored; `auto` is restored only when the account still meets the auto mode requirements; Manual is restored as Manual when a new session would start in auto mode from the built-in default. Pass `--permission-mode` to override.
- Active goal: carries over; its turn count, timer, and token-spend baseline reset.
- Scheduled tasks: tasks that haven't expired are restored. Background Bash and monitor tasks aren't.

Not every configuration flag from the original launch is restored. If the session depended on `--mcp-config`, `--settings`, `--plugin-dir`, `--fallback-model`, or directories added with `--add-dir`, pass them again when you resume; directories added mid-session with `/add-dir` aren't restored either, though the session picker still uses them to locate the session. The standard settings files are re-read at launch.

### Resume from a summary

On a Pro or Max plan, when you resume a session that has been inactive for more than about an hour and is over 100,000 tokens, Claude Code restores the conversation and then opens a dialog before the first message. Options: "Resume from summary" (runs `/compact` immediately; later requests carry the summary, recent exchanges, and up to five recently read files), "Resume full session as-is" (reprocesses and re-caches the full history), "Don't ask me again".

### Where the session picker looks

Sessions are stored per project directory. By default the picker shows sessions from the current worktree (background sessions marked `bg`) and sessions started elsewhere that added the current directory with `/add-dir`. `Ctrl+W` widens to all worktrees of the repository; `Ctrl+A` to every project on this machine.

Sessions whose first prompt was a `/loop` command don't appear in the picker, and `claude --continue` skips them too. Running `/loop` later in a conversation doesn't hide the session. Before v2.1.211, a `/loop` run early in a conversation hid the session from the picker permanently.

From v2.1.169, moving a session with `/cd` relocates it to the new directory's project storage. As of v2.1.196, a moved session stays out of the old directory's picker even after a crash or forced exit.

Selecting a session from another worktree of the same repository resumes it in place; when the session's own worktree no longer exists, it resumes in your current directory. Selecting a session from an unrelated project copies a `cd` and resume command to your clipboard instead; if that project's directory no longer exists, it resumes in the current directory.

Resuming by name resolves across the current repository and its worktrees:

| Command | Exact match | Ambiguous name |
|---|---|---|
| `claude --resume <name>` | Resumes directly | Opens the session picker with the name pre-filled as a search term |
| `/resume <name>` | Resumes directly | Reports an error; run `/resume` with no argument to open the picker |

## Name your sessions

| When | How to set the name |
|---|---|
| At startup | `claude -n auth-refactor` |
| During a session | `/rename auth-refactor`. The name also appears on the prompt bar |
| From the session picker | Highlight a session and press `Ctrl+R` |
| On plan accept | Accepting a plan gives the session a generated title based on the plan unless already named |
| From claude.ai or the Claude app | Rename a Remote Control session; Claude Code applies the same name in the CLI. Requires Claude Code v2.1.221 or later |
| From the desktop app | Rename a session in the desktop app |

When you start or resume an interactive session with a name another live session on this machine already uses, or rename into such a name, Claude Code leaves the name with the session that already has it, renames yours to a variant with a two-word suffix, such as `auth-refactor-graceful-unicorn`, and tells you. Before v2.1.232, both sessions kept the name. Exceptions (no rename): AI-generated titles or default display names aren't checked; the `--name` of a background or `-p` session at startup isn't checked; a session on an earlier version of Claude Code can't be renamed.

Sessions you don't name still get two labels; only the generated title works as a resume handle:

- Default display name: interactive sessions never named get a default display name at start. Requires Claude Code v2.1.196 or later. Combines the working directory's name with a two-character suffix, for example `my-app-3f`, and identifies the session in listings of running sessions, such as agent view and `claude agents --json` output. The default is NOT a resume handle; passing it to `claude --resume` or `/resume` finds nothing.
- Generated title: a short summary of the first prompt, written by a background request to the small/fast model, normally a Haiku-class model. Accepting a plan replaces it with a plan-based title. Either title can be passed to `claude --resume` or `/resume` and resolves like a set name.

## Use the session picker

`/resume` inside a session, or `claude --resume` with no arguments. Shortcuts: up/down navigate; right/left expand/collapse grouped sessions; Enter resume; Space preview (`Ctrl+V` also works); `Ctrl+R` rename; `/` or printable character searches (paste a GitHub/GHE/GitLab/Bitbucket PR or MR URL to find the session that created it); `Ctrl+A` all projects; `Ctrl+W` all worktrees (multi-worktree repos only); `Ctrl+B` filter to current git branch; `Esc` exit.

Each row shows the session name (or AI-generated title, conversation summary, or first prompt), time since last activity, git branch, and file size. Sessions created with `/branch` or `--fork-session` get their own session IDs and appear as separate rows; duplicate entries for the same session group under a single row (`→` expands).

If the session can't be loaded from the `claude --resume` picker, Claude Code prints `Failed to resume the conversation` with a retry command, then exits with code 1. From the `/resume` picker inside a session, the failure is reported and the current conversation keeps running.

## Branch a session

Branching creates a copy of the conversation so far and switches you into it, leaving the original intact. From inside a session: `/branch [name]` (for example `/branch try-streaming-approach`). If the name is omitted, the branch is named after the first prompt; as of v2.1.198 this also applies after compaction (earlier versions fell back to the literal name `Branched conversation`).

From the command line, combine `--continue` or `--resume` with `--fork-session`: `claude --continue --fork-session`.

The `/branch` confirmation prints two session IDs: the new branch and the original. What the branch inherits:

| State | After `/branch` |
|---|---|
| Conversation history | Copied into the branch up to the point you ran `/branch` |
| "Allow for this session" permission grants | Carried over (same process). If you fork into a separate process with `--fork-session`, the new process starts without them and you re-approve there |
| In-flight background subagents and background Bash commands | Keep running. Their output appears in the new branch, not the original |
| Remote Control connection | Stays connected; a connected phone or browser follows you into the branch |

If you resume the same session in two terminals without forking, messages from both interleave into one transcript.

## Manage context within a session

- `/clear`: start fresh with an empty context. The previous conversation is saved; resume with `/resume` or the rewind menu's previous-session entry. A name set with `--name` or `/rename` is kept in the new conversation, but not an AI-generated title.
- `/compact [instructions]`: replace history with a summary, optionally focused.
- `/context`: show what is currently consuming context.

## Export and locate session data

`/export` opens a menu to copy the conversation to the clipboard or save as plain text; pass a filename to write directly.

### Access conversations from scripts

- Run Claude once and capture the result: `claude -p` with `--output-format json` or `stream-json` captures the result, session ID, usage, and cost as structured JSON.
- Ask an existing session a question: pass a session ID to `claude -p --resume` and capture the structured response. Example: `claude -p --resume <session-id> --output-format json "summarize what we changed" | jq -r '.result'`
- React to session events: read the `transcript_path` field that hooks and status line commands receive as input. A `SessionEnd` hook can archive the transcript when a session ends.
- Embed Claude in a TypeScript or Python app: use the Agent SDK.

### Where transcripts are stored

By default, transcripts are JSONL at `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the working directory path with non-alphanumeric characters replaced by `-`. Converted names over 200 characters are truncated to 200 and a hash of the full path appended. Each line is a JSON object for a message, tool use, or metadata entry. The entry format is internal and changes between versions, so scripts that parse these files directly can break on any release; use `/export` or the script interfaces instead.

| To | Set | Where |
|---|---|---|
| Move storage off `~/.claude` | `CLAUDE_CONFIG_DIR` | Environment variable |
| Name the `<project>` directory yourself | `CLAUDE_CODE_PROJECT_DIR_NAME` | Environment variable |
| Change the 30-day retention | `cleanupPeriodDays` | `settings.json` |
| Suppress transcript writes in all modes | `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | Environment variable |
| Suppress writes for one non-interactive run | `--no-session-persistence` | CLI flag with `claude -p` |

### Name the project directory yourself

Set `CLAUDE_CODE_PROJECT_DIR_NAME` alongside `CLAUDE_CONFIG_DIR` to choose the `<project>` name. Requires Claude Code v2.1.234 or later. Rules: set `CLAUDE_CONFIG_DIR` too (ignored otherwise); use 1-64 letters, digits, hyphens, or underscores — don't use a Windows device name such as `con`; set it in the shell environment that starts `claude` (an `env` block in a settings file can't set it). Sessions stored under either the custom or derived name remain resumable by session ID either way.

## See also

Worktrees (isolated parallel sessions), Checkpointing (rewind), Context window, Non-interactive mode (`claude -p`).
