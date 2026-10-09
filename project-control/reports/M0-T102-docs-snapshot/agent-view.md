# Snapshot: Claude Code docs — Agent View

- Source URL: https://code.claude.com/docs/en/agent-view
- Fetched: 2026-08-26
- Purpose: D-024 amendment-3 capability re-baseline, requirement D-024-R147
- Capture method: WebFetch transcription of the official page (two passes over the same cached fetch: a full-page transcription, then a targeted verbatim extract of version-gate / platform / research-preview / supervisor-recovery sentences). No editorial changes; content below reproduces what the page said as fetched.

---

## Part 1 — Full-page transcription

# Manage Multiple Agents with Agent View

Agent view is Claude Code's interface for dispatching and managing many background sessions from one screen. It shows what every session is doing, which ones need your input, and which are done.

## Overview

**Status**: Agent view is in research preview. The interface and keyboard shortcuts may change as the feature evolves.

Open agent view with:

    claude agents

Agent view displays sessions grouped by state (Needs input, Working, Completed), showing each session's name, current activity, and age. Sessions keep running after you close agent view and reappear the next time you open it.

## Core Workflow

1. **Open agent view**: `claude agents`
2. **Dispatch a session**: Type a prompt and press `Enter`
3. **Peek and reply**: Select a row with arrow keys, press `Space` to open peek panel
4. **Attach for full conversation**: Press `Enter` or right-arrow to enter full interactive mode
5. **Detach**: Press left-arrow on empty prompt to return to agent view

## Session States

Each row's icon indicates state:

| State | Icon | Meaning |
|-------|------|---------|
| Working | Animated | Claude actively running tools or generating |
| Needs input | Yellow | Waiting for your answer or permission |
| Idle | Dimmed | Ready for next prompt |
| Completed | Green | Task finished successfully |
| Failed | Red | Task ended with error |
| Stopped | Grey | Stopped with `Ctrl+X` or `claude stop` |

Icon shape shows process status: spinner/asterisk = process alive, replies immediately; small dot = process exited but can be resumed; four-point star = `/loop` session sleeping between iterations.

## Managing Sessions

### From Agent View

**Dispatch new sessions**: Type prompt + `Enter`

**Keyboard shortcuts**: Up/Down move between rows; `Enter` attaches to session or dispatches if text in input; `Space` opens/closes peek panel; `Shift+Enter` dispatches and attaches immediately; right-arrow attaches to selected session; `Ctrl+S` toggles grouping (state vs directory); `Ctrl+T` pins session (keeps process running); `Ctrl+R` renames session; `Ctrl+X` stops — press again within 2 seconds to delete; `Shift+Up`/`Shift+Down` reorder sessions; `?` shows all shortcuts.

**Filtering** (type in dispatch input): `a:<name>` — sessions running named agent; `s:<state>` — sessions in given state (e.g., `s:working`); `s:blocked` — everything waiting on you; `#<number>` or PR/MR URL — session working on that PR/MR; any URL — session whose first prompt contained it.

### From Shell

    # Start background session
    claude --bg "task description"

    # Set custom name
    claude --bg --name "session-name" "task description"

    # Run specific subagent
    claude --agent code-reviewer --bg "review PR 1234"

    # Run shell command as background job
    claude --bg --exec 'pytest -x'

    # List sessions as JSON
    claude agents --json
    claude agents --json --all
    claude agents --json --cwd ~/projects/my-app

    # Attach to session
    claude attach <id>

    # View recent output
    claude logs <id>

    # Stop session
    claude stop <id>
    claude kill <id>

    # Restart session
    claude respawn <id>
    claude respawn --all

    # Remove session
    claude rm <id>

    # Check supervisor status
    claude daemon status

    # Stop supervisor
    claude daemon stop --any
    claude daemon stop --any --keep-workers

### From Inside a Session

- `/background` or `/bg` — Move conversation to background, optionally with new instruction
- `/fork` — Copy conversation to new background session while keeping current one open

## JSON Output Format

`claude agents --json` returns an array with entries containing:

**Always present**: `cwd` — working directory; `kind` — `interactive` or `background`; `startedAt` — Unix milliseconds.

