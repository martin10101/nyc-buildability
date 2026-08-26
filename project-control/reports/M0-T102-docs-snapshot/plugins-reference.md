# Snapshot: Claude Code plugins reference

- Source URL: https://code.claude.com/docs/en/plugins-reference
- Fetch date: 2026-08-26
- Purpose: D-024 amendment-3 capability re-baseline, requirement D-024-R147.
- Capture method: WebFetch (page converted to markdown; extraction-model capture, verbatim where load-bearing). Snapshot of what the docs say; no editorializing.

---

# Claude Code Plugins: Complete Reference

## Plugin Components Overview

A **plugin** is a self-contained directory of components that extends Claude Code with custom functionality. Plugin components include:

- **Skills** – `/name` shortcuts invoked by users or Claude
- **Agents** – Specialized subagents Claude invokes automatically
- **Hooks** – Event handlers responding to Claude Code lifecycle events
- **MCP servers** – Model Context Protocol servers for external tools/services
- **LSP servers** – Language Server Protocol for code intelligence
- **Monitors** – Background processes delivering stdout to Claude as notifications
- **Themes** – Color theme definitions (experimental)
- **Commands** – Flat markdown skill files (legacy; use `skills/` for new plugins)

---

## Plugin Directory Structure

### Standard Layout

```text
enterprise-plugin/
├── .claude-plugin/           # Metadata directory (optional)
│   └── plugin.json             # Plugin manifest
├── skills/                   # Skills with <name>/SKILL.md structure
│   ├── code-reviewer/
│   │   ├── SKILL.md
│   │   ├── reference.md (optional)
│   │   └── scripts/ (optional)
│   └── pdf-processor/
│       └── SKILL.md
├── commands/                 # Skills as flat .md files (legacy)
│   ├── status.md
│   └── logs.md
├── agents/                   # Subagent definitions
│   ├── security-reviewer.md
│   └── performance-tester.md
├── workflows/                # Workflow script files
│   └── release-audit.js
├── output-styles/            # Output style definitions
│   └── terse.md
├── themes/                   # Color theme definitions (experimental)
│   └── dracula.json
├── monitors/                 # Background monitor configurations (experimental)
│   └── monitors.json
├── hooks/                    # Hook configurations
│   ├── hooks.json
│   └── security-hooks.json
├── bin/                      # Executables added to PATH
│   └── my-tool
├── .mcp.json                 # MCP server definitions
├── .lsp.json                 # LSP server configurations
├── .mcp.json or inline       # MCP servers config
├── scripts/                  # Hook and utility scripts
│   ├── security-scan.sh
│   ├── format-code.py
│   └── deploy.js
├── package.json              # Node.js dependencies (auto-installed)
├── LICENSE
└── CHANGELOG.md
```

**Critical note:** `.claude-plugin/` contains `plugin.json`. All other component directories (`commands/`, `agents/`, `skills/`, etc.) must be at the plugin root, **not** inside `.claude-plugin/`.

### File Locations Reference

| Component      | Default Location         | Purpose |
|:---------------|:-------------------------|:--------|
| **Manifest**   | `.claude-plugin/plugin.json` | Plugin metadata (optional) |
| **Skills**     | `skills/`                | Skills with `<name>/SKILL.md` structure |
| **Commands**   | `commands/`              | Flat markdown skills (legacy) |
| **Agents**     | `agents/`                | Subagent markdown files |
| **Workflows**  | `workflows/`             | Workflow script files |
| **Output styles** | `output-styles/`       | Output style definitions |
| **Themes**     | `themes/`                | Color theme definitions (experimental) |
| **Hooks**      | `hooks/hooks.json`       | Hook configuration |
| **MCP servers** | `.mcp.json`             | MCP server definitions |
| **LSP servers** | `.lsp.json`             | Language server configurations |
| **Monitors**   | `monitors/monitors.json` | Background monitor configs (experimental) |
| **Executables** | `bin/`                  | Commands added to Bash tool PATH |
| **Settings**   | `settings.json`          | Default config (only `agent` and `subagentStatusLine` keys supported) |

---

## Plugin Components Reference

### Skills

**Location:** `skills/` or `commands/` directory, or a single `SKILL.md` at plugin root

**File format:** Skills are directories with `SKILL.md`; commands are simple markdown files

**Structure:**
```text
skills/
├── pdf-processor/
│   ├── SKILL.md
│   ├── reference.md (optional)
│   └── scripts/ (optional)
└── code-reviewer/
    └── SKILL.md
```

**Key behaviors:**
- Automatically discovered when plugin is installed
- If no `skills/` directory and no `skills` manifest field, a `SKILL.md` at plugin root loads as a single skill
- Set the frontmatter `name` field to control invocation name
- Without `name`, Claude Code falls back to install directory name (problematic for marketplace installs)
- For plugins with multiple skills, use the `skills/` directory layout

**Boolean frontmatter fields** accept `yes`, `no`, `on`, `off`, `1`, `0` (case-insensitive), plus `true` and `false`. This requires Claude Code v2.1.218+; earlier versions recognized only `true`/`false`.

### Agents

**Location:** `agents/` directory in plugin root

**File format:** Markdown files with frontmatter

**Structure:**
```markdown
---
name: agent-name
description: What this agent specializes in and when Claude should invoke it
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
---

Detailed system prompt for the agent describing its role, expertise, and behavior.
```

**Supported frontmatter fields:**
- `name`, `description`, `model`, `effort`, `maxTurns`
- `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`
- Only valid `isolation` value: `"worktree"`
- **Not supported** (for security): `hooks`, `mcpServers`, `permissionMode`

