# M0-T077 — Read-only MCP audit (D-020 §5)

Conducted 2026-08-19 BEFORE any configuration change, with read-only commands only
(`claude mcp list` fresh processes; JSON key/structure inspection of the applicable
configuration files with secret values masked at read time — no secret, token,
connection string, or account content was ever printed, logged, or committed).
Mechanism behavior confirmed against the official claude-code-settings JSON schema
(json.schemastore.org/claude-code-settings.json, referenced by the settings files
themselves) and code.claude.com documentation links embedded in that schema.
Installed CLI: 2.1.220.

## Inventory (every MCP server visible to sessions in this repository before the policy)

### 1. claude.ai Airtable
- **Exact configured name:** `claude.ai Airtable` (account connector; no local config entry)
- **Displayed name:** `claude.ai Airtable`
- **Server source:** remote HTTP MCP, `https://mcp.airtable.com/mcp`
- **Scope:** claude.ai account (auto-fetched connector)
- **Configuration/account source:** owner's claude.ai account (listed in the local
  `claudeAiMcpEverConnected` state; no server definition on disk)
- **Currently enabled:** yes — fresh repo-worktree process showed `✔ Connected`
- **Follows:** ALL projects on this machine while the account is connected
- **Capability:** full Airtable base/table/record/automation/interface read-write
- **Required by NYC Buildability:** NO (no task contract references it)
- **Repository-scope disable without touching the owner's account:** YES —
  `disableClaudeAiConnectors: true` in checked-in project settings (+ empty
  `allowedMcpServers` backstop)

### 2. claude.ai Microsoft 365
- **Exact configured name:** `claude.ai Microsoft 365` (account connector)
- **Displayed name:** `claude.ai Microsoft 365`
- **Server source:** remote HTTP MCP, `https://microsoft365.mcp.claude.com/mcp`
- **Scope:** claude.ai account (auto-fetched connector)
- **Configuration/account source:** owner's claude.ai account
- **Currently enabled:** loaded in every session (`! Needs authentication` — present and
  offering authentication tools even when unauthenticated)
- **Follows:** ALL projects
- **Capability:** Microsoft 365 account access (mail/files/etc. once authenticated)
- **Required by NYC Buildability:** NO
- **Repository-scope disable without touching the owner's account:** YES — same
  mechanism as #1

### 3. claude.ai Intuit QuickBooks (ever-connected)
- Recorded in the account's ever-connected list; NOT active in current sessions.
  Covered defensively by the same two mechanisms as #1/#2. No other attributes
  observable read-only; no action needed beyond default-deny.

### 4. pencil
- **Exact configured name:** `pencil`
- **Displayed name:** `pencil`
- **Server source:** local stdio executable (Cursor extension
  `highagency.pencildev` `mcp-server-windows-x64.exe`, args `--app cursor --agent
  claudeCodeCLI`)
- **Scope:** USER scope — top-level `mcpServers` in the user-level `~/.claude.json`
- **Configuration/account source:** `~/.claude.json` (owner's global Claude Code config)
- **Currently enabled:** yes — fresh repo-worktree process showed `✔ Connected`
- **Follows:** ALL projects on this machine
- **Capability:** .pen design-file read/generate/export (Pencil editor)
- **Required by NYC Buildability:** NO
- **Repository-scope disable without touching the owner's global config:** YES —
  project-scope `deniedMcpServers: [{"serverName": "pencil"}]` (empirically proven:
  the deny entry in a project `.claude/settings.json` removes the user-scope server
  for that project only) + empty `allowedMcpServers` backstop

### 5. supabase
- **Exact configured name:** `supabase`
- **Displayed name:** `supabase`
- **Server source:** stdio via `npx -y @supabase/mcp-server-supabase@latest
  --project-ref dyiv…` (project ref truncated here on purpose; full value remains only
  in the owner's own file). Its env block carries `SUPABASE_ACCESS_TOKEN` — the VALUE
  was never displayed, logged, or committed.
- **Scope:** `.mcp.json`-style project config in the USER PROFILE directory, reaching
  this repository through ancestor-directory pickup (the repo lives under the profile
  directory); pre-approved machine-wide by user-scope `enabledMcpjsonServers`, which
  also lists `mysql`, `sequential-thinking`, `playwright`
- **Configuration/account source:** user-profile `.mcp.json` + user
  `~/.claude/settings.json` approval list
- **Currently enabled:** yes — attempted in every fresh repo session (observed
  `✔ Connected` in the pre-change non-repo control; one repo-worktree run timed out
  at 30 s, i.e. still configured/attempted)
- **Follows:** every project under the user profile directory (effectively all)
- **Capability:** Supabase project SQL execution, migrations, edge functions, logs —
  this is the PRODUCTION datastore of this program (Permanent Principle 5): ambient
  exposure is the highest-risk item in this audit
- **Required by NYC Buildability:** not for ordinary sessions (database work is
  task-gated; D-020 example: "Supabase may be authorized for a bounded database task")
- **Repository-scope disable without touching the owner's global config:** YES —
  project-scope `disabledMcpjsonServers: ["supabase"]` (empirically proven to override
  the user-scope approval for this project) + `deniedMcpServers` + empty allowlist

### 6-8. mysql, sequential-thinking, playwright
- Present only as names in the user-scope `enabledMcpjsonServers` approval list
  (approvals for other projects' `.mcp.json` files); no server definition reaches this
  repository today, and none appeared in any fresh repo-session listing. Denied
  defensively at repository scope by the same three mechanisms so a future `.mcp.json`
  appearing in an ancestor directory cannot activate them here.

### 9. pyright-lsp@claude-plugins-official
- Claude Code plugin (user scope, `installed_plugins.json`). Provides Python LSP —
  it is NOT an external MCP connector and exposes no external-account capability.
  Out of D-020 scope; unaffected by the policy.

## Managed/enterprise scope
`managed-settings.json` (ProgramData): ABSENT — no managed MCP configuration exists on
this machine. Repo `.mcp.json`: ABSENT at origin/main 31c50a09.

## Conclusion
Four unrelated external servers were active or attempted in ordinary fresh repository
sessions (claude.ai Airtable, claude.ai Microsoft 365, pencil, supabase); three more
names were pre-approved at user scope; every one is disable-able at repository scope
by officially supported settings without modifying the owner's account or global
configuration. Chosen policy: see `docs/MCP_DEFAULT_DENY_POLICY.md`.
