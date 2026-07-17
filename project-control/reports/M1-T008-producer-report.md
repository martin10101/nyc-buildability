# M1-T008 Producer Report — DOB-wide legacy source research

- **Task ID:** M1-T008
- **Producer:** official-source-researcher
- **Date:** 2026-07-17; reworked same day (documentation reconciliation per G3 D1–D4, see §11)
- **Retrievals:** 2026-07-17, tokenless, `data.cityofnewyork.us`, in two same-day sessions: bulk capture **~10:55–11:05 UTC** (authoritative; timestamps embedded in the committed artifacts — catalog extract 10:55Z, views extract 10:56Z, query logs 11:01:25–11:03:54 UTC, response-headers `Date:` 11:04:48 GMT) and a later re-verification **~16:15–16:21 UTC** whose session-only observations are not backed by committed artifacts and are labeled as such in the research doc. An earlier revision of this report wrongly presented 16:15–16:21 UTC as the single retrieval window.
- **Requested status:** `awaiting_gate` (G3 re-review of the D1–D4 documentation rework; producer G2 self-check recorded below)
- **Report path:** `project-control/reports/M1-T008-producer-report.md`

## 1. Files changed (all inside allowed_paths; no code, no contracts, no schema)

| Path | What |
| --- | --- |
| `docs/research/dob-legacy-sources.md` | main research document (12 datasets full treatment, 4 evidence-based rejections, channel-coverage labels, staged priority) |
| `services/api/tests/fixtures/dob_legacy/` (**44 files: 43 fixtures, 146,865 bytes fixtures-only, measured; directory total varies with the README — G1 measured 152,100 bytes with the pre-rework README, post-rework 160,263 bytes**) | SODA fixtures (verbatim response bodies) + 2 producer-assembled metadata extracts + 4 producer-assembled logs/header captures + README with a URL or provenance note for every file. An earlier revision of this report claimed "26 files, ~77 KB", which was wrong |
| `project-control/reports/M1-T008-producer-report.md` | this report |

Forbidden paths untouched. No git write commands, no project_control.py, no gh.

## 2. Scope compliance vs the binding directives (M1-T007-owner-connector-directives.md)

- §6 source list fully covered: BIS family `ipu4-2q9a`, `ic3t-wcy2`, `bs8b-p36w`, `e98g-f8hy`, `bty7-2jhb` + non-BIS flagged `bf97-mjsy`, `g76y-dcqj`, `855j-jady`. Additionally researched (DOB-wide legacy scope + PRD §8.1 "DOB violations and complaints"): `3h2n-5cm9`, `6bgk-3dad`, `eabe-havv`, `6v9u-ndjg`.
- **Naming rule enforced:** `bf97-mjsy` is described exclusively as the DOB Incident Database source (Construction-Related Incidents), never as BIS, in every artifact.
- §5 channel-coverage labeling applied per fact family (research doc §6); §4 staged priority produced (research doc §7); §2/§3 connector-model and parser expectations extended with observed legacy hazards.

## 3. Acceptance scenarios — G2 self-check results

