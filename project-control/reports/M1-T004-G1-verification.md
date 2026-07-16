# M1-T004 — G1 Source and Data-Contract Gate Verification

- **Task:** M1-T004 — Official-source research: NYC Zoning Resolution text corpus
- **Gate:** G1 (source and data-contract)
- **Reviewer:** data-contract-verifier (independent; did not produce the work)
- **Review date / retrieval date for all live verifications:** 2026-07-16
- **Verdict:** **PASS** (with 9 required corrections listed in §5; none invalidates the producer's findings; no guessed claim found; this review additionally RESOLVED both [NEEDS G1 RE-VERIFICATION] items and two OQ-ledger entries via official channels)
- **Method:** Independent live re-verification against official sources (raw curl GET/HEAD on the ZR portal with grep extraction — no reliance on WebFetch summarization for any verbatim claim; Socrata catalog API; council.nyc.gov; legistar.council.nyc.gov; Drupal AJAX endpoint probing). KB-scale fetches only; HEAD-only for every PDF; the 504-prone giant node (18523 print route) was deliberately not re-hammered. Producer conclusions read LAST, after acceptance criteria and deliverables.
- Recording note: the reviewer returned this report content to the orchestrator per ADR-005 (read-only reviewer). **This file is an orchestrator TRANSCRIPTION with condensed formatting in §1.9–§2 and §8 (evidence-index rows compressed to one line each); no finding, correction, verdict, or evidence value was altered.** The reviewer's exact return is preserved verbatim at `project-control/reports/M1-T004-G1-original-return.md` (audit correction 2026-07-16; do not describe this transcription as verbatim).

Artifacts reviewed: `project-control/tasks/M1-T004.json` (S1–S5), `docs/research/zoning-resolution-2026-07-16.md`, `docs/research/source-registry-drafts/zoning-resolution.json`, `project-control/reports/M1-T004-producer-report.md` (read last).

---

## 1. Mandatory live verifications

### 1.1 Portal identity and server-rendered claim — VERIFIED

- `https://zoningresolution.planning.nyc.gov/` → HTTP 200, **62,772 B** — byte-identical size to the producer's E3 capture.
- Banner verbatim in raw HTML: `All text changes approved by the city council as of <span class='date'>May 20, 2026</span>` — **date unchanged** since the producer's fetch.
- `X-Generator: Drupal 9 (https://www.drupal.org)` observed on BOTH the 200 homepage response and the 404 page (producer had it only via the 404 route) — identity claim strengthened. `X-Pantheon-Styx-Hostname` + `Via: 1.1 varnish` confirmed.
- Homepage paragraph verbatim confirmed in raw HTML: "The Zoning Resolution consists of 14 Articles and 11 Appendices, plus 126 Zoning Maps, …" through "…Articles VIII through XIV set forth the purpose and regulations for each Special Purpose District."
- Alias `https://zr.planning.nyc.gov/` → 200, `<title>Homepage | Zoning Resolution`. **New OQ-7 evidence:** each host emits a self-referencing canonical `Link` header (`<https://zr.planning.nyc.gov/node/54>; rel="canonical"` on the alias; `<https://zoningresolution.planning.nyc.gov/node/54>; rel="canonical"` on the primary) — no cross-host canonical; both hosts claim canonicality (C9).
- Server-rendered claim: all verbatim extractions in this review came from raw HTML via curl+grep with no JS execution — the legal text is fully present in server HTML. Confirmed. (But see C1 for the over-broad "no content XHR endpoints" sentence.)

### 1.2 Section URL pattern and markup — VERIFIED

- `/article-i/chapter-1/11-02` → 200, 84,341 B; raw markup exactly as claimed: `Last Amended</span><div class="field-content"><time datetime="1961-12-15T12:00:00Z" class="datetime">12/15/1961</time>`; node/18416 confirmed in page.
- `/article-i/chapter-2/12-01` → 200; defined-term `<em>` markup confirmed raw (`<em>building</em>`, `<em>commercial building</em>`, `<em>community facility building</em>`, `<em>residential building</em>`, `<em>use</em>`).
- `/article-i/chapter-1` → 200, 346,365 B; section hrefs `/article-i/chapter-1/11-00 … 11-02 … 11-111 …` and in-page anchors `id="11-00"` … confirmed; ALL-CAPS heads (`11-00 TITLE`) and 5-digit subsections (11-111, 11-121) confirmed; §11-47 title verbatim "Applications for Certain Approvals Filed Prior to December 5, 2024".
- `/article-i` → 200; chapter list exactly **1, 2, 3, 5, 6** (no chapter 4) — OQ-5 observation re-confirmed.

### 1.3 §12-01 rules of construction — verbatim VERIFIED (incl. the load-bearing (j))

- (j) both sentences verbatim character-for-character, including "…shall refer only to such specific five-digit Section." and "For Sections starting with 101-00, … shall refer only to such specific six-digit Section." Notable raw-markup fact: the "101-00" inside (j) is itself a hyperlinked cross-reference — `<a class="sec-link-inline" target="_blank" href="/article-x/chapter-1#101-00"><span>101-00</span></a>` — confirming both the rule text and the chapter-anchor href convention in one artifact.
- (a) "The particular shall control the general." ✓; (b) "…the text shall control." ✓; (c) confirmed — with the nit that the source uses straight **double** quotes (`The word "shall" is always mandatory…`, verified via `od -c`) where the research doc rendered single quotes inside a "verbatim" quote (C8).

### 1.4 API-absence probes — ALL RE-CONFIRMED

| Probe | Producer claim | This review (2026-07-16) |
|---|---|---|
| `/jsonapi` | 404 | **404** ✓ |
| `/node/18523?_format=json` | 406 | **406** ✓ (also 18416 → 406) |
| `/sitemap.xml` | 404 | **404** ✓ |
| Socrata catalog `q=zoning resolution` | "12 results, all geodata" | **resultSetSize=25**, 20 shown at limit=20 — every one a geodata/derived product; **no ZR-text dataset** ✓ material claim; count wrong/stale (C7) |

Clean 404s re-confirmed: `/article-i/chapter-1/11-99`, `/article-xv`, `/appendix-a`. robots.txt is stock Drupal (no content-path disallows; `Disallow: /search/` does not cover `/search?search_term=…`).

### 1.5 PDF channels via HEAD — ALL FIVE VERIFIED; Appendix I newly pinned

| File | Producer claim | This review (HEAD) |
|---|---|---|
| `Zoning Resolution Complete.pdf` | 102,565,724 B, LM 2026-06-23 | **200, 102,565,724 B, LM Tue, 23 Jun 2026 00:58:19 GMT** ✓ exact |
| `article/32/Article I.pdf` | 3,170,980 B | **200, 3,170,980 B, LM 2026-06-23 00:46:29** ✓ |
| `article/32/chapters/Chapter 1.pdf` | 149,858 B | **200, 149,858 B, LM 2026-06-23 00:00:38** ✓ |
| `2026-06/AllArticles_23Jun2026_compressed_0.pdf` | 75,589,847 B, LM 2026-06-24 | **200, 75,589,847 B, LM Wed, 24 Jun 2026 21:15:07 GMT** ✓ |
| `appendix/21238/APPENDIX I .pdf` (trailing space) | href observed; NOT HEAD-verified | **NOW VERIFIED: 200, application/pdf, 5,069,648 B, LM Tue, 23 Jun 2026 00:53:12 GMT** (C4) |

`/zr-downloads` → 200, 65,470 B; **exactly 10 archive hrefs, byte-identical to the producer's §2.4 list**; sizes 72.09/74.29/76.03/77.34/77.88/77.74/82.26/82.91/84.74/24.32 MB all present; 72.09 MB ↔ 75,589,847 B cross-check holds. **`/index.php/` nuance (C3):** the raw page DOES contain `/index.php/`-prefixed links — in the theme's site-logo and footer (`/index.php/`, `/index.php/disclaimer`, `/index.php/feedback`) — just not on any archive-PDF href. `/index.php/disclaimer` → **200** (valid Drupal front-controller alias for HTML routes); the prefix 404s only for `/sites/default/files/` static assets — cleanly explaining both the summarizer's error and the producer's E7 404.

### 1.6 Undocumented print-PDF endpoint — VERIFIED (gently)

- `/entityprint/pdf/node/18416` → **302** → `/print/pdf/node/18416` → **200, application/pdf, 44,977 B, Content-Disposition: inline; filename="1102.pdf"** — all three claimed values exact.
- Node 18523 NOT re-requested on the print route. Corroborating: the §12-10 HTML page is **1,315,025 B** — consistent with on-the-fly PDF generation timing out.

### 1.7 The [NEEDS G1 RE-VERIFICATION] items — BOTH RESOLVED

**(a) City of Yes ↔ 12/5/2024 linkage (OQ-2) — RESOLVED via THREE official channels, including the ZR portal itself:**

1. **The portal's own amendment-history metadata (§1.8):** §11-47 popup row: Effective Date **12/5/2024** | ULURP/CPC Report **N240290ZRY** | Project Name **"City of Yes for Housing Opportunity"** | Action **Added** | Description "An amendment modifying multiple Sections to expand opportunities for housing within all zoning districts, and across all 59 of the City's Community Districts".
2. **NYC Council press release** `https://council.nyc.gov/press/2024/12/05/2761/` → **200 to curl** (not bot-blocked): "New York City Council Passes Historic Citywide Zoning Reforms…", 2024-12-05, naming "City of Yes for Housing Opportunity" as the "zoning text amendment, initiated by the Department of City Planning and modified by the Council".
3. **NYC Council Legistar** LU 0181-2024 (`ID=6888427`) → **200 to curl**: "City of Yes for Housing Opportunity (N 240290 ZRY)", status **Adopted**, "Approved, by Council", 12/5/2024.

Corroborating in-portal: §11-47 Last Amended = 12/5/2024; §12-10 carries **48** occurrences of 12/5/2024 stamps. Application number **N 240290 ZRY** now officially pinned. Additional discovery: council.nyc.gov and legistar.council.nyc.gov are **automation-accessible official channels** (no 403) — a materially useful fallback for adoption records (C2).

**(b) Appendix I PDF href** — HEAD-verified this review (§1.5, C4).

### 1.8 NEW FINDING — per-section amendment-history AJAX endpoint (resolves OQ-9, informs OQ-3)

Chapter and section pages carry `href="/nojs/get/amendment/section/{sectionEntityId}"` (class `use-ajax action-icon revisions`, e.g. **22740** for §11-47; **51** such links on the chapter-1 page). Probes:

| Request | Result |
|---|---|
| `GET /nojs/get/amendment/section/22740` (plain) | 404 |
| `GET /nojs/...?_wrapper_format=drupal_ajax` + XHR header | 404 JSON "No route found" |
| **`GET /ajax/get/amendment/section/22740?_wrapper_format=drupal_ajax`** + `X-Requested-With: XMLHttpRequest` | **200, application/json, 4,230 B** — Drupal AJAX command array whose `insert` payload is the `amendment_history_popup` view: 6-column table **Effective Date | ULURP/CPC Report | Project Name | Action | Notes | Description** |

Consequences: **OQ-9 RESOLVED** (structured per-section amendment metadata exists — undocumented, AJAX-wrapper-only, same stability caveats as entity-print, far richer than `/recently-adopted` stubs). **OQ-3 NARROWED** (official column label is "Effective Date"; §11-47 Last Amended = popup Effective Date; adoption-vs-effective not discriminated where they coincide). The ULURP cell links to `http://a030-cpc.nyc.gov/html/cpc/report.aspx?num=N 240290 ZRY` → 302 → `https://www1.nyc.gov/assets/planning/download/pdf/about/cpc/240290.pdf` → 301 → **403** (bot protection; URL pattern officially leaked by the redirect; recorded, not promoted). The producer's "No content XHR endpoints exist in the page JS" is **over-broad** (C1) — the core server-rendered claim remains true, and the module was honestly ledgered as OQ-9. Section-entity IDs (22740) are a **third identifier namespace** distinct from node IDs.

### 1.9 Search, amendment feed, appendix page — VERIFIED with two sharpenings

- `/search?search_term=floor+area+ratio` → **35** `views-row` ✓; `?search_term=city+of+yes` → **0** ✓; `?fulltext=…` → "Your search returned **0** results" ✓ — **but** that wrong-param page also contains **25** `views-row` elements in non-results blocks (C6): fixture ZR-F8 must assert on the results-count string/region, not a global row count.
- `/recently-adopted` → 200; 35 views-rows ✓; newest `147-14 Northern Boulevard (N 220416 ZRQ)` + 5/20/2026 ✓; stub raw-verified: `N 240272 ZRK`, 3/26/2026, hyperlinked `74-948` + "(Map 1)", zero attachments ✓. **New (C5):** pager contains `<a href="?page=30" title="Go to last page">` — the feed is **31 pages deep (0–30)**, not "0–8".
- `/appendix-i` → 200; `APPENDIX%20I%20.pdf` href ✓; Last Amended 2024-11-21 now raw-verified ✓.
- `/node/79` (Preamble) → 200 ✓. `/disclaimer` → 200; "CHANGES ARE MADE PERIODICALLY TO THE ZR…" and "WITHOUT WARRANTIES OF ANY KIND…" verbatim ✓; node/8771 ✓.
- nyc.gov 403s re-confirmed live: `zoning-text.page`, `planning/index.page` (S5 discipline held).

### 1.10 WebFetch-summarizer hazard spot-checks (E1/E9/E11/E14) — ALL SURVIVED RAW RE-CHECK

- E9 §12-10: node 18523 ✓; Last Amended 3/26/2026 ✓; applicability notes verbatim ✓; **"FROM 66-11" attribution CONFIRMED in raw HTML** (`<p>FROM <a class="sec-link-inline" … href="/article-vi/chapter-6#66-11"><span>66-11</span></a>: …`). Parser nuance (C8): FROM prefix has variants — `FROM` (95), `FROM SECTION` (5), `FROM Section` (1), `FROM:` (4), double-space `FROM  ` (6) — and each definition is its own Drupal node (`node--type-defined-term`, e.g. `/node/21970`, `id="term-above-grade mass transit station"`).
- E11 stub fields raw-verified ✓. E14 Appendix I raw-verified ✓. E1 "server-rendered" proven by this review's method ✓.
- The producer-caught `/index.php/` summarizer error was real but mis-diagnosed (C3).

### 1.11 Registry draft (PRD §8.2) — PASS

JSON parses; **19 keys = all 18 PRD §8.2 fields + open_questions**; 12 OQ entries mirroring the doc ledger; honest nulls (`api_dataset_identifier`, `last_successful_ingestion`, `rate_limits.documented`); `health_status: "healthy_observed"` consistent with observations; §12-01(j) quotation matches live verbatim; every factual value traced and re-verified — **no invented value found**. Low-storage clean (KB-scale HTML only; PDFs HEAD-only; zero repo binaries).

## 2. Independent scenario walkthrough (S1–S5)

| Scenario | Result |
|---|---|
| S1 channels | PASS with C1 (amendment-history XHR endpoint existed, ledgered as OQ-9 but not enumerated; found by this review) |
| S2 versioning/effective dates | PASS (banner verbatim unchanged; Last-Amended extremes 1961-12-15 / 2026-03-26 raw-verified; 10 snapshots byte-identical; CoY officially resolved §1.7) |
| S3 structure | PASS (14 articles/11 appendices verbatim; chapter gap re-observed; §12-01 verbatim; markup conventions re-verified; nothing guessed) |
| S4 discrepancies | PASS (banner-date vs PDF-generation dates re-verified; search-param trap reproduced; priority order consistent: HTML primary, snapshots archive, chapter PDFs cross-check, entity-print convenience, nyc.gov browser-only) |
| S5 failure honesty | PASS (403 ×2, clean 404s ×3 re-confirmed; 504 corroborated via 1.3 MB page size without re-hammering; both markers genuine and now resolved by verification, not guessing) |

## 3. Reproduction commands

```
curl -sI https://zoningresolution.planning.nyc.gov/            # X-Generator, Link canonical
curl -s https://zoningresolution.planning.nyc.gov/ | grep -o "All text changes[^<]*<span class='date'>[^<]*</span>"
curl -s -o /dev/null -w "%{http_code}" "https://zoningresolution.planning.nyc.gov/jsonapi"          # 404
curl -s -o /dev/null -w "%{http_code}" "https://zoningresolution.planning.nyc.gov/node/18523?_format=json"  # 406
curl -sI "https://zoningresolution.planning.nyc.gov/sites/default/files/article/Zoning%20Resolution%20Complete.pdf"
curl -sI "https://zoningresolution.planning.nyc.gov/sites/default/files/appendix/21238/APPENDIX%20I%20.pdf"
curl -sI "https://zoningresolution.planning.nyc.gov/print/pdf/node/18416"
curl -s -H "X-Requested-With: XMLHttpRequest" "https://zoningresolution.planning.nyc.gov/ajax/get/amendment/section/22740?_wrapper_format=drupal_ajax"
curl -s -A "Mozilla/5.0" "https://council.nyc.gov/press/2024/12/05/2761/"
curl -s "https://zoningresolution.planning.nyc.gov/search?search_term=floor+area+ratio" | grep -c views-row   # 35
curl -s "https://zoningresolution.planning.nyc.gov/recently-adopted" | grep -o '?page=30.\{0,30\}'            # Go to last page
```

## 4. Open-questions ledger after G1 (OQ-1..OQ-12)

| OQ | Status after this review |
|---|---|
| OQ-1 | STILL OPEN (appendix count reconciliation; /appendix-a 404 re-confirmed) |
| OQ-2 | **RESOLVED** — CoY = 12/5/2024, N 240290 ZRY (portal popup + Council press + Legistar; C2) |
| OQ-3 | **NARROWED** — portal labels per-amendment dates "Effective Date"; adoption-vs-effective undiscriminated where they coincide |
| OQ-4 | STILL OPEN (pre-2024-03-22 text channel; nyc.gov 403) |
| OQ-5 | STILL OPEN (full 14-article chapter inventory at connector build) |
| OQ-6 | STILL OPEN (print-route stability/intent) |
| OQ-7 | **NARROWED** — both hosts self-canonicalize via Link headers; no cross-host canonical (C9) |
| OQ-8 | STILL OPEN (table markup) |
| OQ-9 | **RESOLVED** — /ajax/get/amendment/section/{id} endpoint (C1) |
| OQ-10 | **PARTIALLY RESOLVED** — depth 31 pages (C5); entry mutability open |
| OQ-11 | STILL OPEN — authoritative-publication question is qualified-human/legal; must not be guessed |
| OQ-12 | STILL OPEN (102.6 MB vs 75.6 MB content identity — verify at archiver build) |

## 5. Required corrections (C1–C9)

1. **C1** — record the amendment-history endpoint (markup `/nojs/get/amendment/section/{sectionEntityId}`; working form `GET /ajax/get/amendment/section/{id}?_wrapper_format=drupal_ajax` + `X-Requested-With: XMLHttpRequest` → 200 JSON, 6-column table; §11-47 id 22740: 12/5/2024 | N240290ZRY | City of Yes for Housing Opportunity | Added); mark OQ-9 RESOLVED; fix the over-broad "No content XHR endpoints exist in the page JS" sentence; note section-entity IDs as a third ID namespace; same stability caveats as entity-print.
2. **C2** — mark OQ-2 RESOLVED, remove both [NEEDS G1 RE-VERIFICATION] markers: CoY-HO (N 240290 ZRY) adopted by City Council 2024-12-05 (portal popup + council.nyc.gov/press/2024/12/05/2761/ + Legistar LU 0181-2024). Add: council.nyc.gov and legistar.council.nyc.gov are automation-accessible official channels; CPC report chain `a030-cpc.nyc.gov/html/cpc/report.aspx?num={ULURP}` → www1.nyc.gov PDF is 403-bound.
3. **C3** — fix §2.4/§5.5: `/index.php/` DOES appear in raw markup (theme site-logo/footer links; 200 for HTML routes; 404 only for /sites/default/files/ static assets); archive-PDF hrefs carry no prefix.
4. **C4** — Appendix I PDF HEAD-verified: 200, application/pdf, 5,069,648 B, LM 2026-06-23 00:53:12 GMT; remove "size unknown".
5. **C5** — /recently-adopted depth = 31 pages (0–30, "Go to last page" href), not "0–8"; OQ-10 depth component resolved.
6. **C6** — fixture ZR-F8 must assert on the results-count string/results region, not global views-row count (wrong-param page carries 25 stray views-rows).
7. **C7** — Socrata catalog resultSetSize = 25 (all geodata), not "12 results"; absence claim stands; state count as observed or drop it.
8. **C8** — quote/parse fidelity: §12-01(c) uses straight double quotes; FROM-prefix has 5 variants with the section number wrapped in `<a class="sec-link-inline"><span>`; definitions are per-definition Drupal nodes (`node--type-defined-term`, `about="/node/{nid}"`, `id="term-{name}"`) — add to ZR-F3 assertions.
9. **C9** — OQ-7 evidence: each hostname serves a self-referencing `Link: <https://{host}/node/54>; rel="canonical"`; hostname choice is a connector-config decision with the alias recorded.

## 6. Defects

**None material.** No guessed schema, endpoint, unit, date, or value in any deliverable; every re-extracted "verbatim" quote matched raw HTML (two fidelity nits, C3/C8). The two over-broad statements are adjacent to honestly-ledgered items (OQ-9, §5.5). The missed amendment endpoint is an S1 completeness gap remedied here — it strengthens the channel model.

## 7. Recommendation for G3

PASS with C1–C9 applied. G3 should re-run: banner grep, 11-02 Last-Amended extraction, /jsonapi 404 + ?_format=json 406, one PDF HEAD, the amendment-endpoint probe (§3). Treat OQ-1/4/8/11/12 as legitimately open; OQ-11 requires qualified-human/legal input. Verify no large local artifacts (reviewer fetched ~2.5 MB HTML into session sandbox only; zero repo binaries, zero PDF downloads).

## 8. Evidence URL index (retrieved 2026-07-16)

V1 portal home (GET+HEAD); V2 zr.planning.nyc.gov alias; V3 API-absence probes ×7; V4 section/chapter/article/disclaimer/appendix pages ×9; V5 five PDF HEADs (Appendix I newly pinned); V6 /zr-downloads; V7 entity-print chain for node 18416; V8 amendment-history AJAX endpoint (+ /nojs/ 404 probes); V9 council.nyc.gov press 2024-12-05; V10 Legistar LU 0181-2024; V11 a030-cpc.nyc.gov redirect chain (→403, recorded); V12 search/feed/stub/robots; V13 Socrata catalog q=zoning resolution; V14 nyc.gov 403 ×2.
