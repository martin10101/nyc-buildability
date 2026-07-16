# Implementation Status

Authoritative detail lives in `project-control/` (run `python tools/project_control.py status`). This file is the human-readable summary. Updated: 2026-07-16 (end of session 4).

## Milestone: M0 — Engineering control plane and cloud foundation (ACTIVE)

### Accepted
| Task | Title | Producer | Gates passed |
|---|---|---|---|
| M0-T000 | Control-plane lifecycle verification | progress-auditor | G0, G3 |
| M0-T001 | Repository and control-system audit | progress-auditor | G0, G3 |
| M0-T002 | Geoclient/GeoSearch official-source research | official-source-researcher | G1, G3 |
| M0-T003 | Independent review of bootstrap plan | cloud-architect | G0, G3 |
| M0-T004 | Monorepo skeleton + GitHub Actions CI | backend-engineer | G0, G2, G3, G4, G5 — merged `1c1eee3`; accepted 2026-07-15 |
| M0-T006 | ADRs + Render Blueprint + deploy/rollback runbook | cloud-architect | G0, G3 (first G3 FAILED; rework to owner's Actions-gated deploy model passed re-review) — accepted 2026-07-15 |
| M0-T005 | Secrets policy + .env templates + secret scanner + scan workflow | backend-engineer | G0, G2, G3, G5 — merged; scan workflow live and green on main; accepted 2026-07-16 |
| M0-T009 | Canonical contracts v1 (6 schemas, validator, fixtures) | backend-engineer | G0, G2, G3, G4, G5 — merged `fe6cc21`; CI 4/4 green; accepted 2026-07-16 |

### In progress
| Task | State |
|---|---|
| M1-T001 PLUTO/MapPLUTO research | Claimed (official-source-researcher), G0 PASS; producer launched near session-4 end. Gates when delivered: G1 (data-contract-verifier) + G3. |

### Ready / next
- **M0-T005-R1** — scanner + validator hardening (contracted, backlog, ready to claim). 11-item burn-down of all M0-T005/M0-T009 review defects. Must land before any real credential enters the repo or M0 exit. Note: CI runner ships jsonschema 4.10.3, making the legacy RefResolver the LIVE CI path — item 10 priority raised.
- M0-T011 / ADR-004 — drop Vercel, serve Next.js from Render (owner decision 2026-07-14). Stub packet needs filling. Fold in G3 residuals R1 (ADR-001:36 service-role line) and the `"off"`-quoting recommendation. Closes B-003.
- Follow-up tasks to create before M0 exit: D5 production deploy workflow; frontend deploy gating (decide inside M0-T011); M0-T004 G5 hygiene batch (SHA-pin all actions before any CI secret, Dependabot, Python lockfile, remove/restrict generate-lockfile.yml).
- M1 research fan-out: one packet per remaining PRD 8.1 source family after M1-T001 gates.

### Blocked (human actions — see docs/HUMAN_ACTIONS_REQUIRED.md)
- B-001 SUPABASE_ACCESS_TOKEN → M0-T007/T008
- B-002 RENDER_API_KEY → service creation (fresh key needed; temporary key presumed revoked)
- B-003 Vercel → superseded pending ADR-004; close when ADR-004 lands
- B-004 GEOCLIENT_SUBSCRIPTION_KEY → live fixtures
- B-005 3D/UI expansion pack incomplete → M0-T010 (re-audited 2026-07-16: 3/12 files present; no INTEGRATION_MANIFEST.json exists anywhere)
- B-006 GitHub push protection + secret scanning + branch protection (NEW 2026-07-16; G5-designated compensating control for scanner false negatives)

## Repository hygiene note (2026-07-16)
The unknown generic Node/Express `.claude/` pack (63 untracked files: agents, skills, commands, hooks, settings.json) was quarantined to `_quarantine/claude-pack-2026-07-15/` per the owner's isolate-don't-delete decision; `_quarantine/` is gitignored. Project agents/skills/rules are untouched. The pack is unrelated to the B-005 expansion files.

## Deployment model of record (M0-T006, accepted)
Production: `autoDeployTrigger: off` on all Render services; deploys triggered only from the future GitHub Actions deploy workflow (D5) after migration validation → production migrations → required checks → human production approval, via secret deploy hooks with `ref=<validated SHA>`; frontend gated identically. Staging: `autoDeployTrigger: commit` `[confirm at first use]`. Expand → deploy → contract migrations. The D5 workflow does not exist yet; until it does, production deploys are manual with a STOP-on-failed-migration rule (runbook §0).

## Process rules (2026-07-15, in `.claude/rules/project-control.md`)
- ADR-005: orchestrator-only ledger writes; producers/reviewers return evidence.
- Evidence-capture: orchestrator captures executable evidence (gh/python) into committed reports when reviewer/producer sandboxes deny execution; reviewers never BLOCKED for sandbox limits alone.

## Infrastructure facts
- Repo: private `martin10101/nyc-buildability`; monorepo live (Next.js 15 placeholder, FastAPI placeholder, contracts v1 schemas + validator + fixtures, migrations placeholder, secret-scan workflow).
- CI: 4 jobs green on main (run 29463721845) + secret-scan workflow green (run 29461455381 first, subsequent runs green).
- Local footprint: source-only; ≥ 4 GB free floor maintained.