| Scenario | Result | Evidence (exact command outputs in research doc + fixtures) |
| --- | --- | --- |
| S1 every §6 family verified: dataset ID, row count, date range, field inventory from REAL sampled responses, timestamps | PASS | `api/views/<id>.json` ×17 committed in `views_metadata_extract_17_datasets.json` (10:56Z); `$select=count(*)` ×17 committed in `query_log_counts_and_ranges.txt` (11:01 UTC; e.g. ipu4-2q9a 3,989,420; ic3t-wcy2 2,715,651; eabe-havv 3,108,970; e98g-f8hy **0**); min/max, range-filtered, and cast probes committed in the two query logs (e.g. bty7 1989-05-11→2013-04-24; bs8b 2012-07-12→2105-11-05 garbage max; `cast_ipu4` 1989-05-11→2026-07-15; 3h2n 19011215→20260715 / 6bgk 19101004→20260714 filtered); `$limit=2` samples ×17 (fixtures). Session-only LIKE observations (ipu4 `%/1989` 2,985, `%/2026` 4,380; eabe LIKE pair) have no committed artifact and are labeled in the research doc |
| S2 bf97-mjsy per owner C1v2, never labeled BIS | PASS | Research doc §3.3: "documented secondary/future source feeding the M2 property-history/risk fact stage"; re-verified live this session (1,326 rows; 2024-01-03→2026-07-14; rowsUpdatedAt 2026-07-16); grep of the doc confirms no BIS association |
| S3 rate-limit/auth behavior observed or cited | PASS | ~60+ tokenless requests across the two sessions; **no 429/401/403** observed; NOT all 200 — one committed **HTTP 500 `internal-error`** (tag `c4361147-3ff1-4403-b992-78910fb4c383`) on the valid cast aggregation `ic3t_cast_range` (`query_log_key_probes.txt` — connector-relevant failure signature, disclosed in research doc §3.1/§4/§5), plus the deliberate HTTP 400 drift probe; pooled tokenless throttle + app-token lift cited to `dev.socrata.com/docs/app-tokens` (M1-T001 E7) and `docs/queries/limit.html` (M1-T007 §5 verbatim capture); SODA 2.1 `newBackend:true` confirmed on all 12. An earlier revision of this row claimed "all 200", which was contradicted by the committed log |
| S4 channel-coverage labeling per §5; gaps/overlaps with DOB NOW explicit | PASS | Research doc §6 table: per-family BIS vs DOB NOW channel + residual gaps (pre-2012-07 COs, AHV since 2023-04, BIS property master EMPTY, pre-2000 job actions, pre-1989 permits); duplication overlap 3h2n↔855j PROVEN with fixture |
| S5 staged priority per §4 tied to M2 | PASS | Research doc §7: Stage A ic3t/ipu4/bs8b (legacy twins of the directive's first-priority DOB NOW trio; unlocks honest labeling), Stage B dedup-aware violations+complaints (M2 risk stage), Stage C bf97-mjsy/i296-73x5/g76y-dcqj, never-connect bty7/e98g |
| S6 ≥1 candidate examined and rejected with reason | PASS | 4 rejections with live metadata evidence (research doc §8): t8hj-ruu2 (licensee-keyed), ndq3-kuef (no property keys at all), iz2q-9x8d (frozen 2024-01-02 despite "Daily"), nyis-y4yr (frozen 2024-01-03; out of feasibility scope) |
| S7 no schema guessed; fixtures KB-scale; no bulk data | PASS | Every field claim traces to a live `api/views` columns array or a captured response; fixtures total **146,865 bytes (43 files, measured; unchanged by the rework)**; the G1-quoted 152,100 bytes was the directory total including the pre-rework README (fixtures-only vs directory-total must always be distinguished; post-rework directory total 160,263 bytes because the README grew); largest single committed artifact is the 87,829-byte views-metadata extract; nothing citywide downloaded |

## 4. Key commands run (representative; full register in research doc §11)

```
curl "https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=DOB&only=dataset&limit=150"                     → 200, resultSetSize 71 (43 DOB-attributed; committed: catalog_dob_sweep_extract.json)
curl "https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=%22Department%20of%20Buildings%22&only=dataset&limit=150" → 200, resultSetSize 342 (34 DOB-attributed extracted; same committed extract)
# (later re-verification session, no committed artifact, labeled in doc §2.1: q=DOB&limit=100 on both catalog endpoints → 200, resultSetSize 82, identical ID set)
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
- Date-range endpoints for text-date datasets established by range-filtered/cast probes, not full-year sweeps. 6bgk-3dad and 3h2n-5cm9 ranges ARE quantified by committed range-filtered probes (6bgk 19101004→20260714, 64 garbage rows; 3h2n 19011215→20260715, 31 garbage rows; `query_log_key_probes.txt`), but the pre-1930s minima are suspect year mis-keys (one proven case) and per-decade distribution is unprobed — OQ-6 (re-scoped).
- Rejected candidates iz2q-9x8d/nyis-y4yr overlap with ic3t-wcy2 not verified (irrelevant after rejection; recorded as unknown).
- One-day observation (two same-day sessions); rowsUpdatedAt cadence conclusions are one-day snapshots (though g76y's 3-year gap and bty7's 8-year freeze are unambiguous).
- Several session-only observations lack committed artifacts and are explicitly labeled in the research doc: the `q=DOB&limit=100`→82 catalog checks, the eabe rowsUpdatedAt 16:15:31Z refresh, ipu4/eabe LIKE-year counts, ic3t `%/2000`→48,159, the 3h2n `violation_category` group-by counts, eabe `count(distinct dobrundate)`=1, the 6v9u `code=I2` lookup response, and the 28-result AHV catalog probe. None of them is load-bearing alone; committed artifacts cover the substantive conclusions.
- Tokenless capture: 429 behavior not observed and not forced.

## 8. Security/provenance impact

- Research only; no production code, contracts, or connectors changed.
- 6bgk-3dad carries respondent PII-adjacent fields (names/addresses) and eabe-havv complaint records — flagged in the research doc for §17 redaction handling at connector build.
- All fixtures are public official Open Data. Retrieval timestamps are preserved where the artifact embeds them (extracts, query logs, response headers — all bulk-capture session); plain JSON response bodies embed no timestamps and are dated to 2026-07-17 at session granularity. The fixtures README carries an exact URL or an explicit provenance note (including "URL not logged at capture" where true) for every one of the 44 files.

## 9. New risks / dependencies surfaced

- AHV coverage gap (2023-04→present) has no official structured source — product must not imply AHV completeness.
- BIS property master vacuum (e98g-f8hy empty) shifts existing-building facts fully onto PLUTO/Geoclient/CO records for M2.
- Violations counting is wrong-by-construction without 3h2n↔855j dedup — must be contracted into the Stage B connector task.

## 10. Recommended next tasks

1. G1 (data-contract-verifier) on this research; then registry-draft authoring for the 12 sources (a follow-up producer task — registry drafts were NOT in this packet's allowed paths).
2. Contract the Stage A legacy connectors (ic3t-wcy2, ipu4-2q9a, bs8b-p36w) with the parser-hardening list in research doc §7 as explicit acceptance scenarios.
3. Cloud-side extraction of the 12 data dictionaries (OQ-1) bundled with the M1-T007 OQ-2 extraction (same tooling, same session).
4. Browser-capable capture session for the accumulated nyc.gov 403 backlog (now incl. complaint-category PDF and AHV rollout pages).

## 11. Rework record (2026-07-17, documentation reconciliation per G3 FAIL / G1 blocking corrections)

Scope: documentation-only rework of G3 defects D1–D4 (`project-control/reports/M1-T008-G3-code-review.md`) and G1 corrections D1/D2 (`M1-T008-G1-data-contract-review.md`). **No re-research, no new network requests, no fixture-byte changes; fixtures retained as-is.** Files touched: `docs/research/dob-legacy-sources.md`, `services/api/tests/fixtures/dob_legacy/README.md`, this report — nothing else.

- **D1 (provenance narrative):** doc header, §2.1, §2.2, §3.3, §4, §8, §11, README header, and this report now state the true two-session structure — bulk capture ~10:55–11:05 UTC (authoritative, per the timestamps embedded in the committed artifacts) and re-verification ~16:15–16:21 UTC. Every observation unique to the second session is labeled "no committed artifact" (catalog 82-result checks, eabe 16:15:31Z refresh, ipu4/eabe LIKE counts, 3h2n category group-by, eabe distinct-dobrundate, 6v9u code lookup, AHV catalog probe). The false "single 16:15–16:21 window" and the unevidenced eabe "server-time anchor" (epoch 1784304931) were removed; §2.2 now shows the committed eabe `rowsUpdatedAt` 2026-07-16T16:49:33Z. §2.1 rewritten to match the committed catalog extract (`only=dataset&limit=150`: q=DOB → 71; q="Department of Buildings" → 342 — the second sweep was previously unmentioned). The G1 reviewer's independent reproductions are NOT cited as producer provenance.
- **D2 (inventory):** corrected everywhere to the measured values — 44 files = 43 fixtures (146,865 bytes fixtures-only, byte-identical before and after rework) + README; fixtures-only vs directory-total is now stated explicitly everywhere (G1's 152,100 bytes included the pre-rework README; the directory total moves with README edits and is 160,263 bytes post-rework) so the numbers cannot read as contradictory. README now inventories all 44 files with a URL or provenance note each, including the 18 previously undocumented files (3 query logs, 2 producer-assembled extracts, response-headers capture, ECB join pair, 4 rejected-candidate samples, `sample_bf97-mjsy.json`, `sample_i296-73x5.json`, the two earlier `$select` variants, the `bin__=0000000` no-match, and `sample_e98g-f8hy.json`, documented as a byte-identical duplicate of `sample_e98g-f8hy_empty.json` and retained as-is). The "every file is a VERBATIM HTTP response body" claim is now scoped to the `sample_*.json`/`query_*.json` files; the 2 extracts and 4 logs are re-labeled producer-assembled captures.
- **D3 (contradicted/omitted evidence):** the committed HTTP 500 on `ic3t_cast_range` is now disclosed in doc §3.1, §4, §5 and S3 above (the "all 200 / ~60 requests in 6 min" claim is corrected); the quantified 6bgk (19101004→20260714, 64 garbage) and 3h2n (19011215→20260715, 31 garbage) ranges are folded into §3.2, §6, and OQ-6 (re-scoped from "unquantified"); §6's "3h2n 1988→present" replaced with the committed probe values plus the mis-key hedge; the successful `cast_ipu4`/`eabe_cast_range` `::floating_timestamp` technique is surfaced in §3.1/§3.2/§5/§7 as a Stage A range-check tool with a 500-fallback warning.
- **D4 (minor):** §4 now notes its table rows are `$limit=3` slices with the committed full totals (eabe 17, 6bgk 6); the ECB join pair's `19390711`-vs-`20000711` year mis-key added to the §1 date-hazard list and §7 hardening; unfixtured §11/D10 quantifiers enumerated in §7 limitations above.

Self-verification (commands + outputs in the return packet): fixture recount measured 44 files / 146,865 fixture bytes (unchanged; directory total now 160,263 bytes only because this README/report rework grew the README from 5,235 bytes — G1's 152,100 measurement included the pre-rework README); grep over the three edited files for residual "16:15–16:21"-as-sole-window, "26 files", "77 KB", or unscoped "all 200"/"VERBATIM" claims returns only the explicit corrections/labels; `git status` (read-only) confirms only the three allowed files are modified and no fixture bytes changed.

**Requested status: `awaiting_gate`** (G3 re-review, rework scope only per the G3 report).
