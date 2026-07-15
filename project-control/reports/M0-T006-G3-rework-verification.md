# G3 Gate Report — M0-T006 REWORK (independent re-review)

- **Task:** M0-T006 "ADRs + Render Blueprint + deploy/rollback procedures" (rework after G3 FAIL)
- **Gate:** G3 (independent walkthrough, re-run)
- **Reviewer:** code-reviewer (independent of producer cloud-architect)
- **Date:** 2026-07-15 | **Commit reviewed:** efec6b8 on `main`

## Verdict: PASS

## Summary

The rework implements the owner's mandated deployment model exactly and eliminates the Defect-1 contradiction that failed the first G3: all three production Render services now set `autoDeployTrigger: off` (the current field, correctly cited as replacing the deprecated `autoDeploy`), Vercel production git deploys are disabled by planned `git.deploymentEnabled` config, and every "halt" claim is explicitly reframed as the future GitHub Actions `needs:` chain, marked not-yet-implemented in all four files with a manual-mode STOP rule for the interim. The gated sequence (migration validation -> production migrations -> required CI checks -> human approval -> deploy-hook/`ref=<SHA>` + Vercel CLI) is stated in identical order in render.yaml (L33-38), ADR-002 s4 rule 3, ADR-003 D5, and runbook s0/s1.2. Defects 2-6 are all fixed with file evidence; new platform claims are cited to official URLs with 2026-07-15 retrieval dates traceable to the orchestrator-gathered research doc; orchestrator-captured parse evidence covers both render.yaml and ci.yml. Three LOW residual items remain; none is critical/high, so the gate passes with follow-ups.

## Owner-model compliance table

| # | Requirement | Evidence | Result |
|---|---|---|---|
| 1 | `autoDeployTrigger: off` on all prod services (modern field) | render.yaml:73 (web), :116 (worker), :155 (cron, previously defaulting to `commit`); deprecation/precedence cited render.yaml:26-30, ADR-003:25 | PASS |
| 2 | Actions-only prod deploys after validation -> migrations -> checks -> approval | ADR-003:49-54 (D5 chain); ADR-002:57 (rule 3, (a)-(d)); runbook:29 (s1.2 step 4); render.yaml:32-36 - identical order in all four | PASS |
| 3 | Deploy via secret deploy hook (GitHub `production` env secret) with `ref=<validated SHA>` | ADR-003:26 (D2); ADR-002:47; runbook:29; render.yaml:35-38; official cite render.com/docs/deploy-hooks, 2026-07-15 | PASS |
| 4 | Frontend gated the same way; `git.deploymentEnabled` planned config; CLI deploy; one-sentence ADR-004 note | ADR-003:18-20 (D1); ADR-002:36 | PASS |
| 5 | All four files describe the same sequence, no contradictions | Cross-read: same order, gate names, trigger mechanism. Minor wording nuance only (R2) | PASS |
| 6 | No unframed "halts automatically"/"blocks dependent" claims | Grep over docs/ + render.yaml: only hits are the research doc and ADR-003:25 deprecation framing. ADR-003:93 and runbook:65 attribute the halt solely to the future D5 `needs:` chain + manual STOP rule; D5 marked not-yet-implemented (ADR-003:47, :114; runbook:13) | PASS |
| 7 | Expand -> deploy -> contract preserved | ADR-003:36-43 (D4), :113; runbook:96 (s4); ADR-002:56 | PASS |
| D2 | No `ENVIRONMENT: value: production` literals | render.yaml:86-87, :121-122, :161-162 all `sync: false`; grep `value: production` -> no matches; ADR-002:51 documents mechanism | PASS |
| D3 | No phantom "staging smoke-test cron" | ADR-002:76 rewritten; grep -> no matches | PASS |
| D4 | Service-role key not in GitHub CI secrets | ADR-002:44 (Render only, "Not duplicated to GitHub"). Residual: ADR-001:36 still permissive - Defect R1 (LOW) | PASS (LOW residual) |
| D5 | Staging auto-deploy marked [confirm at first use] | render.yaml:39-42; ADR-002:56 + :87; ADR-003:27; runbook:22 | PASS |
| D6 | render.yaml YAML validation step in ci.yml | ci.yml:77-80; `git show efec6b8` confirms diff is ONLY the new step + disclosure comment | PASS |

## Scenario re-run (S1-S5)

| ID | Expected | Actual | Result |
|---|---|---|---|
| S1 | Valid Blueprint; env refs only; no literal secrets | Three services present; every env var `sync: false`; zero `value:` keys; hook URL never in file; parse evidence "render.yaml parse OK" | PASS |
| S2 | Alternatives considered; PRD 14.1 consistent | Unchanged since first review (ADR-001:38-53) | PASS |
| S3 | Concrete env mapping + promotion rules | ADR-002:32-38, :40-51, :53-58 consistent with gated model | PASS |
| S4 | Rollback incl. failed migration without contradiction | ADR-003:93 and runbook s2.5 match shipped config; original FAIL condition resolved | PASS |
| S5 | Official citations with retrieval dates | All new claims dated 2026-07-15, traceable to docs/research/deploy-trigger-gating-2026-07-15.md | PASS |

## Defects (none critical/high)

1. **R1 - LOW** - ADR-001:36 still reads "Supabase service-role key exists only in Render/GitHub Actions secret stores", contradicting ADR-002 s3 (Render only). Remediation: one-line edit on next ADR-001 touch (fold into M0-T011/ADR-004).
2. **R2 - LOW** - mechanism-attribution wording differs slightly between ADR-002 rule 3 / runbook s1.2 (needs: chain enforces all gates) and ADR-003 D5 (branch protection enforces (c), required reviewers enforce (d)). Not a contradiction; harmonize when D5 workflow is implemented.
3. **R3 - INFO** - D5 deploy workflow and apps/web/vercel.json are marked future work but had no task packets at review time. Orchestrator to create follow-ups before M0 exit.

## Note on the `off` spelling

PyYAML parses unquoted `off` as boolean false (YAML 1.1); the file copies the official blueprint-spec spelling verbatim (the non-guessing choice per PRD 31). Acceptable for this gate; quoting "off" is strictly safer and recommended non-blocking; add the accepted-value check to ADR-002's first-setup verification items. No production Blueprint sync can occur before the D5 follow-up work anyway.

## Files reviewed / evidence relied upon

render.yaml; docs/adr/ADR-001..003; docs/DEPLOYMENT_AND_ROLLBACK.md; .github/workflows/ci.yml (+ git show efec6b8 diff isolation); docs/research/deploy-trigger-gating-2026-07-15.md; project-control/reports/M0-T006-rework-summary.md (orchestrator parse evidence L85-93) and M0-T006-producer-report.md; project-control/tasks/M0-T006.json. Greps for contradiction patterns over docs/ and render.yaml.
