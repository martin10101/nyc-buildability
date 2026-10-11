# Research log — every search the library rests on

**Unreviewed draft (ADR-007).** Each row: source · query · result (found / not found / access blocked) ·
the missing item · the next step. Rows marked **[producer]** are the producer's own checks at commit
`aac892fc`; the rest are from the four read-only research-helper returns (H1 closure, H3 DOB, H4 BSA/DCP,
H6 options), saved outside git in the session folder and cited here.

## Producer checks (this task)

| Source | Query | Result | Missing item | Next step |
|---|---|---|---|---|
| [producer] `services/api/app/rules/rulesets/*.rule.json` @ aac892fc | which sections each R6B rule formally cites (`citations[]`) and its applicability set | found | — | none; this is the authoritative `handled_by` source |
| [producer] `r6b_height.rule.json` | does it compute 23-431 / 23-433? | found: `citations[]` = 23-432 only; `computation` emits the 23-432 table only; 23-431/23-433 appear in prose/interactions as context | a rule that computes street-wall placement (23-431) and setback depth (23-433) | RECOMMEND rule-coverage rows; corrects H6's "r6b_height handles 23-431/23-432/23-433" |
| [producer] `docs/research/zr-snapshots/v1/` (185 snapshots) | snapshot_id, content_digest_sha256, last_amended, url for every section + 12-10 term in the closure | found; 68 of 73 sections captured; 30 of 38 terms captured | 24-11, 24-111, 23-154, 77-00, shared-housing sections; 8 12-10 terms | capture via the print/PDF channel (see Recommendations in the producer report) |
| [producer] capture-claim check (`verify_captures.py`) | does every captured entry's snapshot_id + digest equal the snapshot file's, and every NOT CAPTURED entry have no file? | found: PASS (73 sections + 38 terms) | — | re-run on any edit |
| [producer] `zr-12-10.snapshot.json` | does it hold the "wide street" / "narrow street" verbatim text? | found: section_title "Definitions - wide street and narrow street"; contains "wide"/"narrow"/"75 feet"; last amended 2026-03-26; digest 23a9ccad… | — | **confirms the discrepancy below** |
| [producer] `NB-06` rev 2 (read-only) | what does search S3 say about the wide/narrow capture? | found: S3 / evidence record it as "NOT captured in the repository snapshot set" | — | **DISCREPANCY** — see below; NB-06 not edited here (read-only + forbidden path) |
| [producer] `scripts/lanes/check_lane_paths.py --coverage` | lane ownership of the new files | found: PASS (10191 files, each owned by one lane) | — | none |

## H1 — ZR cross-reference closure

| Source | Query | Result | Missing item | Next step |
|---|---|---|---|---|
| `git show aac892fc …/rulesets/*.rule.json` | R6B applicability + citations | found | — | none |
| `docs/research/zr-snapshots/v1/` | every start-set section + its references | found (all in-scope numbered sections captured) | — | none |
| ZR portal `/article-ii/chapter-3/23-344` (live) | section text + references + amend date | found (matches snapshot; R1-R12; Last Amended 12/5/2024) | — | none |
| ZR portal `/article-i/chapter-2/12-10` (live) | wide/narrow street verbatim definitions | **access blocked** — page truncated before the street definitions | live re-verification of the wide/narrow text | re-capture via print/PDF or a browser-UA GET and sha-pin; meanwhile rely on `zr-12-10.snapshot.json` |
| snapshot scan for uncaptured referenced ids | 23-361, 23-425, 25-621/622/85, 26-50, 23-613, 23-30/63, 37-727/73, 74-761 | not found (uncaptured) | — | none — each out of scope for an R6B/C2-2 lot |
| snapshot scan for 12-10 term snapshots | MIH areas, UAP developments, outer court, bulk, Commercial District/use, community facility use, residential use, development/enlargement/conversion, detached/semi-/attached/zero-lot-line, required yard | not found | the 8 load-bearing 12-10 terms | capture these 12-10 terms via the print/PDF channel |

## H3 — DOB Buildings Bulletins + determinations

| Source | Query | Result | Missing item | Next step |
|---|---|---|---|---|
| DOB Buildings Bulletins index + all 18 year pages (2008-2025) | bulletins touching floor area / lot / height / setback / street wall / yard / DU / obstructions / cellar / court | found (the rows in `pitfalls.md`, titles only) | verbatim PDF text | confirm each hit's status + cited section numbers |
| DOB determinations page | a browsable list of issued ZRD1/CCD1 | **not found** (submission-only via DOB NOW; per-job retrieval) | a public determinations index | none without a specific job number; never generalize |
| nyc.gov search: BB 2019-009 / 2009-030 / 2016-011 / 2020-003 / 2016-012 | subject/date/scope/rescission | found (snippets) | the PDF bytes | a human browser session if verbatim text is needed |
| direct PDF fetch `bb_2019-009.pdf` | the bulletin text | **access blocked** — served 716 KB binary the fetch tool could not parse (not a 403) | extractable text | human browser session (registry §9.4 G1 method) |
| (not re-verified) status of BB 2008-003, 2011-010, 2012-008, 2018-002 | current vs rescinded | not checked | current status | confirm before citing (older bulletins are rescinded in bulk) |

