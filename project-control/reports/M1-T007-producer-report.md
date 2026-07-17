# M1-T007 — Producer report (official-source-researcher)

- **Task:** M1-T007 — Official-source research: DOB NOW Open Data family
- **Producer:** official-source-researcher
- **Date:** 2026-07-17 (all retrievals 07:45–08:05 UTC, live, tokenless, throttled)
- **Status requested:** `awaiting_gate` (G1 data-contract-verifier + G3)
- **Report path:** `project-control/reports/M1-T007-producer-report.md`

## 1. Deliverables produced (new files only; no existing file modified)

1. `docs/research/M1-T007-dob-now-sources.md` — full findings: 11-dataset family inventory (6 recommended core + 5 secondary), S1–S4 evidence sections, failure behaviors, 5 evidenced rule-outs + permit-issuance relationship, fixture-pack proposal, connector plan, 7-item OQ ledger, D1–D13 source register.
2. `docs/research/source-registry-drafts/dob-now.json` — 9 registry records (6 core + 3 secondary; the two child datasets xmmq-y7za/juyv-2jek are documented inside their parents' records since they have no independent location semantics). Valid JSON verified (`python json.load` → 9 records). Every PRD §8.2 field present or explicitly tied to an OQ.
3. `docs/research/fixtures/m1-t007/` — 26 files, 181,972 bytes total: 11 verbatim `$limit=2` samples, 11 verbatim targeted-query fixtures (positive / no-match / HTTP 400 drift signature / serialization probe), 3 labeled extract fixtures (catalog ×2 hosts, views metadata ×16 datasets with raw epochs, row counts ×6), README with every exact command + timestamps.

## 2. Scenario evidence (S1–S6)

### S1 — every recommended dataset live-verified (PASS, evidence attached)
Two catalog queries (api.us.socrata.com + data.cityofnewyork.us hosts) returned identical 21-result sets on 2026-07-17. All 11 family datasets verified via live `api/views/<4x4>.json` (HTTP 200 each; sizes 37,878–210,284 bytes; extract fixture retains verbatim values) AND via live `resource/<4x4>.json?$limit=2` (HTTP 200, 2 records each, verbatim fixtures). Nothing asserted from memory: every ID, name, column count, cadence field, attachment assetId, and description quote traces to a 2026-07-17 fetch.

### S2 — BBL/BIN join semantics from observed records (PASS)
- BBL: 10-digit zero-padded strings observed in 7 datasets (`"1004410016"` etc.); `text` in 5, **`number` in rbx6-tga4/xxbr-ypig** (serialization probe showed NO decimal artifact, unlike PLUTO C6 — single probe, defensive normalization still required, OQ-3); `gis_bbl` naming in dm9a-ab7w; **no BBL at all in xubg-57si**; **only number-typed `bin_number` in 52dp-yji6** (no BBL/address/borough).
- BIN: 7-digit, borough-prefixed, observed in all location-bearing datasets; the only universal join key → BIN-primary fan-out recommended.
- Cross-dataset join PROVEN on one real property (BIN 1006014/BBL 1004410016, taken from an observed record, not guessed): same `job_filing_number M00855935-I1` in w9ak-ipjd (filing) and rbx6-tga4 (permit `M00855935-I1-SG`); boiler filings via `bin_number=1006014`; clean `[]` no-matches in pkdm/xubg/e5aq with separate positive controls from each dataset's own observed BINs.
- Format quirks recorded verbatim: block/lot NOT zero-padded; borough casing differs across datasets for the same BBL ("Manhattan" vs "MANHATTAN"); non-ISO text dates in 52dp-yji6 (`02/22/2018 00:00:00`) and pkdm-hqz6 (`02/15/22 11:08:46 AM`); child tables (xmmq-y7za, juyv-2jek) join only via `job_filing_number`.

### S3 — freshness cross-check (PASS, no staleness)
Stated cadence Daily (10) / Every weekday (1), Automation Yes (all 11) vs observed `rowsUpdatedAt`: **all 11 within 24 h of retrieval** (2026-07-16 14:16Z–21:48Z; raw epochs in fixture; machine-converted via `datetime.fromtimestamp(tz=utc)`, no manual arithmetic). No `degraded_suspected` flag warranted anywhere in the family — M1-T003 ZTLDB precedent checked and not triggered. Rule-out corroboration: bty7-2jhb frozen at 2018-08-07 matches its "Historical data" cadence.

### S4 — negative/deprecated rule-outs with evidence (PASS, 5 rule-outs)
`ipu4-2q9a` ("only includes permits issued in BIS ... see rbx6-tga4" — verbatim), `ic3t-wcy2` ("does not include jobs submitted through DOB NOW" — verbatim), `bs8b-p36w` (COs only to March 2021, "see pkdm-hqz6" — verbatim), `e98g-f8hy` ("Now Retired" in the official name + replacement pointer), `bty7-2jhb` ("this historical dataset is now redundant" — verbatim). Family relationship to permit issuance documented: permits/jobs/COs are split BIS-vs-DOB NOW by filing channel; absence of a DOB NOW record is channel-dependent absence, not "no activity" (findings §6.1).

### S5 — PRD §8.2 completeness (PASS)
All 18 registry fields present in each of the 9 draft records or explicitly marked with an OQ reference (OQ-1 rollout dates/nyc.gov 403; OQ-2 dictionary XLSX extraction; OQ-3 numeric-BBL serialization; OQ-4 facades legacy-cycle depth; OQ-5 device namespaces; OQ-6 possible additional Safety datasets; OQ-7 app token = existing HUMAN_ACTIONS §7 item).

### S6 — no scope creep (PASS)
No connector code, no schema changes, no edits to any existing file. BIS datasets touched only to rule them out. g76y-dcqj / 855j-jady (DOB but not DOB NOW) explicitly deferred to the legacy task.

## 3. Exact fetches (all 2026-07-17, producer session; full register in findings §10)

Catalog ×2 (271 KB each, trimmed to labeled extracts); `api/views` ×16; `resource?$limit=2` ×11; targeted SODA queries ×11 (incl. deliberate HTTP 400 retention); `count(*)` ×6; attachment HEAD probe (200, octet-stream, 74,405 B); `www.nyc.gov/site/buildings/industry/dob-now.page` → **403 recorded**; data.gov mirror page (200, raw-grep `w9ak-ipjd` confirmed — summarizer not trusted per memory guard); data.gov CKAN action API → **404 recorded**; `dev.socrata.com/docs/queries/limit.html` (200, verbatim limits) after `/docs/paging(.html)` → **404 ×2 recorded**.

## 4. Deviations, assumptions, limitations

1. **Worktree base discrepancy (disclosed):** at session start the worktree branch pointed at `2d592bc`, which did NOT contain the task packet; the packet lived at `6392bc1` (the packet's stated base, an ancestor of main). I ran `git merge --ff-only 6392bc1` — a fast-forward pointer move, no commit object created — to obtain the committed packet. No other git state was touched.
2. **Allowed-paths vs outputs tension (disclosed for orchestrator adjudication):** the packet's `outputs` require registry drafts in "the same draft location/format the accepted M1-T003/T004 research used" (= `docs/research/source-registry-drafts/`), but `allowed_paths` lists only the findings doc, fixtures dir, and this report. I followed the outputs clause with a strictly NEW file (`dob-now.json`); no existing draft file was modified. If the orchestrator rules otherwise, the file can be relocated without content change.
3. **Extract fixtures are not full responses:** full catalog (271 KB) and `api/views` (up to 210 KB) responses exceed KB-scale fixture discipline; labeled extracts preserve verbatim values with the exact generating commands in the fixtures README. G1 can re-fetch live to confirm.
4. **Assumption-free claims:** the only compositional inferences (tracking_number structure in 52dp-yji6; `-SG`/`-EL`/`-I1` suffix meanings) are labeled as observed-pattern inferences with dictionary verification routed to OQ-2.
5. **Not done here:** XLSX dictionary content extraction (OQ-2, binary/low-storage), HTTP 429 capture (cannot force politely tokenless), pagination page-pair fixture (deferred to connector build), BIS family research (next task by design).
6. Local footprint: ~1 MB temp files in `%LOCALTEMP%\m1t007` (deletable), 182 KB committed fixtures; no datasets downloaded; disk budget untouched.

## 5. Security/provenance impact

Research-only. Provenance-relevant findings: no per-record version field anywhere in the family (stamp retrieval time + rowsUpdatedAt); join-key pollution in rbx6-tga4 means key-format validation is a provenance-integrity requirement; boiler dataset carries personal names (log-redaction note in its draft record).

## 6. Recommended next tasks

1. **BIS/legacy DOB family research** (already planned as the next task) — required before DOB facts can be labeled complete for any property (channel-split finding, §6.1).
2. Browser-capable capture session for the 403-walled nyc.gov DOB pages (closes OQ-1 here + OQ backlog from M1-T001/T003).
3. Cloud-side (Codespaces/Render) XLSX dictionary extraction pass over the 11 captured attachment assetIds (closes OQ-2, feeds OQ-4/OQ-5).
4. M2 connector-build tasks per findings §8 (BIN-primary fan-out; key-format validation; per-field date parsers; drift check on columns arrays).
