# M1-T005 G5 — reviewer's return (verbatim preservation)

> Provenance: complete final return of the security-reviewer for M1-T005 G5, received 2026-07-16 via the agent-return channel; saved verbatim by the orchestrator (transport entity-decoding only) per the report-preservation rule in `.claude/rules/project-control.md`.

---

I have completed my independent verification. No scratch files were created (all probes ran via stdin heredocs). Per ADR-005 and the gate reporting protocol, I am read-only and return the full report content to the orchestrator rather than writing it.

---

# Gate Report — G5 (Security & Privacy)

- **Gate:** G5 — security and privacy
- **Task:** M1-T005 — Property-profile API v1: `GET /api/v1/properties/{bbl}` via pluto-soda connector
- **Reviewer:** security-reviewer (independent; did not produce this work)
- **Producer:** backend-engineer
- **Review location:** `.claude/worktrees/M1-T005`, branch `task/M1-T005-property-profile-api`, HEAD `555db54` — reviewed read-only
- **Date:** 2026-07-16
- **Result:** **PASS** (F1–F4 all CLOSED; 0 critical/high/medium; 2 informational notes). One G5 deployment condition applies (no-auth).
- **Method:** read task packet S1–S8, predecessor M1-T002 G5 report (F1–F5), then `properties.py`, `builder.py`, `bbl.py`, the `pluto_soda.py` hardening diff, `main.py`, `render.yaml`; producer report read last. Ran full suite (140 passed) plus my own adversarial TestClient + transport-level probes with a canary token in env. No implementation modified; no scratch files left.

---

## 1. F1–F4 closure verification (primary duty)

**F1 — bounded read: CLOSED.** `_bounded_read()` (`pluto_soda.py:290-298`) reads `MAX_RESPONSE_BYTES + 1` (10 MiB) and raises typed `TransportFailure` on oversize. Applied on **both** read paths: the 200 body (`urllib_transport` success branch) and the `HTTPError` body branch (`body = _bounded_read(exc)`). Refused 3xx redirects also arrive via the HTTPError path, so their body is bounded too. Probe results: oversize→TransportFailure; at-cap (exactly 10 MiB) passes; an **endless/chunked stream cannot bypass** — `stream.read(n)` respects the byte limit (verified with a stream that raises MemoryError on any unbounded read; it was capped instead).

**F2 — RecursionError / hostile JSON: CLOSED.** `RecursionError` is caught in **both** `json.loads` sites: `fetch_by_bbl` body parse (`:617`, → `SourceUnavailableError`) and `_classify_400` (`:378`, → `None`/unparseable). These are the **only two** `json.loads` calls in the module (grep-confirmed); `properties.py`/`builder.py` use `json.dumps` only. Probe: 200,000-deep `[` body → typed `SourceUnavailableError`, no raw stack escaped; 400 deep body → `None`, not mis-classified as drift.

**F3 — redirects: CLOSED.** `_NoRedirectHandler.redirect_request` returns `None` for **all** of 301/302/303/307/308 (probed each). Module-level `_OPENER = build_opener(_NoRedirectHandler)` is used on the request path (`_OPENER.open`); no stray `urllib.request.urlopen` call remains (grep-confirmed — only the `Request` constructor and docstring text). A 3xx becomes `HTTPError`→`TransportResponse(3xx)`→ typed `source_unavailable`, so **the X-App-Token never egresses to any redirect target**, same-host or cross-host.

**F4 — errorCode sanitization: CLOSED.** `_sanitize_error_code()` allowlist `^[A-Za-z0-9._-]{1,120}$` is correct: official dotted codes (`query.soql.no-such-column`) pass verbatim; CRLF, >120-char, `<script>`, and non-ASCII inputs are `repr()`-sanitized. Applied to **both** 400 branches (schema-drift and generic). No other untrusted response field enters `detail`/logs unsanitized: connector-built `detail` carries only `http_status` (int), `url` (digits-only constructed), and the sanitized `error_code`.

## 2. New API surface

- **Validate-first confirmed.** A spy fetcher that asserts on invocation proved **zero connector calls** for malformed inputs: `123`, `abcdefghij`, `12345678901`, `%2e%2e`, `1000010100%00` (null byte), `0000000000`, `6000010100`, a 5000-char string — all 422. A URL-encoded *valid* BBL (`%31%30...`) correctly decoded and reached the connector — expected, not a bypass.
- **Path traversal** `..%2f..%2fetc%2fpasswd` → routing 404, no connector call.
- **X-Correlation-ID.** The route always mints a fresh `uuid4().hex`; a client-supplied `X-Correlation-ID: injected\r\nSet-Cookie: evil` was **not reflected** (response carried a fresh hex). No inbound-header echo, no CRLF/header-injection vector.

