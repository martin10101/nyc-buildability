# M1-T008 Producer Report — DOB-wide legacy source research

- **Task ID:** M1-T008
- **Producer:** official-source-researcher
- **Date:** 2026-07-17 (all live retrievals 16:15–16:21 UTC, tokenless, `data.cityofnewyork.us`)
- **Requested status:** `awaiting_gate` (G1 next; producer G2 self-check recorded below)
- **Report path:** `project-control/reports/M1-T008-producer-report.md`

## 1. Files changed (all inside allowed_paths; no code, no contracts, no schema)

| Path | What |
| --- | --- |
| `docs/research/dob-legacy-sources.md` | main research document (12 datasets full treatment, 4 evidence-based rejections, channel-coverage labels, staged priority) |
| `services/api/tests/fixtures/dob_legacy/` (26 files, ~77 KB total) | verbatim SODA fixtures + README with exact URL per file |
| `project-control/reports/M1-T008-producer-report.md` | this report |

Forbidden paths untouched. No git write commands, no project_control.py, no gh.

## 2. Scope compliance vs the binding directives (M1-T007-owner-connector-directives.md)

- §6 source list fully covered: BIS family `ipu4-2q9a`, `ic3t-wcy2`, `bs8b-p36w`, `e98g-f8hy`, `bty7-2jhb` + non-BIS flagged `bf97-mjsy`, `g76y-dcqj`, `855j-jady`. Additionally researched (DOB-wide legacy scope + PRD §8.1 "DOB violations and complaints"): `3h2n-5cm9`, `6bgk-3dad`, `eabe-havv`, `6v9u-ndjg`.
- **Naming rule enforced:** `bf97-mjsy` is described exclusively as the DOB Incident Database source (Construction-Related Incidents), never as BIS, in every artifact.
- §5 channel-coverage labeling applied per fact family (research doc §6); §4 staged priority produced (research doc §7); §2/§3 connector-model and parser expectations extended with observed legacy hazards.

## 3. Acceptance scenarios — G2 self-check results

