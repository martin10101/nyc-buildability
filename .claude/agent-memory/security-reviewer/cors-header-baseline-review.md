---
name: cors-header-baseline-review
description: G5 probe set and accepted residuals for the M0-T015 CORS/security-header baseline in services/api/app/main.py (revisit at M1-T005 exposure review)
metadata:
  type: project
---

M0-T015 baseline (services/api/app/main.py): exact-origin CORS allowlist from
`API_CORS_ALLOWED_ORIGINS`; wildcard entries raise RuntimeError inside
`_parse_allowed_origins` called at module import (`app = create_app()`), so a
wildcard deploy crashes before binding — structural, not test-only. Unset/empty
env = deny-all. Security-header middleware added after CORSMiddleware so it runs
outermost and stamps preflights; CSP exemption is exact-path {"/docs","/redoc"}.

**Why:** owner deployment-blocker directive (wildcard+credentials must be
impossible); this module is the pattern future services will copy.

**How to apply (re-review probe set):** import app.main with wildcard env set
(must traceback); probe Origin values null / case-variant / :443 port /
suffix+prefix host tricks / trailing-slash and scheme-less config entries — all
must yield no ACAO grant; probe /docsx, /openapi.json, /docs/oauth2-redirect for
CSP presence. Accepted residuals (LOW, in the M0-T015 G5 report): a literal
`null` allowlist entry is NOT rejected at startup and grants `ACAO: null` with
credentials (operator-misconfig class — recommend scheme validation when the
module is next touched); `API_CORS_ALLOWED_ORIGINS` absent from
services/api/.env.example (path was outside M0-T015 allowed_paths — follow-up
owed); header middleware uses setdefault so routes can override. Revisit
allow_methods/allow_headers and HSTS includeSubDomains if a custom apex domain
fronts the API (M1-T005 G5). See [[project-control-cli-hardening-review]] for
ledger-side method.
