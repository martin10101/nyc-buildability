# Snapshot: Claude Code hooks reference

- Source URL: https://code.claude.com/docs/en/hooks
- Fetch date: 2026-08-26
- Purpose: D-024 amendment-3 capability re-baseline, requirement D-024-R147.
- Capture method: WebFetch (page converted to markdown; extraction-model capture, verbatim where load-bearing). Snapshot of what the docs say; no editorializing.

---

## Complete list of hook events (as documented on this page)

1. SessionStart
2. Setup
3. UserPromptSubmit
4. UserPromptExpansion
5. PreToolUse
6. PermissionRequest
7. PermissionDenied
8. PostToolUse
9. PostToolUseFailure
10. PostToolBatch
11. Notification
12. MessageDisplay
13. SubagentStart
14. SubagentStop
15. TaskCreated
16. TaskCompleted
17. Stop
18. StopFailure
19. TeammateIdle
20. InstructionsLoaded
21. ConfigChange
22. CwdChanged
23. DirectoryAdded
24. FileChanged
25. WorktreeCreate
26. WorktreeRemove
27. PreCompact
28. PostCompact
29. Elicitation
30. ElicitationResult
31. SessionEnd

---

## Hook events reference

### SessionStart

**When it fires:** When a session begins or resumes

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** Yes. Filters on how the session started: `startup`, `resume`, `clear`, `compact`, `fork`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `model` (not guaranteed to be present; only SessionStart hooks receive it)

**Timeout default:** 600 seconds for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `systemMessage`, `additionalContext`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user, session proceeds
- Other non-zero: non-blocking error

---

### Setup

**When it fires:** When you start Claude Code with `--init-only`, or with `--init` or `--maintenance` in `-p` mode. For one-time preparation in CI or scripts.

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** Yes. Filters on which CLI flag triggered setup: `init`, `maintenance`

**Common input fields:** `session_id`, `cwd`, `hook_event_name`

**Timeout default:** 600 seconds for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `systemMessage`, `additionalContext`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user, setup proceeds
- Other non-zero: non-blocking error

---

### UserPromptSubmit

**When it fires:** When you submit a prompt, before Claude processes it

**Can block:** Yes. Blocks prompt processing and erases the prompt on exit 2.

**Matcher support:** No. Always fires on every occurrence.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`

**Event-specific input fields:** `user_prompt` (the text of the prompt)

**Timeout default:** 30 seconds (lowered from 600) for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `permissionDecision`, `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success; plain-text stdout is added as context Claude can see
- Exit 2: blocks prompt, erases prompt; stderr shown
- Other non-zero: non-blocking error; plain-text stdout added as context

**Note:** stdout is written to the Claude context (visible), not to debug log only.

---

### UserPromptExpansion

**When it fires:** When a user-typed command expands into a prompt, before it reaches Claude. Can block the expansion.

**Can block:** Yes. Blocks the expansion on exit 2.

**Matcher support:** Yes. Filters on command name (your skill or command names).

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`

**Event-specific input fields:** `command_name`, `expanded_prompt`

**Timeout default:** 600 seconds for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `permissionDecision`, `additionalContext`, `updatedInput`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: blocks expansion; stderr shown
- Other non-zero: non-blocking error

---

### PreToolUse

**When it fires:** Before a tool call executes. Can block it.

**Can block:** Yes. Blocks the tool call on exit 2.

**Matcher support:** Yes. Filters on tool name (e.g., `Bash`, `Edit`, `mcp__memory__.*`)

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort` (when present in tool-use context and model supports it), `hook_event_name`, `agent_id` (when running in subagent), `agent_type` (when running with `--agent` or in subagent)

**Event-specific input fields:** `tool_name`, `tool_input` (contains the tool parameters), `tool_use_id`

**Timeout default:** 600 seconds for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `permissionDecision`, `additionalContext`, `updatedInput`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: blocks tool call; stderr shown; timed-out `command`/`http`/`mcp_tool` hooks do not block (but Agent SDK callback hooks do)
- Other non-zero: non-blocking error

**Note on `if` condition:** Supports permission rule syntax like `"Bash(rm *)"` or `"Edit(*.ts)"`. Only evaluated on tool events.

**Note on Agent SDK:** A timed-out Agent SDK callback hook blocks the tool call.

---

### PermissionRequest

**When it fires:** When a tool call needs a permission decision

**Can block:** No. Exit code 2 is not honored; use the `decision` object instead.