| Scenario | Result | Evidence (exact command outputs in research doc + fixtures) |
| --- | --- | --- |
| S1 every §6 family verified: dataset ID, row count, date range, field inventory from REAL sampled responses, timestamps | PASS | `api/views/<id>.json` ×17 at ~16:16Z; `$select=count(*)` ×12 at 16:17:50Z (e.g. ipu4-2q9a 3,989,420; ic3t-wcy2 2,715,651; eabe-havv 3,108,970; e98g-f8hy **0**); min/max + LIKE-year probes at 16:18:52Z (e.g. bty7 1989-05-11→2013-04-24; bs8b 2012-07-12→2105-11-05 garbage max; ipu4 2,985 rows @ `%/1989`, 4,380 @ `%/2026`); `$limit=2` samples ×12 (fixtures) |
| S2 bf97-mjsy per owner C1v2, never labeled BIS | PASS | Research doc §3.3: "documented secondary/future source feeding the M2 property-history/risk fact stage"; re-verified live this session (1,326 rows; 2024-01-03→2026-07-14; rowsUpdatedAt 2026-07-16); grep of the doc confirms no BIS association |
| S3 rate-limit/auth behavior observed or cited | PASS | ~60 tokenless requests in 6 min, all 200, no 429/401/403; pooled tokenless throttle + app-token lift cited to `dev.socrata.com/docs/app-tokens` (M1-T001 E7) and `docs/queries/limit.html` (M1-T007 §5 verbatim capture); SODA 2.1 `newBackend:true` confirmed on all 12 |
| S4 channel-coverage labeling per §5; gaps/overlaps with DOB NOW explicit | PASS | Research doc §6 table: per-family BIS vs DOB NOW channel + residual gaps (pre-2012-07 COs, AHV since 2023-04, BIS property master EMPTY, pre-2000 job actions, pre-1989 permits); duplication overlap 3h2n↔855j PROVEN with fixture |
| S5 staged priority per §4 tied to M2 | PASS | Research doc §7: Stage A ic3t/ipu4/bs8b (legacy twins of the directive's first-priority DOB NOW trio; unlocks honest labeling), Stage B dedup-aware violations+complaints (M2 risk stage), Stage C bf97-mjsy/i296-73x5/g76y-dcqj, never-connect bty7/e98g |
| S6 ≥1 candidate examined and rejected with reason | PASS | 4 rejections with live metadata evidence (research doc §8): t8hj-ruu2 (licensee-keyed), ndq3-kuef (no property keys at all), iz2q-9x8d (frozen 2024-01-02 despite "Daily"), nyis-y4yr (frozen 2024-01-03; out of feasibility scope) |
| S7 no schema guessed; fixtures KB-scale; no bulk data | PASS | Every field claim traces to a live `api/views` columns array or a verbatim `$limit≤3` response; fixtures total ~77 KB; largest single transfer this session was a 142 KB metadata document; nothing citywide downloaded |

## 4. Key commands run (representative; full register in research doc §11)

```
curl "https://data.cityofnewyork.us/api/catalog/v1?q=DOB&limit=100&search_context=data.cityofnewyork.us"   → 200, resultSetSize 82
curl "https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=DOB&limit=100" → 200, identical 82
curl "https://data.cityofnewyork.us/api/views/<id>.json"  ×17                                              → 200 each
curl "https://data.cityofnewyork.us/resource/<id>.json?$limit=2" ×12                                       → 200 each
curl ".../resource/<id>.json?$select=count(*) as n" ×12                                                    → e.g. e98g-f8hy [{"n":"0"}]
curl ".../resource/ic3t-wcy2.json?$select=length(bbl) as len,count(*) as n&$group=len&$order=n DESC"       → len 10: 1,802,216; len 7: 884,315; null: 29,120
curl ".../resource/ic3t-wcy2.json?bin__=1006014&$select=...bbl..."                                         → bbl "1006014" AND "1004410016" on same job
curl ".../resource/855j-jady.json?bin=1006014&$select=violation_number,..."                                → "040618LBLVIO00614" (dup of 3h2n "00614"@"20180406")
curl ".../resource/ipu4-2q9a.json?$select=not_a_real_column&$limit=1"                                      → HTTP 400 query.soql.no-such-column
curl ".../api/catalog/v1?q=after%20hour%20variance&limit=10"                                               → 28 results, no g76y-dcqj successor
```

## 5. Expected vs actual (surprises disclosed)

- Expected the BIS family to be the straightforward "old but stable" channel; actual: systemic BIN-in-BBL pollution (32.6% of ic3t rows), TEST records in production data, garbage/mixed date encodings, and a future-dated CO (2105-11-05).
- Expected e98g-f8hy to be a retired-but-readable BIS property extract; actual: **0 rows** — the BIS property master has left Open Data entirely.
- Expected g76y-dcqj to be a live DOB NOW output; actual: frozen 2023-04-18 with no successor dataset.
- Expected 855j-jady ("newer" violations) to start ~2023; actual: violation_issue_date back to 1989-10-12 (migrated/payable-in-DOB-NOW items) — issuance date cannot partition the two civil-penalty datasets.

## 6. Assumptions and defaults

- BIN 1006014 / BBL 1004410016 reused as the cross-task anchor property (continuity with M1-T007 evidence); its `[]` results in bs8b-p36w and bf97-mjsy treated as legitimate no-match, not source failure.
- The LL84 energy-disclosure series and OATH datasets were classified out of scope (energy benchmarking / other agency), not researched — recorded, not silently dropped.
- `dev.socrata.com` pagination/app-token facts cited from accepted M1-T001/M1-T007 evidence rather than re-fetched (identical platform, same week).

## 7. Known limitations

- Data-dictionary XLSX/PDF attachments not content-extracted (binary; octet-stream API; low-storage policy) — OQ-1/OQ-3; value-domain semantics (violation type codes, complaint categories, infraction codes) rest on observation only.
- Date-range endpoints for text-date datasets established by LIKE-year probes at the boundary years, not full-year sweeps; 6bgk-3dad range unquantified (garbage min "0") — OQ-6.
- Rejected candidates iz2q-9x8d/nyis-y4yr overlap with ic3t-wcy2 not verified (irrelevant after rejection; recorded as unknown).
- Single-session observation; rowsUpdatedAt cadence conclusions are one-day snapshots (though g76y's 3-year gap and bty7's 8-year freeze are unambiguous).
- Tokenless capture: 429 behavior not observed and not forced.

## 8. Security/provenance impact

- Research only; no production code, contracts, or connectors changed.
- 6bgk-3dad carries respondent PII-adjacent fields (names/addresses) and eabe-havv complaint records — flagged in the research doc for §17 redaction handling at connector build.
- All fixtures are public official Open Data; retrieval timestamps and exact URLs preserved for every artifact.

## 9. New risks / dependencies surfaced

- AHV coverage gap (2023-04→present) has no official structured source — product must not imply AHV completeness.
- BIS property master vacuum (e98g-f8hy empty) shifts existing-building facts fully onto PLUTO/Geoclient/CO records for M2.
- Violations counting is wrong-by-construction without 3h2n↔855j dedup — must be contracted into the Stage B connector task.

## 10. Recommended next tasks

1. G1 (data-contract-verifier) on this research; then registry-draft authoring for the 12 sources (a follow-up producer task — registry drafts were NOT in this packet's allowed paths).
2. Contract the Stage A legacy connectors (ic3t-wcy2, ipu4-2q9a, bs8b-p36w) with the parser-hardening list in research doc §7 as explicit acceptance scenarios.
3. Cloud-side extraction of the 12 data dictionaries (OQ-1) bundled with the M1-T007 OQ-2 extraction (same tooling, same session).
4. Browser-capable capture session for the accumulated nyc.gov 403 backlog (now incl. complaint-category PDF and AHV rollout pages).
