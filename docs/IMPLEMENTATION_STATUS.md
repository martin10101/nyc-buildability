# Implementation Status

Authoritative detail lives in `project-control/` (run `python tools/project_control.py status`). This file is the human-readable summary. Updated: 2026-07-15.

## Milestone: M0 — Engineering control plane and cloud foundation (ACTIVE)

### Accepted
| Task | Title | Producer | Gates passed |
|---|---|---|---|
| M0-T000 | Control-plane lifecycle verification | progress-auditor | G0, G3 (incl. intentional FAIL/rework path) |
| M0-T001 | Repository and control-system audit | progress-auditor | G0, G3 |
| M0-T002 | Geoclient/GeoSearch official-source research | official-source-researcher | G1 (data-contract-verifier), G3 |
| M0-T003 | Independent review of bootstrap plan | cloud-architect | G0, G3 |
| M0-T004 | Monorepo skeleton + GitHub Actions CI | backend-engineer | G0, G2, G3, G4, G5 — merged `1c1eee3`, main CI run 29455862963 all green; accepted 2026-07-15 |

### In rework
| Task | Title | Producer | State |
|---|---|---|---|
| M0-T006 | ADR-001/002/003 + render.yaml + rollback runbook | cloud-architect | G3 FAIL 2026-07-15 (auto-deploy vs migration-halt contradiction + defects 2-6; report: `project-control/reports/M0-T006-G3-verification.md`). Owner deployment model mandated: production `autoDeployTrigger: off`, GitHub Actions triggers deploys via secret deploy hook only after migration validation → prod migrations → required checks → human approval. Rework producer running; then G3 re-review. |

### Ready / next
- M0-T009 Canonical contracts v1 — packet contracted (G0) with D1/D2/D3 remediation scope; launches now that M0-T004 is accepted (ci.yml excluded from scope until M0-T006 rework integrates).
- M0-T011 / ADR-004 — owner decision 2026-07-14: drop Vercel, serve Next.js from Render. Sequenced after M0-T006 rework passes G3 (same files).
- M0-T005 secrets policy + CI secret scan.
- G5 follow-ups from M0-T004 (tracked, medium/low): pin actions to SHAs before any CI secret lands; Dependabot/audit; Python lockfile; remove or restrict generate-lockfile.yml.

### Blocked (human actions — see docs/HUMAN_ACTIONS_REQUIRED.md)
- B-001 SUPABASE_ACCESS_TOKEN → Supabase migrations/RLS/storage work (M0-T007/T008)
- B-002 RENDER_API_KEY → service creation (temporary chat key likely revoked; Blueprint authoring NOT blocked)
- B-003 Vercel → superseded by owner decision to drop Vercel (M0-T011/ADR-004); close after ADR-004 lands
- B-004 GEOCLIENT_SUBSCRIPTION_KEY → live fixtures (connector scaffolding NOT blocked)
- B-005 3D/UI expansion pack incomplete → M0-T010 (4 docs + 5 agent files still missing as of 2026-07-15)

## Process rules added 2026-07-15
- Evidence-capture division of labor (owner directive, in `.claude/rules/project-control.md`): orchestrator captures executable evidence (gh/python) into committed `project-control/reports/` artifacts; read-only reviewers verify stored evidence and never return BLOCKED for sandbox-execution limits alone.

## Infrastructure facts
- Repo: private `martin10101/nyc-buildability`, branch `main`; monorepo skeleton live (apps/web Next.js 15, services/api FastAPI, packages/contracts v1 schemas, supabase/migrations placeholder).
- CI: 4 jobs (web, api, contracts, control-plane regression) green on main; zero secrets required.
- Control plane: verified end-to-end; regression suite runs locally and in CI.
- Local footprint: source-only checkout; ~5 GB free on owner PC; 4 GB floor enforced.

## Defects found and fixed during bootstrap
1. `project_control.py` crashed on UTF-8 BOM JSON (found by lifecycle test) → `utf-8-sig`.
2. `state.json` rosters never updated by CLI (found by progress-auditor + cloud-architect independently) → `sync_state()` on every transition.
3. Gate records overwrote history, erasing the FAIL trail (found by progress-auditor) → history array preserved.
4. Credential blockers were narrative-only (found by cloud-architect) → B-001..B-004 formal records.