**Matcher support:** Yes. Filters on tool name.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`, `agent_id`, `agent_type`

**Event-specific input fields:** `tool_name`, `tool_input`, `tool_use_id`, `permission_already_denied` (boolean; true if a hook already denied this tool call)

**Timeout default:** 600 seconds for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `decision` (object with `allow` boolean and optional `reason` string)

**Exit code contract:**
- Exit 0: success; JSON `decision` object is honored
- Exit 2: not honored; use JSON `decision` instead
- Other non-zero: non-blocking error

---

### PermissionDenied

**When it fires:** When auto mode denies a tool call, including denials without a classifier verdict.

**Can block:** No. Exit code and stderr are ignored because the denial already occurred.

**Matcher support:** Yes. Filters on tool name.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`, `agent_id`, `agent_type`

**Event-specific input fields:** `tool_name`, `tool_input`, `tool_use_id`, `denial_reason`, `classifier_verdict` (present when classifier produced a verdict; absent for no-verdict denials)

**Timeout default:** 600 seconds

**JSON decision fields:** `hookSpecificOutput.retry` (boolean; tells model it may retry the denied tool call). Claude Code ignores `retry: true` for no-verdict denials.

**Exit code contract:**
- Exit code and stderr are ignored
- JSON `hookSpecificOutput.retry: true` is honored (except for no-verdict denials)

---

### PostToolUse

**When it fires:** After a tool call succeeds

**Can block:** No. Shows stderr to Claude; the tool already ran.

**Matcher support:** Yes. Filters on tool name.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`, `agent_id`, `agent_type`

**Event-specific input fields:** `tool_name`, `tool_input`, `tool_use_id`, `tool_output` (the result of the tool call)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to Claude
- Other non-zero: non-blocking error; stderr shown

---

### PostToolUseFailure

**When it fires:** After a tool call fails

**Can block:** No. Shows stderr to Claude; the tool already failed.

**Matcher support:** Yes. Filters on tool name.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`, `agent_id`, `agent_type`

**Event-specific input fields:** `tool_name`, `tool_input`, `tool_use_id`, `tool_error` (error message or details)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to Claude
- Other non-zero: non-blocking error; stderr shown

---

### PostToolBatch

**When it fires:** After a full batch of parallel tool calls resolves, before the next model call

**Can block:** Yes. Stops the agentic loop before the next model call on exit 2.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`

**Event-specific input fields:** `tool_calls` (array of tool call objects with `tool_name`, `tool_input`, `tool_use_id`, `tool_output`, `tool_error`)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stops agentic loop
- Other non-zero: non-blocking error

---

### Notification

**When it fires:** When Claude Code sends a notification

**Can block:** No. Exit code and stderr are ignored.

**Matcher support:** Yes. Filters on notification type: `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled`

**Common input fields:** `session_id`, `hook_event_name`

**Event-specific input fields:** `notification_type`, `notification_data` (varies by notification type)

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:** Exit code and stderr are ignored

---

### MessageDisplay

**When it fires:** While assistant message text is displayed

**Can block:** No. The original text is displayed regardless.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`

**Event-specific input fields:** `message_text` (the assistant message being displayed)

**Timeout default:** 10 seconds (lowered from 600) for `command`, `http`, `mcp_tool`; 30 seconds for `prompt`; 60 seconds for `agent`

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:** Exit 0: success

---

### SubagentStart

**When it fires:** When a subagent is spawned

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** Yes. Filters on agent type: `general-purpose`, `Explore`, `Plan`, custom agent names, or plugin-scoped names like `^my-plugin:reviewer$`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `agent_type`, `agent_id`

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user only; subagent proceeds
- Other non-zero: non-blocking error; stderr shown

---

### SubagentStop

**When it fires:** When a subagent finishes

**Can block:** Yes. Prevents the subagent from stopping on exit 2.

**Matcher support:** Yes. Filters on agent type (same values as `SubagentStart`)

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`

**Event-specific input fields:** `agent_type`, `agent_id`, `last_assistant_message` (the final assistant text from the subagent), `stop_reason` (why the subagent stopped)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: prevents subagent from stopping
- Other non-zero: non-blocking error

---

### TaskCreated

**When it fires:** When a task is being created via `TaskCreate`

**Can block:** Yes. Rolls back the task creation on exit 2.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `task_name`, `task_description`

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: rolls back task creation
- Other non-zero: non-blocking error

---

### TaskCompleted

**When it fires:** When a task is being marked as completed

**Can block:** Yes. Prevents the task from being marked as completed on exit 2.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `task_id`, `task_name`

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: prevents task completion
- Other non-zero: non-blocking error

---

### Stop

**When it fires:** When Claude finishes responding

**Can block:** Yes. Prevents Claude from stopping on exit 2; continues the conversation.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`

