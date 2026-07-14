# Human Actions Required

Only actions requiring ownership or private authority are listed. Everything else proceeds without you. Each action maps to a blocker record in `project-control/blockers/`.

Never paste any secret into chat, source code, documentation, or a committed `.env` file. Use the locations specified below.

## 1. Supabase access token (B-001) — HIGHEST PRIORITY
Unblocks: database migrations, RLS baseline, storage buckets — the entire M0 cloud foundation.

1. Go to https://supabase.com/dashboard/account/tokens
2. Create a personal access token (name suggestion: `claude-code-nyc-buildability`).
3. Add it to the Supabase MCP server configuration for Claude Code as `SUPABASE_ACCESS_TOKEN` (Claude Code → Settings → MCP servers → supabase → environment), then restart Claude Code so the MCP server picks it up.
4. Minimum permissions: Supabase PATs are account-scoped; if you have unrelated production projects in other organizations, consider a dedicated Supabase organization for this product.
5. How it will be tested: a read-only `list_tables` call. The token value will never be displayed or logged.

Note: the MCP server already resolves project `dyiviaalkqxeyyxotvvh.supabase.co`. If that project is NOT intended for this product, say so — a dedicated development project will be created instead of touching it.

## 2. Render API key (B-002) — DONE 2026-07-14 (temporary key)
Temporary key provided and verified (read-only calls only; 4 pre-existing unrelated services excluded from all operations; key never written to disk or repo). **One remaining step:** keep the key valid until the initial services are created from the monorepo (immediately after M0-T004/M0-T006 land — expected same session), then revoke it. If you revoke earlier, that's fine — I'll ask for a fresh key or use the dashboard Blueprint flow at deployment time. Future secrets: use environment variables or MCP config, not chat.

## 3. Vercel (B-003) — ON HOLD, likely not needed
Owner decision 2026-07-14: prefer serving the frontend from Render instead of Vercel. ADR-004 (task M0-T011) will formalize this with trade-offs (Render supports Next.js web services and PR preview environments; Vercel's edge network/preview UX is the main loss). No Vercel action needed unless the ADR concludes otherwise.

## 4. NYC Geoclient subscription key (B-004)
Unblocks: live fixture capture and rate-limit confirmation for the address-resolution connector (M1). Research is already complete without it.

1. Sign up at https://api-portal.nyc.gov/ (free).
2. Products → subscribe to "Geoclient User", selecting "Geoclient - v2".
3. Profile → Subscriptions → Show key. While there, note the rate limits displayed on the subscription page (they are only visible when logged in).
4. Provide the key as environment variable `GEOCLIENT_SUBSCRIPTION_KEY`.
5. How it will be tested: one documented `/v2/address` request expecting HTTP 200 JSON. Key never echoed.

## 5. Complete the 3D/UI expansion pack copy (B-005)
Unblocks: integration of the 3D massing / premium UI / financial / opportunity workstreams.

Three expansion files arrived mid-bootstrap and are committed, but the continuation prompt references 4 more documents (`.claude/rules/3d-ui-expansion.md`, `docs/COMPETITIVE_FEATURE_EXPANSION.md`, `docs/3D_AND_UI_EXECUTION_PLAN.md`, `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md`) and 5 new subagents (`3d-massing-engineer`, `product-design-director`, `visual-quality-reviewer`, `financial-feasibility-engineer`, `opportunity-search-engineer`) that are not present. Copy the rest of the pack into the project root, or say the pack is withdrawn. Integration (task M0-T010) proceeds automatically once the files exist. Core M0/M1 work is NOT blocked by this.

## Later (not yet blocking — will be requested when reached)
- Production deployment approval (G7).
- Qualified NYC zoning professional to approve the first verified rule set (G6). Rule ingestion/extraction/testing proceeds meanwhile; nothing is published as "verified" until this approval.
- Pilot/validation property list from the client for golden-property comparison (M6).

## Status log
| Date | Action | Status |
|---|---|---|
| 2026-07-14 | B-001 Supabase token | OPEN — requested |
| 2026-07-14 | B-002 Render API key | OPEN — requested |
| 2026-07-14 | B-003 Vercel | OPEN — requested (low urgency) |
| 2026-07-14 | B-004 Geoclient key | OPEN — requested |
