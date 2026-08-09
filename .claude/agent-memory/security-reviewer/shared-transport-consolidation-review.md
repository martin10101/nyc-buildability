---
name: shared-transport-consolidation-review
description: M2-T011 G5 method — verifying G5-accepted connector hardening moved verbatim into the shared app.resilience.transport module
metadata:
  type: project
---

M2-T011 moved the shared HTTP transport + bounded-retry loop for the four gov connectors
(pluto_soda, zoning_features_arcgis, ztldb_soda, mappluto_geometry_arcgis) into
`services/api/app/resilience/transport.py`. G5 focus was "did all prior hardening move
verbatim with no new exposure," not new-feature review.

**Why:** four connectors each carried G5-accepted primitives (M1-T002 F1 bounded read + F3
no-redirect; M1-T009 Retry-After sanitization; F4 errorCode sanitization). Consolidation
risk = a primitive silently dropped or weakened during the move.

**How to apply (probe set for re-reviews of this module):**
- Bounded read: `MAX_RESPONSE_BYTES = 10*1024*1024`, `_bounded_read` does `read(cap+1)` then
  raises `TransportFailure` if over — transport.py:140-148. Preserved.
- No-redirect: `NoRedirectHandler.redirect_request` returns `None`; `DEFAULT_OPENER =
  build_opener(NoRedirectHandler)` — transport.py:108-123. Rationale (X-App-Token exfil on
  cross-host redirect) is the load-bearing reason; confirm the opener path stays wired.
  pluto keeps `_OPENER`/`_NoRedirectHandler` aliases as the monkeypatch seam.
- Retry-After sanitize: `_RETRY_AFTER_SAFE_RE` allowlist + `sanitize_retry_after` repr()
  fallback — transport.py:69,216-221. errorCode sanitize (`_sanitize_error_code`, F4) stays
  IN the SODA connectors, not the shared module. Correct — connector-specific.
- Token secrecy: SODA `_build_headers` (pluto:410, ztldb:529) sets `X-App-Token` only when
  configured; logs emit `token_configured=bool(app_token)` only (pluto:640, ztldb:1168),
  never the value. Shared module treats headers as opaque — its log lines interpolate only
  log_label/url/attempt/correlation_id/status. The two ArcGIS connectors are keyless
  (headers = `{"Accept": "application/json"}`).
- SSRF/allowlist: URLs are built in the connectors from pinned constants + layer/field/value
  allowlists BEFORE I/O; shared module never constructs URLs and hardcodes `method="GET"`.
  Not weakened.
- Registry `docs/SOURCE_ACCESS_REGISTRY.md`: no secret values; "scrape/evasion" appear only
  as PROHIBITIONS (governance rules), not bypass instructions.
- No new dependency (requirements/pyproject untouched); transport.py imports stdlib +
  `app.resilience.budget` only.

**Note on commit hash:** orchestrator said "merged at 555d68a" but that is the M2-T010 merge;
M2-T011 actually merged at 6dfac68 (impl 85cea98). Working tree still reflects merged M2-T011
state, so review stands. Flag hash mismatches but review on-disk main state.

Tests: `tests/resilience` 76 passed; `tests/resilience/test_transport_shared.py`+`tests/connectors`
347 passed. Verdict PASS, no BLOCKING/LOW findings.
