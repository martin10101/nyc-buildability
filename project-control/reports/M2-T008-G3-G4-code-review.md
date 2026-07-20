# M2-T008 - G3 Independent Walkthrough + G4 Integration Review (code-reviewer)

*(Orchestrator note: saved verbatim from the reviewer's agent-return channel per the report-preservation rule; transport entity-decoding only. This single report backs BOTH the G3 and G4 gate records, recorded separately — precedent M2-T006/M2-T007.)*

## 1. Scope and method

- **Reviewer:** code-reviewer (independent; did not produce this work). Read-only per ADR-005 — no ledger writes, no git/gh writes; this return is the report.
- **Target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T008`, branch `task/M2-T008-ztldb-connector`, HEAD `afacff2` (task PR #42). Merge base with main = main tip `f410914`, so `git diff main...HEAD` is the exact task delta. Worktree clean (`git status --porcelain` empty).
- **Head-commit provenance verified:** `git diff 7e40e81..afacff2` touches only `services/api/tests/connectors/test_ztldb_soda.py`, exactly two lines, both trailing-comment-string changes on the fake-token lines (adds `# secretscan:allow fake token for leak-absence test`). No code change. Matches the disclosed orchestrator pragma fix, and matches the established convention at `test_pluto_soda.py:398` verbatim.
- **Order of evidence:** task packet `project-control/tasks/M2-T008.json` and gate/scenario standards first; then full reads of `services/api/app/connectors/ztldb_soda.py` (1,948 lines) and `services/api/app/profile/zoning_crosscheck.py` (375 lines); `builder.py` diff vs main; both new test modules in full; fixtures + `MANIFEST.json` + `build_fixture_pack.py`; registry draft; producer report LAST.
- **CI:** GitHub Actions down (B-009). Per instructions, local re-execution below is the evidence; CI attestation is the orchestrator's post-restore duty. Not treated as BLOCKED.

## 2. G3 findings

### 2.1 Re-executed evidence (clean committed worktree, `services/api`)

| Command | Result |
|---|---|
| `python -m pytest tests/connectors/test_ztldb_soda.py -q` | **72 passed** in 0.20s |
| `python -m pytest tests/profile/test_ztldb_crosscheck.py -q` | **14 passed** in 0.56s |
| `python -m pytest tests -q` | **442 passed** in 4.81s (356 baseline + 72 + 14 = 442, exactly as expected) |
| `python -m ruff check .` | All checks passed! |

All totals match the producer report exactly.

### 2.2 Downstream-consumer walkthrough of the public API

- **`fetch_by_bbl` normal (ZT01):** 16-column contract mapped from the authoritative api/views columns array (a transcription-drift test pins `ZTLDB_COLUMN_TYPES` against fixture ZT08, which I verified contains `rowsUpdatedAt=1775414816` and exactly 16 columns). Number-typed columns arrive as JSON strings, normalized to ints with verbatim originals preserved. Every fact carries the full source_fact v1 field set plus additive provenance keys (`fact_key`, `observation_id`, `value_digest`, `response_digest`, `source_rows_updated_at`).
- **Zero records (ZT03):** well-formed `[]` for a syntactically valid BBL is a typed `no_record` RESULT (not an error), with explanation, digests, and source_freshness. Malformed 200 bodies (non-JSON, non-array, non-object record — ZT94/ZT95) are typed `malformed_response` and can never become an empty result.
- **Multiple records (ZT93):** two rows for one BBL raises typed `schema_drift` with `record_count=2` — uniqueness is treated as part of the dataset contract; no record is picked.
- **`fetch_source_freshness`:** validates the columns snapshot (removed/re-typed = typed drift; added = visible `added_column:*` signals); missing/invalid `rowsUpdatedAt` is typed drift ("the guard cannot be silently skipped"). Age computed against the injected clock only.
- **Pagination (`scan_rows`):** mandatory `max_pages` hard-capped at 50; deterministic `$order=bbl` URLs match the fixture-captured URLs byte-for-byte; duplicate page, no-progress, repeated record, within/cross-page ordering violation, page overflow, and page-budget exhaustion are all distinct typed `paging_pathology` reasons — budget exhaustion is an explicit failure, never silent truncation.
- **Resilient fetcher:** cache-hit stamps `{served_from_cache: true, stale: false}`; LKG serve stamps `{stale: true, upstream_error_type}` with a self-describing note; budget exhaustion is never masked by LKG; circuit-open makes zero upstream I/O; BBL validation runs before cache lookup.

### 2.3 ZT-S1..S17 scenario mapping — all real and non-vacuous

I traced all 17 scenarios to concrete assertions (the producer's section-5 map is accurate). Notes on the specifically-flagged items:

- **Omitted-key never-confirmed-null (ZT-S4):** proven three ways — no fact exists for any absent column; every one of the 16 columns is either a fact or a classified absence entry; explicit JSON null (ZT92) is a distinct fact with `observed_null:` observation and is asserted NOT to appear in absences. Four presence states genuinely distinct.
- **Split-lot ordering (ZT-S2):** the synthetic swap test (`C4-1` in position 1, `R3-2` in position 2) proves ordering is positional column order, never a lexicographic resort.
- **Slash tie (ZT-S6):** `GI/WP` parses to both components with verbatim value, `tie: True`, dictionary tie semantics, and observation; the underlying fact is untouched.
- **PARK (ZT-S7):** caveat flag + verbatim official caveat text + observation + note; negative case asserted.
- **Open ZD1 (ZT-S8):** ZR-section-number value `107-42` accepted, observation emitted, explicitly asserted NOT to be drift.
- **Four-quadrant two-staleness proof (ZT-S10):** `test_s10_regression_the_two_staleness_dimensions_vary_independently` drives (old-source, fresh-transport), (fresh-source, fresh-transport), (old-source, cached), (old-source, LKG-stale) — both client serve paths — and asserts fresh serves carry no staleness object at all while source_freshness is copied verbatim on cache/LKG serves. This is the strongest form of the owner rule I have reviewed to date.
- **Cross-check both-observations-preserved (ZT-S13/S14):** conflicts always carry all observations (two- and three-way tested) with provenance in derivation text and `resolution="unresolved"`; cross-property and `no_record` inputs are refused (would fabricate conflicts).
- **Injection refusal (ZT-S16):** 10 injection/malformed BBL shapes rejected via `BBLValidationError` with `transport.calls == []` asserted (before any query construction), on both the plain function and the resilient fetcher.
- **Token discipline:** header-only on every call, absent from URL, caplog text, result payloads, and typed error payloads; fixture pack scanned with the M2-T007 G5 O4 widened needle set (token/apikey/api_key/authorization/bearer/password/secret) — re-ran, passes.
- **Digest determinism (ZT-S15):** shuffled-key/whitespace fixture proves raw digest flips while response/normalized digests hold; value change flips both; cross-platform anchor digest asserted and reproduced on this Windows host; manifest digests verified against committed fixture bytes with mandatory `derived_from` lineage for all 13 synthetics.

### 2.4 Clarity, recovery, hidden defaults

- Error payloads are actionable (correlation_id, source_id, dataset_id, sanitized detail); untrusted upstream text passes through shape allowlists or repr-sanitization; no stack traces or headers in payloads.
- No hidden result-changing defaults found. The two judgment calls (case-only = uncertainty; zmcode true/Y comparison predicate) are disclosed, documented in code, and never rewrite values. `dataset_version = socrata-rows-<rowsUpdatedAt>` is research-grounded (dataset has no version column), not invented.
- Owner-PC storage: fixture files total 104,456 bytes; with MANIFEST (21,211) and build script (18,448), the directory totals 144,115 bytes. KB-scale, no downloads, no litter (worktree clean after full runs).

## 3. G3 VERDICT: **PASS**

One LOW defect (D1) and observations below; nothing blocks acceptance. All 17 scenarios are genuinely tested; the two-staleness and presence-state safeguards are exemplary.

## 4. G4 findings

- **Scope — EXACT match.** `git diff --stat main...HEAD` file list maps 1:1 onto `allowed_paths`: new connector module, new `zoning_crosscheck.py`, `builder.py` (profile integration only), new test modules, `tests/fixtures/ztldb/**`, the one registry draft, the producer report. **Forbidden paths untouched:** `packages/contracts/**`, `_contract_schemas/**`, `app/resilience/**`, `pluto_soda.py`, `bbl.py`, `zoning_features_arcgis.py`, `apps/web/**`, `.github/workflows/**`, `.claude/**`, `project-control/**` (except own report). Zero existing test files modified (the packet's disclosed-additive-assertion allowance was not needed).
- **builder.py additive-only:** verified by diff — three optional kwargs defaulting to None; `[*result.facts, *(additional_provenance or [])]` etc. is element-equal to the previous `list(result.facts)` when defaults apply. The docstring claim that additional conflicts gate readiness is TRUE: `profile["conflicts"]` (combined list) is passed into `_status_dimensions` (builder.py:677-681), and `zonedist1` is in `CRITICAL_COLUMNS` (builder.py:186), so a crosscheck conflict on zonedist1 produces `blocked_data_conflict` through the existing M2-T004 machinery — proven by `test_integration_critical_conflict_gates_analysis_readiness` with schema validation, and the non-blocking overlay1 counterpart.
- **Byte-identity proof — qualified (O1):** the named regression test proves omitted-kwargs == explicit-None-kwargs dict equality on the NEW builder, not a direct comparison against main's builder output. Equivalence to main rests on (a) diff inspection (constructions are element-equal) and (b) the 356 unmodified baseline tests — including the existing profile/data-semantics suites that pin default profile content — all passing. I judge this adequate; the producer report's phrasing slightly overstates what that one test proves.
- **No second resilience system / no double retry:** `ResilientZtldbFetcher` composes only M1-T009 primitives (TTLCache, CircuitBreaker, AnalysisBudget, ResilienceConfig, ResilienceMetrics); retry authority lives solely in `_request_with_retry`, with the fetcher passing config through — same consolidated-retry shape as the M2-T007 precedent. Transport, transport signal types, and `canonical_json_digest` are read-only imports from the accepted `pluto_soda`.
- **Error taxonomy alignment:** the nine `error_type` strings are IDENTICAL to `zoning_features_arcgis.py` (including `paging_pathology`, which I confirmed exists there at line 352), plus shared `BBLValidationError`; `no_record` is a result status in both. Distinctness is test-asserted.
- **No import cycles:** `zoning_crosscheck` imports both connectors; `builder` takes plain lists and does not import `zoning_crosscheck`; connectors do not import profile.
- **Regression:** full suite 442 green; contract schemas/typegen untouched; profile default path unchanged; PLUTO module-state non-interference explicitly asserted.
- **Determinism/budgets:** injected clocks (`FIXED_CLOCK`/`APRIL_CLOCK`), scripted transports, `Random(1)`, `SleepRecorder`, `FakeMonotonic` throughout; bounded retries (max_attempts), pages (50 hard cap), page sizes (1000), record query limit (10), offsets (1M); Retry-After beyond cap fails typed without blocking a thread. Suite runs in ~5s with zero wall-clock dependence.
- **Pragma fix afacff2:** comment-only (verified), convention-matching (`test_pluto_soda.py:398` identical comment text), disclosure accurate.
- **Registry draft:** completed with implementation description, 2026-07-20 staleness re-confirmation (OQ-3 stall persists across a second monthly boundary), new live-observed limitations (blank-ZD1 rows, 203-value vocabulary probe, zonemap case difference), OQ-8 probe results. Consistent with the code.

## 5. G4 VERDICT: **PASS**

## 6. Defects

- **D1 (LOW)** — `services/api/app/connectors/ztldb_soda.py`, `check_columns_for_drift` (lines 749-767): an untyped `TypeError` escapes the typed-error contract when the metadata `columns` array mixes an entry lacking `fieldName` (producing a `None` key) with an unknown string-named column — `sorted()` over mixed `None`/`str`. Reproduction (from `services/api`):
  `python -c "from app.connectors.ztldb_soda import check_columns_for_drift; check_columns_for_drift({'columns':[{'dataTypeName':'text'},{'fieldName':'brand_new','dataTypeName':'text'}]})"`
  → `TypeError: '<' not supported between instances of 'str' and 'NoneType'`. Inside `fetch_source_freshness` this would surface as an unhandled exception rather than typed `schema_drift`/`malformed_response`. It fails loudly (no data corruption) and requires a doubly-malformed official metadata document, hence LOW and non-blocking. Suggested fix at next touch: filter/repr non-string `fieldName` values before the set arithmetic and classify as drift.

No other defects found.

## 7. Observations

- **O1** — "Byte-identical default path" evidence is indirect (see G4 findings): omitted-vs-None equality test + untouched 356-test baseline + diff inspection, not a main-vs-branch output diff. Adequate, but the producer-report wording is slightly stronger than the single test.
- **O2** — Test hermeticity nit: helpers pass `app_token=None`, which activates the `SOCRATA_APP_TOKEN` environment fallback inside the fetch functions; a developer machine with that variable set would fail the headers-only assertions. Same pattern as the accepted PLUTO suite (which monkeypatches only in its own token test), so consistent with precedent — worth fixing repo-wide if a hermetic-test policy is ever adopted.
- **O3** — ZT96 (duplicate-page synthetic): `MANIFEST.json` `derived_from` = ZT07b (the offset-5 request slot) while its body bytes duplicate ZT07a — deliberate and documented in `build_fixture_pack.py` (models the upstream returning page 1's content for the page 2 request). Not a defect; recorded so future reviewers don't re-flag it.
- **O4** — The "~104 KB" pack claim equals the 24 fixture files alone (104,456 bytes); with MANIFEST and the build script the directory is 144,115 bytes. Both are comfortably KB-scale/low-storage compliant.
- **O5** — OQ-3 escalation: the Socrata rows-update stall (2026-04-05, re-confirmed 2026-07-20) has crossed a second monthly boundary; the producer recommends a human email to DCP Open Data. The orchestrator should track this as a follow-up/blocker item.
- **O6** — The per-connector `_request_with_retry` loop is a third structural copy of the pluto/zoning-features pattern; the shared-transport/retry refactor already tracked at M2-T007 acceptance now has three consumers and is worth scheduling before a fourth connector.
- **O7** — The cross-platform normalized-digest anchor (`ZT01_NORMALIZED_DIGEST`) reproduced on this Windows host; the Linux confirmation arrives with the orchestrator's post-B-009 CI attestation.
- **O8** — Recommended next tasks in the producer report (API route wiring, Render monthly sync, ZT90 live replacement) are sensible and correctly out of this task's scope.

Key file paths (worktree root `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T008`):
- `services\api\app\connectors\ztldb_soda.py` (D1 at `check_columns_for_drift`)
- `services\api\app\profile\zoning_crosscheck.py`, `services\api\app\profile\builder.py`
- `services\api\tests\connectors\test_ztldb_soda.py`, `services\api\tests\profile\test_ztldb_crosscheck.py`
- `services\api\tests\fixtures\ztldb\MANIFEST.json`, `...\build_fixture_pack.py`
- `docs\research\source-registry-drafts\ztldb.json`, `project-control\reports\M2-T008-producer-report.md`

**Overall: G3 PASS, G4 PASS** — one LOW non-blocking defect (D1) recommended for a follow-up fix; orchestrator to record gates, save this report, and attach CI evidence after B-009 restore.
