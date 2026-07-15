---
name: m0-t006-g3-carryforward
description: M0-T006 rework G3 PASS (2026-07-15); residual low items to re-check when the D5 deploy workflow, vercel.json, and first Blueprint sync are built
metadata:
  type: project
---

M0-T006 rework G3 (2026-07-15, commit efec6b8) returned **PASS**. The owner-mandated deploy model (Render `autoDeployTrigger: off` in prod, GitHub Actions deploy via secret deploy hooks with `ref=<SHA>` after migration-validation → prod migrations → required checks → human approval; Vercel git deploys disabled for `production` via planned `git.deploymentEnabled`, CLI deploy from Actions) is implemented consistently across render.yaml, ADR-002 §2-4, ADR-003 D1/D2/D5/R-sections, and the runbook. Original defects 1-6 all fixed.

Residual LOW items to re-verify at the named follow-up tasks:
1. ADR-001 rule 5 still says service-role key lives in "Render/GitHub Actions secret stores" — contradicts ADR-002 §3 row 1 ("Render only, not duplicated to GitHub"). One-line ADR-001 fix; check at next ADR-001 touch or defect sweep.
2. `autoDeployTrigger: off` is unquoted; PyYAML (YAML 1.1) parses it as boolean false. Render's own spec examples write it unquoted, so current spelling follows official docs, but quoting `"off"` is unambiguous in YAML 1.1 and 1.2 and I recommended it. Verify actual accepted value at first Blueprint sync.
3. ADR-002 rule 3 / runbook §1.2 attribute all four production gates to the `needs:` chain; ADR-003 D5 (authoritative) correctly splits mechanisms (needs: for migrations, branch protection for checks, environment required reviewers for approval). Harmonize wording when D5 workflow is implemented.
4. Preconditions for first production deploy (tracked follow-ups, not yet tasks as of 2026-07-15): D5 GitHub Actions production deploy workflow; `vercel.json` with `git.deploymentEnabled` in apps/web.

**Why:** the first G3 FAIL was a hidden-assumption contradiction (docs claimed an automatic halt the shipped config could not produce); the rework resolved it by disabling all platform auto-deploys in production and honestly marking the enforcement chain as a future task everywhere.
**How to apply:** when reviewing the D5 deploy-workflow task, ADR-004/M0-T011 (Vercel decision), or the first Blueprint deploy evidence, check items 1-4 above first. See [[m0-t004-g3-carryforward]] for ADR-005 process facts.
