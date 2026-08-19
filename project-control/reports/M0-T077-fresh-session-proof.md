# M0-T077 — Fresh-session proof (D-020 §7)

All listings below are FRESH PROCESSES (`claude mcp list`, CLI 2.1.220): each
invocation starts a new `claude` process that performs full configuration resolution
and (for stdio/HTTP servers) real connection attempts — nothing is inherited from the
already-running orchestrator session, whose deferred tool definitions play no part in
this evidence.

## 1. BEFORE (clean main worktree `wt-m0t064` @ origin/main 31c50a09 — no policy)

```
claude.ai Airtable: https://mcp.airtable.com/mcp - ✔ Connected
claude.ai Microsoft 365: https://microsoft365.mcp.claude.com/mcp - ! Needs authentication
pencil: …highagency.pencildev…\mcp-server-windows-x64.exe --app cursor --agent claudeCodeCLI - ✔ Connected
supabase: npx -y @supabase/mcp-server-supabase@latest --project-ref dyiv… - ✘ Failed to connect — connection timed out after 30000ms
```

Four unrelated external servers loaded/attempted (the supabase timeout is a connection
outcome; the server is configured, approved, and launched — in the non-repo control
below the same server reports `✔ Connected`).

## 2. AFTER (policy committed at a2bee92)

**Run A — fresh CLEAN worktree** (`git worktree add --detach … a2bee92`; `git status`
empty; brand-new directory never used by any session):

```
No MCP servers configured. Use `claude mcp add` to add a server.
```

**Run B — second fresh process in the same clean worktree after Run A's process
exited** (restart-survival: the result is carried by tracked files alone, no session
state involved):

```
No MCP servers configured. Use `claude mcp add` to add a server.
```

**Run C — the task worktree `wt-m0t077`** (same result before the reports were even
committed — the policy needs only `.claude/settings.json`):

```
No MCP servers configured. Use `claude mcp add` to add a server.
```

Per-item evidence required by D-020 §7:
- Airtable NOT active ✔ (absent from Runs A/B/C)
- Microsoft 365 NOT active ✔ (absent)
- Pencil NOT active ✔ (absent)
- Supabase NOT active ✔ (absent — not even attempted)
- No unexpected external MCP server active ✔ (empty list; `allowedMcpServers: []`
  additionally guarantees any FUTURE server of any scope is blocked here)
- Repository settings still load normally ✔ (the same fresh processes read
  `.claude/settings.json` without error; `tools/validate_mcp_policy.py` parses it and
  exit 0; the pre-existing model/env/hooks keys are intact — see §4)
- Unrelated settings preserved ✔ (§4)
- No global account connector removed ✔ (§3)
- Survives closing and starting a fresh repository session ✔ (Run B after Run A's
  process exit; each `claude mcp list` is itself a fresh session-config resolution)

## 3. Global preservation (owner account and machine-wide config untouched)

Byte digests (sha256) captured BEFORE implementation and re-captured AFTER all proofs:

| File | Before | After | Identical |
|---|---|---|---|
| user-profile `.mcp.json` | `1fc898cc6935…` | `1fc898cc6935…` | YES |
| user `~/.claude/settings.json` | `a738fcfa9573…` | `a738fcfa9573…` | YES |
| user `~/.claude.json` → `mcpServers` (structural) | `7500a3e4dad6…` | `7500a3e4dad6…` | YES |
| user `~/.claude.json` → `claudeAiMcpEverConnected` (structural) | `c838ec230a5b…` | `c838ec230a5b…` | YES |
| user settings → `enabledMcpjsonServers` (structural) | `e2f8bdbc3b6f…` | `e2f8bdbc3b6f…` | YES |

(The user-level `~/.claude.json` is volatile session state that Claude Code itself
rewrites constantly, so the MCP-relevant substructures are digested; both structural
digests are unchanged, and the two non-volatile files are byte-identical.)

**Functional control — fresh process from a NON-repository directory (unrelated
projects), run AFTER the policy landed:**

```
claude.ai Airtable: https://mcp.airtable.com/mcp - ✔ Connected
claude.ai Microsoft 365: https://microsoft365.mcp.claude.com/mcp - ! Needs authentication
pencil: … - ✔ Connected
supabase: npx -y @supabase/mcp-server-supabase@latest --project-ref dyiv… - ✔ Connected
```

Every connector remains fully available outside this repository: nothing was
disconnected, deleted, or modified account-wide (D-020 §6.5-6.7).

## 4. Settings preservation (merge, not replacement)

`git diff 31c50a09..a2bee92 -- .claude/settings.json` is purely ADDITIVE: the five
policy keys inserted after `effortLevel`; `$schema`, `model`, `fallbackModel`,
`effortLevel`, `env` (both timeout vars), and all four hook registrations
byte-identical. `tools/validate_mcp_policy.py` p7 asserts this permanently.

## 5. Honest limitations

- The proof medium is `claude mcp list` from fresh processes (plus the isolated
  scratch-project ablations recorded in the G0 report). A full interactive session
  restart of THIS orchestrator session cannot be self-verified from inside it; the
  fresh-process runs above are the smallest safe equivalent (D-020 §7 fallback),
  and they exercise the same configuration-resolution path a new session uses.
- The policy governs sessions launched from THIS repository and its worktrees.
  Sessions launched elsewhere (including the user profile root) are outside
  repository-scope authority by design; blocking there would require changing the
  owner's global configuration, which D-020 §6 prohibits.
- An interactive user can still take explicit manual action in their own session
  (e.g. `claude mcp add` at local scope). The policy removes the ambient DEFAULT
  presence, which is D-020's stated objective; it is not (and cannot be) a
  machine-wide mandatory control without managed settings, which would be an
  owner-machine action, not a repository change.
