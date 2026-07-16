# M1-T002 Producer Report — PLUTO SODA connector (64uk-42ks)

- **Task:** M1-T002 — PLUTO SODA connector with provenance and contract tests
- **Producer agent:** backend-engineer
- **Date:** 2026-07-16
- **Worktree/branch:** `.claude/worktrees/M1-T002` / `task/M1-T002-pluto-soda-connector`
- **Status requested:** `awaiting_gate` (G1 data-contract-verifier, G3, G5 per packet)
- **Progress claim:** 75% (all producer scenarios run; submission for independent gates)

---

## 1. Files changed (all inside allowed paths)

| File | Change | Notes |
|---|---|---|
| `services/api/app/connectors/__init__.py` | new | package marker + connector charter docstring |
| `services/api/app/connectors/bbl.py` | new | BBL validation/normalization, typed `BBLValidationError`, component assembly, identifier-conflict detection |
| `services/api/app/connectors/pluto_soda.py` | new | connector: `fetch_by_bbl`, injectable transport, retry/backoff, error taxonomy, fact mapping, 108-column inventory + Socrata type map (from F08), `check_columns_for_drift`, `build_page_url` |
| `services/api/tests/connectors/__init__.py` | new | test package marker |
| `services/api/tests/connectors/test_bbl.py` | new | 38 tests (S2/S4/S6) |
| `services/api/tests/connectors/test_pluto_soda.py` | new | 47 tests (S1–S7 + fixture hygiene + drift check) |
| `services/api/tests/fixtures/pluto/*.json` | new | 18 fixture files, 273 KB total (listing in §4) |
| `services/api/pyproject.toml` | modified | added `jsonschema>=4.21,<5` to the `dev` extra ONLY (test-time contract validation; the connector itself is stdlib-only — no runtime dependency added) |
| `project-control/reports/M1-T002-producer-report.md` | new | this report |

**Contracts consumed, none changed:** `packages/contracts/schemas/v1/source_fact.schema.json`, `common.schema.json` (read-only; `git status` shows no modification anywhere under `packages/contracts/**`).

## 2. Design decisions (disclosed)

