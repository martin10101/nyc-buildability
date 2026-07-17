<!-- Verbatim reviewer return (agent-return channel; agentId a12146ece603cc786, security-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. -->

# G5 Security & Privacy Gate Report — M0-T015 (Deployment reconciliation preflight)

- **Gate:** G5 (security and privacy)
- **Task:** M0-T015 — Deployment reconciliation preflight (Render blueprint blockers)
- **Producer:** cloud-architect | **Reviewer:** security-reviewer (independent; did not implement)
- **Review target:** branch `task/M0-T015-deploy-reconciliation` @ `93a17d2` (merge of branch work `a6f4f52` side with hardened main `7abfac5`), worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T015`
- **Diff scope verified:** `git diff <merge-base 7abfac5>..HEAD` touches exactly: `render.yaml`, `services/api/requirements.txt` (new), `services/api/app/main.py`, `services/api/tests/test_security_middleware.py` (new), `docs/DEPLOYMENT_AND_ROLLBACK.md`, `project-control/reports/M0-T015-producer-report.md`. Nothing else under `project-control/`, `.github/`, `.claude/`, `apps/web/` is changed in the reviewed commit. Read-only review; no ledger or git writes performed.
- **Date:** 2026-07-17

## 1. Charge table

| # | Charge | Evidence | Result |
|---|--------|----------|--------|
| 1a | Wildcard + credentials structurally impossible | `services/api/app/main.py:60-76` (`_parse_allowed_origins` raises `RuntimeError` on any `*` entry) called at `main.py:81` inside `create_app()`, which executes at **module import** via `main.py:125` (`app = create_app()`). Probe A: `import app.main` with `API_CORS_ALLOWED_ORIGINS="https://ok.example, *"` → `RuntimeError` traceback from line 71; uvicorn cannot boot, health check fails. Not a test-only assertion. | PASS |
| 1b | `allow_credentials` semantics | `main.py:95-101`: `allow_credentials=True` with an exact-origin list; Starlette 0.46.2 echoes only the matched allowlist entry as `Access-Control-Allow-Origin` (never `*`), `Vary: Origin` present (probe I2). `allow_methods`/`allow_headers` are enumerated (no `["*"]` anywhere). | PASS |
| 1c | Unset env = deny-all | `main.py:68` (empty/unset parses to `[]`); probes + tests `test_unset_env_means_no_cross_origin_access` / `test_empty_env...` (`test_security_middleware.py:110-121`): no ACAO grant emitted. | PASS |
| 1d | Bypass attempts | See section 2 — all fail closed except one deliberate-misconfiguration residual (D1, LOW). | PASS with residual D1 |
| 2 | Env-configurable origins, names-only | Env var name `API_CORS_ALLOWED_ORIGINS` documented at `main.py:35-38`, `render.yaml:121-128` (`sync: false`, name only, no value), `docs/DEPLOYMENT_AND_ROLLBACK.md` reconciliation note 5. No origin values committed anywhere (grep across worktree: 5 files, all name/comment references). Gap: `services/api/.env.example` (the service's own var inventory) lacks the entry — that path was outside `allowed_paths`, see D2. | PASS with follow-up D2 |
| 3 | Security headers correctness + CSP exemption scope + HSTS | `main.py:44-57,103-113`. Set is correct for a JSON API (nosniff, XFO DENY, no-referrer, CSP `default-src 'none'; frame-ancestors 'none'`, HSTS 2y, no-store). CSP exemption is **exact-path** `{"/docs","/redoc"}` — probed: `/docsx`, `/openapi.json`, `/docs/oauth2-redirect` all carry CSP; `/docs/` reaches the exempt page only via redirect to `/docs`. Headers stamp preflight responses too (verified live: OPTIONS carries all six). HSTS on a not-yet-TLS internal deploy: harmless — browsers ignore HSTS received over non-secure transport, and every Render deployment is TLS-fronted at the edge; `includeSubDomains` is scoped to the service's own hostname (no subdomains) — revisit only if a custom apex domain later fronts the API. | PASS |
| 4 | No-auth honesty / no false protection claims | `main.py:6-11` (docstring: "authentication is NOT enabled… must NOT be publicly exposed until… M0-T007/T008… blocked on B-001"), `main.py:86-89` (OpenAPI description repeats it), `render.yaml:27-30` (AUTH STATUS block), runbook note 1. CORS baseline is explicitly framed as "a prerequisite… NOT a substitute for authentication" (`main.py:9-11`). No protection is claimed that does not exist. | PASS |
| 5 | Supply chain: pins inside pyproject ranges, new deps, no install scripts | `requirements.txt:23-25`: fastapi==0.128.0 ∈ `>=0.115,<1`; uvicorn[standard]==0.40.0 ∈ `>=0.30,<1` (`pyproject.toml:11-14`). starlette==0.46.2 is the only **new explicit pin** — it is not a new package (transitive dep of FastAPI); I independently verified fastapi 0.128.0 requires `starlette<0.51.0,>=0.40.0` → 0.46.2 satisfies; pin rationale documented in the file header. No URL/VCS requirements, no pip options, no install scripts. Dev/test tools stay out of the deploy set. | PASS |
| 6 | Secrets | `python .github/scripts/secret_scan.py` in the worktree: **exit 0**, "PASS — no findings" (549 files). All new render.yaml env vars are `sync: false` name-only (`render.yaml:107-128, 201-214`); both `.env.example` files names-only; runbook contains no credentials. | PASS |
| 7 | No provisioning | Diff is declarative config/code/docs only; producer report section 6 states zero network calls; no Render API artifacts anywhere in the diff. `project-control/blockers/` untouched on the branch (branch diff under `project-control/` = producer report only; B-002 last modified by unrelated commit `11f9d2c`). | PASS |
| 8 | Run middleware suite; coverage judgment | `pytest tests/test_security_middleware.py -q` → **14 passed, exit 0** (report says 13 — see D4). Full suite `pytest tests -q` → **156 passed, exit 0**. Coverage judgment: the suite covers wildcard×4 forms, allowed/disallowed simple+preflight, unset/empty deny-all, headers on 200/404, CSP exemption, health regression. Gaps vs my charge-1 vectors: no null-origin, case-variant, host-suffix/prefix, port-variant, or malformed-config-entry tests (see D5 — I probed all manually, all fail closed). | PASS with gap note D5 |

## 2. Bypass attempts and outcomes

All probes run live against `create_app()` in the worktree (Starlette 0.46.2, the pinned deploy version):

| Probe | Config | Attack origin | Outcome |
|---|---|---|---|
| A | env = `"https://ok.example, *"` | — | **Import-time RuntimeError** (twice confirmed: controlled probe + accidental re-import). Wildcard cannot reach a running app. |
| B | exact origin configured | `Origin: null` | No grant (fail closed) |
| C | exact origin configured | `https://NYCDF-WEB.onrender.com` (case) | No grant — match is exact/case-sensitive; browsers send normalized lowercase origins, so legit config works, miscased config fails closed |
| D | config has trailing slash `.../` | real origin without slash | No grant (fail closed; operator must fix — deploy visibly broken, not silently open) |
| E | config = literal `null` | `Origin: null` | **Grants `ACAO: null` + credentials** — see D1 (LOW) |
| F | scheme-less config `host.com` | `https://host.com` | No grant (fail closed) |
| G | exact origin configured | `...onrender.com:443` (explicit port) | No grant (fail closed; correct — browser origin string omits default port) |
| H | exact origin configured | `https://<allowed-host>.evil.com` and `https://evil<allowed-host>` | No grant (exact string match, no regex/substring path — `allow_origin_regex` is not used) |
| I | exact origin configured | disallowed preflight | 400, no grant, no credential header |
| J | any | CSP-exemption scope | Exempt only at exactly `/docs`, `/redoc`; `/openapi.json`, `/docs/oauth2-redirect`, `/docsx` (404) all carry the deny-all CSP; all other headers (incl. HSTS, nosniff) present on exempt pages and on preflights |

Comma-in-origin and whitespace tricks are neutralized by the split/strip/drop-empty parse (`main.py:68`); an entry containing `*` anywhere is rejected before the middleware ever sees it.

## 3. Defects

No critical, high, or medium findings. No contract-breaking or architectural findings — the wiring decision (cross-origin `NEXT_PUBLIC_API_BASE_URL` + exact-origin allowlist, no proxy) is sound: no credential is hidden by proxying, and the decision is recorded for M2-T002.

| ID | Severity | Blocking | Finding | Reproduction | Remediation |
|---|---|---|---|---|---|
| D1 | LOW | No | A literal `null` entry in `API_CORS_ALLOWED_ORIGINS` is not rejected at startup and yields `Access-Control-Allow-Origin: null` with `allow-credentials: true`. `null` is a spoofable origin (sandboxed iframes, `data:`/`file:` contexts), so this would defeat the allowlist — but only via deliberate operator misconfiguration contrary to the documented `scheme://host[:port]` format; every other malformed entry fails closed. | `API_CORS_ALLOWED_ORIGINS=null`, then `GET /api/v1/health` with `Origin: null` → grant echoed (probe E). | When `main.py` is next touched: extend `_parse_allowed_origins` to reject any entry not matching `^https?://` (this also catches `null`, scheme-less, and trailing-garbage entries at startup instead of silently failing closed). Not required for this gate. |
| D2 | LOW | No | `services/api/.env.example` self-describes as the inventory of "variables the FastAPI service… read[s]" but lacks `API_CORS_ALLOWED_ORIGINS`; `docs/SECRETS_POLICY.md` inventory likewise not updated. Cause: both paths were outside M0-T015 `allowed_paths` — the producer could not add them honestly. | Read `services/api/.env.example:1-44` — no CORS entry; `main.py:38` reads it. | Orchestrator: attach a one-line follow-up (names-only entry + SECRETS_POLICY inventory row) to the next task allowed to touch those files. |
| D3 | LOW | No (must be resolved before merge) | The review worktree carries an **uncommitted** modification to `apps/web/.env.example` (comment-only, names-only, referencing M0-T015/D8) that is NOT in reviewed commit `93a17d2`, while the producer report line 19 states "NO CHANGE NEEDED" for that file. Content is benign (verified: no values), but the dirty state is an evidence-hygiene defect and this PASS applies to `93a17d2` only. | `git status --short` in the worktree → `M apps/web/.env.example`; `git diff -- apps/web/.env.example` shows a 5-line comment addition. | Orchestrator: either commit the comment (path is in `allowed_paths`, names-only) as part of the task branch with the report table corrected, or discard it. Do not merge a dirty worktree. |
| D4 | INFO | No | Producer report says "13 tests"; the file collects **14** (10 functions, one 4-way parametrize). Arithmetic in report section 4.2 (143+13=156) is internally consistent only if the pre-existing count was 142. Evidence quality nit; all tests pass either way. | `pytest tests/test_security_middleware.py --collect-only -q` → "14 tests collected". | Correct the count in the report when the orchestrator saves gate artifacts. |
| D5 | INFO | No | Test-coverage gap for charge-1 adversarial vectors: null origin, case variant, port variant, host suffix/prefix tricks, malformed config entries are untested. I probed all manually — every one fails closed on Starlette 0.46.2 — but the pinned-version behavior is currently guaranteed by the pin, not by regression tests. | Section 2 probes B–H. | Add these as parametrized negative tests when the middleware is next touched (pairs naturally with D1's remediation). |

## 4. Judgment on the overall posture

The wildcard+credentials class is eliminated structurally (startup crash before bind, health-check fail — misconfiguration is loud, not silent). Deny-all default is correct for the current no-auth, no-exposure state. The no-auth prohibition is stated in every operator-facing artifact and the baseline is honestly framed as a prerequisite, not protection. Supply-chain surface added is minimal (three pins inside declared ranges). Phantom worker/cron entrypoints — a real "unreviewed code fills a deployed slot" risk — are removed with a tracked restoration duty. No provisioning occurred; B-002 remains owner-gated. Residuals are LOW, documented above, and none blocks acceptance.

## 5. Commands run (exact, all in the worktree)

```
pytest tests/test_security_middleware.py -q        → 14 passed, exit 0
pytest tests -q                                    → 156 passed, exit 0
python .github/scripts/secret_scan.py              → PASS, no findings, exit 0
python -c "importlib.metadata: fastapi 0.128.0 / starlette 0.46.2 / uvicorn 0.40.0; fastapi requires ['starlette<0.51.0,>=0.40.0']"
python <probe scripts, sections 2/J>               → outputs quoted above
git diff <merge-base>..HEAD --stat / --name-only   → 6 files, no forbidden paths
```

## 6. Verdict

Scenario S4: PASS. S5: PASS. S6: PASS. S7 (this review): PASS. Blocking conditions for the orchestrator before merge/acceptance: resolve D3 (commit or discard the dirty `apps/web/.env.example`); D1/D2/D5 are non-blocking follow-ups, D4 is a report correction.

PASS
