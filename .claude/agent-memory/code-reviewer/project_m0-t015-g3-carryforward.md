---
name: m0-t015-g3-carryforward
description: M0-T015 deploy-reconciliation G3 PASS (2026-07-17); interpreter-pin gap + .env.example drift; CORS/header baseline facts for future deploy/G5 reviews
metadata:
  type: project
---

M0-T015 G3 (2026-07-17, target 93a17d2 = merge of task a6f4f52 + hardened main 7abfac5) returned **PASS** with corrections. Verified facts: render.yaml has only nycdf-api + nycdf-web; worker/cron blocks removed with restoration duty bound to the delivering tasks (prior blocks in git history at d61c9b6); healthCheckPath /api/v1/health everywhere; `pip install -r requirements.txt` with pins fastapi==0.128.0 / starlette==0.46.2 / uvicorn==0.40.0 (coherent with pyproject ranges; fastapi 0.128.0 wants starlette<0.51,>=0.40); CORS exact-origin allowlist from `API_CORS_ALLOWED_ORIGINS` with wildcard→startup RuntimeError, deny-all default; D8 resolved as NEXT_PUBLIC_API_BASE_URL env var (not proxy), consumed at apps/web/src/lib/api.ts:101.

Carry-forwards to re-check at B-002 provisioning / first Blueprint sync (add to [[m0-t006-g3-carryforward]] items):
1. **No interpreter pin**: render.yaml sets no PYTHON_VERSION (nycdf-api) or NODE_VERSION (nycdf-web); no .python-version file; pyproject `requires-python >=3.12` is NOT enforced by the requirements.txt build path. Render default interpreter drifts — pin before provisioning.
2. Producer report M0-T015 said "13 tests / 143 pre-existing"; actual = 14 cases in test_security_middleware.py, 142 pre-existing, 156 total (parametrize counting). Totals correct.
3. Cron restoration note names PRD 14.1 but no milestone ID (worker names M1) — confirm the source-monitor cron restoration gets attached to a ledger task.
4. Worktree had an UNCOMMITTED apps/web/.env.example comment addition contradicting the report's "NO CHANGE NEEDED" — orchestrator was told to commit-or-discard deliberately before merge; verify at G4/G5 which way it went.

**Why:** deploy config is now the reconciled truth source; the next reviewer of any deploy/provisioning task should not re-derive these facts.
**How to apply:** at B-002 provisioning, D5 deploy-workflow, M1 job-system (worker block restoration), or M0-T007/T008 auth exposure reviews, check items 1–4 first; auth absence + no-public-exposure statements live in main.py docstring, render.yaml header, runbook note 1.