**Event-specific input fields:** `last_assistant_message` (the final Claude response text), `stop_reason` (why Claude stopped)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: prevents Claude from stopping; continues conversation
- Other non-zero: non-blocking error

---

### StopFailure

**When it fires:** When the turn ends due to an API error

**Can block:** No. Output and exit code are ignored, except `terminalSequence`.

**Matcher support:** Yes. Filters on error type: `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `unknown`

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `error_type`, `error_message`

**Timeout default:** 600 seconds

**JSON decision fields:** `terminalSequence` (side-effect field only)

**Exit code contract:** Output and exit code are ignored (except `terminalSequence`)

---

### TeammateIdle

**When it fires:** When an agent team teammate is about to go idle

**Can block:** Yes. Prevents the teammate from going idle on exit 2.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `teammate_type`, `teammate_id`

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: prevents teammate from going idle
- Other non-zero: non-blocking error

---

### InstructionsLoaded

**When it fires:** When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session.

**Can block:** No. Exit code is ignored.

**Matcher support:** Yes. Filters on load reason: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `file_path`, `file_content`, `load_reason`

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:** Exit code is ignored

---

### ConfigChange

**When it fires:** When a configuration file changes during a session

**Can block:** Yes. Blocks the configuration change on exit 2 (except `policy_settings`).

**Matcher support:** Yes. Filters on configuration source: `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `config_source`, `changed_keys` (which settings changed)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: blocks configuration change (except `policy_settings`)
- Other non-zero: non-blocking error

---

### CwdChanged

**When it fires:** When the working directory changes, for example when Claude executes a `cd` command. Useful for reactive environment management with tools like direnv.

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** No. Always fires on every directory change.

**Common input fields:** `session_id`, `transcript_path`, `cwd` (the new working directory), `hook_event_name`

**Event-specific input fields:** `previous_cwd`, `new_cwd`

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user only
- Other non-zero: non-blocking error; stderr shown

---

### DirectoryAdded

**When it fires:** When a working directory is added mid-session via `/add-dir` or the SDK `register_repo_root` control request

**Can block:** No. Stderr goes to the debug log; the directory is already added.

**Matcher support:** Yes. Filters on how the directory was added: `slash_command`, `register_repo_root`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `directory_path`, `how_added`

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:** Stderr goes to debug log only; exit code is not honored

---

### FileChanged

**When it fires:** When a watched file changes on disk. The `matcher` field specifies which filenames to watch.

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** Yes. Filters on literal filenames to watch using exact-match characters only (letters, digits, `_`, `|`). Example: `.envrc|.env`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `file_path`, `change_type` (`created`, `modified`, `deleted`)

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user only
- Other non-zero: non-blocking error; stderr shown

**Note on matcher:** `FileChanged` does not follow the standard matcher rules when building its watch list. Use exact-match syntax only.

---

### WorktreeCreate

**When it fires:** When a worktree is being created via `--worktree`, `isolation: "worktree"`, or for a background session. Replaces default git behavior.

**Can block:** Yes. Any non-zero exit code causes worktree creation to fail (not just exit 2).

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `worktree_path`, `base_branch` (the git branch to create the worktree from)

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Any non-zero exit code: worktree creation fails (not just exit 2), regardless of JSON output

---

### WorktreeRemove

**When it fires:** When a worktree is being removed at session exit, when a subagent finishes, or when you delete a background session

**Can block:** No. Failures are logged in debug mode only.

**Matcher support:** No. Always fires.

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `worktree_path`

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:** Failures are logged in debug mode only; exit code is not honored for blocking

---

### PreCompact

**When it fires:** Before context compaction

**Can block:** Yes. Blocks compaction on exit 2.

**Matcher support:** Yes. Filters on what triggered compaction: `manual`, `auto`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `compaction_reason`

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: blocks compaction
- Other non-zero: non-blocking error

---

### PostCompact

**When it fires:** After context compaction completes

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** Yes. Filters on what triggered compaction: `manual`, `auto`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `compaction_reason`, `tokens_before`, `tokens_after`

