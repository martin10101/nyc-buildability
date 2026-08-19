# MCP Default-Deny Policy (owner directive D-020, task M0-T077)

**Rule: every ordinary Claude Code session working in NYC Buildability defaults to
having NO unrelated external MCP server active.** Connectors installed globally on the
owner's machine or connected to the owner's claude.ai account (Airtable, Microsoft 365,
Pencil, Supabase, or anything added later) must not accompany ordinary repository,
control-plane, testing, context, or application sessions. Installation or account
availability is NOT task authorization.

## Why

External MCP servers expose side-effectful tools (databases, SaaS records, design
files) to every session that loads them. This program's authority model routes every
side effect through gates, contracts, and frozen task scopes; an ambient connector
bypasses all of it. Default-deny makes connector access an explicit, reviewed,
per-task decision instead of an accident of what is installed.

## The policy (checked-in `.claude/settings.json`)

The policy is five additive keys merged into the existing project settings — the file
was never replaced, and every prior setting (`$schema`, `model`, `fallbackModel`,
`effortLevel`, `env`, `hooks`) is preserved verbatim. All keys are officially
supported Claude Code settings (claude-code-settings JSON schema; settings/MCP docs at
code.claude.com). Effect proven empirically by fresh-process probes
(`project-control/reports/M0-T077-fresh-session-proof.md`).

| Key | Value | What it does here |
|---|---|---|
| `disableClaudeAiConnectors` | `true` | The supported switch for claude.ai account connectors: they are not auto-fetched or connected (removes claude.ai Airtable + Microsoft 365 and any future account connector). `true` in any settings source wins. Requires CLI ≥ 2.1.182. |
| `allowedMcpServers` | `[]` | Default-deny allowlist: an EMPTY list means no MCP server of any scope may load. This is the backstop that also blocks *unexpected/future* servers. (An absent key means "all allowed" — absence is a policy failure.) |
| `deniedMcpServers` | 5 entries | Explicit denials by the exact audited identifiers: `pencil`, `supabase`, `mysql`, `sequential-thinking`, `playwright`. The denylist merges from all settings sources and takes precedence over any allowlist, so these stay blocked even after a future task allowlists a different connector. |
| `disabledMcpjsonServers` | 4 entries | Rejects the audited `.mcp.json`-defined servers (`supabase`, `mysql`, `sequential-thinking`, `playwright`) so they are never approved or started for this project. |
| `enableAllProjectMcpServers` | `false` | Auto-approval of project `.mcp.json` servers is explicitly off. |
| `permissions.deny` | `["mcp__*"]` | Deny-first TOOL rule: per the official settings precedence, "if a tool is denied at any level, no other level can allow it" — so even a server that some other settings source later allowlists exposes no usable MCP tool in this repository. |

Documented caveat, recorded honestly: without `allowManagedMcpServersOnly` in MANAGED
settings (none exist on this machine), `allowedMcpServers` lists MERGE from every
settings source, so an explicit user-scope allowlist entry could broaden the empty
project allowlist for a *new* server. The audited identifiers stay blocked regardless
(`deniedMcpServers` merges from all sources and "nothing overrides a denylist match"),
and `permissions.deny: ["mcp__*"]` keeps every MCP tool unusable here regardless of
connection state. Such an edit is explicit user action, not the ambient default D-020
governs.

Scope of effect: **this repository and its worktrees only** (project-scope settings).
Nothing was changed in the owner's global configuration (`~/.claude.json`, user
`~/.claude/settings.json`, user-level `.mcp.json`) or the claude.ai account: the same
connectors remain fully available in unrelated projects. Proof digests are in the
fresh-session-proof report.

## Audited inventory (2026-08-19)

Full 10-attribute audit: `project-control/reports/M0-T077-mcp-audit.md`. Summary:

| Server | Source / scope | Blocked here by |
|---|---|---|
| claude.ai Airtable | claude.ai account connector | `disableClaudeAiConnectors` + empty allowlist |
| claude.ai Microsoft 365 | claude.ai account connector | `disableClaudeAiConnectors` + empty allowlist |
| claude.ai Intuit QuickBooks | claude.ai account connector (ever-connected) | `disableClaudeAiConnectors` + empty allowlist |
| pencil | user scope (`~/.claude.json` → Cursor-extension stdio exe) | `deniedMcpServers` + empty allowlist |
| supabase | user-profile `.mcp.json` (ancestor-directory pickup), pre-approved by user-scope `enabledMcpjsonServers` | `disabledMcpjsonServers` + `deniedMcpServers` + empty allowlist |
| mysql / sequential-thinking / playwright | user-scope `enabledMcpjsonServers` approvals for other projects' `.mcp.json` | same three mechanisms (defensive) |
| pyright-lsp | Claude Code plugin (LSP, not an external MCP connector) | not in scope — no external capability |