**Background sessions**: `id` — short ID for `claude attach`/`logs`/`stop`; `state` — `working`, `blocked`, `done`, `failed`, or `stopped`.

**While process running**: `pid` — process ID; `status` — current status.

**When waiting**: `waitingFor` — `permission prompt`, `input needed`, `sandbox request`, `worker request`, or `dialog open`.

**When set**: `sessionId` — full UUID for `claude --resume`; `name` — display name.

## Configuration Flags

Open agent view with defaults for all dispatched sessions:

    claude agents --permission-mode plan --model opus --effort high
    claude agents --agent code-reviewer
    claude agents --dangerously-skip-permissions
    claude agents --allow-dangerously-skip-permissions

    # Add directories and load MCP/plugins
    claude agents --add-dir ../shared-lib
    claude agents --mcp-config ./mcp.json
    claude agents --plugin-dir ./my-plugin
    claude agents --settings ./ci-settings.json

## File Isolation

Background sessions automatically move into git worktrees under `.claude/worktrees/` before editing files, allowing parallel sessions to work independently. To disable:

    {
      "worktree": {
        "bgIsolation": "none"
      }
    }

When a session finishes with code changes, it: **commits and pushes** the work; **opens a draft PR** when appropriate; **never** force-pushes or merges to main.

## Pull Request Status

Sessions show linked PR/MR numbers at the row's right edge: `#1234` — pull request; `!1234` — GitLab merge request; `3 PRs` — multiple pull requests. Color indicates status: yellow — waiting on checks/review or checks failed; green — checks passed, no review blocking; purple — merged; grey — draft or closed.

## Session Deletion

`Ctrl+X` (twice) or `claude rm <id>` removes a session from the list. Worktree handling: **agent view** removes the worktree (including uncommitted changes); **`claude rm`** keeps the worktree if it has uncommitted changes; **neither** removes worktrees with unpushed commits or locked by other sessions. The transcript always stays on disk via `claude --resume`.

## Background Session Hosting

Sessions run via a per-user supervisor process (`~/.claude/daemon.log`). Key behaviors:

- Sessions survive machine sleep
- Idle non-pinned sessions stop after ~1 hour to free resources (auto-resume when attached)
- Supervisor auto-updates to new Claude Code versions
- Supervisor captures environment from the shell that opened agent view
- Gateway variables (`ANTHROPIC_BASE_URL`) forwarded only when both conditions met: supervisor started from a shell with the same gateway, and the session dispatched into the same directory or is your own backgrounded session

**State storage**:

    ~/.claude/daemon.log              Supervisor log
    ~/.claude/daemon/roster.json      Running sessions list
    ~/.claude/jobs/<id>/state.json    Per-session state
    ~/.claude/jobs/<id>/tmp/          Session scratch directory

Sessions have a `CLAUDE_JOB_DIR` environment variable pointing to their directory.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `claude agents` lists subagents | Run `claude update` |
| Agent view closed when opening | Check `disableAgentView` setting or `CLAUDE_CODE_DISABLE_AGENT_VIEW` env var |
| Sessions show failed after shutdown | Sleep preserves sessions; shutdown stops them. Attach/peek/reply to resume |
| "Conversation already open in another session" | Reply in the session that has it, or exit it |
| "No saved transcript" on stopped session | Press `Enter` again to restart fresh, or `claude respawn <id>` |
| "Possibly low memory" exit | Free memory and retry; supervisor auto-stops idle sessions if needed |
| "Background service did not respond" | `claude daemon stop --any --keep-workers` then retry |
| Desktop/Documents/Downloads inaccessible on macOS | Grant file access in System Settings > Privacy & Security > Files and Folders |
| Can't reach local-network hosts on macOS 15+ | Grant Local Network permission when prompted |

## Limitations

- **Rate limits apply**: background sessions consume quota at the session count (10 parallel is about 10x usage)
- **Local only**: sessions run on your machine, preserved across sleep but stopped by shutdown
- **Worktree cleanup**: commit changes before deleting a session that edited files

## Disabling Agent View

Set `disableAgentView: true` in settings or the `CLAUDE_CODE_DISABLE_AGENT_VIEW` environment variable to turn off agent view entirely.

---

