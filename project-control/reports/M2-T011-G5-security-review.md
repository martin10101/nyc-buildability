<!-- Preserved VERBATIM by the orchestrator from the security-reviewer G5 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

# G5 SECURITY & PRIVACY GATE REPORT — M2-T011

**Task:** Shared connector transport/retry consolidation + source access registry
**Reviewer:** security-reviewer (independent; did not implement)
**Scope reviewed (on-disk main state):** `services/api/app/resilience/transport.py`, the four connectors' header/token/retry wrappers, `docs/SOURCE_ACCESS_REGISTRY.md`
**Method:** read shared module + connectors; diffed the M2-T011 implementation commit (85cea98) to confirm verbatim move; ran resilience + connector test suites.

## VERDICT: PASS

No BLOCKING, LOW, or new-exposure findings. All G5-accepted hardening moved verbatim; no new external call, dependency, or log exposure introduced.

## Evidence per required point

1. **Bounded body read — PRESERVED.** `MAX_RESPONSE_BYTES = 10*1024*1024` (transport.py:62); `_bounded_read` reads `read(cap+1)` and raises `TransportFailure` when over-cap instead of unbounded `.read()` (transport.py:140-148). Used on both success and `HTTPError` paths (transport.py:174, 183). Diff confirms this block was *removed* from pluto_soda and now imported. No unbounded `.read()` remains in the transport path.

2. **Redirects refused (X-App-Token exfil defense) — PRESERVED.** `NoRedirectHandler.redirect_request` returns `None` (transport.py:117-118); `DEFAULT_OPENER = build_opener(NoRedirectHandler)` (transport.py:123) is the opener used by `urllib_transport` (transport.py:168-171). Rationale documented intact (transport.py:108-116). pluto_soda retains `_OPENER`/`_NoRedirectHandler` aliases as the accepted monkeypatch seam and passes its own `_OPENER` at call time (pluto_soda.py:344-355). The three other connectors bind the shared `urllib_transport` (same no-redirect opener). Refused 3xx surfaces as a non-retried unexpected status.

3. **Retry-After / errorCode / network-reason sanitization — PRESERVED.** Retry-After allowlist `_RETRY_AFTER_SAFE_RE` + `sanitize_retry_after` repr()-fallback (transport.py:69, 216-221), applied before the value enters `last_detail` (transport.py:482-484). Network-failure reason flows through per-connector `sanitize_network_reason` hook (`_safe_text` for ArcGIS connectors, identity for pluto per accepted M1-T002; transport.py:463-468). errorCode sanitization (G5 F4, `_sanitize_error_code`) correctly stays *in* the SODA connectors (pluto_soda.py:436-445; ztldb same) — connector-specific classification, not shared-module concern. No attacker-controlled header/body value reaches a log line or exception unsanitized.

4. **App-token / secret secrecy — PRESERVED.** `_build_headers` sets `X-App-Token` only when `app_token` is configured (pluto_soda.py:410-416; ztldb_soda.py:529-535); token value is never logged — logs emit only `token_configured=%s ... bool(app_token)` (pluto_soda.py:640-641; ztldb_soda.py:1168-1169). The shared module treats `headers` as an opaque dict: its log statements (transport.py:459-496) interpolate only `log_label`, `url`, `attempt`, `correlation_id`, `status` — never headers or body. `grep -i token|header|authorization|body` on transport.py shows no token/header value in any log/exception. The two ArcGIS connectors are keyless (`{"Accept": "application/json"}` only).

5. **No new external call / SSRF surface — NOT WEAKENED.** The shared module never constructs URLs; it receives a fully-built URL and hardcodes `method="GET"` (transport.py:169). Endpoint allowlisting (pinned host constants, layer allowlist, field/value character allowlists, bounds checks) remains entirely in the connectors and executes BEFORE network I/O (zoning_features_arcgis.py:390-565; ztldb build_*_url bounds checks). No new endpoints, no caller-controlled host/method/scheme.

6. **`docs/SOURCE_ACCESS_REGISTRY.md` — CLEAN.** No secret/token values (only the `X-App-Token`/`SOCRATA_APP_TOKEN` mechanism described as optional config, "never logged"). "Scrape"/"evasion" appear only as **prohibitions** (governance rules forbidding ZoLa scraping and evasion), never as bypass/CAPTCHA-circumvention instructions.

7. **Dependency / logging sanity — CLEAN.** No dependency change in this commit (requirements.txt/pyproject.toml untouched); `transport.py` imports stdlib (`logging`, `re`, `urllib`, `dataclasses`, `typing`, `collections.abc`) + one internal `app.resilience.budget`. No sensitive data in any new log statement.

## Tests run (read-only)
- `python -m pytest tests/resilience -q` → **76 passed**
- `python -m pytest tests/resilience/test_transport_shared.py tests/connectors -q` → **347 passed**

## Observations (non-blocking, for orchestrator record)
- **OBS-1 (hash mismatch):** the tasking says M2-T011 "merged at 555d68a," but that hash is the **M2-T010** merge (PR #51). M2-T011 actually merged at **6dfac68** (impl **85cea98**). Working tree on `main` correctly reflects the merged M2-T011 state, so the review stands — recording the correct hash for the ledger.
- **OBS-2:** Producer-disclosed micro-behaviors (L2 in the report — log `%s`-format vs literal prefix, defensive `get_retry_after`, shared header dict identity, class `__module__` change) are behaviorally inert and carry no security impact; rendered log messages and logger names are byte-identical, no token/header value exposed. Confirmed independently.

Relevant paths: `services/api/app/resilience/transport.py`; `services/api/app/connectors/{pluto_soda,ztldb_soda,zoning_features_arcgis,mappluto_geometry_arcgis}.py`; `docs/SOURCE_ACCESS_REGISTRY.md`.

**RECOMMENDED GATE RESULT: PASS** — orchestrator to record (I did not run the ledger CLI, per ADR-005).
