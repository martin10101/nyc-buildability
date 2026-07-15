---
name: vercel-dropped-frontend-on-render
description: Owner decided 2026-07-14 to drop Vercel and serve the frontend from Render (M0-T011 / ADR-004)
metadata:
  type: project
---

On 2026-07-14 the owner decided to drop Vercel and serve the Next.js frontend from Render, tracked as task M0-T011 / ADR-004. As of the M0-T006 G3 review, ADR-001/002/003 and docs/DEPLOYMENT_AND_ROLLBACK.md still assume Vercel (PRD 14.1 also still mandates Vercel), and ADR-004 did not exist yet.

**Why:** Owner decision postdating M0-T006; consolidating on Render reduces vendor count. Note PRD 14.1 names Vercel as required provider, so ADR-004 must record an owner-approved PRD deviation/change.

**How to apply:** When reviewing anything referencing Vercel (Instant Rollback, preview deployments, Hobby/Pro gating, branch-scoped env vars), check whether ADR-004 has landed and superseded those sections. Do not treat Vercel references in pre-ADR-004 docs as defects of their producing tasks. Verify current state of docs/adr/ before relying on this memory.