## Part 2 — Targeted verbatim extract (same page, same fetch date)

Sentences extracted verbatim in a second pass focused on version gates, platform behavior, research-preview status, and supervisor/daemon recovery.

### (1) Specific Claude Code version requirements

- "Copying the session requires Claude Code v2.1.212 or later; on v2.1.161 through v2.1.211, `/fork` starts a forked subagent instead, which is now `/subtask`."
- "To bring a session back on Claude Code v2.1.212 or later, type `/resume` in the dispatch input."

### (2) Platform support / platform-specific behavior

Windows:

- "On Windows, if you press the left-arrow within about half a second of attaching, Claude Code shows `Ambiguous, press again to detach`, because in that window the terminal can redeliver a press from before you attached."
- "On Windows, if the supervisor doesn't respond to the stop request, the command prints its process ID."

macOS:

- "On macOS, the background session host runs as its own process and requests access to protected folders separately from your terminal."
- "On macOS 15 and later, the system blocks a process from reaching devices on your local network until you grant Local Network permission, so a command targeting a LAN address can fail with `connect: no route to host` in a background session even though it works in a foreground terminal."
- "With the native installer, the entry appears as Claude Code and the grant persists across updates."

### (3) Research preview / experimental status

- "Agent view is in research preview. The interface and keyboard shortcuts may change as the feature evolves."
- "Agent view is in research preview with the following limitations:"

### (4) Daemon/supervisor behavior, including recovery after crash/restart/sleep/shutdown

- "Background sessions don't need any terminal open to keep working. A separate supervisor process runs them, so you can close agent view, close your shell, or start a new interactive session and your dispatched work keeps going."
- "Session state persists on disk through auto-updates and supervisor restarts."
- "Sessions are also preserved when your machine sleeps. Their processes resume on wake and the supervisor reconnects to them instead of treating the time gap as idle."
- "Shutting down still stops running sessions; see Sessions show as failed after shutdown for how to recover them."
- "A session that was mid-response when the machine slept can come back unresponsive. When you open a session that has stopped responding, the supervisor restarts its process and the session continues the interrupted response from where it left off."
- "Once a session finishes and sits unattached for about an hour, the supervisor stops its process to free resources."
- "When every session has finished and no terminal is connected, the supervisor itself exits and starts again the next time you need it."
- "The supervisor also restarts a session whose process exits unexpectedly, with three safeguards so a restart never overrides a stop or acts on stale input."
- "A session whose state on disk already shows it as done, failed, or stopped isn't restarted, unless a reply you sent is still waiting to be delivered."
- "Ending the process of a session you backgrounded with the left-arrow or `/background` yourself, for example with `kill`, marks the session stopped instead of restarting it."
- "A session the supervisor restarts is told it was restarted and that you haven't sent a new message since, so it can re-verify time-sensitive context such as branch state before continuing."
- "A restarted left-arrow or `/background` session also doesn't resume an interrupted response older than about an hour; it waits for your next message instead."
- "Background work the session itself started at the top level is handed off when its process is stopped, restarted, or updated, including on Windows."
- "The supervisor watches the installed Claude Code binary on disk and restarts into the new version after the regular auto-updater replaces it."
- "Background sessions are detached processes, so they keep running through the restart and the new supervisor reconnects to them."
- "An idle pinned session is also restarted in place onto the new version so it picks up the update without you reattaching."
- "Once the new supervisor takes over, it also restarts the remaining idle sessions onto the new version, a few at a time in the background, after a short delay that lets terminals attached across the restart reconnect first."
- "A session that is working, waiting on your input, or has a terminal attached isn't interrupted; it moves to the new version the next time its process restarts."
- "These restarts only ever move a session onto a newer version. A supervisor running an older Claude Code version than the one a session's process was started with leaves that process alone; the session keeps running the newer version until a newer supervisor takes over."
- "Running `claude attach` while the supervisor is restarting a session, whether for an update, a stall, or a migration, waits for the replacement process instead of failing."
- "Sleep alone doesn't cause this. Sessions are preserved across sleep and the supervisor reconnects to them on wake."
- "Shutting down or restarting your machine stops running background sessions, so they show as failed when you next open agent view."