**Discovery:** Agents appear in [@-mention typeahead](/docs/en/sub-agents#invoke-subagents-explicitly) as scoped names like `my-plugin:code-reviewer` once plugin is enabled.

### Hooks

**Location:** `hooks/hooks.json` or inline in `plugin.json`

**Format:** JSON configuration with event matchers and actions

**Example:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}
```

**Hook types:**
- `command` – Execute shell commands or scripts
- `http` – Send event JSON as POST to URL
- `mcp_tool` – Call tool on configured MCP server
- `prompt` – Evaluate prompt with LLM (uses `$ARGUMENTS` placeholder)
- `agent` – Run agentic verifier with tools for complex verification

**Supported lifecycle events:**

| Event | When it fires |
|:------|:--------------|
| `SessionStart` | When session begins or resumes |
| `Setup` | When `--init-only`, `--init`, or `--maintenance` in `-p` mode |
| `UserPromptSubmit` | Before Claude processes user prompt |
| `UserPromptExpansion` | When command expands into prompt; can block |
| `PreToolUse` | Before tool execution; can block |
| `PermissionRequest` | When tool needs permission decision |
| `PermissionDenied` | When auto mode denies tool. Use JSON `hookSpecificOutput.retry: true` for retry |
| `PostToolUse` | After successful tool call |
| `PostToolUseFailure` | After tool call fails |
| `PostToolBatch` | After full batch of parallel tool calls |
| `Notification` | When Claude Code sends notification |
| `MessageDisplay` | While assistant message displays |
| `SubagentStart` | When subagent spawned |
| `SubagentStop` | When subagent finishes |
| `TaskCreated` | When task created via `TaskCreate` |
| `TaskCompleted` | When task marked completed |
| `Stop` | When Claude finishes responding |
| `StopFailure` | When turn ends due to API error |
| `TeammateIdle` | When agent team teammate about to idle |
| `InstructionsLoaded` | When CLAUDE.md or `.claude/rules/*.md` loaded |
| `ConfigChange` | When config file changes during session |
| `CwdChanged` | When working directory changes (useful for direnv) |
| `DirectoryAdded` | When working directory added mid-session |
| `FileChanged` | When watched file changes on disk |
| `WorktreeCreate` | When worktree created; replaces default git behavior |
| `WorktreeRemove` | When worktree removed at session exit |
| `PreCompact` | Before context compaction |
| `PostCompact` | After context compaction completes |
| `Elicitation` | When MCP server requests user input during tool call |
| `ElicitationResult` | After user responds to MCP elicitation |
| `SessionEnd` | When session terminates |

**Scoped MCP tool matching:** Hooks targeting plugin's bundled MCP server must use scoped names:
- Tool matchers and `if` fields take: `mcp__plugin_<plugin-name>_<server-name>__<tool>`
- `mcp_tool` hook's `server` field takes: `plugin:<plugin-name>:<server-name>`
- Bare server key never fires

### MCP Servers

**Location:** `.mcp.json` in plugin root or inline in `plugin.json`

**Format:** Standard MCP server configuration

**Example:**
```json
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data"
      }
    },
    "plugin-api-client": {
      "command": "npx",
      "args": ["@company/mcp-server", "--plugin-mode"]
    }
  }
}
```

**Integration behavior:**
- Plugin MCP servers start automatically when plugin is enabled
- Appear as standard MCP tools in Claude's toolkit
- Can be configured independently of user MCP servers
- If `/reload-plugins` run mid-session, Claude Code keeps live connections of servers with unchanged configuration

### LSP Servers

**Location:** `.lsp.json` in plugin root or inline in `plugin.json`

**Format:** JSON mapping language server names to configurations

**Example `.lsp.json`:**
```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

**Inline in `plugin.json`:**
```json
{
  "name": "my-plugin",
  "lspServers": {
    "go": {
      "command": "gopls",
      "args": ["serve"],
      "extensionToLanguage": {
        ".go": "go"
      }
    }
  }
}
```

**Required fields:**

| Field | Description |
|:------|:------------|
| `command` | LSP binary to execute (must be in PATH) |
| `extensionToLanguage` | Maps file extensions to language identifiers |

**Optional fields:**

| Field | Description |
|:------|:------------|
| `args` | Command-line arguments for LSP server |
| `transport` | Communication transport: `stdio` (default) or `socket`. Claude Code accepts `socket` but runs over stdio |
| `env` | Environment variables when starting server |
| `initializationOptions` | Options passed during initialization |
| `settings` | Settings via `workspace/didChangeConfiguration` |
| `workspaceFolder` | Workspace folder path |
| `startupTimeout` | Max time to wait for startup (milliseconds) |
| `shutdownTimeout` | Max time for graceful shutdown (milliseconds). When elapsed, Claude Code terminates process. When unset, no timeout |
| `restartOnCrash` | Whether to restart after crash. Default `true`. Requires v2.1.205+ |
| `maxRestarts` | Maximum restart attempts before giving up |
| `diagnostics` | Whether to push diagnostics into context after edits (default `true`). Set `false` to suppress automatic injection |

**Critical note on `shutdownTimeout` and `restartOnCrash`:** These require Claude Code v2.1.205+. Before v2.1.205, setting either caused Claude Code to skip that LSP server entirely at startup (visible only in `claude --debug` output).

**Multiple servers for same extension:** When multiple enabled LSP servers declare the same file extension (from one or different plugins), the first registered server handles that extension; others never start. The `/plugin` interface shows a warning.

**Servers that fail to initialize:** Claude Code skips invalid servers (missing `command`, `extensionToLanguage`, etc.); other configured servers still start. Run `claude --debug` to see why. Skipped servers don't claim their extensions, so another valid server can handle them.

**Stdout handling:** Claude Code reads a server's stdout as protocol messages only. It accepts message headers up to 64 KiB and message body up to 32 MiB. Claude Code disconnects servers exceeding either limit or writing non-protocol output to stdout, counting the disconnect as a crash for `restartOnCrash` and `maxRestarts`. Run with `--debug` to see error details.

**⚠️ Critical:** You must install the language server binary separately. LSP plugins configure connection only, they don't include the server itself. If you see `Executable not found in $PATH` in `/plugin` Errors tab, install the required binary.

**Available LSP plugins:**

| Plugin | Language Server | Install Command |
|:-------|:----------------|:----------------|
| `pyright-lsp` | Pyright (Python) | `pip install pyright` or `npm install -g pyright` |
| `typescript-lsp` | TypeScript Language Server | `npm install -g typescript-language-server typescript` |
| `rust-analyzer-lsp` | rust-analyzer | [See rust-analyzer installation](https://rust-analyzer.github.io/manual.html#installation) |

Install the language server first, then install the plugin from marketplace.

### Monitors

**Location:** `monitors/monitors.json` in plugin root or inline in `plugin.json`

**Status:** Experimental component

**Format:** JSON array of monitor entries

**Example `monitors/monitors.json`:**
```json
[
  {
    "name": "deploy-status",
    "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/poll-deploy.sh",
    "description": "Deployment status changes"
  },
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log",
    "when": "on-skill-invoke:debug"
  }
]
```

**Inline in `plugin.json`:**
```json
{
  "experimental": {
    "monitors": "./config/monitors.json"
  }
}
```

Or set `experimental.monitors` to relative path string like `"./config/monitors.json"`.

**How monitors work:**
- Run as persistent background processes during session
- Deliver every stdout line to Claude as notification
- Claude reacts without being asked to start the watch
- Share mechanism with [Monitor tool](/docs/en/tools-reference#monitor-tool)
- Run only in interactive CLI sessions, unsandboxed at same trust level as [hooks](#hooks)
- Skipped on hosts where Monitor tool unavailable

**Required fields:**

| Field | Description |
|:------|:------------|
| `name` | Identifier unique within plugin. Prevents duplicate processes on reload or skill re-invoke |
| `command` | Shell command run as persistent background process in session working directory |
| `description` | Short summary of what is being watched. Shown in task panel and notification summaries |

**Optional fields:**

| Field | Description |
|:------|:------------|
| `when` | Controls when monitor starts. `"always"` (default) starts at session start and plugin reload. `"on-skill-invoke:<skill-name>"` starts first time named skill in this plugin is dispatched |

**Path substitutions in `command`:**
- `${CLAUDE_PLUGIN_ROOT}` – Plugin installation directory
- `${CLAUDE_PLUGIN_DATA}` – Persistent data directory
- `${CLAUDE_PROJECT_DIR}` – Project root
- `${ENV_VAR}` – Any environment variable

Use `cd "${CLAUDE_PLUGIN_ROOT}" && ` if script needs to run from plugin's directory.

**Limitations:**
- Can't reference `${user_config.*}` values; Claude Code rejects monitor with error instead of substituting
- Processes don't receive `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables
- Have monitor script read config values from a file it owns
- If you disable plugin mid-session, Claude Code doesn't stop already-running monitors; they stop when session ends

### Themes

**Status:** Experimental component

**Location:** `themes/` directory in plugin root

**Format:** JSON file with base preset and sparse color token overrides

**Example theme `themes/dracula.json`:**
```json
{
  "name": "Dracula",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "error": "#ff5555",
    "success": "#50fa7b"
  }
}
```

**Behavior:**
- Appear in `/theme` alongside built-in presets and user's local themes
- When user selects plugin theme, Claude Code saves `custom:<plugin-name>:<slug>` in config
- Plugin themes are read-only; pressing `Ctrl+E` copies into `~/.claude/themes/` for editing

---

## Plugin Manifest Schema (`plugin.json`)

The `.claude-plugin/plugin.json` file defines plugin metadata and configuration.

**Manifest is optional.** If omitted, Claude Code auto-discovers components in default locations and derives plugin name from directory name. Use manifest when you need metadata or custom component paths.

### Complete Schema

```json
{
  "name": "plugin-name",
  "displayName": "Plugin Name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "metadata": { "catalogId": "cat-123", "tier": "pro" },
  "skills": "./custom/skills/",
  "commands": ["./custom/commands/special.md"],
  "agents": ["./custom/agents/reviewer.md"],
  "workflows": "./custom/workflows/",
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json",
  "experimental": {
    "themes": "./themes/",
    "monitors": "./monitors.json"
  },
  "userConfig": { /* ... */ },
  "channels": [ /* ... */ ],
  "dependencies": [
    "helper-lib",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ],
  "defaultEnabled": true
}
```

### Required Fields

If you include a manifest, **`name` is the only required field.**

| Field | Type | Description | Example |
|:------|:-----|:------------|:--------|
| `name` | string | Unique identifier (kebab-case, no spaces). Used for namespacing components like `plugin-dev:agent-creator` | `"deployment-tools"` |

### Unrecognized Fields

Claude Code ignores top-level fields it doesn't recognize. You can keep metadata from another ecosystem (VS Code extension, npm `package.json`, MCPB/DXT bundle manifest) and the plugin still loads.

`claude plugin validate` reports unrecognized fields as warnings, not errors. If a field is one or two characters off from recognized field, the warning suggests the likely name.

A plugin with only unrecognized-field warnings still passes validation and loads at runtime.

**Type mismatches depend on field:**
- **Most fields:** Plugin fails to load (e.g., `keywords` as string instead of array is load error)
- **`experimental` and `metadata`:** Claude Code ignores non-object value; `validate` reports warning

Pass `--strict` to treat warnings as errors (useful in CI):
```bash
claude plugin validate ./my-plugin --strict
```

### Metadata Fields

| Field | Type | Description | Example |
|:------|:-----|:------------|:--------|
| `$schema` | string | JSON Schema URL for editor autocomplete. Claude Code ignores at load time | `"https://json.schemastore.org/claude-code-plugin-manifest.json"` |
| `displayName` | string | Human-readable name in `/plugin` picker. Falls back to `name` when omitted. May contain spaces and any casing. Not used for namespacing | `"Deployment Tools"` |
| `version` | string | Semantic version. Pins plugin to that version; users get updates only when you bump it (except `command` source). If also in marketplace entry, `plugin.json` wins. If omitted, version comes from next source in Version management | `"2.1.0"` |
| `description` | string | Brief plugin purpose | `"Deployment automation tools"` |
| `author` | object | Author information | `{"name": "Dev Team", "email": "dev@company.com"}` |
| `homepage` | string | Documentation URL | `"https://docs.example.com"` |
| `repository` | string | Source code URL | `"https://github.com/user/plugin"` |
| `license` | string | License identifier | `"MIT"`, `"Apache-2.0"` |
| `keywords` | array | Discovery tags | `["deployment", "ci-cd"]` |
| `metadata` | object | Free-form data (catalog fields, entitlement). Claude Code doesn't read it; values never affect behavior. Before v2.1.222, was unrecognized field | `{"catalogId": "cat-123"}` |
| `defaultEnabled` | boolean | Whether plugin starts enabled when user hasn't set preference. Defaults to `true`. See [Default enablement](#default-enablement). Requires v2.1.154+ | `false` |

### Default Enablement

Set `defaultEnabled: false` to ship plugin installing disabled. User enables with `claude plugin enable <plugin>` or `/plugin` interface. Use for plugins adding cost or requiring opt-in (e.g., external service connections). Requires Claude Code v2.1.154+; earlier versions ignore and enable on install.

`defaultEnabled` is fallback when nothing else decided state. Two things take precedence:

1. **User's setting:** Entry in `enabledPlugins` at any scope. Once written, persists across updates/reinstalls; changing `defaultEnabled` in later release doesn't flip existing user
2. **Dependency requirement:** When plugin required by another active one, Claude Code writes `true` at install/enable time, giving explicit setting so default no longer applies

Same field can appear in marketplace entry, taking precedence over `plugin.json`.

### Component Path Fields

| Field | Type | Description | Example |
|:------|:-----|:------------|:--------|
| `skills` | string\|array | Custom skill directories containing `<name>/SKILL.md`. Adds to default `skills/` scan | `"./custom/skills/"` |
| `commands` | string\|array | Custom flat `.md` skill files or directories (replaces default `commands/`) | `"./custom/cmd.md"` or `["./cmd1.md"]` |
| `agents` | string\|array | Custom agent files (replaces default `agents/`) | `"./custom/agents/reviewer.md"` |
| `workflows` | string\|array | Custom workflow script files or directories (replaces default `workflows/`) | `"./custom/workflows/"` |
| `hooks` | string\|array\|object | Hook config paths or inline config | `"./my-extra-hooks.json"` |
| `mcpServers` | string\|array\|object | MCP config paths or inline config | `"./my-extra-mcp-config.json"` |
| `outputStyles` | string\|array | Custom output style files/directories (replaces default `output-styles/`) | `"./styles/"` |
| `lspServers` | string\|array\|object | LSP configs (replaces default `.lsp.json`) | `"./.lsp.json"` |
| `experimental.themes` | string\|array | Color theme files/directories (replaces default `themes/`) | `"./themes/"` |
| `experimental.monitors` | string\|array | Background Monitor configurations (replaces default `monitors/monitors.json`) | `"./monitors.json"` |
| `userConfig` | object | User-configurable values prompted at enable time | See section below |
| `channels` | array | Channel declarations for message injection (Telegram, Slack, Discord style) | See section below |
| `dependencies` | array | Other plugins required, optionally with semver version constraints | `[{ "name": "secrets-vault", "version": "~2.1.0" }]` |

### Experimental Components

Components under `experimental` key (`themes`, `monitors`) have manifest schema that may change between releases while they stabilize. Top-level still works; `claude plugin validate` warns; future release will require `experimental.*`.

### Path Behavior Rules

Whether custom path replaces or extends default directory:

**Replaces the default:** `commands`, `agents`, `workflows`, `outputStyles`, `experimental.themes`, `experimental.monitors`
- Example: when manifest specifies `commands`, default `commands/` directory not scanned
- To keep default and add more, list explicitly: `"commands": ["./commands/", "./extras/"]`
- Exception: for [marketplace entry with `source` resolving to marketplace root](/docs/en/plugin-marketplaces#advanced-plugin-entries), declaring specific subdirectories replaces default `skills/` scan

**Adds to the default:** `skills`
- Default `skills/` directory always scanned; directories listed in `skills` loaded alongside

**Own merge rules:** `hooks`, `mcpServers`, `lspServers`
- See each section for how multiple sources combine

**Path validation rules:**
- All paths relative to plugin root, start with `./`, except `skills` field also accepts `"."`
  - Both `"."` and `"./"` denote plugin root
  - Before v2.1.221, `"."` failed validation; use `"./"` for earlier version support
- Components from custom paths use same naming/namespacing rules
- Multiple paths specified as arrays
- Skill path can point directly to directory containing `SKILL.md` (e.g., `"skills": ["."]` for plugin root)
  - Invocation name from frontmatter `name` field in `SKILL.md`, staying stable across installs
  - Without `name`, falls back to directory basename
- Single-skill plugin at root: `SKILL.md` loads automatically if no `skills/` subdirectory and no `skills` manifest field; don't need `"skills": ["./"]`

**Path examples:**
```json
{
  "commands": [
    "./specialized/deploy.md",
    "./utilities/batch-process.md"
  ],
  "agents": [
    "./custom-agents/reviewer.md",
    "./custom-agents/tester.md"
  ]
}
```

### Environment Variables

Claude Code provides three variables for referencing paths:

| Variable | Resolves to | Use it for |
|:---------|:------------|:-----------|
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to plugin's installation directory | Scripts, binaries, config files bundled with plugin |
| `${CLAUDE_PLUGIN_DATA}` | Persistent directory surviving plugin updates, created on first reference | Installed dependencies (`node_modules`, Python venvs), generated code, caches |
| `${CLAUDE_PROJECT_DIR}` | Project root | Project-local scripts and config files |

All three exported as environment variables to hook processes, MCP/LSP server subprocesses.

**Which fields substitute them inline depends on component:**

| Plugin Component | Fields where placeholders resolve |
|:-----------------|:----------------------------------|
| Skill and agent content | Anywhere the placeholder appears |
| Hook and monitor commands | Anywhere the placeholder appears |
| MCP `stdio` servers | `command`, `args`, `env` |
| MCP `http`, `sse`, `ws` servers | `url`, `headers`, `headersHelper` |
| LSP servers | `command`, `args`, `env`, `workspaceFolder` |

**In hook commands:** Use [exec form](/docs/en/hooks#exec-form-and-shell-form) with `args` so each path is one argument with no quoting.

**In shell-form hooks and monitor commands:** Wrap variables in double quotes: `"${CLAUDE_PROJECT_DIR}/scripts/server.sh"`

**Example shell-form hook running bundled script:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/process.sh"
          }
        ]
      }
    ]
  }
}
```

