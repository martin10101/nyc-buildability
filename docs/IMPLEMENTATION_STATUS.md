# Implementation Status

> **HISTORICAL — DO NOT USE FOR CURRENT STATUS.** The task tables below are stale (last updated
> 2026-07-16, session 5) and are kept only for history. They predate almost all accepted work.
> For current, authoritative state run `python tools/current_state.py` (compact) or
> `python tools/project_control.py status`, and read `docs/SESSION_HANDOFF.md`. Do not plan work
> from this file and do not maintain it as a live task board — the ledger is the single source of truth.

Authoritative detail lives in `project-control/` (run `python tools/project_control.py status`). This file is the human-readable summary. Updated: 2026-07-16 (session 5, after M1-T002 acceptance).

## Session 5 additions (2026-07-16)

| Task | Title | Result |
|---|---|---|
| M0-T005-R1 | Scanner + validator hardening (11 items) | **ACCEPTED** (G0/G2/G3/G5) — merged `84b6a15`; SECRETS_POLICY §5 accuracy + ADR-004 update included; hardened scanner immediately caught fake demo values in gate reports (pragma-allowlisted, visible suppressions); Low residuals F1/F2/F3 carried to hygiene follow-up + B-006 |
| M0-T011 | ADR-004: frontend on Render, drop Vercel | **ACCEPTED** (G0/G3) — `nycdf-web` additive service, all `autoDeployTrigger` quoted `"off"`, no previews initially (Pro-gated = owner billing decision); **B-003 CLOSED**; Vercel residuals cleaned repo-wide (CLAUDE.md principle 5, READMEs, .env.example headers, agent description, ADR-001/002/003 headers flipped to Accepted) |
| M1-T002 | **PLUTO SODA connector** (64uk-42ks) | **ACCEPTED** (G0/G1/G2/G3/G4/G5) — merged `4a3537a` + fixup; 101 tests; live-verified fixtures; BBL decimal normalization with raw preserved; typed error taxonomy incl. schema-drift signature; stdlib-only runtime; CI + secret-scan green on `69b5509`. G5 F1–F4 (Low) hardening folded into M1-T005 |
| M1-T003 | GIS Zoning Features + ZTLDB research | **ACCEPTED** (G0/G1/G3) — 2 products, 3 registry records; cap-exceedance paging hazard; ZTLDB `degraded_suspected` (3.4-month Socrata stall); ZD1 open enum (Queens ZR sections); 7 connector carry-forwards recorded |
| M1-T004 | Zoning Resolution text research | **ACCEPTED** (G0/G1/G3 — G3 zero defects) — server-rendered Drupal portal, no API anywhere (tier-4 HTML ceiling); 10 dated snapshots = only history; City of Yes = N 240290 ZRY adopted 2024-12-05 (three official channels); amendment-history AJAX endpoint = OPTIONAL ENRICHMENT ONLY (owner directive); G1 original return preserved verbatim per owner audit; 9 M3 carry-forwards in the G3 report §9 |
| M1-T005 | Property-profile API v1 (`GET /api/v1/properties/{bbl}`) | **ACCEPTED** (G0/G2/G3/G5/G4) — merged `ae44554`, 142 tests, CI+scan green; M1-T002 G5 F1–F4 hardening CLOSED; D1 (500-contract escape) fixed pre-merge. **Binding follow-ups:** contract v1.1 MANDATORY before Priority 4 consumes additive keys; INTERNAL/DEV until B-001 auth; missing_inputs filter policy; N2 healthCheckPath mismatch |
| — | GDS requirements (root) | `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md` integrated at root design level (CLAUDE.md read list + IMPLEMENTATION_SEQUENCE note); Section 15 integration plan **DRAFT FOR OWNER REVIEW** at `docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md`; no GDS tasks contracted |

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

### Accepted (M1)
| Task | Title | Producer | Gates passed |
|---|---|---|---|
| M1-T001 | PLUTO/MapPLUTO official-source research | official-source-researcher | G0, G1 (live re-verification), G3 (live SODA spot-tests) — corrections C1-C6 + D1-D3 applied; accepted 2026-07-16. Only OQ-4/OQ-10 residuals (nyc.gov-403-bound file URLs) and OQ-6 observation window open — carried into the connector packets. |

### In progress
| Task | State |
|---|---|
| (none) | Next up: M0-T005-R1, M0-T011/ADR-004, PLUTO SODA connector packet, M1 research fan-out |

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
