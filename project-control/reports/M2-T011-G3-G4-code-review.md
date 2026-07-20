<!-- Preserved VERBATIM by the orchestrator from the code-reviewer G3+G4 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

# M2-T011 G3 + G4 Gate Report — Shared transport/retry consolidation

**Task:** M2-T011 (extract duplicated transport+retry loop from four connectors into `services/api/app/resilience/transport.py` via a `RetryHooks` seam)
**Merged commit:** 555d68a
**Reviewer:** code-reviewer (independent; did not implement)
**Scope reviewed:** G3 (null-hypothesis behavior-unchanged) + G4 (integration/regression). NOT registry TC-S6 (G1/data-contract-verifier scope).

## VERDICT: **PASS**

## Commands + results (Windows, Python 3.11.9, pytest 8.4.2, ruff 0.9.9)

```
cd services/api
ruff check .                          -> All checks passed!
python -m pytest tests/ -q            -> 538 passed in 7.47s
python -m pytest tests/resilience/test_transport_shared.py -q -> 16 passed in 0.21s
grep -c "for attempt in range(1, max_attempts + 1)" app/connectors/* app/resilience/transport.py
  -> pluto_soda:0  zoning_features_arcgis:0  ztldb_soda:0  mappluto_geometry_arcgis:0  transport.py:1
python -c "from app.resilience import ResilientPlutoFetcher, build_default_resilient_fetcher, BudgetExceededError, CircuitOpenError"  -> OK
python -c "import app.resilience.fetcher; import app.main"  -> both import clean
```

Producer's claim of 522 unmodified + 16 new = 538 green independently reproduced. TC-S2, TC-S8 (local proxy) confirmed.

## Highest-risk item — lazy PEP 562 `__getattr__` (RESOLVED, not a defect)
The lazy shim in `app/resilience/__init__.py:60` breaks a genuine import cycle (fetcher→pluto_soda→transport). It **cannot hide a startup ImportError** because:
1. `app.resilience.fetcher` imports cleanly standalone (verified).
2. The real startup consumer `app/api/v1/properties.py:127` imports `build_default_resilient_fetcher` **directly** from `app.resilience.fetcher`, bypassing the shim — a genuine fetcher ImportError surfaces at first request build.
3. The shim only covers the convenience `from app.resilience import X` re-export path, which I confirmed still resolves all four names.

## Disclosed L2 micro-behaviors — explicit judgment (each NON-observable, no regression)
| # | Change | Judgment |
|---|--------|----------|
| L2.1 | `get_retry_after` non-mapping `.items()` guard | **Non-observable.** Defensive-only; reachable only by a hand-built `TransportResponse` with non-mapping headers — no caller/test exists. |
| L2.2 | Shared header dict reused across attempts vs fresh-per-attempt | **Non-observable.** Only visible to a transport that mutates its `headers` arg; none exists (`transport.py:456` passes the same dict; contract is read-only). |
| L2.3 | Log format `"%s timeout url=…"`+label arg vs literal prefix | **Non-observable.** Rendered `getMessage()` byte-identical (log_label = correct connector prefix); logger names unchanged. caplog tests (test_pluto_soda:410, test_ztldb_soda:1106) assert `token not in caplog.text` and pass. |
| L2.4 | `TransportResponse/Timeout/Failure.__module__` → `app.resilience.transport` | **Non-observable.** Single class identity everywhere (isinstance unchanged). Critically, `pluto_soda.urllib_transport.__module__` **stays** `app.connectors.pluto_soda` — verified live + guard test test_mappluto:1245 passes. |
| L2.5 | zf/ztldb/mappluto default transport binds shared `urllib_transport` | **Non-observable.** No test's monkeypatch of `pluto_soda._OPENER` ever affected those three; pluto path unchanged via compat wrapper reading `_OPENER` at call time. |
| L2.6 | Lazy exports dropped from `dir(app.resilience)` without access | **Non-observable** for functional callers; attribute access unchanged. |

## Test-quality assessment (16 new tests genuinely exercise shared path)
`tests/resilience/test_transport_shared.py` is not a shell: TC-S2 code-shape guards; TC-S3 budget-consumed-before-IO (`test_s3_budget_unit_consumed_before_every_attempt`, asserts `transport.calls==2`, `budget.consumed==2`), Retry-After honored exactly (`sleeps==[7.0]`, HTTP-date `[30.0]`), over-cap stop (1 attempt/0 sleeps), seed-replay jitter (`Random(7)` replay), legacy fixed-exponential (`[0.5,1.0]`); TC-S7 fault matrix drives all four **public** connectors (`fetch_by_bbl`/`fetch_layer_metadata`) and asserts accepted typed outcomes (pluto `source_unavailable` vs M2-wave `upstream_error`). Assertions look original and specific.

## Observations (LOW / non-blocking)
1. **OBS-L1 (LOW):** Packet said "net LOC reduction"; raw app LOC rose +236 (shared module ~44% docs). Code-only SLOC flat (+17). Four loop copies genuinely became one — duplication eliminated. Owner-disclosed deviation L1; acceptable, but the packet's literal "net LOC reduction" acceptance criterion is met only on the SLOC metric, not raw. Non-blocking.
2. **OBS-2 (LOW):** `request_with_retry` blast radius is now all four connectors (producer R1). Guarded by 16 shared tests + four untouched connector suites. Any future edit needs full-suite re-run.
3. **DEFERRED to G1:** TC-S6 (registry live-page spot-verification of quota/terms/attribution links + last-policy-verification dates) is data-contract-verifier scope. `docs/SOURCE_ACCESS_REGISTRY.md` (203 lines) present with ZoLa-non-API (rule 1), no-SLA/permanence (rule 2), "none published" markers, and "to verify at G1" for unevidenced rows — structurally complete for G3/G4; content verification is the separate G1 gate.

**No BLOCKING defects.** Null hypothesis holds: refactor preserves observable behavior; all connector-specific semantics (SODA 400 classification, layer tagging, error taxonomies, budget/Retry-After/jitter policies, compat monkeypatch seams) intact and routed through hooks. Suite green, ruff clean, consolidation grep-proven.

Relevant files:
- `services/api/app/resilience/transport.py`
- `services/api/app/resilience/__init__.py`
- `services/api/tests/resilience/test_transport_shared.py`
- `services/api/app/connectors/{pluto_soda,zoning_features_arcgis,ztldb_soda,mappluto_geometry_arcgis}.py`
- `docs/SOURCE_ACCESS_REGISTRY.md`