## H4 — BSA + DCP

| Source | Query | Result | Missing item | Next step |
|---|---|---|---|---|
| BSA resolutions search portal | how to search / fields / coverage | found (1998+; no API; keyword = address / ZR section / application type) | — | use Open Data for machine access |
| NYC Open Data `yvxd-uipr` api/views | dataset fields / attribution / freshness | found (25 fields; attribution BSA) | — | a G1 reviewer re-reads for a registry row |
| `data.cityofnewyork.us/resource/yvxd-uipr.json` `$where zoning_district LIKE '%R6B%'` (+ 72-21, 73-%) | R6B cases + cited sections | found (47 R6B records; ~22 transcribed with cal. no., section, date, status) | — | discovery examples only; never generalize |
| [producer] `yvxd-uipr` freshness | convert `rowsUpdatedAt` epoch 1790020601 to UTC | found: **1790020601 = 2026-09-21T19:56:41Z** (producer-computed with `datetime.utcfromtimestamp`); the fetch model's "Jan 17 2025" is wrong (that would be epoch 1737072000) | — | record 2026-09-21T19:56:41Z in any BSA registry row (G1 A2) |
| 2025 DCP Zoning Handbook PDF | R6B / contextual / overlay warnings + page numbers | **access blocked** — ">10 MB" fetch limit + nyc.gov 403 | Handbook page-cited warnings | browser capture of the R6 / contextual-district / overlay pages |
| DCP districts-tools `r6.page` / `residence-districts-r1-r10.page` (fetch + curl) | live page / redirect target / R6B content | **access blocked** — "this page has moved"; direct curl HTTP 403 (AkamaiGHost) | the new live URL | resolve in a browser and record the new path |

## H6 — the eleven options

| Source | Query | Result | Missing item | Next step |
|---|---|---|---|---|
| repo grep @ aac892fc | `ELEVEN_OPTIONS` order; rule files; catalogue `rule_ids` | found (order in `options.py` lines 21-33; 6 R6B rules; several catalogue add-ons `rule_ids=()`) | — | used as the canonical order |
| WebFetch ZR `/article-ii/chapter-4/24-11` | community-facility FAR for R6B | found (title; R6B FAR 2.00 / coverage 80 / 60; last amended 12/5/2024) | the snapshot capture | RECOMMEND capture of 24-11 |
| WebFetch ZR `/article-ii/chapter-3/23-154` (both portal hosts) | UAP section text | **access blocked** — HTTP 403 on both hosts | the primary-page read | retry via the print/PDF node channel with a browser UA, or record access_blocked |
| WebSearch "shared housing City of Yes section" | the shared-housing ZR use/density sections | not found (no single clean ZR use-section surfaced) | the exact section numbers | open the City-of-Yes shared-housing provisions (not done) |
| WebSearch / repo | ZR 77-00 (split-lot by district boundary) | not fetched | the 77-xx family text | read the sample "split lot" page + the official 77-00 vs multiple-buildings provisions |

## Open discrepancies and unknowns (preserved, not resolved)

1. **NB-06 vs `zr-12-10.snapshot.json` (CONFIRMED by the producer).** NB-06 rev 2 (search S3; evidence
   lines) records the ZR 12-10 "street, wide" / "street, narrow" text as **not captured**. The producer
   checked `zr-12-10.snapshot.json`: the text **IS captured** (section_title "Definitions - wide street
   and narrow street"; contains "wide"/"narrow"/"75 feet"; last amended 2026-03-26; digest
   `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`). NB-06's claim is stale at this
   commit (likely cause: a search for a hyphenated-term filename, while the text sits in the plain
   `zr-12-10.snapshot.json`). **Not edited here** — NB-06 is read-only and outside this task's allowed
   paths. **Next step (orchestrator):** correct NB-06 search S3 / its freshness note through the
   research-and-verification workflow, or open a research request.
2. **`yvxd-uipr` freshness date (resolved by the producer, G1 A2).** `rowsUpdatedAt` epoch 1790020601 =
   **2026-09-21T19:56:41Z** (UTC), not the "Jan 17 2025" the fetch model rendered (that would be epoch
   1737072000). **Next step:** record 2026-09-21T19:56:41Z in any BSA registry row at a G1 read.
3. **Access blocks to record, never evade:** nyc.gov asset PDFs (bulletins; 716 KB binary unparsed by the
   fetch tool); the 2025 DCP Zoning Handbook (>10 MB + 403); the moved DCP districts-tools pages (403,
   new URL unknown); ZR 23-154 (HTTP 403 on both portal hosts). Each is recorded, not worked around.
4. **Not sure:** the "split lot" meaning (two buildings on one zoning lot vs a district-boundary split);
   the shared-housing ZR section numbers; whether 215-16 Northern Blvd falls under an airport imaginary
   surface; the exact R6B UAP wording; the current status of several older DOB bulletins.
