---
name: no-shared-per-caller-route-rate-limiter
description: services/api has NO shared per-caller ROUTE rate limiter; the "rate_limited" states in lot_geometry/properties map UPSTREAM connector throttling, not caller QPS
metadata:
  type: project
---

When a route packet's spec says "per-caller rate limit — reuse the repo's existing
rate-limit mechanism (see app/api/v1/lot_geometry.py / properties.py)", there is in
fact NO reusable per-caller ROUTE limiter to reuse.

**What actually exists:** every `RateLimitedError` / `rate_limited` state in
`app/connectors/*`, `lot_geometry.py`, `properties.py`, `app/resilience/*` maps an
UPSTREAM source throttle (SODA/ArcGIS HTTP 429 → a 429/503 response state) after the
retry budget. None of them bound a CALLER's request rate.

**How to apply:** a route needing a genuine per-caller limit must build a minimal
stdlib limiter (monotonic fixed window or token bucket, `threading.Lock`, keyed by
`request.client.host`) INSIDE its own module — zero new dependencies (the policy
forbids a new package like slowapi). Make it injectable via a `get_rate_limiter()`
module hook (mirror the `get_max_envelope_registry()` pattern) so tests can inject a
tight or always-allow instance. Record it as a deviation in the producer report:
you are NOT reusing a shared mechanism because none exists. First done in
`app/api/v1/dxf_import_api.py` (M5-T108, PKT-F).

Related: the accepted UNMOUNTED-route boundary primitives ARE reusable — import
`MAX_BODY_BYTES`, `_read_body_within_ceiling`, `_declared_content_length`,
`_bounded_message` from `app/api/v1/proposal_validation.py` (the T053 bounded stream),
gate on `app.config.internal_rule_eval_enabled`, and copy the generic-404
`_not_found()` sentinel. See [[agent-supervisor-rotation-and-model-machinery]] for the
reuse-never-fork discipline.
