# Connection Audit

Audited 2026-07-14 by the orchestrator. Statuses: Connected and tested / Connected but not yet tested / Not connected / Authentication required / Human action required.

| Service | Status | Evidence (no secrets) |
|---|---|---|
| Terminal (PowerShell 5.1 + Bash) | Connected and tested | All bootstrap commands executed locally |
| File editing | Connected and tested | Docs, ledger, and code edits in this repo |
| Git | Connected and tested | git 2.47.1; repo initialized; commit 8ba7278 on `main` |
| GitHub (gh CLI) | Connected and tested | gh 2.83.2 authenticated as `martin10101` (scopes: gist, read:org, repo, workflow); private repo `martin10101/nyc-buildability` created and pushed |
| GitHub Actions / remote CI | Connected but not yet tested | Push access + `workflow` scope verified; no workflow file exists yet (first CI task will prove it) |
| Web research (WebSearch/WebFetch) | Connected and tested | M0-T002 research retrieved official NYC documentation incl. a live keyless GeoSearch API call |
| Supabase (MCP) | Authentication required | MCP server resolves project URL `https://dyiviaalkqxeyyxotvvh.supabase.co`; management calls return Unauthorized (needs `SUPABASE_ACCESS_TOKEN`, blocker B-001) |
| Supabase CLI (local) | Not connected | Intentionally not installed (low-storage policy); remote MCP + migrations in git is the working model |
| Render | Connected and tested (temporary key) | 2026-07-14: owner-provided temporary API key verified via read-only GET /v1/owners + /v1/services (200); 4 pre-existing unrelated services identified and excluded from all operations; key held in memory only, never written to disk/repo; owner will revoke after initial service creation |
| Vercel | Decision pending — owner prefers dropping Vercel and serving the frontend from Render | ADR-004 task registered (M0-T011); B-003 on hold pending that ADR |
| Browser automation (Playwright) | Not connected (deferred by policy) | Not installed locally to protect disk budget; will run in GitHub Actions/Codespaces when UI work starts |
| Docker | Not connected (prohibited) | Verified absent; low-storage policy forbids local Docker |
| Airtable MCP, Microsoft 365 MCP, Pencil MCP | Connected but not used | Present in the session; not part of this architecture; will not be used for project data |

## Notes
- The Supabase MCP server being pointed at `dyiviaalkqxeyyxotvvh` needs owner confirmation that this project is intended for NYC Buildability (see HUMAN_ACTIONS_REQUIRED.md #1). No writes will occur until confirmed and authenticated.
- Cursor-connected services were not assumed; every status above was verified from this Claude Code session.
- Secret handling: all keys go into the harness/OS secret store or MCP server env, never chat/repo. Test procedures are defined per blocker in `project-control/blockers/`.