**Timeout default:** 600 seconds

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user only
- Other non-zero: non-blocking error; stderr shown

---

### Elicitation

**When it fires:** When an MCP server requests user input during a tool call

**Can block:** Yes. Denies the elicitation on exit 2.

**Matcher support:** Yes. Filters on MCP server name (your configured MCP server names)

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `server_name`, `elicitation_type` (type of input requested), `elicitation_data` (details about what the server is requesting)

**Timeout default:** 600 seconds

**JSON decision fields:** Note: `hookSpecificOutput` is ignored on exit 2 for this event.

**Exit code contract:**
- Exit 0: success
- Exit 2: denies the elicitation; `hookSpecificOutput` is ignored
- Other non-zero: non-blocking error

---

### ElicitationResult

**When it fires:** After a user responds to an MCP elicitation, before the response is sent back to the server

**Can block:** Yes. Blocks the response on exit 2 (action becomes decline).

**Matcher support:** Yes. Filters on MCP server name (your configured MCP server names)

**Common input fields:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `server_name`, `elicitation_result` (the user response), `elicitation_type`

**Timeout default:** 600 seconds

**JSON decision fields:** `additionalContext`, `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: blocks the response (action becomes decline)
- Other non-zero: non-blocking error

---

### SessionEnd

**When it fires:** When a session terminates

**Can block:** No. Shows stderr to user only on exit 2.

**Matcher support:** Yes. Filters on why the session ended: `clear`, `resume`, `logout`, `prompt_input_exit`, `other`

**Common input fields:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`

**Event-specific input fields:** `end_reason`

**Timeout default:** Hooks share a 1.5-second budget; if settings set a longer per-hook `timeout`, Claude Code raises the budget to match, up to 60 seconds.

**JSON decision fields:** `systemMessage`, `terminalSequence`

**Exit code contract:**
- Exit 0: success
- Exit 2: stderr shown to user only
- Other non-zero: non-blocking error; stderr shown

---

## General exit code contract

### Exit Code 0

**Meaning:** Success. This is the intended exit code when you print JSON for structured control.

**Behavior:**
- For most events, stdout is written to the debug log but not shown in the transcript
- Exceptions: `UserPromptSubmit`, `UserPromptExpansion`, and `SessionStart` add plain-text stdout as context Claude can see and act on
- Claude Code reads stdout as JSON output if it starts with `{` (ignoring leading whitespace); otherwise as plain text
- For events using the standard decision model, a parsed object that fails schema validation is a non-blocking error
- Stderr goes to debug log only

### Exit Code 2

**Meaning:** Blocking error.

**Behavior:**
- On events that can block, exit 2 blocks whether or not you print JSON
- A JSON `permissionDecision` of `"allow"` cannot override exit 2
- Claude Code reads any valid JSON output on stdout
- The blocking message is the reason from the JSON blocking decision (if one makes a decision) or the stderr text otherwise
- Effect varies by event: `PreToolUse` blocks the tool call, `UserPromptSubmit` rejects the prompt, etc.
- A hook that exits 2 while printing JSON that fails schema validation still blocks: Claude Code uses stderr as the blocking reason

### Other exit codes

**Behavior:**
- Does not block on its own for most hook events
- For events using the standard decision model:
  - With a parsed object that passes schema validation: the JSON decision is honored; the hook is not reported as an error
  - With a parsed object that fails schema validation: non-blocking error (same as exit 0)
  - With plain-text stdout or empty stdout: non-blocking error; transcript shows `<hook name> hook error` with first line of stderr
- Exception: `WorktreeCreate` fails creation on any nonzero exit code

---

## JSON output schema

All hook types (command, HTTP, prompt, agent, MCP tool) that return structured control use this schema. Parse error or non-2xx HTTP status on non-`WorktreeCreate` events renders a non-blocking error.