**Critical:** `${CLAUDE_PLUGIN_ROOT}` changes when plugin updates. Previous version's directory remains briefly; treat as ephemeral, don't write state there. See [plugin caching](#plugin-caching-and-file-resolution).

When plugin updates mid-session, hook commands, monitors, MCP/LSP servers keep using previous version's path. Run `/reload-plugins` to switch hooks, MCP, LSP servers to new path; monitors require restart. For plugin with `command` source, Claude Code [can reload the plugin itself](/docs/en/plugin-marketplaces#when-claude-code-re-runs-the-command).

MCP servers can call `roots/list` request to read session's working directories at runtime. See [what `roots/list` returns](/docs/en/mcp#option-3-add-a-local-stdio-server).

#### Persistent Data Directory

`${CLAUDE_PLUGIN_DATA}` resolves to `~/.claude/plugins/data/{id}/`, where `{id}` is plugin identifier with characters outside `a-z`, `A-Z`, `0-9`, `_`, `-` replaced by `-`.

Example: `formatter@my-marketplace` → `~/.claude/plugins/data/formatter-my-marketplace/`

**Common use:** Install language dependencies once, reuse across sessions/updates. Use for Python dependencies, Yarn/pnpm-locked packages, packages with lifecycle scripts.

**Dependency manifest pattern:** For marketplace-installed plugin, may not need at all; Claude Code installs eligible [Node.js package dependencies](#nodejs-package-dependencies) automatically.

Compare bundled manifest against copy in data directory; reinstall when they differ. Recommended pattern using `SessionStart` hook:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
          }
        ]
      }
    ]
  }
}
```

`diff` exits nonzero when stored copy missing or differs; covers both first run and dependency-changing updates. If `npm install` fails, trailing `rm` removes copied manifest so next session retries.

Scripts bundled in `${CLAUDE_PLUGIN_ROOT}` can run against persisted `node_modules`:

```json
{
  "mcpServers": {
    "routines": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"],
      "env": {
        "NODE_PATH": "${CLAUDE_PLUGIN_DATA}/node_modules"
      }
    }
  }
}
```

Data directory deleted automatically when you uninstall plugin from last scope where it's installed. `/plugin` interface shows directory size and prompts before deletion. CLI deletes by default; pass [`--keep-data`](#plugin-uninstall) to preserve.

### User Configuration

`userConfig` field declares values Claude Code prompts user for when plugin enabled. Use instead of requiring hand-edit of `settings.json`.

**Example:**
```json
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

