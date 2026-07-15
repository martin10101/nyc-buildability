# Implementation Status

Authoritative detail lives in `project-control/` (run `python tools/project_control.py status`). This file is the human-readable summary. Updated: 2026-07-14.

## Milestone: M0 — Engineering control plane and cloud foundation (ACTIVE)

### Accepted
| Task | Title | Producer | Gates passed |
|---|---|---|---|
| M0-T000 | Control-plane lifecycle verification | progress-auditor | G0, G3 (incl. intentional FAIL/rework path) |
| M0-T001 | Repository and control-system audit | progress-auditor | G0, G3 |
| M0-T003 | Independent review of bootstrap plan | cloud-architect | G0, G3 |

### In review
| Task | Title | Producer | Waiting on |
|---|---|---|---|
| M0-T004 | Monorepo skeleton + GitHub Actions CI (G0/G2/G3 PASS; CI green incl. S4 fail/revert proof) | backend-engineer | G5 security review, then merge + G4 |
| M0-T006 | ADR-001/002/003 + render.yaml + rollback runbook (committed on main) | cloud-architect | G3 review |

M0-T002 was accepted 2026-07-14 after G1 (data-contract-verifier) + G3. See docs/SESSION_HANDOFF.md for the exact resume queue.

### Ready / next
See `docs/MASTER_EXECUTION_PLAN.md` — M0-T004 (monorepo skeleton + CI) is the next unblocked implementation task.

### Blocked (human actions — see docs/HUMAN_ACTIONS_REQUIRED.md)
- B-001 SUPABASE_ACCESS_TOKEN → Supabase migrations/RLS/storage work
- B-002 RENDER_API_KEY → service deployment (Blueprint authoring NOT blocked)
- B-003 Vercel → frontend deployment (frontend build/CI NOT blocked)
- B-004 GEOCLIENT_SUBSCRIPTION_KEY → live fixtures (connector scaffolding NOT blocked)

## Infrastructure facts
- Repo: private `martin10101/nyc-buildability`, branch `main`, initial commit `8ba7278` pushed.
- Control plane: verified end-to-end; defects found in bootstrap were fixed (BOM tolerance, state sync, gate history).
- Local footprint: ~0.2 MB; ~6 GB free on owner PC; 4 GB floor enforced.
- No application code exists yet — M0 foundation tasks are next.

## Defects found and fixed during bootstrap
1. `project_control.py` crashed on UTF-8 BOM JSON (found by lifecycle test) → `utf-8-sig`.
2. `state.json` rosters never updated by CLI (found by progress-auditor + cloud-architect independently) → `sync_state()` on every transition.
3. Gate records overwrote history, erasing the FAIL trail (found by progress-auditor) → history array preserved.
4. Credential blockers were narrative-only (found by cloud-architect) → B-001..B-004 formal records.
