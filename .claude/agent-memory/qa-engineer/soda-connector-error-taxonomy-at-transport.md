---
name: soda-connector-error-taxonomy-at-transport
description: SODA connectors (pluto/ztldb/dtm_condo) delegate retry/429/timeout to shared app.resilience.transport; per-connector suites often do NOT re-test those error paths
metadata:
  type: project
---

The accepted SODA connectors (`pluto_soda.py`, `ztldb_soda.py`, and the M5-T042
`dtm_condo_soda.py`) share the retry engine `app.resilience.transport.request_with_retry`
+ `standard_retry_hooks`, and each mirrors the same `_classify_400` +
`_raise_for_unexpected_status` wiring (400 `query.soql.no-such-column` -> SchemaDrift;
other 400 / status -> SourceUnavailable; 429/5xx/timeout -> RateLimited/Timeout/Unavailable
after a bounded retry budget).

**Why:** In the M5-T042 offline suite, the retry/429/timeout/400-drift/non-JSON-200
paths have NO per-connector regression test — the transport engine is tested in its own
suite and the connector only wires it. This is defensible when the packet explicitly
scopes tests (M5-T042 scoped to C1-C7/C9/C10 and deferred C11-C14 rate-limit/live-era),
but it means a connector-level logic error in `_raise_for_unexpected_status`,
`_fetch_rows` JSON/array guards, or `_collect_base_lots` drift raises would not be caught
by the connector's own tests.

**How to apply:** When gating a new SODA connector, check (a) whether the error-taxonomy
wiring is byte-identical to an already-accepted sibling (mirror = lower risk), and (b)
whether the fail-closed claims in its docstrings ("anything not a JSON array is schema
drift") have any regression test. Flag the untested drift-400 / non-JSON / non-array /
unit-empty branches as ADVISORY when the packet scoped them out; escalate to BLOCKING only
if the packet's own acceptance scenarios require them. Related:
[[modularity-sloc-counts-docstrings]].
