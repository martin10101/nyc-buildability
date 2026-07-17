# M0-T015 Producer Report — Deployment reconciliation preflight (Render blueprint blockers)

- **Task ID:** M0-T015
- **Producer:** cloud-architect
- **Requested status:** `awaiting_gate`
- **Date:** 2026-07-17
- **Base:** worktree from `d61c9b6` (verified: `git log --oneline -3` shows d61c9b6 head)
- **Runbook confirmed at G0:** the M0-T006 deployment runbook is `docs/DEPLOYMENT_AND_ROLLBACK.md` (its own header cites ADR-003/ADR-002 and the render.yaml header points at it: "Operator steps: docs/DEPLOYMENT_AND_ROLLBACK.md").

## 1. Files changed

| File | Change |
|---|---|
| `render.yaml` | Health path → `/api/v1/health`; `[PLACEHOLDER]` markers reconciled; worker + cron service blocks REMOVED with tracked restoration note; `API_CORS_ALLOWED_ORIGINS` added to nycdf-api envVars (name only); `NEXT_PUBLIC_API_BASE_URL` added to nycdf-web envVars (name only) with D8 decision comment; header block updated with reconciliation + no-auth status |
| `services/api/requirements.txt` | NEW — pinned deployment set (fastapi==0.128.0, starlette==0.46.2, uvicorn[standard]==0.40.0) with decision rationale in header |
| `services/api/app/main.py` | `create_app()` factory; CORS exact-origin allowlist middleware read from `API_CORS_ALLOWED_ORIGINS` (wildcard → startup RuntimeError); security-header middleware (nosniff, X-Frame-Options DENY, Referrer-Policy no-referrer, CSP default-src 'none' with /docs//redoc exemption, HSTS, Cache-Control no-store); honest no-auth docstring; module-level `app` preserved for uvicorn + existing tests |
| `services/api/tests/test_security_middleware.py` | NEW — 13 tests covering S4 (see section 3) |
| `docs/DEPLOYMENT_AND_ROLLBACK.md` | M0-T015 reconciliation note block before §0 (no-auth exposure prohibition, health path, worker/cron removal, pin set, CORS/env-var wiring); `/health` → `/api/v1/health` in §1.1(4), §1.2(5), §2.2(3); worker/cron "not in Blueprint yet" annotations in §2.2/§2.3 |
| `apps/web/.env.example` | NO CHANGE NEEDED — already carries `NEXT_PUBLIC_API_BASE_URL=` name-only with the security boundary comment (added by M2-T001). Verified names-only. |
| `project-control/reports/M0-T015-producer-report.md` | this report |

`git status --short` in the worktree shows exactly: `M docs/DEPLOYMENT_AND_ROLLBACK.md`, `M render.yaml`, `M services/api/app/main.py`, `?? services/api/requirements.txt`, `?? services/api/tests/test_security_middleware.py` (+ this report). All within `allowed_paths`; no forbidden path touched (`app/api/`, `app/connectors/`, `app/profile/`, `packages/contracts/**`, `apps/web/**` beyond .env.example, `.github/**`, `.claude/**` untouched).

## 2. Decisions recorded (owner blocker bullets)

1. **requirements.txt vs pyproject (bullet 1):** KEEP `pip install -r requirements.txt` in render.yaml and CREATE `services/api/requirements.txt` as a pinned deployment set. Rationale: pyproject ranges (`fastapi>=0.115,<1`) are correct for development but non-deterministic across Render rebuilds; pins keep deploys and rebuild-after-rollback reproducible (ADR-003). pyproject stays the source of truth for ranges; pins verified inside those ranges; dev deps (pytest/ruff/httpx/jsonschema) are never installed on Render. Pin coherence verified: fastapi 0.128.0 requires `starlette<0.51.0,>=0.40.0` → 0.46.2 OK (importlib.metadata output captured in section 4).
2. **Health path (bullet 2):** `healthCheckPath: /api/v1/health` in the blueprint; runbook updated in all three verification steps. The live route is proven by tests (`/health` → 404 regression kept).
3. **Web↔API wiring (bullet 3, resolves M2-T001 D8):** env var `NEXT_PUBLIC_API_BASE_URL` on nycdf-web + exact-origin CORS allowlist on nycdf-api — NOT a same-origin proxy. Rationale: (a) apps/web already consumes `NEXT_PUBLIC_API_BASE_URL` with a local default (M2-T001); (b) a proxy adds a second hop and a moving part with no security gain — the value is a publishable URL, no credential is hidden by proxying; (c) a proxy implementation would require `apps/web` code changes, which are forbidden to this task (parallel-task exclusivity), so it could not be implemented honestly here anyway. Decision + rationale recorded in render.yaml comments and the runbook so M2-T002 does not hardcode assumptions.
4. **Phantom entrypoints (bullet 4):** `app/workers/job_runner` and `app/jobs/source_monitor` verified ABSENT from `services/api/app/` (contains only `__init__.py`, `api/`, `connectors/`, `profile/`, `main.py`). Both service blocks REMOVED from render.yaml with a tracked restoration note: worker returns with the M1 job-system work (PRD §22), cron returns with scheduled source monitoring (PRD 14.1); the delivering task must restore the block in the same change; prior content preserved in git history at `d61c9b6`. No phantom entrypoints remain (scripted proof, section 4).
5. **Security baseline (bullet 5):** CORS exact-origin allowlist from env var `API_CORS_ALLOWED_ORIGINS` (documented name; comma-separated origins; unset/empty = deny all cross-origin — safe default). Wildcard + credentialed requests made IMPOSSIBLE by startup rejection (explicit negative tests, 4 wildcard forms). Security headers on every response (incl. 404s); CSP-only exemption for `/docs`/`/redoc` so interactive docs keep working (all other headers still applied there). Honest no-auth documentation in main.py docstring, render.yaml header, and runbook: M0-T007/T008 blocked on B-001 → no public exposure until auth lands (M1-T005 G5 condition).

## 3. Acceptance scenarios and results

| Scenario | Result | Evidence |
|---|---|---|
| S1 blueprint truth | PASS | Scripted check (section 4.3): every rootDir/buildCommand/startCommand/npm script/ASGI attribute/healthCheckPath resolves; no `[PLACEHOLDER]`, `app.workers`, `app.jobs` outside comments. Services remaining: nycdf-api, nycdf-web |
| S2 health alignment | PASS | `healthCheckPath: /api/v1/health` (render.yaml:101); runbook grep shows zero stale `/health` paths (only the render.com/docs/health-checks citation URL matches); tests prove route live and `/health` 404 |
| S3 wiring | PASS | `NEXT_PUBLIC_API_BASE_URL` declared on nycdf-web (name only, `sync: false`); decision + rationale in render.yaml + runbook note 5; `apps/web/.env.example` verified names-only (pre-existing entry, no values) |
| S4 CORS/headers | PASS | 13 pytest tests: configured origin allowed (simple + preflight, credentials header echoed), disallowed origin no grant + preflight 400, wildcard×4 forms → RuntimeError at create_app (negative test), unset/empty env = deny-all, headers on 200/404, /docs CSP exemption, health contract regression. Full suite 156 passed |
| S5 honesty/secrets | PASS | No-auth statements in main.py, render.yaml header, runbook note 1; secret scan over all changed files green (section 4.4); every new envVar is `sync: false`, names only |
| S6 no provisioning | PASS | Zero Render account/API interaction of any kind this task (no network calls made at all); B-002 untouched |
| S7 G5 review | PENDING | For security-reviewer at gate — this report is the input |

## 4. Commands run (exact) and outputs

Working dir: `.claude\worktrees\agent-a12d75b959d17307d` (base d61c9b6). Local tool versions: Python 3.11.9, fastapi 0.128.0, uvicorn 0.40.0, starlette 0.46.2, pytest 8.4.2, ruff 0.9.9.

### 4.1 Ruff (expected: clean; actual: clean)
```
$ cd services/api && python -m ruff check .
All checks passed!
RUFF EXIT: 0
```

### 4.2 Pytest (expected: all pass incl. 13 new; actual: 156 passed)
```
$ cd services/api && python -m pytest tests -q
156 passed in 7.61s
PYTEST EXIT: 0
```
(Pre-existing suite was 143; the 13 additions are `tests/test_security_middleware.py`.)

### 4.3 S1 scripted blueprint-truth check (expected: PASS; actual: PASS)
Inline Python (yaml.safe_load of render.yaml; per service: rootDir exists, requirements.txt exists where referenced, `uvicorn mod:attr` module file + attribute exist, `python -m` modules exist, npm scripts exist in package.json, python healthCheckPath is a literal route in app/main.py; plus repo-wide scan that `[PLACEHOLDER]`/`app.workers`/`app.jobs` appear only in comments):
```
services checked: ['nycdf-api', 'nycdf-web']
PASS: every buildCommand/startCommand/entrypoint/healthCheckPath resolves to real files/modules; no phantom entrypoints; no [PLACEHOLDER] markers outside comments
S1 EXIT: 0
```

### 4.4 Secret scan (expected: no matches; actual: none)
```
$ grep -nE "(sk-[A-Za-z0-9]{8,}|eyJ[A-Za-z0-9_-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN|postgres://|postgresql://[^ ]*:[^ ]*@)" \
    render.yaml services/api/requirements.txt services/api/app/main.py \
    services/api/tests/test_security_middleware.py docs/DEPLOYMENT_AND_ROLLBACK.md apps/web/.env.example
SECRET-SCAN EXIT: 1 (no matches = green)
```

### 4.5 Pin coherence (expected: starlette pin inside fastapi's range; actual: OK)
```
$ python -c "from importlib.metadata import requires; print([r for r in requires('fastapi') if 'starlette' in r])"
['starlette<0.51.0,>=0.40.0']
```

## 5. Assumptions and defaults

- The M0-T006 runbook file is `docs/DEPLOYMENT_AND_ROLLBACK.md` (confirmed via its header and the render.yaml pointer; no other deployment runbook exists under docs/).
- `allow_credentials=True` is configured now because Supabase auth (cookies/Authorization) is the contracted next step (M0-T007/T008); an exact-origin allowlist is required for that mode, which is precisely why wildcard rejection is enforced rather than assumed.
- Deny-all cross-origin when `API_CORS_ALLOWED_ORIGINS` is unset is safe for current local/CI use: the M2-T001 frontend dev flow calls the API from the browser at a different local origin only in dev setups where the operator can set the env var; CI/unit flows use TestClient (same-process) and are unaffected.
- Restoration duty for worker/cron blocks is carried as comments in render.yaml + runbook (this task cannot create ledger tasks; the orchestrator may want to attach the restoration duty to the M1 job-system task packet).

## 6. Known limitations

- Local Python is 3.11.9 while pyproject targets `>=3.12`; tests import `app` from the source tree (not an installed wheel), so the suite runs fine, but CI (3.12) remains the authoritative interpreter. No 3.12-only syntax was introduced.
- Pinned versions were verified against the local resolver, not a fresh `pip install -r requirements.txt` into a clean venv (low-storage policy: no new venv on the owner PC). CI/Render build is the authoritative install proof; the pin set is three packages inside declared ranges.
- The S1 check script is inline evidence (this report), not a committed tool — `tools/` is outside allowed_paths. G3 can re-run it from section 4.3's description.
- `Cache-Control: no-store` is applied globally via `setdefault`; a future caching decision can override per-route without touching the middleware.
- Starlette's 400 preflight rejection body is plain text ("Disallowed CORS origin") — acceptable for a preflight; not customized.

## 7. Security / provenance impact

- Positive: removes the wildcard-CORS-with-credentials class of misconfiguration structurally (startup failure, not runtime warning); adds baseline hardening headers; documents the no-auth exposure prohibition in every operator-facing artifact; removes phantom deploy entrypoints that would have failed or, worse, been filled by unreviewed code.
- No secrets introduced anywhere; all new env vars are `sync: false` names only.
- No provisioning occurred; B-002 unchanged; zero network calls.

## 8. Recommended next tasks

1. Attach the worker/cron blueprint-block restoration duty to the task packets that deliver `app/workers/job_runner` and `app/jobs/source_monitor`.
2. M2-T002 (Confirm screen) should consume `NEXT_PUBLIC_API_BASE_URL` as already wired and must not assume same-origin.
3. When M0-T007/T008 unblock (B-001), revisit `allow_headers`/`allow_methods` against the real auth flow and lift the exposure prohibition via M1-T005 G5.

## 9. Report path

`project-control/reports/M0-T015-producer-report.md`
