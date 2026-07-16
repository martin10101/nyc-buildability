# M0-T011 — G0 Definition-of-Ready Review

- **Task:** M0-T011 — ADR-004: Frontend hosting on Render (drop Vercel) — owner decision 2026-07-14
- **Gate:** G0
- **Reviewer:** orchestrator
- **Date:** 2026-07-16
- **Verdict:** PASS

| G0 criterion | Evidence |
|---|---|
| Objective unambiguous | Owner decision already made (2026-07-14); task formalizes it: ADR-004 + amendment map application + additive render.yaml web service + runbook/README updates. S1–S5 pin the checks |
| Dependencies accepted | M0-T006 accepted 2026-07-15 (deploy model of record, render.yaml, runbook) |
| File scope exclusive | docs/adr/**, render.yaml, docs/DEPLOYMENT_AND_ROLLBACK.md, README.md — disjoint from M1-T002 (services/api), M0-T005-R1 (.github/scripts + docs/SECRETS_POLICY.md), M1-T003 (docs/research/zoning-*) |
| Inputs and outputs defined | Official Render doc evidence pre-captured by orchestrator at docs/research/render-nextjs-previews-2026-07-16.md (WebFetch, 2026-07-16); amendment map in M0-T006-G3-verification.md |
| Acceptance scenarios exist | S1–S5 (decision fidelity + citations, additive YAML + quoted "off", cross-reference completeness, deploy-model consistency, B-003 closure/PRD deviation) |
| Source documentation available | Captured research file in repo; official URLs cited for producer re-verification |
| Credentials | None (no purchases, no service creation — decision + config text only) |
| Gates assigned | G0/G3; producer cloud-architect; G3 code-reviewer |
| Execution location + disk | Text-only edits in main checkout allowed paths; KB-scale |
| Cleanup / durable routing | Committed docs/config only |

Note: any preview-strategy option with billing impact is decided as a *recommendation* in the ADR; actual plan purchase remains a human action.