1. **Stdlib-only HTTP.** Default transport is `urllib.request` with explicit timeout; the transport is an injectable callable (`Transport = Callable[[url, headers, timeout], TransportResponse]`) so all 85 new tests run fully offline against stored fixtures. No new runtime dependency.
2. **Error taxonomy.** `validation_error` = `BBLValidationError` raised **before any network call**; `no_match` is a RESULT status (never an exception) with an explanation — condo unit-lot BBLs (1001–6999) get the billing-lot explanation per README 26v1/meta_mappluto; `rate_limited` (429 through retry budget), `schema_drift` (no-such-column 400, malformed/missing `version`, non-array 200 body, >1 record per BBL, record/query BBL mismatch), `timeout`, `source_unavailable` (network down, 5xx exhausted, non-drift 400/4xx, non-JSON 200). Payloads carry `error_type`, `message`, `correlation_id`, `source_id`, `dataset_id`, `detail` — never a stack trace, header, or token.
3. **Retry policy.** Bounded (`max_attempts=3` default), exponential backoff (0.5s, 1.0s; injectable `sleep`), retryable ONLY on 429/5xx/timeout/network-failure. 400s are never retried; `query.soql.no-such-column` raises `SchemaDriftError` immediately (fixture F13); other 400s (e.g. live-captured `query.soql.type-mismatch`, F13b) are classified distinctly.
4. **Schema from inventory, never from record keys.** The module embeds the 108-column inventory + official Socrata `dataTypeName` map transcribed from the live `/api/views/64uk-42ks.json` capture (F08); a test compares module constants against the fixture byte-for-byte, so transcription drift fails the build. Absent keys → `absent_columns` on the result (fact unknown/absent); unknown keys → `drift_signals` (`unknown_column:*`) with NO fact emitted.
5. **Fact shape.** Every fact contains the full required source_fact v1 field set plus additive keys `dataset_id`, `request_url`, `input_vintages` (source_fact v1 does not set `additionalProperties: false`, verified by jsonschema validation in tests; schema file untouched). `provenance_id` is the deterministic key `pluto-64uk-42ks-<version>-<bbl>-<field>` (S6 idempotency). `confidence` = 1.0 (deterministic official retrieval per the schema's own description). Normalization is per official Socrata type: number → int/float, checkbox → bool passthrough, calendar_date → date part, text → verbatim; `bbl`/`appbbl` → canonical 10-digit string (F12 rule). Units from the 26v1 dictionary (sq ft / feet / US dollars / EPSG:2263 coordinates); FAR columns unitless informational facts, never rule outputs.
6. **`effective_date` is explicitly `null`** on every fact: PLUTO publishes per-INPUT vintage dates (the eight `*date` columns), but no official per-FIELD → input mapping, so mapping facts to a vintage would be a guess. Instead the vintages are carried verbatim in `input_vintages` when present. Live evidence (F01v): all eight vintage columns are NULL for the sampled record — SODA omits them even under `$select`; the capture path is proven with a clearly-labeled synthetic variant test.
7. **App token.** Read from `SOCRATA_APP_TOKEN` env (or `app_token=` parameter), sent only as the `X-App-Token` header, never required, never in URLs, logs, or error payloads (tested). Human action to obtain a production token remains tracked separately (packet risk item; carried in HUMAN_ACTIONS_REQUIRED by the orchestrator — I did not edit that file, outside my scope).
8. **Correlation IDs** on every result and error payload (uuid4 hex, injectable).

## 3. Deviation disclosure (S3a input)

The packet's S3(a) names BBL `9999999999` as "syntactically valid, nonexistent". That value violates the **accepted** canonical BBL pattern `^[1-5][0-9]{5}[0-9]{4}$` (common.schema.json, M0-T009) — borough digit 9. The connector therefore rejects it client-side as `validation_error` (`invalid_borough`) with zero network calls (tested). To still prove the `[]` no-match path with official evidence I live-captured **F03b** (`bbl=5999999999` — valid pattern, nonexistent lot → `[]`) and kept **F03** (raw API behavior for `9999999999` → `[]`) as documentation. Both behaviors are tested. Reviewers should confirm this reading; I believe it is the only one consistent with the accepted contract.

## 4. Fixture pack (services/api/tests/fixtures/pluto/, 273 KB total)

Every fixture embeds `request_url`, `retrieval_timestamp_utc`, `capture_method`, `http_status`, and the raw unmodified `response_body_raw`. Live capture log (17 fixtures live; 19 HTTP requests total this session including one liveness probe and one overwritten first F5 attempt, all single KB-scale GETs spaced ≥3 s, tokenless, polite shared-pool use):

| Capture | Request URL | UTC timestamp | HTTP | Bytes |
|---|---|---|---|---|
| F1 | `…/resource/64uk-42ks.json?bbl=1000010100` | 2026-07-16T20:26:46Z | 200 | 1346 |
| F3 | `…?bbl=9999999999` | 20:26:50Z | 200 | 3 |
| F9 | `…?$select=version&$limit=1` | 20:26:53Z | 200 | 21 |
| F12 | `…?$select=bbl&$order=bbl&$limit=2` | 20:26:57Z | 200 | 63 |
| F13 | `…?$select=nonexistent_col` | 20:27:00Z | 400 | 360 |
| (F5 attempt 1) | `…?$where=splitzone='Y'&$limit=1&$order=bbl` | 20:27:11Z | 400 | 5767 — discarded; shape recaptured as F13b |
| F2a | `…?$where=lot between 7501 and 7599&$limit=1&$order=bbl` | 20:27:15Z | 200 | 1630 |
| F5 | `…?$where=splitzone=true&$limit=1&$order=bbl` | 20:27:34Z | 200 | 1737 |
| F2b | `…?bbl=1000041001` | 20:27:38Z | 200 | 3 |
| F4 | `…?$order=bbl&$limit=1&$offset=2` | 20:27:41Z | 200 | 1471 |
| F6a | `…?$order=bbl&$limit=5` | 20:27:45Z | 200 | 7659 |
| F6b | `…?$order=bbl&$limit=5&$offset=5` | 20:27:48Z | 200 | 6918 |
| F10 | `…?$where=borocode=1 and zipcode=10463&$limit=1&$order=bbl` | 20:27:59Z | 200 | 1403 |
| F14 | `…/resource/qt5r-nqxp.json?$limit=1` | 20:28:03Z | 200 | 131 |
| F8 | `…/api/views/64uk-42ks.json` | 20:28:07Z | 200 | stored `response_body_raw` = 202598 chars = 202647 UTF-8 bytes (49 multibyte chars account for the char/byte difference; fixture file on disk 228576 bytes incl. provenance envelope — corrected per G1 C4) |
| F3b | `…?bbl=5999999999` | 20:31:11Z | 200 | 3 |
| F13b | `…?$where=splitzone='Y'&$limit=1` | 20:31:15Z | 400 | 5709 |
| F1v | `…?$select=bbl,basempdate,…,zoningdate&bbl=1000010100` | 20:31:36Z | 200 | 32 |

**F7 (429)** is `synthetic-from-official-doc` per the packet: constructed from https://dev.socrata.com/docs/app-tokens (only the 429 STATUS is officially documented; body left empty and never asserted — the connector classifies 429 on status alone). The shared pool was NOT burst. **F11 is out of scope** (M2 bulk importer) — not captured.

Notable live findings baked into fixtures/tests: full records (not just `$select`) serialize `bbl`/`appbbl` with decimal tails; `splitzone`/`irrlotcode`/`mih_opt*`/`zmcode` are JSON booleans (Socrata checkbox) — the SoQL predicate is `splitzone=true`, and `splitzone='Y'` produces the non-drift 400 `query.soql.type-mismatch`; the real F4 record (BBL 1000010101) natively exhibits the dictionary p.28 case (numfloors omitted, numbldgs=10); F10 (Marble Hill, MN block 2215) shows borocode 1 with sanitboro 2/zipcode 10463 and is also split-zone.

## 5. Scenario results (S1–S8)

All producer commands run from `services/api/` in the worktree; Python 3.11.9, pytest 8.4.2, jsonschema 4.26.0, ruff 0.9.9 (pre-existing on this machine; nothing was installed).

| Scenario | Tests | Expected | Actual |
|---|---|---|---|
| S1 normal | `test_s1_normal_fetch_returns_one_canonical_record`, `test_s1_every_fact_validates_against_source_fact_v1`, `test_s1_provenance_fields_on_a_concrete_fact` | one canonical record; every fact validates against source_fact v1 with full provenance | PASS — 67 facts from F1 (67 record keys; corrected per G1 C2/G3 D4, previously misstated as 66); jsonschema Draft2020-12 + referencing registry; provenance fields asserted value-by-value |
| S2 boundary | `test_normalize_socrata_decimal_serialization_f12`, `test_bbl_from_components_bounds` (borough 1/5, block 1/99999, lot 1/9999), `test_s2a_record_bbl_decimal_serialization_normalized_with_raw_preserved`, `test_s2c_condo_billing_lot_returns_complex_record`, `test_s2c_condo_unit_lot_is_no_match_with_condo_explanation` | F12 normalization with raw preserved; padded assembly; condo billing found / unit no_match with explanation | PASS |
| S3 missing/null | `test_s3a_valid_nonexistent_bbl_is_explicit_no_match_not_error` (F3b), `test_s3a_packet_bbl_9999999999_is_rejected_before_any_network_call` (see §3), `test_s3b_null_field_omission_yields_absent_columns_never_fabrication`, `test_s3b_f04_fixture_record_keys_are_subset_of_inventory`, `test_s3c_numfloors_absent_with_buildings_is_flagged_not_available` (real F4 record) | no_match not error; omitted keys = absent/unknown never fabricated; NumFloors "not available" per dictionary p.28 | PASS |
| S4 ambiguous/conflicting | 18-case parametrized `test_malformed_inputs_rejected_with_typed_codes` + `test_s4a_malformed_bbl_rejected_typed_with_no_network_call` (zero transport calls) + `test_s4b_identifier_conflict_flagged_never_silently_resolved` + bbl.py consistency tests | typed errors naming the defect, no network; conflicts flagged at provenance level, both values visible | PASS |
| S5 failure | `test_s5a_429_bounded_retry_with_backoff_then_typed_rate_limited` (3 calls, sleeps [0.5, 1.0]), `test_s5a_429_then_success_recovers`, `test_s5b_no_such_column_400_is_schema_drift_and_never_retried` (exactly 1 call), `test_s5b_other_400_is_distinct_from_schema_drift` (F13b), `test_s5c_timeout…`, `test_s5d_network_unavailable…`, `test_s5e_5xx…`, `test_s5_no_partial_facts_on_failure`, `test_s5_error_payloads_never_contain_token_or_stack_trace`, `test_s5_tokenless_operation_sends_no_token_header`, malformed-JSON-200 and non-array-200 and multi-record cases | typed errors; drift never retried; no partial facts; no token/stack anywhere | PASS |
| S6 idempotency | `test_s6_same_input_twice_yields_identical_canonical_output`, `test_s6_retry_after_transient_failure_produces_same_facts`, `test_normalization_is_deterministic` | identical canonical output; deterministic provenance keys; stable sorted fact order; no duplicates | PASS |
| S7 provenance completeness | `test_s7_no_normalized_value_without_full_provenance`, `test_s7_version_regex_enforced_f9`, `test_s7_malformed_version_is_schema_drift`, `test_s7_vintage_columns_absent_on_f1_record_yields_empty_vintages`, `test_s7_vintage_columns_captured_when_present`, `test_s7_unknown_column_yields_drift_signal_and_no_fact`, `test_f8_embedded_inventory_matches_api_views_snapshot` | no normalized value without provenance; `^\d{2}v\d+(\.\d+)?$` enforced; vintages captured when present | PASS |
| S8 regression | full suite + contracts validator | `test_health.py` passes; `validate_contracts.py` passes; no contract files modified | PASS (outputs below) |

### Exact commands and outputs

```
$ cd services/api && python -m pytest tests -q
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 0.79s        # 2 test_health + 38 test_bbl + 47 test_pluto_soda

$ python -m pytest tests/connectors/test_bbl.py -q          → 38 passed in 0.06s
$ python -m pytest tests/connectors/test_pluto_soda.py -q   → 47 passed in 0.19s
$ python -m pytest tests/test_health.py -q                  → 2 passed in 0.58s

$ python .github/scripts/validate_contracts.py   (from worktree root, read-only)
...
Checked 6 schema file(s); 0 failure(s).
EXIT=0

$ python -m ruff check app/connectors tests/connectors
All checks passed!

$ git status --short   (worktree root)
 M services/api/pyproject.toml
?? services/api/app/connectors/
?? services/api/tests/connectors/
?? services/api/tests/fixtures/
# plus this report file after it is written — nothing outside allowed paths.
```

## 6. Assumptions and defaults

1. `9999999999` handled as described in §3 (deviation disclosure) — needs reviewer confirmation.
2. `effective_date: null` on all facts; per-input vintages carried in `input_vintages` instead (no official per-field mapping exists; see §2.6).
3. Additive fact keys (`dataset_id`, `request_url`, `input_vintages`) rely on source_fact v1 permitting additional properties — verified by validating every emitted fact with jsonschema against the untouched schema.
4. `>1` record for an exact `bbl=` query is treated as schema drift (PLUTO carries one record per tax lot / condo complex; uniqueness is part of the dataset contract per README 26v1).
5. Defaults: timeout 10 s, max_attempts 3, backoff base 0.5 s — all injectable; none silently affect facts.
6. `condono` normalized to int like other Socrata number columns (dictionary: unique within borough; cross-borough joins must also use borocode — that is downstream logic, not this connector's).

## 7. Known limitations

1. **No live-run of the connector's default urllib transport against the API** in the test suite (deliberate: tests are offline/deterministic). The captured fixtures ARE live evidence from today; a live smoke of `fetch_by_bbl("1000010100")` is a one-liner for the G1/G3 reviewer.
2. **F11 (MapPLUTO bulk manifest) out of scope** — M2 bulk importer task (OQ-4/OQ-10 residuals still open).
3. **F7 (429) body is synthetic** — only the status code is officially documented; classification is status-based by design.
4. **Vintage-capture path proven only synthetically** (labeled in-test); the eight columns were NULL on every politely-sampled record today (F1v evidence). A record with populated vintages should be spot-checked at G1 if one is found cheaply.
5. No per-block query, caching, or `raw_source_records` persistence yet — the packet scopes this task to the connector; DB persistence layers arrive with the property-profile API task.
6. `requires-python = ">=3.12"` in pyproject vs local 3.11.9 used for self-check: code uses nothing newer than 3.11 (`datetime.UTC`, PEP 604); CI runs the authoritative matrix.

## 8. Security / provenance impact

- Token: optional env `SOCRATA_APP_TOKEN`, header-only, never logged/never in payloads/URLs — regression-tested (`test_s5_error_payloads_never_contain_token_or_stack_trace`, `test_s5_tokenless_operation_sends_no_token_header`).
- No secrets in code or fixtures (all captures tokenless public data).
- Facts are impossible to obtain without provenance: the ONLY fact emission path builds the full source_fact v1 record; failures raise typed errors with no partial facts.
- Prompt-injection surface: none (no AI in this connector; government values passed as data only).
- Low storage: fixture pack 273 KB in-repo; no datasets downloaded; nothing installed. **Pending cleanup (disclosed):** raw capture dir `C:\Users\MLFLL\AppData\Local\Temp\pluto_cap` (~0.5 MB, OS temp, outside repo) — my `rm` permission was denied; orchestrator/owner may delete it.

## 9. New risks / observations for the orchestrator

1. **Socrata checkbox typing** (`splitzone` etc. as JSON booleans, `='Y'` → type-mismatch 400) is new, fixture-proven knowledge; any future SoQL-writing code must use boolean predicates.
2. Full records also decimal-serialize `bbl`/`appbbl` (not just `$select` projections) — F12 hazard is broader than G1 recorded; handled.
3. The permission sandbox for this producer session ALLOWED python/network execution (unlike M1-T001) — evidence in this report is first-hand, not orchestrator-captured.

## 10. Recommended next tasks

1. Property-profile API (Priority 3) consuming `PlutoFetchResult.facts` → `property_source_facts` persistence + `raw_source_records` snapshot storage (Supabase).
2. Scheduled drift monitor job wiring `check_columns_for_drift` + `$select=version` freshness poll (research §7.3).
3. M2 `mappluto-bulk` importer (closes OQ-4/OQ-10; F11).
4. Human action: create a production Socrata app token (optional but recommended; record in HUMAN_ACTIONS_REQUIRED.md).

**Report path:** `project-control/reports/M1-T002-producer-report.md`

---

## 11. Fixup pass 2026-07-16 (post-G1/G3 review fixes; producer: backend-engineer)

Scope: apply the exact G3 D1–D3/F5 and G1 C1–C2/C4 corrections. No redesign; connector + tests + this report only. All edits inside `services/api/app/connectors/pluto_soda.py`, `services/api/tests/connectors/test_pluto_soda.py`, and this report.

| Fix | Change | Test |
|---|---|---|
| G3 D1 (Medium) | `pluto_soda.py` record-BBL check (`fetch_by_bbl`): `normalize_bbl(record["bbl"])` now wrapped in `try/except BBLValidationError` → raises `SchemaDriftError` (`error_type=schema_drift`) with `detail.record_bbl_raw` + `detail.validation_code`. An unparseable record-level bbl is source-shape drift, never a caller `validation_error`. | `test_d1_unparseable_record_bbl_is_schema_drift_not_validation_error` (F01 replay, bbl mutated to `"0000000000.00000000"`; asserts schema_drift, not BBLValidationError, single call) |
| G3 D2 (Low) | `_normalize_value` number path: added `math.isfinite` guard. Non-finite parses (`"NaN"`, `"Infinity"`, `"-Infinity"`) emit `drift_signals` entry `non_finite_number_value:<column>` and pass the verbatim raw value through (no float nan/inf normalized fact; `json.dumps(..., allow_nan=False)` verified clean). | `test_d2_non_finite_number_is_drift_signal_with_raw_preserved` (parametrized: NaN, Infinity, -Infinity) |
| G3 D3 (Low) | `retrieved_at` is now stamped AFTER `_request_with_retry` returns the successful response (was: before the request; retry skew up to ~31.5 s). Fixed-clock pattern preserved; no existing test pinned the old ordering. | `test_d3_retrieved_at_stamped_after_successful_response` (stepping clock + event ordering: `["request", "request", "clock"]` across a 503 retry; result and all facts carry the post-response stamp) |
| G1 C1 (minor) | `yearbuilt` semantics per dictionary p.34-35 (0/null = unknown), mirroring the `numfloors_not_available` pattern: when `yearbuilt` is 0 or absent, a `yearbuilt_unknown` note is appended and the fact (when present) keeps `original_value` verbatim (`"0"`) with `normalized_value: null` — never a confident normalized 0. Genuine years are unaffected. | `test_c1_yearbuilt_zero_is_unknown_not_confident_zero` (real F01 record), `test_c1_yearbuilt_absent_is_flagged_unknown`, `test_c1_real_construction_year_stays_a_normal_numeric_fact` |
| G3 F5 (test gap) | Offline unit tests for `urllib_transport` error translation via monkeypatched `urllib.request.urlopen`: success status/body/timeout/header pass-through; `HTTPError` body → `TransportResponse` (never propagates); `TimeoutError` → `TransportTimeout`; `URLError(TimeoutError)` → `TransportTimeout`; `URLError(ConnectionRefusedError/gaierror)` → `TransportFailure` with type-name-only message (no URL/secret leakage). | `test_urllib_transport_success_returns_status_and_decoded_body`, `test_urllib_transport_http_error_body_passes_through_as_response`, `test_urllib_transport_timeout_error_maps_to_transport_timeout`, `test_urllib_transport_urlerror_timeout_reason_maps_to_transport_timeout`, `test_urllib_transport_urlerror_network_reason_maps_to_transport_failure[connection_refused/dns_gaierror]` |
| G1 C2 / G3 D4 | §5 S1 row corrected: 67 facts from F1 (was misstated 66). | n/a (report text; 67 already asserted implicitly by fixture key count) |
| G1 C4 | §4 F8 capture row corrected: stored `response_body_raw` = 202598 chars = 202647 UTF-8 bytes (multibyte accounting), fixture file 228576 bytes on disk. | n/a (report text) |

### Fixup commands and exact outputs

```
$ cd services/api && python -m pytest tests -q
........................................................................ [ 71%]
.............................                                            [100%]
101 passed in 1.36s      # was 87; +14 fixup tests (2 health + 38 bbl + 61 pluto)

$ python -m pytest tests/connectors/test_pluto_soda.py -q
.............................................................            [100%]
61 passed in 0.24s       # was 47

$ python -m ruff check app/connectors tests/connectors
All checks passed!
```

No fixtures, contracts, or pyproject touched in this pass. Status requested remains `awaiting_gate` (G5/merge per orchestrator); this producer does not accept its own work.
