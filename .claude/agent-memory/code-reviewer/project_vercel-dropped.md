---
name: vercel-dropped-frontend-on-render
description: ADR-004 landed (M0-T011, G3 PASS 2026-07-16) - Vercel dropped, frontend is Render web service nycdf-web; known allowed Vercel residuals list
metadata:
  type: project
---

ADR-004 (docs/adr/ADR-004-frontend-hosting-render.md) landed at commit 8e6bdf4 and passed G3 on 2026-07-16: the Next.js frontend is Render web service `nycdf-web` (runtime node, rootDir apps/web, plan starter, `autoDeployTrigger: "off"` quoted, deploy-hook gated identically to the API). ADR-001/002/003, runbook, README, render.yaml were amended; both M0-T006 R1 residuals applied. See [[m0-t011-g3-carryforward]] for residuals still open.

**Why:** Owner decision 2026-07-14 (single deployment platform); PRD §14.1 deviation recorded per PRD §34 inside ADR-004.

**How to apply:** Vercel references are now DEFECTS unless they are: inside ADR-004; superseded-marked rows in ADR-001/002/003/runbook; immutable source docs (PRD.md, PRODUCT_FLOW, LOW_STORAGE, IMPLEMENTATION_SEQUENCE); project-control history; or on the tracked cleanup list (SECRETS_POLICY.md, apps/web/.env.example, services/api/.env.example, README_START_HERE.md, cloud-architect agent description, CLAUDE.md principle 5). Verify the cleanup task landed before flagging those again.