## How a future task gets a connector (the ONLY path)

1. The owner issues a directive that names the **specific connector** and the **stated
   purpose** (e.g. "Supabase for bounded database task M0-TXXX").
2. That task's frozen contract includes `.claude/settings.json`,
   `tools/validate_mcp_policy.py`, and `tools/test_mcp_policy.py` in its allowed paths.
3. In one reviewed change the task: adds the connector to `allowedMcpServers`; removes
   it from `deniedMcpServers`/`disabledMcpjsonServers` **only if it is one of the
   audited identifiers**; and amends the validator's expectations to the new, still
   explicit, still minimal state. The validator failing until all three move together
   is intended visibility, not an obstacle to work around.
4. The change lands through the normal lifecycle (independent review, gates, owner
   merge authorization). When the authorizing work is done, a follow-up task restores
   the default-deny state.

Never: editing the owner's global configuration, connecting via `claude mcp add` at
user scope "just for this repo", or piggybacking on a connector another session left
active.

## Durable validation

`tools/validate_mcp_policy.py --check` (stdlib, read-only, fail-closed) asserts the
policy keys' exact values, that the pre-existing settings survived the merge (with a
documented string-level residual for hook commands, backstopped by the hook test
suites in the same job), and a whole-file shape assertion — every key present must be
known and correctly shaped, because one mistyped key makes Claude Code silently
discard the entire file. It runs with `tools/test_mcp_policy.py` in the
**control-plane** CI job on every push and PR, so accidental removal or weakening of
the policy fails that job visibly. (Failing checks gate merges only to the extent
branch protection requires them — a pre-existing repository setting this policy does
not change.)

## Official documentation (mechanism confirmation, D-020 §5)

- Managed MCP, allow/denylists, `disableClaudeAiConnectors`, deny-precedence quotes:
  https://code.claude.com/docs/en/managed-mcp
- Settings precedence (managed > CLI > local > project > user; deny-at-any-level wins):
  https://code.claude.com/docs/en/permissions#settings-precedence
- MCP tool permission rules (`mcp__*` wildcards): https://code.claude.com/docs/en/permissions#mcp
- `.mcp.json` scoping and `disabledMcpjsonServers`: https://code.claude.com/docs/en/mcp-quickstart
  and https://code.claude.com/docs/en/debug-your-config#check-mcp-servers
- Settings reference (key shapes; also mirrored by the `$schema` this file declares):
  https://code.claude.com/docs/en/settings

## Honest enforcement boundary

- Project-scope settings govern sessions launched **from the ROOT of this repository
  or one of its worktrees**. They cannot govern sessions launched outside the
  repository, and an interactive user can always take explicit manual action in
  their own session; this policy removes the *default* presence, which is what D-020
  requires.
- **Subdirectory limitation (G3 F-1, independently reproduced and re-proven):**
  Claude Code resolves `.claude/settings.json` from the session's starting directory
  only — it does not walk up to the repository root. A session started in a
  SUBDIRECTORY (e.g. `<repo>/tools`) loads no project settings and therefore gets
  the full ambient connector set, including live Supabase tools. Committed evidence:
  `project-control/reports/M0-T077-fresh-session-proof.md` Runs F/G. Mitigations in
  place: supervised workers always launch with `cwd` set to the worktree ROOT
  (`tools/agent_supervisor/claude_runner.py` path, verified read-only), so agent
  sessions are covered; the residual is a HUMAN starting a session one level down.
  Do not "fix" this by scattering settings files into subdirectories. **Smallest
  owner-gated next step:** the only supported machine-wide close-out is an
  owner-installed managed settings file (an owner-machine action outside repository
  scope, deliberately not performed by this task); short of that, start repository
  sessions from the repo root.
- Supervised launches: the supervisor starts workers with `cwd` set to a repository
  worktree (`tools/agent_supervisor/claude_runner.py`), so fresh supervised sessions
  load the same checked-in settings. Details and residual owner-gated items:
  `project-control/reports/M0-T077-supervisor-compatibility.md`.