## 3. Error hygiene end-to-end (canary token in env)

All error types map correctly and carry `X-Correlation-ID`: rate_limited→503, timeout→504, source_unavailable→503, schema_drift→502, unexpected→500 (generic body: `internal_error`, correlation id only). Across every path, canary token, `X-App-Token`, `Traceback`, and `File "` were **absent** from bodies, headers, and DEBUG logs. The 500 handler logs `type(exc).__name__` + correlation id only — no `str(exc)`/traceback. JSON escaping verified at the response layer: a raw `\r\n` renders as `\\r\\n` in the body bytes, so even control chars in `detail` cannot inject headers or log lines.

## 4. Log hygiene (F5)

Payload-only logging confirmed: connector errors log `json.dumps(payload)` (escapes control chars); unexpected errors log type + correlation id; validation errors log `code` + correlation id. No raw exception/response text is logged. BBL raw values are `repr()`-sanitized in `bbl.py:to_payload`.

## 5. No-auth condition (G5 CONDITION — must be tracked)

INTERNAL/DEV marking is present in `main.py` (app description + docstring) and `properties.py` (module docstring + OpenAPI). **Explicit condition:** this endpoint has no authentication/authorization/org-scoping and must NOT be publicly exposed or routed production traffic until auth lands (M0-T007/T008, B-001). `render.yaml` was **not modified** by this task (last touched by `8e6bdf4`/M0-T011; this commit's diff touches no `render.yaml` or `.github`), and all services carry `autoDeployTrigger: "off"` — nothing routes public traffic. Condition satisfied for merge; must remain enforced at deploy.

## 6. DoS / dependencies / fixtures

10 MiB cap is sane (~1.5 KB expected bodies). Retry amplification unchanged from M1-T002 (bounded; schema_drift never retried). Route is stateless — no per-request state growth. `pyproject.toml` unchanged (empty diff); runtime imports are stdlib + FastAPI only; `jsonschema` stays dev-only. New test file uses `secretscan:allow`-pragma'd fake tokens; fixtures were not modified (forbidden path).

## 7. Findings

**No critical, high, or medium findings.** Two informational notes:

- **N1 (Info).** The route passes `payload["detail"]` verbatim into the response body — it trusts the connector's F4 sanitization rather than re-sanitizing at the boundary. Non-exploitable today (connector sanitizes `error_code`; JSONResponse json-escapes control chars; all connector `detail` fields are safe by construction). If a future connector or error source populates `detail` with unsanitized untrusted strings, the route would forward them. Defense-in-depth suggestion for a later task: sanitize/allowlist `detail` keys at the API boundary. Not blocking.
- **N2 (Info, non-security).** `render.yaml` `healthCheckPath: /health`, but `main.py` exposes `/api/v1/health` (no `/health`). Deployment-correctness mismatch; `render.yaml` is a documented `[PLACEHOLDER]` and out of this task's scope. Flag for the deploy-reconciliation task. Not a security issue.

## 8. Verdict

**PASS.**

- F1 bounded read — **CLOSED** (both read paths capped; chunked/endless cannot bypass; at-cap passes).
- F2 RecursionError — **CLOSED** (caught in both `json.loads` sites; only two exist).
- F3 redirects — **CLOSED** (all 3xx refused; module `_OPENER` on every path; no stray urlopen; token never egresses).
- F4 errorCode sanitization — **CLOSED** (allowlist correct; both 400 branches; no other untrusted field unsanitized).
- **New findings:** N1 (info) route forwards connector `detail` verbatim, non-exploitable, harden later. N2 (info, non-security) render.yaml health-path mismatch, out of scope.
- **Canary/leak results:** token, `X-App-Token`, `Traceback`, `File "` absent from all bodies/headers/logs across 200/422/404/502/503/504/500; 500 handler generic; JSON escaping neutralizes control chars.
- **No-auth condition:** INTERNAL/DEV marked in code + OpenAPI; `render.yaml` unmodified with `autoDeployTrigger: "off"`; must not be publicly exposed until auth (M0-T007/T008, B-001) lands.
- **Blocks merge:** nothing. The no-auth condition must be recorded and enforced through deployment.
