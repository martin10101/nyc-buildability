---
name: zoning-features-connector-review
description: G5 probe set and accepted residuals for the M2-T007 ArcGIS zoning-features connector (layer allowlist, bounded where/paging, reused pluto transport)
metadata:
  type: project
---

M2-T007 baseline (services/api/app/connectors/zoning_features_arcgis.py): all
URLs originate from the pinned SERVICE_ROOT plus an exact-dict-key layer
allowlist (`_require_layer`, no normalization); where clauses only `1=1` or
`FIELD='value'` with per-layer queryable-field allowlist + value char
allowlist `[A-Za-z0-9 .,'()/&+-]{1,120}` + quote doubling; `_require_known_where`
re-validates any where by regex round-trip so accepted strings are exactly
builder-reproducible. outFields/orderBy validated against LAYER_SPECS;
resultRecordCount 1..2000, resultOffset 0..1000000, HARD_MAX_PAGES 200.
Transport is pluto_soda.urllib_transport reuse (10 MiB bounded read,
_NoRedirectHandler refuses all 3xx; 3xx never retried). Keyless, only Accept
header. Upstream text enters payloads/logs only via `_safe_text` /
`_safe_field_name` / `_sanitize_retry_after` (allowlist-or-repr).

**Why:** first ArcGIS outbound surface; packet safeguard 1 made SSRF refusal
the G5 focus; pattern for M2-T008/T009 connectors.

**How to apply (re-review probe set):** run the repl probes — layer values
`nyzd/../pluto`, `nyzd?`, `nyzd#frag`, ` nyzd`, `Nyzd`, bytes — all must raise
DisallowedRequestError pre-network; where probes `ZONEDIST='a'='a'`,
`1=1 OR 1=1`, percent/semicolon values must be refused; outFields
`["ZONEDIST&f=html"]` refused; `ZONEDIST=''' OR 1 --'` is ACCEPTED by design
(round-trips to a properly escaped literal, chars all allowlisted — not
injection). pytest -k "s11 or s5 or s12" offline. Accepted residuals (Low,
M2-T007 G5 report): (1) caller-supplied correlation_id is logged/emitted
unsanitized (internal callers only; same as pluto — bound it when wired to
HTTP); (2) worst-case extraction memory approx page_budget(<=200) x 10 MiB if
the pinned official host turns hostile (per-response cap only, no aggregate
cap); (3) build_fixture_pack.py capture() uses default urllib opener
(follows redirects, unbounded read) — static allowlisted URLs, producer-local
only, never CI. See [[hardened-client-review]] for the frontend pair matrix.
