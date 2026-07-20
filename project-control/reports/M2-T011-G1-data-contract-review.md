<!-- Preserved VERBATIM by the orchestrator from the data-contract-verifier G1 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

---

# G1 GATE REPORT — M2-T011 (Shared connector transport/retry consolidation + canonical source access registry)

**Reviewer:** data-contract-verifier (independent; did not implement)
**Date:** 2026-07-20
**Actual reviewed commit:** `85cea98` (M2-T011 work; merged PR #50 at `6dfac68`). NOTE: the prompt's stated SHA `555d68a` is PR #51 = **M2-T010**, not this task — I diffed the correct commit.

## VERDICT: **PASS**

No blocking defects. Consolidation is byte-behavior-preserving; the registry is complete, cited, and its independently-checkable claims verified against live official sources.

---

## Evidence — commands run (tails)

| # | Command | Result |
|---|---|---|
| 1 | `pytest tests/connectors tests/resilience -q` | **407 passed in 3.15s** |
| 2 | `pytest tests/ -q` (full suite) | **538 passed in 6.40s** (522 pre-existing + 16 new) |
| 3 | `pytest tests/connectors -k "url or manifest or capture or digest or byte"` | **35 passed** — capture-URL byte-reproducibility + raw/normalized digest tests green through the consolidated path |
| 4 | grep `for attempt in range(1, max_attempts + 1)` over `app/` | exactly **1 hit** — `resilience/transport.py:451`; **0** in all four connectors (TC-S2 ✓) |
| 5 | `git diff 85cea98~1 85cea98 --stat` | 9 files, all within `allowed_paths`; only new test file `test_transport_shared.py`; **no existing test modified** |
| 6 | `pytest --collect-only test_transport_shared.py` | 16 tests: TC-S2 guards, TC-S3 (retry-after/jitter/budget/legacy-exp/timeout), TC-S7 fault matrix parametrized `[timeout, 429_over_cap, 5xx_burst]` |

**Data-contract safety (TC-S1/S4):** grep of the connector diffs for `def (canonical_json_digest|_build*url|_capture_url|_digest|_normalized)` returned **empty** — no URL-builder or digest-normalization function was touched; the removed lines are exclusively transport primitives + retry-loop + retry-after helpers that moved verbatim into `transport.py`. Provenance/retrieval-timestamp code untouched.

**Config-semantics (TC-S3, forbidden-path):** no `ResilienceConfig`, TTL, breaker-threshold, retry-count, or budget default changed. The only `max_attempts=`/`budget=` diff lines are connector wrappers passing their **existing** values into the shared engine. Retry counts, budgets, breaker thresholds, cache TTLs, staleness typing all preserved.

## Registry verification (TC-S5/TC-S6) — independently confirmed vs live official sources

| Claim | Registry | Live check | Result |
|---|---|---|---|
| Socrata token/quota | rule 5: "not throttled unless abusive/malicious; no numeric quota; 429 signal" | dev.socrata.com/docs/app-tokens | **CONFIRMED verbatim** |
| PLUTO `64uk-42ks` | 108 cols, "Primary Land Use Tax Lot Output (PLUTO)" | api/views raw | **108 ✓ name ✓** |
| ZTLDB `fdkv-4t4z` | 16 cols; rowsUpdatedAt stall | api/views raw | **16 cols ✓; rowsUpdatedAt 1775414816 still frozen ✓** (corroborates the documented stall observation) |
| zoning-features `nyzd` ArcGIS | maxRecordCount 2000, CRS 102718/2263 | FeatureServer/0?f=json | **CONFIRMED** |
| MapPLUTO ArcGIS | maxRecordCount 2000, CRS 102718/2263 | FeatureServer/0?f=json | **CONFIRMED** |
| ZoLa non-API + no-permanence/no-SLA | governance rules 1 & 2 present | doc read | **PRESENT ✓** |

**Could-not-verify (legitimately blocked, correctly marked "to verify at G1" in the doc):** MapPLUTO bulk zip URLs (nyc.gov 403 bot wall), Geoclient portal quota (requires owner sign-in), bulk FileGDB internal schema, DOB dictionary XLSX contents. These are genuinely unverifiable without credentials/browser session — acceptable per the packet.

## Observations (non-blocking, for orchestrator awareness)

1. **OBSERVATION** — `docs/SOURCE_ACCESS_REGISTRY.md` §4 (MapPLUTO): registry pins "103 PascalCase fields" from fixture MPG01_meta.json (2026-07-20). I confirmed the fixture body has exactly **103** fields, but the **live** MAPPLUTO service now returns **138** fields — DCP added ~35 since capture. This is legitimate post-snapshot schema drift, covered by governance rule 2 and the connector's `check_columns_for_drift`, **not** a registry error. The pinned fixture (and thus any downstream drift-baseline) is now stale vs live; a future MapPLUTO connector task should re-capture. No action required for M2-T011 acceptance.
2. **OBSERVATION** — `nyzd` `dataLastEditDate` now reads a value beyond the registry's recorded 2026-07-01/2026-07-20 observations (a new monthly release). Expected source evolution; the registry records observation dates, not permanence contracts (rule 2). No defect.
3. **OBSERVATION (LOW)** — Producer disclosure L1 stands: raw app-code line count rose (+236) despite eliminating four duplicated loops (net −277 in tracked connector files; ~44% of the new module is docs). The packet asked for "net LOC reduction"; on the connector files this holds, on raw-total it does not. Fully disclosed by the producer; a documentation/accounting matter, not a data-contract defect.
4. **OBSERVATION** — Producer micro-behavior disclosures L2.1–L2.6 (defensive `get_retry_after` guard, per-attempt header dict identity, `%s`-templated log msg vs literal, class `__module__` relocation, lazy `app.resilience.__getattr__`) are all unreachable-by-any-test or byte-identical-when-rendered; I independently confirmed none is exercised by the 538-test suite and none alters emitted provenance, URLs, or digests. Accept as disclosed.

## Bottom line

The refactor's null hypothesis ("behavior unchanged") holds on the data-contract dimension: capture URLs remain byte-reproducible, raw/normalized digest computation is untouched, provenance/timestamps unchanged, config semantics unchanged, and every connector-specific semantic test is green and unmodified. The registry is complete with the owner-mandated fields, every independently-checkable quota/identifier/endpoint claim verified live, ZoLa-non-API and no-SLA rules present, and unverifiable items honestly flagged rather than invented.

**G1 = PASS.** (Observations 1–2 recommended as follow-up re-capture notes for the eventual MapPLUTO bulk/connector task; none blocks acceptance.)

Files reviewed: `docs/SOURCE_ACCESS_REGISTRY.md`, `services/api/app/resilience/transport.py`, `services/api/app/connectors/{pluto_soda,zoning_features_arcgis,ztldb_soda,mappluto_geometry_arcgis}.py`, `services/api/app/resilience/__init__.py`, `services/api/tests/resilience/test_transport_shared.py`, `project-control/tasks/M2-T011.json`, `project-control/reports/M2-T011-producer-report.md`.