### Universal fields (apply to all events):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "systemMessage": "Your message here",
    "additionalContext": "Context for Claude",
    "terminalSequence": "\u001b]9;4;3;4\u001b\\"
  }
}
```

| Field | Type | Events | Description |
|-------|------|--------|-------------|
| `systemMessage` | string | Most events (see decision control per event) | Message displayed to the user; some events discard it |
| `additionalContext` | string | Events with standard decision model | Context added to the Claude context window |
| `terminalSequence` | string | All events | Escape sequence for terminal notifications (desktop notification, set window title, ring bell, etc.) |

### Decision fields (event-specific):

| Field | Type | Events | Description |
|-------|------|--------|-------------|
| `permissionDecision` | string enum | `PreToolUse`, `UserPromptSubmit`, `UserPromptExpansion` | Values: `"allow"`, `"deny"`, `"escalate"` |
| `permissionDecisionReason` | string | Decision-bearing events | Reason for the decision |
| `decision` | object | `PermissionRequest` | `{ "allow": boolean, "reason": string }` |
| `retry` | boolean | `PermissionDenied` | If `true`, model may retry the denied tool call; ignored for no-verdict denials |
| `updatedInput` | object | `PreToolUse`, `UserPromptExpansion` | Modified tool input or expanded prompt |

Example decision outputs:

```json
{ "hookSpecificOutput": { "permissionDecision": "deny", "permissionDecisionReason": "Policy violation" } }
```

For `PermissionRequest`:

```json
{ "hookSpecificOutput": { "decision": { "allow": false, "reason": "Requires manual approval" } } }
```

For `PermissionDenied`:

```json
{ "hookSpecificOutput": { "retry": true } }
```

---

## Configuration format

### Hook locations and scope:

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects | No, local to machine |
| `.claude/settings.json` | Single project | Yes, can be committed |
| `.claude/settings.local.json` | Single project | No, gitignored |
| Managed policy settings | Organization-wide | Yes, admin-controlled |
| Plugin `hooks/hooks.json` | When plugin enabled | Yes, bundled with plugin |
| Skill frontmatter | Rest of session after invocation | Yes, in skill file |
| Subagent frontmatter | While subagent runs | Yes, in subagent file |

### Top-level structure:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/script.sh",
            "args": [],
            "timeout": 30,
            "statusMessage": "Validating...",
            "if": "Bash(rm *)"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/session-start",
            "timeout": 30,
            "headers": { "Authorization": "Bearer $MY_TOKEN" },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  },
  "disableAllHooks": false
}
```

### Common hook handler fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | One of: `"command"`, `"http"`, `"mcp_tool"`, `"prompt"`, `"agent"` |
| `if` | string | no | Permission rule syntax (tool events only): `"Bash(git *)"`, `"Edit(*.ts)"` |
| `timeout` | number | no | Seconds before canceling. Defaults: 600 (`command`/`http`/`mcp_tool`), 30 (`prompt`), 60 (`agent`). Lowered to 30 for `UserPromptSubmit` and 10 for `MessageDisplay` |
| `statusMessage` | string | no | Custom spinner message while hook runs |
| `once` | boolean | no | If `true`, runs once per session then removed (skill frontmatter only) |

### Command hook fields (in addition to common):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | yes | Shell command or executable. With `args`, resolved as executable; without `args`, passed to shell |
| `args` | array | no | Argument list. When present, enables exec form (no shell); absent enables shell form |
| `async` | boolean | no | If `true`, runs in background without blocking |
| `asyncRewake` | boolean | no | If `true`, runs in background and wakes Claude on exit code 2; implies `async` |
| `shell` | string | no | `"bash"` or `"powershell"`. Ignored when `args` set. Defaults to `"bash"`, or `"powershell"` on Windows |

**Exec form vs. shell form:**
- **Exec form** (when `args` present): no shell; each `args` element is one argument exactly as written; special characters pass through verbatim
- **Shell form** (when `args` absent): shell tokenizes, expands variables, interprets pipes, `&&`, redirects, globs

### HTTP hook fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | yes | URL for POST request |
| `headers` | object | no | Additional HTTP headers; values support `$VAR_NAME` or `${VAR_NAME}` substitution for listed env vars |
| `allowedEnvVars` | array | no | Environment variables allowed in header values; unlisted refs replaced with empty strings |

**HTTP response handling:** 2xx with empty body: success. 2xx with JSON: parsed using same schema as command hooks. 2xx with other body (plain text): non-blocking error. Non-2xx: non-blocking error. Connection failure: non-blocking error. Timeout: hook canceled, no decision.

### MCP tool hook fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `server` | string | yes | Configured MCP server name; for plugin-bundled servers use `plugin:<plugin-name>:<server-name>` |
| `tool` | string | yes | Tool name on that server |
| `input` | object | no | Tool arguments; string values support `${path}` substitution from hook JSON input (e.g., `${tool_input.file_path}`) |