**Key requirements:** Keys must be valid identifiers.

**Schema fields per option:**

| Field | Required | Description |
|:------|:---------|:------------|
| `type` | Yes | One of `string`, `number`, `boolean`, `directory`, `file` |
| `title` | Yes | Label in configuration dialog |
| `description` | Yes | Help text beneath field |
| `sensitive` | No | If `true`, masks input; stores in secure storage instead of `settings.json` |
| `required` | No | If `true`, validation fails when empty |
| `default` | No | Value when user provides nothing |
| `multiple` | No | For `string` type, allow array of strings |
| `min` / `max` | No | Bounds for `number` type |

**Availability for substitution:**
- In MCP and LSP server configs and hook commands: `${user_config.KEY}`
- In skill and agent content (non-sensitive only): `${user_config.KEY}`
- In all processes as environment variable: `CLAUDE_PLUGIN_OPTION_<KEY>` (uppercased)

**Shell-field rejection:** Fields running in shell reject `${user_config.*}` to prevent shell injection. Alternatives:

| Rejected Field | How to Pass Value |
|:---------------|:------------------|
| Shell-form hook commands | Use [exec form](/docs/en/hooks#exec-form-and-shell-form) with `args`, or read `CLAUDE_PLUGIN_OPTION_<KEY>` from environment |
| [Monitor](#monitors) commands | Read value from config file in script |
| MCP [`headersHelper`](/docs/en/mcp#use-dynamic-headers-for-custom-authentication) | Read value from config file in script |

Before v2.1.207, these fields substituted `${user_config.KEY}` values; update plugins relying on this.

**Storage:** Non-sensitive values stored under [`pluginConfigs`](/docs/en/settings-reference#pluginconfigs) key in user `settings.json` as `pluginConfigs[<plugin-id>].options`.

**Sensitive values:** Go to macOS Keychain or `~/.claude/.credentials.json` on platforms without supported keychain. Keychain storage shared with OAuth tokens; ~2 KB total limit, so keep sensitive values small.

**Settings sources:** Claude Code reads all `pluginConfigs` from three sources only:
- **User settings:** `~/.claude/settings.json` (file enable-time prompt writes to)
- **`--settings`:** CLI flag or SDK inline settings
- **Managed settings:** [Organization-controlled policy](/docs/en/permissions#managed-settings)

When multiple sources set same key: managed settings > `--settings` > user settings.

Only user settings removable: pass [`--setting-sources`](/docs/en/cli-reference#cli-flags) without `user`; Claude Code skips them. Managed settings and `--settings` stay as passed. SDK's [`settingSources`](/docs/en/agent-sdk/claude-code-features#what-settingsources-does-not-control) option sets same list.

**Project scope limitation:** Entries in project's `.claude/settings.json` or `.claude/settings.local.json` ignored (before v2.1.207 were read). Both files live in workspace, so cloned repository could supply values; those would flow into hook commands, MCP server configs, LSP commands, monitor commands. Restriction specific to `pluginConfigs`; [`enabledPlugins`](/docs/en/settings-reference#enabledplugins) still honors project/local settings.

### Channels

`channels` field lets plugin declare message channels injecting content into conversation. Each channel binds to MCP server plugin provides.

**Example:**
```json
{
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": {
          "type": "string",
          "title": "Bot token",
          "description": "Telegram bot token",
          "sensitive": true
        },
        "owner_id": {
          "type": "string",
          "title": "Owner ID",
          "description": "Your Telegram user ID"
        }
      }
    }
  ]
}
```

- `server` field (required): Must match key in plugin's `mcpServers`
- `userConfig` (optional): Per-channel `userConfig` using same schema as top-level, prompts for bot tokens/owner IDs when plugin enabled

---

## Plugin Installation Scopes

When you install plugin, you choose **scope** determining availability and sharing:

| Scope | Settings File | Use Case |
|:------|:--------------|:---------|
| `user` | `~/.claude/settings.json` | Personal plugins available across all projects (default) |
| `project` | `.claude/settings.json` | Team plugins shared via version control |
| `local` | `.claude/settings.local.json` | Project-specific plugins, gitignored |
| `managed` | [Managed settings](/docs/en/managed-settings) | Managed plugins (read-only, update only) |

Plugins use same scope system as other Claude Code configurations. For installation instructions and scope flags, see [Install plugins](/docs/en/discover-plugins#install-plugins). For complete scope explanation, see [Configuration scopes](/docs/en/settings#where-settings-live).

---

## Skills-Directory Plugins

Any folder under skills directory containing `.claude-plugin/plugin.json` manifest loads as plugin named `<name>@skills-dir` on next session, with no marketplace/install step. Scaffold with [`plugin init`](#plugin-init).

Unlike copied marketplace install, plugin discovered in place rather than copied into plugin cache.

### Skills Directory Tree Structure

Skills directory tree supports three distinct things:

| What You Have | What It Is |
|:--------------|:-----------|
| `<skills-dir>/foo/SKILL.md` with no manifest | Plain [skill](/docs/en/skills) named `foo` |
| `<skills-dir>/foo/.claude-plugin/plugin.json` | Plugin `foo@skills-dir`, can bundle skills, agents, hooks, more |
| `<plugin>/skills/bar/SKILL.md` | Skill `bar` packaged inside a plugin |

### Where Plugins Load From

| Skills Directory | Scope | Loads |
|:-----------------|:------|:------|
| `~/.claude/skills/` | personal | In every project (location is yours alone) |
| `<cwd>/.claude/skills/` | project | Only after accepting workspace [trust dialog](/docs/en/permissions#what-runs-before-you-trust-a-folder) |

Project-scope plugin checked into repository reaches every collaborator who clones it. Content comes from repository, not from you, so loads only after same trust gate as project allow rules in `.claude/settings.json`. Trusting parent folder or running with `-p` isn't enough. Components running code restricted further:

- **MCP servers:** Go through [same per-server approval](/docs/en/mcp)
- **LSP servers:** Start only after trusting workspace
- **Background monitors:** Do not load

Personal-scope plugins have no restrictions.

**⚠️ Critical:** Project-scope `@skills-dir` plugins load only from `.claude/skills/` of directory where you start Claude Code. They don't [walk up to repository root](/docs/en/skills#discovery-from-parent-and-nested-directories) like plain skills/commands do. Launching from subdirectory misses plugin at repo root. Launch from repository root or run `/reload-plugins` after changing directories.

### Edit, Reload, and Disable

Changes to skill's `SKILL.md` take effect immediately in current session. Changes to plugin's other components (`hooks/`, `.mcp.json`, `agents/`, `output-styles/`) do not. Run `/reload-plugins` or restart Claude Code to pick them up. See [Live change detection](/docs/en/skills#live-change-detection).

To stop loading skills-directory plugin, delete its folder or disable by name (no `uninstall` step):
```bash
claude plugin disable my-tool@skills-dir
```

---

## Plugins Synced from claude.ai

In [Cowork](https://claude.com/product/cowork) and [cloud sessions](/docs/en/cloud-environments#what-carries-over-from-your-setup), Claude Code downloads plugins enabled for your claude.ai account into `~/.claude/plugins/synced/` in session's own environment and loads each as `<name>@synced`, with no marketplace/install record. Claude Code doesn't load them in sessions you start in your own terminal.

On machine where synced session has run, `claude plugin list` shows downloaded copies under `Synced from claude.ai` heading noting they load only in synced session. Before v2.1.239, Claude Code loaded these as `<name>@inline`, the identity that `--plugin-dir` plugins use.

**Manage synced plugin by `<name>@synced` ID** that `claude plugin list` prints:

- **Turn off:** In synced session, run `claude plugin disable <name>@synced`, or ask Claude. Saves as `"<name>@synced": false` in environment's user-level [`enabledPlugins`](/docs/en/settings-reference#enabledplugins). To turn back on, run `claude plugin enable <name>@synced` in same session. To keep out of every synced session, [turn off for your claude.ai account](/docs/en/desktop#extend-claude-code). To keep out of one project's synced sessions, set `"<name>@synced": false` under `enabledPlugins` in project's committed `.claude/settings.json`
- **Manage on claude.ai:** `claude plugin install`, `update`, `uninstall` don't apply to synced plugin. To remove, turn off for claude.ai account; next synced session starts without it

**Name conflict resolution:** When enabled plugin from any other source (marketplace install, skills-directory plugin, `--plugin-dir` plugin) matches synced plugin's name, Claude Code loads that plugin and reports synced copy as not loaded. To use claude.ai copy instead, disable your own copy. Before v2.1.239, Claude Code loaded synced copy instead of same-named marketplace install.

---

## Plugin Caching and File Resolution

Plugins specified in two ways:

1. **`--plugin-dir` or `--plugin-url`** – For duration of session
2. **Marketplace** – Installed for future sessions

For security/verification, Claude Code copies **marketplace plugins** to user's local **plugin cache** (`~/.claude/plugins/cache`) rather than using in place, except for [`command` sources in link mode](/docs/en/plugin-marketplaces#copy-mode-and-link-mode), which Claude Code uses in place via cache links.

For copied plugins, each installed version is separate directory in cache, grouped by marketplace/plugin, named for resolved version, with own copy of files and [Node.js package dependencies](#nodejs-package-dependencies). Dependency resolved from [release tag](/docs/en/plugin-dependencies#tag-plugin-releases-for-version-resolution) gets directory with commit-SHA suffix.

When you update/uninstall plugin, Claude Code marks previous version directory orphaned and removes in background sweep ~14 days later. Grace period lets concurrent Claude Code sessions already loaded old version keep running without errors. Sweep runs only while at least one plugin installed; after uninstalling last plugin, orphaned directories stay until you install plugin again.

Claude Code removes plugin/marketplace folder from cache only when no longer contains any directory/symlink. If you symlink development checkout into cache as plugin's version entry, Claude Code never marks link orphaned/removed; also never writes version-tracking files inside linked checkout.

Claude's Glob and Grep tools skip orphaned version directories during searches, so file results don't include outdated plugin code.

### Node.js Package Dependencies

When Claude Code copies plugin into cache, it installs plugin's Node.js package dependencies there, so plugin's hooks/MCP servers can load them. Covers npm and Bun packages in plugin's own `package.json`. For plugins depending on other plugins, see [plugin dependency versions](/docs/en/plugin-dependencies).

Claude Code runs install inside copied version directory each time creating one: on plugin install, on update to new version, at session start when enabled plugin isn't cached yet (new machine).

**Install runs only when plugin root contains both `package.json` and supported lockfile:**

| Lockfile | Command |
|:---------|:--------|
| `bun.lock` or `bun.lockb` | `bun install --frozen-lockfile --ignore-scripts` |
| `npm-shrinkwrap.json` or `package-lock.json` | `npm ci --ignore-scripts` |

If plugin contains multiple lockfiles, Claude Code uses first match (checked in order): `bun.lock`, `bun.lockb`, `npm-shrinkwrap.json`, `package-lock.json`. Skips `yarn.lock` and `pnpm-lock.yaml` (Yarn/pnpm support resolution-time config hooks bypassing `--ignore-scripts`).

Ship npm lockfile for widest reach. Claude Code runs matched lockfile's package manager from user's PATH; doesn't fall back if missing. For npm-source plugin distribution, use `npm-shrinkwrap.json`; npm excludes `package-lock.json` from published packages.

**Constraints on dependency install:**
- **Frozen resolution:** Bun/npm install exactly what lockfile pins; fail rather than re-resolve
- **No lifecycle scripts:** `--ignore-scripts` prevents preinstall/install/postinstall scripts
- **60-second timeout:** Claude Code stops install running longer; treats as failed

Fetching npm-source plugin itself runs `npm install` with lifecycle scripts enabled, before this dependency install.

**Failed/skipped install never blocks plugin.** When install fails or Claude Code skips yarn/pnpm lockfile, records reason as warning in [debug output](#debugging-commands). Plugin with `package.json` and no lockfile skipped without log entry. Timed-out install can leave partial `node_modules` tree in cached copy.

**No off-switch:** Can't turn automatic install off; no setting/environment variable disables it.

**Restricted networks:** See [network access requirements](/docs/en/network-config#network-access-requirements) for hosts to allow.

**Dependencies automatic install can't provide** (packages needing lifecycle scripts to build, Python dependencies, yarn/pnpm-locked): Install from hook into [persistent data directory](#persistent-data-directory).

### Path Traversal Limitations

Copied plugins cannot reference files outside their directory. Paths traversing outside plugin root (e.g., `../shared-utils`) won't work after installation because external files not copied to cache.

### Share Files Within Marketplace With Symlinks

If plugin needs to share files with other marketplace parts, create symbolic links inside plugin directory. When copied into cache, symlink handling depends on target:

**Within plugin's own directory:** Symlink preserved as relative symlink in cache; keeps resolving to copied target at runtime.

**Elsewhere within same marketplace:** Symlink dereferenced; target's content copied into cache in its place. Lets meta-plugin's `skills/` directory link to skills defined by other marketplace plugins.

**Outside marketplace:** Symlink skipped for security; prevents plugins from pulling arbitrary host files into cache.

For plugins installed with `--plugin-dir`, local path, or [`command` source](/docs/en/plugin-marketplaces#copy-mode-and-link-mode) in copy mode: only symlinks resolving within plugin's own directory preserved; all others skipped.

**Example creating link from marketplace plugin to sibling plugin's shared skill.** On Windows, use `mklink /D` from elevated Command Prompt or enable Developer Mode:

```bash
ln -s ../../shared-plugin/skills/foo ./skills/foo
```

---

## CLI Commands Reference

Claude Code provides CLI commands for non-interactive plugin management, useful for scripting/automation.

### plugin init

Scaffold new plugin at `~/.claude/skills/<name>/`. On next Claude Code session loads automatically as `<name>@skills-dir`; appears in `/plugin` and `claude plugin list` with no install step.

See [Skills-directory plugins](#skills-directory-plugins) for scope/trust requirements.

```bash
claude plugin init <name> [options]
```

**Arguments:**
- `<name>`: Plugin name. Becomes skill namespace and directory name under `~/.claude/skills/`, cannot contain spaces/path separators

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `--description <text>` | Manifest description | |
| `--author <name>` | Author name | `git config user.name` |
| `--author-email <email>` | Author email | `git config user.email` |
| `--with <components...>` | Also scaffold folders. Valid: `skills`, `agents`, `hooks`, `mcp`, `lsp`, `output-style`, `channel` | |
| `-f, --force` | Overwrite existing `.claude-plugin/` at target | |
| `-h, --help` | Display help | |

**Aliases:** `new`

**Component scaffolding:**

| Component | What it scaffolds |
|:----------|:------------------|
| `skills` | Extra namespaced `<name>:example` skill alongside default |
| `agents` | `agents/` subagent definition |
| `hooks` | `hooks/hooks.json` with sample event handler |
| `mcp` | `.mcp.json` with HTTP and stdio server examples |
| `lsp` | `.lsp.json` language-server example |
| `output-style` | `output-styles/<name>.md` applying automatically while plugin enabled |
| `channel` | MCP-based channel: stdio server (`server.ts`), `.mcp.json`, `package.json` |

Scaffolded plugin uses `@skills-dir` source. Admins can block with `strictKnownMarketplaces` or `{"source": "skills-dir"}` in `blockedMarketplaces` in [managed settings](/docs/en/plugin-marketplaces#managed-marketplace-restrictions). When blocked, `plugin init` fails before writing.

**Examples:**
```bash
# Minimal plugin
claude plugin init my-helper

# With skill and hook folders
claude plugin init my-helper --with skills hooks

# Overwrite existing
claude plugin init my-helper --force
```

### plugin install

Install plugin from available marketplaces.

```bash
claude plugin install <plugin> [options]
```

**Arguments:**
- `<plugin>`: Plugin name or `plugin-name@marketplace-name` for specific marketplace

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-s, --scope <scope>` | Installation scope: `user`, `project`, `local` | `user` |
| `--config <key=value>` | Set [`userConfig`](#user-configuration) option. Repeat for multiple | |
| `-y, --yes` | Accept [`command` source](/docs/en/plugin-marketplaces#command-sources) or [`headersHelper`](/docs/en/plugin-marketplaces#authenticate-archive-downloads) without confirmation. Requires v2.1.238+ for `headersHelper`. Skipped inside Claude Code session | |
| `-h, --help` | Display help | |

Scope determines which settings file plugin added to (e.g., `--scope project` writes to `.claude/settings.json`, sharing with team).

**Examples:**
```bash
# Install to user scope (default)
claude plugin install formatter@my-marketplace

# Install to project scope (team-shared)
claude plugin install formatter@my-marketplace --scope project

# Install to local scope (not team-shared)
claude plugin install formatter@my-marketplace --scope local
```

### plugin uninstall

Remove installed plugin.

```bash
claude plugin uninstall <plugin> [options]
```

**Arguments:**
- `<plugin>`: Plugin name or `plugin-name@marketplace-name`

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-s, --scope <scope>` | Uninstall from: `user`, `project`, `local` | `user` |
| `--keep-data` | Preserve plugin's [persistent data directory](#persistent-data-directory) | |
| `--prune` | Remove auto-installed dependencies no other plugin requires. See [plugin prune](#plugin-prune) | |
| `-y, --yes` | Skip `--prune` confirmation. Required when stdin/stdout not TTY | |
| `-h, --help` | Display help | |

**Aliases:** `remove`, `rm`

By default, uninstalling from last remaining scope deletes `${CLAUDE_PLUGIN_DATA}` directory. Use `--keep-data` to preserve (e.g., reinstalling after testing new version).

**Note:** When installed plugins from different marketplaces share name, `plugin-name@marketplace-name` form uninstalls only from named marketplace. Before v2.1.212, qualified form could match same-name plugin from different marketplace.

### plugin prune

Remove auto-installed plugin dependencies no longer required by any installed plugin. Dependencies Claude Code pulled in satisfying another plugin's [`dependencies`](/docs/en/plugin-dependencies) field are removed; directly installed plugins never touched.

```bash
claude plugin prune [options]
```

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-s, --scope <scope>` | Prune at scope: `user`, `project`, `local` | `user` |
| `--dry-run` | List what would be removed without removing | |
| `-y, --yes` | Skip confirmation prompt. Required when stdin/stdout not TTY | |
| `-h, --help` | Display help | |

**Aliases:** `autoremove`

Lists orphaned dependencies; asks confirmation before removing. To remove plugin and clean dependencies in one step: `claude plugin uninstall <plugin> --prune`

### plugin enable

Enable disabled plugin. If declares [dependencies](/docs/en/plugin-dependencies), Claude Code enables transitively at same scope; fails when dependency not installed.

```bash
claude plugin enable <plugin> [options]
```

**Arguments:**
- `<plugin>`: Plugin name or `plugin-name@marketplace-name`

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-s, --scope <scope>` | Scope to enable: `user`, `project`, `local`. When omitted, auto-detect | Auto-detect |
| `-h, --help` | Display help | |

### plugin disable

Disable plugin without uninstalling. Fails when another enabled plugin [depends on](/docs/en/plugin-dependencies#enable-or-disable-a-plugin-with-dependencies) target. Error message includes chained command to disable all dependents first.

```bash
claude plugin disable [plugin] [options]
```

**Arguments:**
- `[plugin]`: Plugin name or `plugin-name@marketplace-name`. Optional with `--all`

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-a, --all` | Disable all enabled plugins. Can't combine with `--scope` | |
| `-s, --scope <scope>` | Scope to disable: `user`, `project`, `local`. When omitted, auto-detect | Auto-detect |
| `-h, --help` | Display help | |

### plugin update

Update plugin to latest version.

```bash
claude plugin update <plugin> [options]
```

**Arguments:**
- `<plugin>`: Plugin name or `plugin-name@marketplace-name`

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-s, --scope <scope>` | Scope to update: `user`, `project`, `local`, `managed` | `user` |
| `-y, --yes` | Accept [`command` source](/docs/en/plugin-marketplaces#command-sources) or [`headersHelper`](/docs/en/plugin-marketplaces#authenticate-archive-downloads) without confirmation. Requires v2.1.238+ for `headersHelper`. Skipped inside Claude Code session | |
| `-h, --help` | Display help | |

**Note:** Claude Code resolves bare plugin name against installed plugins. When plugins from different marketplaces share name, Claude Code refuses update and lists `plugin-name@marketplace-name` commands. Before v2.1.246, Claude Code rejected bare name as not found.

### plugin list

List installed plugins with version, source marketplace, enable status.

```bash
claude plugin list [options]
```

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `--json` | Output as JSON | |
| `--available` | Include available plugins from marketplaces. Requires `--json` | |
| `-h, --help` | Display help | |

**Interactive session** (`/plugin list`) prints similar listing inline but covers marketplace installs only:

- Plugins from skills directories appear in `/plugin` interface and `claude plugin list`, not in inline `/plugin list`
- On v2.1.239+, [plugins synced from claude.ai](#synced-plugins) appear in `claude plugin list` with note they load only in synced session; not in inline `/plugin list`
- Plugins loaded with `--plugin-dir`/`--plugin-url` appear in `/plugin` interface; in `claude plugin list` only when same flag precedes subcommand (`claude --plugin-dir <dir> plugin list`). Only flag names location (unlike synced/skills-dir whose fixed directories Claude Code scans)

Interactive form accepts `--enabled`/`--disabled` to show only that state; `ls` shorthand for `list`.

### plugin details

Show plugin's component inventory and projected token cost. Lists all components plugin contributes, grouped as Skills, Agents, Hooks, MCP servers, LSP servers, plus token estimate added to each session. Skills group includes both `skills/` and `commands/` entries.

```bash
claude plugin details <name>
```

**Arguments:**
- `<name>`: Plugin name or `plugin-name@marketplace-name`

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-h, --help` | Display help | |

**Output shows two cost figures per component:**

- **Always-on:** Tokens added to every session by plugin's listing text (skill descriptions, agent descriptions, command names), regardless of invocation
- **On-invoke:** Tokens component costs when fires. Shown per component; typical session invokes only subset

**Example output:**
```
dependency-guard 1.2.0
  Dependency analysis for Claude Code sessions
  Source: dependency-guard@example-marketplace

Component inventory
  Skills (2)  scan-dependencies, review-changes
  Agents (0)
  Hooks (1)  SessionStart  (harness-only — no model context cost)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~180 tok   added to every session

Per-component (rounded)
  component            always-on  on-invoke
  scan-dependencies        ~100      ~2400
  review-changes            ~80      ~1800

  On-invoke cost is paid each time a skill or agent fires.
  Token counts are estimates and may differ from actual usage.
```

Always-on total computed via `count_tokens` API for active model. Per-component scaled from total. If API unreachable, falls back to character-based estimate.

### plugin tag

Create release git tag for plugin. By default tags plugin in current directory; pass path to tag elsewhere. See [Tag plugin releases](/docs/en/plugin-dependencies#tag-plugin-releases-for-version-resolution).

```bash
claude plugin tag [path] [options]
```

**Arguments:**
- `[path]`: Path to plugin directory. Defaults to current directory

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `-v, --version <version>` | Tag version. Defaults to version in `plugin.json` or latest git tag | |
| `-m, --message <message>` | Commit message for tag | |
| `--force` | Force-create tag even if exists | |
| `-h, --help` | Display help | |

### plugin validate

Validate plugin structure and manifest.

```bash
claude plugin validate [path] [options]
```

**Arguments:**
- `[path]`: Path to plugin directory. Defaults to current directory

**Options:**

| Option | Description | Default |
|:-------|:------------|:--------|
| `--strict` | Treat warnings as errors | |
| `-h, --help` | Display help | |

Checks:
- Directory structure
- `plugin.json` schema
- Required files present
- File permissions
- Version format

Reports unrecognized fields as warnings (including misspellings of recognized fields). Plugin with only unrecognized-field warnings still passes and loads.

`--strict` treats warnings as errors (useful in CI for catching typos before publishing).

---

## Version Control: Manifest and Environment

### Environment Variable Substitution Reference

**In plugin components where substitution works:**

- Skill/agent content: All placeholders
- Hook/monitor commands: All placeholders
- MCP stdio servers: `command`, `args`, `env`
- MCP HTTP/SSE/WS: `url`, `headers`, `headersHelper`
- LSP servers: `command`, `args`, `env`, `workspaceFolder`

**Substitution patterns:**
```bash
# In shell form (quote paths to handle spaces)
"${CLAUDE_PLUGIN_ROOT}/scripts/deploy.sh"
"${CLAUDE_PLUGIN_DATA}/node_modules"
"${CLAUDE_PROJECT_DIR}/config.json"

# In exec form (each path as separate arg)
["${CLAUDE_PLUGIN_ROOT}/scripts/deploy.sh"]
```

---

## Windows-Specific Caveats

**Symlink creation:** When creating symlinks for [share files within marketplace](#share-files-within-marketplace-with-symlinks):
- Use `mklink /D` from elevated Command Prompt, or
- Enable Developer Mode (Windows 10+ feature)

**Path format:** 
- Claude Code handles forward slashes (`/`) and backslashes (`\`) in paths
- Substitute variables work cross-platform
- Wrap variables in quotes in shell commands: `"${VARIABLE}"`

**Executables in `bin/`:**
- Added to Bash tool's PATH when plugin enabled
- Must be executable (`.sh` scripts or native binaries)
- Run within Bash tool context; availability depends on `bash` being available

**Package installation:**
- `npm ci` (Windows) vs `npm ci` (Linux/macOS) — Claude Code handles transparently
- Bun package manager works cross-platform

---

## Plugin Dependency Management

Plugins can declare dependencies on other plugins via the `dependencies` field. See [Plugin dependencies](/docs/en/plugin-dependencies) for:
- Declaring dependencies with semver version constraints
- Enabling/disabling plugins with dependencies (transitive)
- Tagging releases for version resolution
- Constrain plugin dependency versions

Example dependency declaration:
```json
{
  "dependencies": [
    "base-plugin",
    { "name": "feature-plugin", "version": "^2.1.0" }
  ]
}
```

---

## Plugin Marketplaces

Plugins distributed through marketplaces via marketplace configuration files. See [Plugin marketplaces](/docs/en/plugin-marketplaces) for:
- Creating a marketplace (`marketplace.json` schema)
- Plugin entries and sources (GitHub, npm, archive, command, static)
- Version management and updates
- Copy mode vs. link mode for `command` sources
- Managed marketplace restrictions

---

## Summary of Critical Version Notes

**Requires Claude Code v2.1.154+:**
- `defaultEnabled` field in `plugin.json`

**Requires Claude Code v2.1.205+:**
- `shutdownTimeout` and `restartOnCrash` in LSP server configs

**Requires Claude Code v2.1.207+:**
- Shell-form hook/monitor command rejection of `${user_config.*}` values

**Requires Claude Code v2.1.212+:**
- Qualified `plugin-name@marketplace-name` form for `plugin uninstall` when multiple marketplaces share name

**Requires Claude Code v2.1.218+:**
- Boolean frontmatter fields accepting `yes`, `no`, `on`, `off`, `1`, `0` (case-insensitive)

**Requires Claude Code v2.1.221+:**
- Path field accepting `"."` to denote plugin root

**Requires Claude Code v2.1.238+:**
- Accepting `headersHelper` in `plugin install` and `plugin update` with `--yes`

**Requires Claude Code v2.1.239+:**
- Synced plugins reporting as `<name>@synced` instead of `<name>@inline`

**Requires Claude Code v2.1.246+:**
- Bare plugin name resolution in `plugin update` (before rejected as not found)