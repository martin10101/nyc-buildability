---
name: m0-t011-g3-carryforward
description: M0-T011 (ADR-004 frontend on Render) G3 PASS 2026-07-16 with 6 low/medium residuals; carry-forwards for the D5 deploy-workflow task and doc cleanup
metadata:
  type: project
---

M0-T011 G3 verdict: PASS (report: project-control/reports/M0-T011-G3-review.md; commit 8e6bdf4). All 5 scenarios passed on independent re-execution; render.yaml = 4 services, all `autoDeployTrigger` parse as string 'off'.

Open residuals to re-check later (verify current file state before flagging — orchestrator may have fixed them):
1. CLAUDE.md:23 principle 5 still names Vercel (MEDIUM; owner/orchestrator edit).
2. Cleanup task pending for: docs/SECRETS_POLICY.md Vercel rows, apps/web/.env.example header, services/api/.env.example:15-16 VERCEL_* comment (was UNDISCLOSED by producer), README_START_HERE.md:8/28/56, .claude/agents/cloud-architect.md:3.
3. ADR-001/002/003 headers still "Proposed (pending G3 gate review)" despite M0-T006 acceptance — status hygiene.

D5 deploy-workflow carry-forwards: single deploy-render job calls FOUR hooks (API/worker/cron then nycdf-web last) with ref=SHA; halt-on-failed-migration exists ONLY in D5 needs: chain; staging `autoDeployTrigger: commit` at instantiation [confirm at first use]; service-previews plan-gating unverified (fresh capture of render.com/docs/service-previews before enablement); Blueprint-sync behavior with "off" unconfirmed.

**Why:** These are the residuals I adjudicated as non-blocking; future gates (D5 task, first Blueprint sync, M2 preview re-evaluation) must confirm they were closed rather than assume it.

**How to apply:** At the D5 workflow G3 and at the doc-cleanup task review, grep `vercel` again and check items 1-3; enforce the four-hook order and needs:-chain halt. Related: [[vercel-dropped-frontend-on-render]], [[m0-t006-g3-carryforward]].