**Note:** Server must already be connected; hook never triggers OAuth or connection flow.

### Prompt and agent hook fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | yes | Prompt text; use `$ARGUMENTS` as placeholder for hook input JSON; escape literals with `\` (e.g., `\$1.00`) |
| `model` | string | no | Model to use; defaults to fast model |

---

## Matcher patterns

### Evaluation rules:

| Value | Evaluated as | Example |
|-------|--------------|---------|
| `"*"`, `""`, omitted | Match all | fires on every occurrence |
| Only letters, digits, `_`, `-`, spaces, `,`, `\|` | Exact string or `\|`-separated list | `Bash`, `Edit\|Write`, `code-reviewer` |
| Contains other characters | JavaScript regex (unanchored) | `^Notebook`, `mcp__memory__.*` |

### Event-specific matcher fields:

| Event | Matcher filters | Example values |
|-------|-----------------|-----------------|
| Tool events (`PreToolUse`, `PostToolUse`, etc.) | tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | session start method | `startup`, `resume`, `clear`, `compact`, `fork` |
| `Setup` | CLI flag | `init`, `maintenance` |
| `SessionEnd` | exit reason | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |
| `Notification` | notification type | `permission_prompt`, `idle_prompt`, `auth_success`, etc. |
| `SubagentStart`/`SubagentStop` | agent type | `general-purpose`, `Explore`, `Plan`, custom names, `^my-plugin:reviewer$` |
| `PreCompact`/`PostCompact` | compaction trigger | `manual`, `auto` |
| `ConfigChange` | config source | `user_settings`, `project_settings`, `policy_settings`, etc. |
| `CwdChanged` | no matcher | always fires |
| `DirectoryAdded` | how directory added | `slash_command`, `register_repo_root` |
| `FileChanged` | literal filenames (exact-match only) | `.envrc\|.env` |
| `StopFailure` | error type | `rate_limit`, `overloaded`, `authentication_failed`, etc. |
| `InstructionsLoaded` | load reason | `session_start`, `nested_traversal`, `include`, etc. |
| `UserPromptExpansion` | command name | your skill/command names |
| `Elicitation`/`ElicitationResult` | MCP server name | your configured server names |
| `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `MessageDisplay` | no matcher | always fires |

### MCP tool naming:

MCP tools appear as `mcp__<server>__<tool>`, e.g. `mcp__memory__create_entities`, `mcp__filesystem__read_file`, `mcp__github__search_repositories`. Match all tools from a server with `mcp__memory__.*` (the `.*` is required). Plugin-bundled MCP servers use scoped names: `mcp__plugin_<plugin-name>_<server-name>__<tool>`.

---

## Path placeholders

Use these in hook commands (especially exec form) and HTTP hook URLs:

- `${CLAUDE_PROJECT_DIR}`: project root where session started
- `${CLAUDE_PLUGIN_ROOT}`: plugin installation directory
- `${CLAUDE_PLUGIN_DATA}`: plugin persistent data directory

These are also set as environment variables on spawned processes.

**Worktree note:** `${CLAUDE_PROJECT_DIR}` stays at the main project root when Claude enters a worktree. The `cwd` field in hook input JSON reflects the worktree directory.

---

## Disable or remove hooks

- Remove a hook: delete its entry from the settings JSON.
- Temporarily disable all hooks: `"disableAllHooks": true`.
- Settings precedence applies: project `.claude/settings.json` with `false` overrides user settings with `true`.
- Pass `--settings` with a `disableAllHooks: true` JSON object to override for one run.
- `disableAllHooks` in user/project/local settings cannot disable managed hooks; only managed-tier `disableAllHooks` can.
- Direct edits to settings files are normally picked up automatically.

---

## Windows-specific caveats

### Command hooks with `args`:

Exec form requires `command` to resolve to a real executable (`.exe`). `.cmd` and `.bat` shims from npm, eslint, etc., cannot be spawned in exec form. Workaround: invoke with `node` directly:

```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/node_modules/eslint/bin/eslint.js", "--fix"]
}
```

### PowerShell hooks:

```json
{
  "type": "command",
  "command": "powershell.exe",
  "args": [
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "${CLAUDE_PROJECT_DIR}/.claude/hooks/script.ps1"
  ]
}
```

The `-NoProfile` flag skips profile loading for speed; `-ExecutionPolicy Bypass` allows local script execution.

### Shell selection:

Set `"shell": "powershell"` to run shell form via PowerShell (Windows only). Does not require `CLAUDE_CODE_USE_POWERSHELL_TOOL` env var.

### Git Bash path caveat (verbatim from the docs):

"Git Bash treats unquoted backslashes as escape characters, so a Windows-style path such as `C:\Users\username\script.mjs` reaches the script runner with its separators removed and the command fails without a visible error. Write file paths in the `command` string with forward slashes, as shown in the examples below. The `~` shorthand also works and expands to your Windows home directory."

---

## Workspace trust

- **Project settings hooks**: registered when you start Claude Code in a `-p` mode in that folder, before trust dialog
- **Skill frontmatter hooks**: follow the same rule as settings; can run in `-p` before trust
- **Subagent frontmatter hooks**: run only after you accept the workspace trust dialog (not in `-p` mode). Before v2.1.218, these could run untrusted.

---

## Hooks in skills and agents

Hooks defined in YAML frontmatter are registered when the skill/agent is invoked:

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

- **Subagent hooks**: run only while that subagent is running; removed when it finishes. `Stop` hook is converted to `SubagentStop`.
- **Skill hooks**: registered when invoked and kept for the rest of the session. Set `once: true` to run once then remove.

---

## `/hooks` menu

Type `/hooks` in Claude Code to browse configured hooks. Shows all five hook types, matcher groups, and full handler details. Read-only; edit settings JSON to modify hooks. Sources displayed: User Settings, Project Settings, Local Settings, Plugin Hooks, Session Hooks, Built-in Hooks.

---

## HTTP hook allowlists

Global settings can restrict HTTP hook URLs:

```json
{
  "allowedHttpHookUrls": ["http://localhost:*", "https://internal.company.com/*"],
  "httpHookAllowedEnvVars": ["MY_TOKEN", "API_KEY"]
}
```

Applies to hooks from all sources (settings, plugins, managed policy). When defined at any level, HTTP hook URLs must match the merged allowlist. Variables in hook headers must be listed in `httpHookAllowedEnvVars`.

---

## Async hooks

Set `"async": true` on command hooks to run in the background without blocking. Set `"asyncRewake": true` to run in background and wake Claude on exit code 2, with the hook stderr (or stdout if stderr empty) shown as a system reminder.

---

## Emit terminal notifications

Use the `terminalSequence` field to trigger desktop notifications, set window titles, or ring the bell:

```json
{ "hookSpecificOutput": { "terminalSequence": "\u001b]9;4;3;4\u001b\\" } }
```

Supported on all events and all hook types.

---

## Debug hooks

Enable debug logging (set `DEBUG_CLAUDE_CODE=1` in the environment before launching Claude Code) to see hook output, stderr, and errors. Debug logs show: hook command invocations and exit codes, full stderr from hooks, JSON parsing errors, timeout events.

---

## Environment variables

Hooks run with the Claude Code environment and inherit:

- `${CLAUDE_PROJECT_DIR}`
- `${CLAUDE_PLUGIN_ROOT}`
- `${CLAUDE_PLUGIN_DATA}`
- `$CLAUDE_EFFORT` (effort level: `low`, `medium`, `high`, `xhigh`, `max`)
- `$CLAUDE_CODE_REMOTE` (`"true"` in web; unset locally)
- `$CLAUDE_CODE_BRIDGE_SESSION_ID` (Remote Control session ID; v2.1.199+)

**Removed from all subprocesses:** `OTEL_*` exporter variables (telemetry)

---

## Decision control

### Standard decision model (most events):

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|escalate",
    "permissionDecisionReason": "string"
  }
}
```

**Events supporting this model:** `PreToolUse`, `UserPromptSubmit`, `UserPromptExpansion`

### PermissionRequest model: JSON `decision` object (`allow` boolean + `reason`).

### PermissionDenied model: JSON `retry` boolean; ignored for no-verdict denials.

### Other events: may use `additionalContext`, `systemMessage`, `terminalSequence` but no `permissionDecision`.

---

## Version requirements ("requires vX.Y.Z" notes on this page)

- Comma separators in matchers: v2.1.191+
- Hyphens in exact-match matchers: v2.1.195+
- `prompt_id` field in common input: v2.1.196+
- `$CLAUDE_CODE_BRIDGE_SESSION_ID` env var: v2.1.199+
- Subagent frontmatter hooks run only after workspace trust is accepted; before v2.1.218, these could run untrusted.