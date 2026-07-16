# M1-T002 — G1 Source and Data-Contract Gate Verification

- **Task:** M1-T002 — PLUTO SODA connector (64uk-42ks) with provenance and contract tests
- **Gate:** G1 (source and data-contract)
- **Reviewer:** data-contract-verifier (independent; did not produce this work)
- **Review location:** `.claude/worktrees/M1-T002`, branch `task/M1-T002-pluto-soda-connector`, commit `9e22839`
- **Date:** 2026-07-16 (all live requests this date, ~21:00Z, tokenless, KB-scale, sequential)
- **Method:** started from the task packet acceptance criteria (S1–S8), research §4/§5.2/§6, and the binding contracts (`source_fact.schema.json` v1 + `common.schema.json`); read the implementation and tests; re-ran the full suite; live spot-checked five fixtures plus the column inventory against the official endpoint; ran a live smoke through the connector's real transport; cross-checked against a second official presentation (ArcGIS MapPLUTO FeatureServer). Producer report read LAST.

**VERDICT: PASS** — with minor corrections C1–C4 (none material; none block G3).

---

## 1. G1 checklist walkthrough

| # | Check | Expected | Actual | Evidence |
|---|---|---|---|---|
| 1 | Official source identity | NYC Open Data PLUTO, DCP, dataset `64uk-42ks`; `SOURCE_ID` matches registry draft | `SOURCE_ID = "nyc-dcp-pluto-soda"` = `docs/research/source-registry-drafts/pluto-mappluto.json` record 1; endpoint `https://data.cityofnewyork.us/resource/64uk-42ks.json` matches registry `api_dataset_identifier` | pluto_soda.py:79-82; registry draft read this session |
| 2 | Current endpoint/dataset id | Endpoint live and version-current | Live `?$select=version&$limit=1` → `[{"version":"26v1"}]` HTTP 200 (matches F09 byte-for-byte) | curl 2026-07-16 ~21:00Z |
| 3 | Auth and rate limits | Tokenless works; `X-App-Token` optional env-driven header; never logged/never in URL/payload; 429 → bounded retry | All my live calls tokenless HTTP 200. Code: token from `SOCRATA_APP_TOKEN` env or param, header-only (`_build_headers`); log line emits only `token_configured=bool`. Test `test_s5_error_payloads_never_contain_token_or_stack_trace` sets a token, forces failure, asserts token absent from payload, logs, and URL | pluto_soda.py:316-322, 527-530; test_pluto_soda.py:389-407 |
| 4 | Pagination | Stable ordering, no dupes/gaps | F06a/F06b live-captured (`$order=bbl&$limit=5[&$offset=5]`); `test_f6_pagination_fixtures_stable_order_no_dupes_no_gaps` asserts sorted, deduped across the boundary; `build_page_url` rejects limit<1/offset<0 | fixtures F06a/F06b; test_pluto_soda.py:602-611 |
| 5 | Actual response fixtures | Raw official bodies with request URL + retrieval timestamp + capture method | 18 fixtures: 17 live-captured, 1 (F07/429) explicitly `synthetic-from-official-doc` with `retrieval_timestamp_utc: null` (packet risk register REQUIRED it not be captured by bursting the shared pool). Hygiene enforced by `test_every_fixture_embeds_url_timestamp_and_capture_method`. My live authenticity spot-checks: §2 below — 5/5 identical | tests/fixtures/pluto/*; test_pluto_soda.py:627-644 |
| 6 | Field mapping and units | Per 26v1 dictionary: lotarea sq ft int; lotfront/lotdepth ft decimal; assess* dollars; coords EPSG:2263 survey feet; FAR informational/unitless; numfloors fractional; condo billing-BBL | `FIELD_UNITS` matches research §4.1 exactly (areas "square feet", frontage/depth "feet", DOF "US dollars", xcoord/ycoord EPSG:2263 survey feet, lat/lon decimal degrees); residfar/commfar/facilfar/affresfar/mnffar/builtfar carry `units: null` and are emitted only as facts, never as rule outputs; types normalized per the official Socrata `dataTypeName` (F08), never guessed; condo unit-lot (1001–6999) → explicit `no_match` + billing-lot (7501–7599) explanation citing README 26v1 | pluto_soda.py:104-181, 429-482; test_s1_provenance_fields_on_a_concrete_fact; test_s2c_* |
| 7 | Null/unknown semantics | SODA null-omission never fabricated; schema never inferred from record keys; numfloors p.28 rule | Schema comes ONLY from the embedded 108-column inventory (asserted equal to F08 fixture at test time — transcription drift fails the build — and equal to LIVE api/views by me, §3). Absent keys → `absent_columns`; unknown keys → `drift_signals` + NO fact. `numfloors` absent with `numbldgs>0` → `numfloors_not_available` note (real F04 record, numbldgs=10). YEARBUILT 0-unknown: see C1 | test_s3b_*, test_s3c_*, test_s7_unknown_column_*; my live drift check §3 |
| 8 | Retrieval/version timestamps | RFC 3339 retrieval timestamp on every fact; version regex enforced | `retrieved_at` on result and every fact (matches common `date_time` pattern); `VERSION_RE ^\d{2}v\d+(\.\d+)?$`; missing/malformed version → `SchemaDriftError` (facts refuse to exist without a valid release version) | pluto_soda.py:86, 605-612; test_s7_version_regex_enforced_f9, test_s7_malformed_version_is_schema_drift |
| 9 | Provenance persistence | Impossible to obtain a normalized fact without full provenance; deterministic keys | Single fact-emission path builds the complete source_fact v1 required set inline (code read: no other constructor); `provenance_id = pluto-64uk-42ks-<version>-<bbl>-<field>` deterministic (S6 tests: identical facts across repeat and retry-after-503); conflicts (bbl vs borocode/block/lot) surfaced as `conflict_status: "conflicting"` on BOTH identifier facts with both values verbatim — never silently resolved | pluto_soda.py:648-677; test_s4b_*, test_s6_*, test_s7_no_normalized_value_without_full_provenance |
| 10 | Schema-drift handling | Drift ONLY on the no-such-column signature; other 400s distinct; drift never retried | 400 + `errorCode query.soql.no-such-column` → `SchemaDriftError`, exactly 1 transport call; 400 + `query.soql.type-mismatch` (live-captured F13b) → distinct non-drift error, also unretried; additional drift triggers: non-array 200 body, >1 record per exact-BBL query, record/query BBL mismatch, malformed version, unknown columns (signal). Retry only on 429/5xx/timeout/network, bounded (3 attempts), exponential backoff (0.5s, 1.0s asserted) | pluto_soda.py:378-404; test_s5a_*, test_s5b_*, test_f8_drift_check_* |
| 11 | Cross-check vs second official presentation | Same record on another official channel | ArcGIS MapPLUTO FeatureServer (DCP_GIS, verified official at M1-T001 G1) `where=BBL=1000010100` → `LotArea 23121, ZoneDist1 "R3-2", SPDist1 "GI", LotFront 297.49, LotDepth 67.01, YearBuilt 0, Version "26v1"` — every value matches the SODA fixture/connector output | curl FeatureServer/0/query 2026-07-16 |

## 2. Fixture-authenticity spot-checks (live vs stored, 2026-07-16 ~21:00Z)

| Fixture | Request re-issued live | Result |
|---|---|---|
| F01 (bbl=1000010100) | `?bbl=1000010100` → HTTP 200 | **Byte-identical record** (all 67 keys, incl. `bbl:"1000010100.00000000"`, `appbbl:"1000010010.00000000"`, `splitzone:false` boolean, `version:"26v1"`) |
| F12 ($select=bbl) | `?$select=bbl&$order=bbl&$limit=2` → 200 | **Identical**: `"1000010010.00000000"`, `"1000010100.00000000"` — decimal-serialization hazard confirmed live |
| F13 (drift 400) | `?$select=nonexistent_col` → HTTP 400 | **Identical body**: `errorCode: "query.soql.no-such-column"` |
| F09 (version) | `?$select=version&$limit=1` → 200 | **Identical**: `[{"version":"26v1"}]` |
| F02a (condo billing lot) | `?bbl=1000047501` → 200 | **Field-for-field identical** to the fixture record (condono 835, 1 WATER STREET) — note the fixture was discovered via a `$where lot between 7501 and 7599` query, but the record it stores is exactly what a direct `?bbl=` fetch returns, so replaying it through the connector's `?bbl=` path is sound |
| F08 (columns) | `/api/views/64uk-42ks.json` live | 108 columns, `check_columns_for_drift(live)` → `{added: [], removed: [], type_changed: []}` vs the embedded inventory; test separately pins inventory == F08 fixture, so fixture == live transitively. `rowsUpdatedAt` still 1779997848 = 2026-05-28T19:50:48Z (26v1, unchanged) |

All fixture provenance headers (request URL, UTC timestamp, capture method) present on all 18 files and enforced by a test. F07 is the only synthetic fixture, correctly labeled, body empty and never asserted (classification is status-based; only HTTP 429 is officially documented at dev.socrata.com/docs/app-tokens).

## 3. Live smoke through the connector's real transport (closes the producer's disclosed gap)

```
cd .claude/worktrees/M1-T002/services/api
python -c "import sys; sys.path.insert(0,'.'); from app.connectors.pluto_soda import fetch_by_bbl; r=fetch_by_bbl('1000010100'); print(r.status, r.dataset_version, len(r.facts), r.conflicts, r.drift_signals)"
```
Result (default `urllib_transport`, live endpoint, tokenless): `status=ok`, `version=26v1`, **67 facts**, `conflicts=[]`, `drift_signals=[]`, `retrieved_at=2026-07-16T21:01:06Z`, `lotarea 23121 -> 23121 "square feet"`, `bbl "1000010100.00000000" -> "1000010100"`, `provenance_id pluto-64uk-42ks-26v1-1000010100-lotarea`. I then independently validated the live-emitted `bbl` fact against `source_fact.schema.json` v1 (Draft 2020-12 + referencing registry): **0 errors**; negative control (fact with `retrieved_at` deleted) correctly fails with 1 error, proving the validator bites.

## 4. Test-suite re-run and regression (S8)

- `cd services/api && python -m pytest tests -q` → **87 passed** (matches producer claim; 2 test_health + 38 test_bbl + 47 test_pluto_soda; connector-only re-run: 85 passed).
- `python .github/scripts/validate_contracts.py` (worktree root) → `Checked 6 schema file(s); 0 failure(s)`.
- `git show --stat 9e22839`: 26 files, all inside `allowed_paths` (`services/api/app/connectors/**`, `tests/connectors/**`, `tests/fixtures/pluto/**`, `services/api/pyproject.toml`, `project-control/reports/M1-T002-*`). `packages/contracts/**` untouched. pyproject change is dev-extra-only (`jsonschema>=4.21,<5`); connector runtime is stdlib-only (low-storage policy respected; fixture pack 273 KB).
- Test quality: I inspected assertions, not just outcomes. S1–S8 assertions match the packet's expected outcomes value-by-value (e.g. S1 asserts `original_value "23121"` verbatim vs `normalized_value 23121` int vs `units "square feet"`; S5a asserts exactly 3 transport calls and sleeps `[0.5, 1.0]`; S4a asserts `transport.calls == []`). Synthetic in-test variants (conflicting borocode, mangled version, injected vintage dates, unknown column) are clearly labeled SYNTHETIC and exercise connector logic only — no fabricated data presented as official.

## 5. Adjudications

### 5.1 S3a deviation (packet BBL 9999999999 vs producer's 5999999999) — **APPROVED**

The packet's S3(a) called `9999999999` "syntactically valid". Under the ACCEPTED M0-T009 contract (`common.schema.json#/$defs/bbl`, pattern `^[1-5][0-9]{5}[0-9]{4}$`, grounded in the Geoclient recognition rule "first digit is 1-5"), borough digit 9 is client-side invalid — and the packet's own S4(a) requires borough 6 to be rejected with no network call, so borough 9 cannot coherently reach the network. The producer did the right thing on all three axes: (a) rejects `9999999999` as `validation_error/invalid_borough` with zero transport calls (tested); (b) live-captured F03b (`5999999999` — valid pattern, borough 5, block 99999, lot 9999 boundary values — → `[]`) to prove the official no-match path; (c) retained F03 documenting that the raw API happens to return `[]` for `9999999999` anyway. The packet text was internally inconsistent; the implementation follows the binding contract. No task-packet change required, but the orchestrator may annotate S3a for the record.

### 5.2 Additive fact keys (`dataset_id`, `request_url`, `input_vintages`) — **APPROVED**

`source_fact.schema.json` v1 is Draft 2020-12 and contains **no `additionalProperties` keyword** (verified by direct read), so additional properties are permitted by default. The three additive keys collide with no defined key; the full v1 required set (all 12 fields) is present and correctly used on every fact: `original_value` verbatim (untrimmed, e.g. `"1000010100.00000000"`), `normalized_value` deterministic, `units` string-or-null (defined optional key, used per dictionary), `effective_date` explicitly `null` — correct, because PLUTO publishes per-INPUT vintages (the eight `*date` columns, carried verbatim in `input_vintages` when present) but no official per-FIELD→input mapping; mapping one would be a guess, which the PRD forbids. Independently re-validated live (§3). Observation (non-blocking): the additive keys are currently unconstrained by the schema; a future contract minor version could formalize them.

## 6. Corrections (proposed; for orchestrator/producer — reviewer edits nothing)

- **C1 (minor, semantics):** `yearbuilt` 0/null means "unknown" per dictionary p.34–35 (research §4.1), and live BBL 1000010100 has `yearbuilt "0"` → normalized `0` with `confidence 1.0` and no unknown marker — unlike the parallel `numfloors` rule which gets an explicit note. Nothing is fabricated (value is verbatim official), but a downstream consumer could read 0 as a year. Add a `yearbuilt_unknown` note analogous to `numfloors_not_available`, or explicitly document in the connector docstring that 0-means-unknown interpretation is owned by the property-profile mapping layer.
- **C2 (cosmetic, report):** producer report §5/S1 says "66 facts from F1"; the F1 record yields **67** facts (67 record keys, all in the inventory; confirmed offline and live).
- **C3 (low, taxonomy):** a non-drift 400 (e.g. F13b `query.soql.type-mismatch`) is raised as `SourceUnavailableError` (`error_type: "source_unavailable"`). It is correctly unretried and correctly distinct from `schema_drift`, and `detail.error_code` preserves the signature, but "source_unavailable" can misclassify a client-side query bug as an outage on dashboards. Consider a distinct `bad_request`-style type in a follow-up; not blocking (packet S5 only mandated drift-vs-other-400 distinctness, which holds).
- **C4 (cosmetic, provenance log):** producer report §4 capture log lists F8 as 202,647 bytes while the stored `response_body_raw` is 202,598 chars (likely trailing-byte/newline accounting); and the commit message says "18 official KB-scale fixtures" though F07 is (correctly, per the risk register) synthetic-from-official-doc. Both trivially misstated; fixture files themselves are accurate.

## 7. Defects

None material. No wrong mapping, no guessed schema, no contract violation, no fixture fabrication found. The one behavior gap the producer disclosed (no live-transport run in the suite, by design) was closed by this review's live smoke (§3).

## 8. Reproduction commands (from `.claude/worktrees/M1-T002` unless noted)

```
cd services/api && python -m pytest tests -q                      # 87 passed
cd services/api && python -m pytest tests/connectors -q           # 85 passed
python .github/scripts/validate_contracts.py                      # 6 schemas, 0 failures
git show --stat --oneline 9e22839                                 # file scope
# live spot-checks (KB-scale, spaced):
curl "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010100"
curl "https://data.cityofnewyork.us/resource/64uk-42ks.json?%24select=bbl&%24order=bbl&%24limit=2"
curl "https://data.cityofnewyork.us/resource/64uk-42ks.json?%24select=version&%24limit=1"
curl "https://data.cityofnewyork.us/resource/64uk-42ks.json?%24select=nonexistent_col"   # 400 no-such-column
curl "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000047501"
curl "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query?where=BBL%3D1000010100&outFields=BBL,LotArea,ZoneDist1,SPDist1,LotFront,LotDepth,YearBuilt,Version&returnGeometry=false&f=json"
# live drift + smoke (see §3): python one-liners importing app.connectors.pluto_soda from services/api
```

## 9. Recommendation

**G1 PASS.** Apply C1–C4 at the orchestrator's discretion (C1 is the only one touching behavior semantics and can also be carried as an explicit note into the property-profile mapping task). Suitable to proceed to G3; the G3 reviewer can reuse the §8 commands and should exercise the condo unit-lot path (`fetch_by_bbl('1000041001')` → no_match with billing-lot explanation) live.
