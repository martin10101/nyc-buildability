---
name: m0-t006-g3-carryforward
description: G3 FAIL findings on M0-T006 (ADRs + render.yaml + runbook) that must be re-checked at rework and when the deploy CI pipeline is built
metadata:
  type: project
---

M0-T006 G3 (2026-07-15) returned FAIL with one high defect plus follow-ups:

1. HIGH — internal contradiction: `render.yaml` sets `autoDeploy: true` (and Vercel deploys are git-push-triggered), but ADR-003 failed-migration step 1 and runbook section 2.5 claim "a failed migration job blocks the dependent deploy jobs" / "pipeline halts automatically". Platform-native auto-deploys fire on the push, not after the GitHub Actions migration job. Rework must either gate deploys on CI checks (e.g., Render `autoDeployTrigger: checksPass` — verify against the current blueprint spec), use `autoDeploy: false` + CI-triggered deploy hooks, or rewrite the halt claim as a future-pipeline requirement with D4 (expand→deploy→contract) named as the actual safety net.
2. MEDIUM — `ENVIRONMENT: value: production` literal in all three services; the staging override mechanism referenced in the comment is not defined in ADR-002.
3. MEDIUM — ADR-002 section 6 watch item cites a "staging smoke-test cron (see render.yaml comments)" that does not exist in render.yaml (keep-warm mechanism for free Supabase projects is undefined).
4. LOW — service-role key duplicated to GitHub environment secrets though the cited Supabase CI flow needs only ACCESS_TOKEN/DB_PASSWORD/project ref; least-privilege nit.

**Why:** the FAIL is confined to the failure-handling path (S4); S1/S2/S3/S5 passed. Docs were status "Proposed" and the CI deploy pipeline does not exist yet, but an incident runbook asserting a halt that the shipped config contradicts is a hidden-assumption defect.
**How to apply:** when reviewing M0-T006 rework, the deploy CI workflow task, or ADR-004 (drop Vercel, frontend on Render — needs a documented PRD 14.1 deviation with owner approval), verify defect 1 first. Also re-check that mechanical YAML validation of render.yaml ran somewhere (this gate's sandbox denied Bash; only a manual parse was done). See [[m0-t004-g3-carryforward]] for ADR-005 process facts.
