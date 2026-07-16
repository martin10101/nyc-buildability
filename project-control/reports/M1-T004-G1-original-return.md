# M1-T004 G1 — reviewer's original return (verbatim preservation)

> Provenance: this is the data-contract-verifier's complete final return message for the M1-T004 G1 review, received by the orchestrator 2026-07-16 via the agent-return channel and preserved here without alteration (HTML entities from the transport layer decoded to their literal characters: `<`, `>`, `&`). The companion file `M1-T004-G1-verification.md` is an orchestrator transcription of the same content with condensed formatting. Recorded per the owner's audit directive 2026-07-16 (ADR-005 evidence preservation).

---

All verification is complete. Per the ADR-005 gate protocol in my operating rules (reviewers are read-only; the orchestrator saves the report file after validating), I am returning the full report content rather than writing it myself. Here is the complete report for `project-control/reports/M1-T004-G1-verification.md`, followed by the summary verdict.

---

# M1-T004 — G1 Source and Data-Contract Gate Verification

- **Task:** M1-T004 — Official-source research: NYC Zoning Resolution text corpus
- **Gate:** G1 (source and data-contract)
- **Reviewer:** data-contract-verifier (independent; did not produce the work)
- **Review date / retrieval date for all live verifications:** 2026-07-16
- **Verdict:** **PASS** (with 9 required corrections listed in §5; none invalidates the producer's findings; no guessed claim found; this review additionally RESOLVED both [NEEDS G1 RE-VERIFICATION] items and two OQ-ledger entries via official channels)
- **Method:** Independent live re-verification against official sources (raw curl GET/HEAD on the ZR portal with grep extraction — no reliance on WebFetch summarization for any verbatim claim; Socrata catalog API; council.nyc.gov; legistar.council.nyc.gov; Drupal AJAX endpoint probing). KB-scale fetches only; HEAD-only for every PDF; the 504-prone giant node (18523 print route) was deliberately not re-hammered. Producer conclusions read LAST, after acceptance criteria and deliverables.

Artifacts reviewed:
- `project-control/tasks/M1-T004.json` (S1–S5 — starting point)
- `docs/research/zoning-resolution-2026-07-16.md`
- `docs/research/source-registry-drafts/zoning-resolution.json`
- `project-control/reports/M1-T004-producer-report.md` (read last)

---

## 1. Mandatory live verifications

### 1.1 Portal identity and server-rendered claim — VERIFIED

- `https://zoningresolution.planning.nyc.gov/` → HTTP 200, **62,772 B** — byte-identical size to the producer's E3 capture.
- Banner verbatim in raw HTML: `All text changes approved by the city council as of <span class='date'>May 20, 2026</span>` — **date unchanged** since the producer's fetch (no cadence movement to report).
- `X-Generator: Drupal 9 (https://www.drupal.org)` observed by this reviewer on BOTH the 200 homepage response and the 404 page (producer had it only via the 404 route) — identity claim strengthened. `X-Pantheon-Styx-Hostname` + `Via: 1.1 varnish` confirmed.
- Homepage paragraph verbatim confirmed in raw HTML: "The Zoning Resolution consists of 14 Articles and 11 Appendices, plus 126 Zoning Maps, …" through "…Articles VIII through XIV set forth the purpose and regulations for each Special Purpose District."
- Alias `https://zr.planning.nyc.gov/` → 200, `<title>Homepage | Zoning Resolution`. **New OQ-7 evidence:** each host emits a self-referencing canonical `Link` header (`<https://zr.planning.nyc.gov/node/54>; rel="canonical"` on the alias; `<https://zoningresolution.planning.nyc.gov/node/54>; rel="canonical"` on the primary) — there is no cross-host canonical; both hosts claim canonicality for themselves (C9).
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
| Socrata catalog `q=zoning resolution` | "12 results, all geodata" | **resultSetSize=25**, 20 shown at limit=20 — every one a geodata/derived product (E-Designations, ZTLDB fdkv-4t4z, PLUTO 64uk-42ks, Appendix J maps, MIH, zoning map indexes…); **no ZR-text dataset** ✓ material claim; count wrong/stale (C7) |

Clean 404s re-confirmed: `/article-i/chapter-1/11-99`, `/article-xv`, `/appendix-a`. robots.txt is stock Drupal (Disallow /core/, /admin/, /search/ etc. — no content-path disallows; note `Disallow: /search/` does not cover `/search?search_term=…`).

### 1.5 PDF channels via HEAD — ALL FIVE VERIFIED; Appendix I newly pinned

| File | Producer claim | This review (HEAD) |
|---|---|---|
| `Zoning Resolution Complete.pdf` | 102,565,724 B, LM 2026-06-23 | **200, 102,565,724 B, LM Tue, 23 Jun 2026 00:58:19 GMT** ✓ exact |
| `article/32/Article I.pdf` | 3,170,980 B | **200, 3,170,980 B, LM 2026-06-23 00:46:29** ✓ |
| `article/32/chapters/Chapter 1.pdf` | 149,858 B | **200, 149,858 B, LM 2026-06-23 00:00:38** ✓ |
| `2026-06/AllArticles_23Jun2026_compressed_0.pdf` | 75,589,847 B, LM 2026-06-24 | **200, 75,589,847 B, LM Wed, 24 Jun 2026 21:15:07 GMT** ✓ |
| `appendix/21238/APPENDIX I .pdf` (trailing space) | href observed; NOT HEAD-verified; size unknown | **NOW VERIFIED: 200, application/pdf, 5,069,648 B, LM Tue, 23 Jun 2026 00:53:12 GMT** — consistent with the 2026-06-23 batch (C4) |

`/zr-downloads` → 200, 65,470 B; **exactly 10 archive hrefs, byte-identical to the producer's §2.4 list** (both naming styles); listed sizes 72.09/74.29/76.03/77.34/77.88/77.74/82.26/82.91/84.74/24.32 MB all present; 72.09 MB ↔ 75,589,847 B cross-check holds. **`/index.php/` nuance found (C3):** the raw page DOES contain `/index.php/`-prefixed links — in the theme's site-logo and footer links (`/index.php/`, `/index.php/disclaimer`, `/index.php/feedback`) — just not on any archive-PDF href. `/index.php/disclaimer` → **200** (valid Drupal front-controller alias for HTML routes); the prefix 404s only for `/sites/default/files/` static assets — which cleanly explains both the summarizer's error (it transferred a real prefix to the wrong hrefs) and the producer's E7 404.

### 1.6 Undocumented print-PDF endpoint — VERIFIED (gently)

- `/entityprint/pdf/node/18416` → **302** → `/print/pdf/node/18416` → **200, application/pdf, 44,977 B, Content-Disposition: inline; filename="1102.pdf"** — all three claimed values exact.
- The 504-prone node 18523 was NOT re-requested on the print route (owner instruction). Corroborating evidence instead: the §12-10 HTML page is **1,315,025 B** — by far the largest page fetched — consistent with on-the-fly PDF generation timing out on it.

### 1.7 The [NEEDS G1 RE-VERIFICATION] items — BOTH RESOLVED

**(a) City of Yes ↔ 12/5/2024 linkage (OQ-2) — RESOLVED via THREE official channels, including the ZR portal itself:**

1. **The ZR portal's own amendment-history metadata (primary resolution — see §1.8):** the per-section amendment-history popup for §11-47 returns a structured table row: Effective Date **12/5/2024** | ULURP/CPC Report **N240290ZRY** | Project Name **"City of Yes for Housing Opportunity"** | Action **Added** | Description "An amendment modifying multiple Sections to expand opportunities for housing within all zoning districts, and across all 59 of the City's Community Districts". The linkage is stated by DCP on the official portal — no secondary source needed.
2. **NYC Council press release** `https://council.nyc.gov/press/2024/12/05/2761/` → **200 to curl** (not bot-blocked): "New York City Council Passes Historic Citywide Zoning Reforms…", dated December 5, 2024, naming "City of Yes for Housing Opportunity" as the "zoning text amendment, initiated by the Department of City Planning and modified by the Council".
3. **NYC Council Legistar** `legistar.council.nyc.gov/LegislationDetail.aspx?ID=6888427&…` (LU 0181-2024) → **200 to curl**: matter "City of Yes for Housing Opportunity (N 240290 ZRY)", status **Adopted**, action "Approved, by Council", 12/5/2024 on the action record.

Corroborating in-portal fact: `/article-i/chapter-1/11-47` Last Amended = `<time datetime="2024-12-05T12:00:00Z">12/5/2024</time>`, and §12-10 carries **48** occurrences of 12/5/2024 stamps. The application number is **N 240290 ZRY** — the producer never asserted a number (correctly), so nothing to contradict; the number is now officially pinned. Additional discovery: council.nyc.gov and legistar.council.nyc.gov are **automation-accessible official channels** (no 403), a materially useful fallback for adoption records (C2).

**(b) Appendix I PDF href** — HEAD-verified this review (§1.5, C4).

### 1.8 NEW FINDING — per-section amendment-history AJAX endpoint (resolves OQ-9, informs OQ-3)

Chapter and section pages carry a per-section "History" link: `href="/nojs/get/amendment/section/{sectionEntityId}"` (class `use-ajax action-icon revisions`, e.g. **22740** for §11-47; **51** such links on the chapter-1 page; 1 on each raw-captured section page — the links were present in the producer's own raw captures but not enumerated). Probe results:

| Request | Result |
|---|---|
| `GET /nojs/get/amendment/section/22740` (plain) | 404 (HTML error page) |
| `GET /nojs/...?_wrapper_format=drupal_ajax` + XHR header | 404 JSON "No route found for GET /nojs/…" |
| **`GET /ajax/get/amendment/section/22740?_wrapper_format=drupal_ajax`** + `X-Requested-With: XMLHttpRequest` | **200, application/json, 4,230 B** — Drupal AJAX command array whose `insert` payload is the `amendment_history_popup` view: a 6-column table **Effective Date | ULURP/CPC Report | Project Name | Action | Notes | Description** |

Consequences:
- **OQ-9 RESOLVED:** `nyczr_amendment_popup` DOES expose structured per-section amendment metadata beyond the Last Amended stamp — including a DCP-labeled **"Effective Date"** column and ULURP linkage. This is the closest thing to a structured amendment API on the portal: undocumented, AJAX-wrapper-only, same stability caveats as entity-print, but far richer than the `/recently-adopted` stubs.
- **OQ-3 NARROWED:** the portal's own metadata vocabulary calls the per-amendment date "Effective Date", and §11-47's Last Amended (12/5/2024) equals the popup's Effective Date. Adoption and effective dates coincide in this instance, so the adoption-vs-effective question is not fully discriminated — but the official column label is now known.
- The ULURP cell links to `http://a030-cpc.nyc.gov/html/cpc/report.aspx?num=N 240290 ZRY` → **302** → `https://www1.nyc.gov/assets/planning/download/pdf/about/cpc/240290.pdf` → 301 → **403** (nyc.gov bot protection). The CPC-report URL pattern is officially leaked by the redirect even though the PDF needs a browser session. Recorded honestly; not promoted beyond the observed chain.
- The producer's §2.1 sentence "No content XHR endpoints exist in the page JS" is **over-broad** and must be corrected (C1) — though the core claim (legal text is server-rendered) remains fully true, and the producer honestly ledgered the module as OQ-9.
- Section-entity IDs (22740) are a **third identifier namespace** distinct from Drupal node IDs — connector data model must not conflate them.

### 1.9 Search, amendment feed, appendix page — VERIFIED with two sharpenings

- `/search?search_term=floor+area+ratio` → **35** `views-row` ✓; `/search?search_term=city+of+yes` → **0** `views-row` ✓; `/search?fulltext=floor+area+ratio` → "Your search returned **0** results" ✓ — **but** that wrong-param page also contains **25** `views-row` elements in non-results blocks (C6): fixture ZR-F8 must assert on the results-count string/results region, not a global row count.
- `/recently-adopted` → 200; 35 views-rows ✓; newest entries `147-14 Northern Boulevard (N 220416 ZRQ)` + 5/20/2026 ✓; stub page raw-verified: `N 240272 ZRK`, 3/26/2026, hyperlinked `74-948` + "(Map 1)", zero PDF/doc attachments ✓. **New (C5):** the pager contains `<a href="?page=30" title="Go to last page">` — the feed is **31 pages deep (0–30)**, not the "0–8 observed" range; the producer read only the visible pager numbers.
- `/appendix-i` → 200; `APPENDIX%20I%20.pdf` href ✓; Last Amended `<time datetime="2024-11-21T12:00:00Z">11/21/2024</time>` now raw-verified (was summarizer-based E14) ✓.
- `/node/79` (Preamble) → 200 ✓. `/disclaimer` → 200; "CHANGES ARE MADE PERIODICALLY TO THE ZR AND THESE CHANGES MAY OR MAY NOT BE IMMEDIATELY REFLECTED IN THE MATERIALS LOCATED AT OR INFORMATION PRESENT ON HTTPS://ZR.PLANNING.NYC.GOV." verbatim ✓; "WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED…" ✓; node/8771 ✓.
- nyc.gov 403s re-confirmed live: `zoning-text.page` → 403, `planning/index.page` → 403 ✓ (S5 discipline held; nothing 403-bound was asserted as fact anywhere in the deliverables).

### 1.10 WebFetch-summarizer hazard spot-checks (E1/E9/E11/E14) — ALL SURVIVED RAW RE-CHECK

- E9 §12-10 claims: node 18523 ✓; section Last Amended 3/26/2026 ✓; applicability notes verbatim ("Applicable to Article VI - Chapter 6", "…- Chapter 1") ✓; **"FROM 66-11" attribution CONFIRMED in raw HTML** — `<p>FROM <a class="sec-link-inline" … href="/article-vi/chapter-6#66-11"><span>66-11</span></a>: For the purposes of this Chapter, an "above-grade mass transit station" shall refer to…` (my first grep missed it because the section number sits inside `<a><span>` markup — the quoted text is real). Parser-relevant nuance (C8): the FROM prefix has variants — `FROM` (95), `FROM SECTION` (5), `FROM Section` (1), `FROM:` (4), double-space `FROM  ` (6) — and each definition is its own Drupal node (`node--type-defined-term`, e.g. `/node/21970`, `id="term-above-grade mass transit station"`).
- E11 stub fields: raw-verified ✓ (§1.9). E14 Appendix I: raw-verified ✓. E1 "server-rendered": proven by this review's method ✓.
- The one summarizer error the producer caught (`/index.php/`) was real but mis-diagnosed as "no such prefix in the actual markup" — the prefix exists in theme links; see C3.

### 1.11 Registry draft (PRD §8.2) — PASS

- JSON parses cleanly (`json.load`); **19 keys = all 18 PRD §8.2 fields + `open_questions`**; 12 OQ entries exactly mirroring the doc's §8 ledger.
- Honest nulls: `api_dataset_identifier: null`, `last_successful_ingestion: null`, `rate_limits.documented: null` — all correct.
- `health_status: "healthy_observed"` — consistent with every observation in this review (all channels 200; only the undocumented print route and 403-bound nyc.gov companions excepted, both disclosed in the value itself).
- §12-01(j) quotation in the draft's structure notes ("Sections starting with 101-00") matches the live section verbatim.
- Every factual value traced to a source I re-verified: sizes, dates, node IDs, URL patterns, search param, snapshot list, disclaimer quotes, banner verbatim. **No invented value found.**
- Low-storage: zero downloads beyond KB-scale HTML; all PDFs HEAD-only; temp captures in the session sandbox only; zero repo binaries.

---

## 2. Independent scenario walkthrough (S1–S5)

| Scenario | Expected | Actual (this reviewer's independent run) | Result |
|---|---|---|---|
| S1 normal — channel enumeration | Every channel evidenced live; undocumented XHR endpoints recorded with exact URLs | Portal/alias/PDF/print/search/feed channels all re-verified live with exact matches; Socrata absence re-confirmed. One undocumented XHR endpoint (amendment history) existed and was NOT enumerated (module was ledgered as OQ-9; endpoint found by this review, C1) | PASS with C1 |
| S2 boundary — versioning/effective-date model | Verbatim currency statements; historical retrievability; CityAPA/CoY handling | Banner verbatim, unchanged; Last-Amended time elements raw-verified at both extremes (1961-12-15, 2026-03-26); 10 snapshots byte-identical list; CoY linkage now OFFICIALLY resolved (portal popup + Council + Legistar, §1.7) | PASS |
| S3 missing/ambiguous — structure inventory | Hierarchy from official source; unknowns ledgered; no guessed semantics | 14 articles/11-appendix statement verbatim; chapter gap (1,2,3,5,6) re-observed; §12-01 (a)(b)(c)(j) verbatim; `<em>` markup, anchors, 5-digit subsections, appendix aliases, `/appendix-a` 404 all re-verified; OQ ledger honest — nothing guessed | PASS |
| S4 conflict — cross-channel discrepancies | Discrepancies surfaced with evidence; PRD §8 priority order | Banner-date (May 20) vs PDF-generation (Jun 23/24) distinction re-verified from raw HEAD dates; search-parameter trap reproduced (35 vs "0 results"); priority order (HTML primary, snapshots archive, chapter PDFs cross-check, entity-print convenience, nyc.gov browser-only) consistent with all evidence including mine | PASS |
| S5 failure — bot protection, dead links, JS-only content | 403/limits recorded honestly; no unverified promotion | nyc.gov 403 ×2 re-confirmed; clean 404s ×3 re-confirmed; 504 corroborated via the 1.3 MB page size without re-hammering; the only two [NEEDS G1 RE-VERIFICATION] markers were genuine and are now resolved by this review, not by guessing | PASS |

## 3. Reproduction commands (all runnable as-is)

```
# Identity + banner
curl -sI https://zoningresolution.planning.nyc.gov/            # X-Generator, Link canonical
curl -s https://zoningresolution.planning.nyc.gov/ | grep -o "All text changes[^<]*<span class='date'>[^<]*</span>"
curl -sI https://zr.planning.nyc.gov/                          # alias + its own canonical Link
# API absence
curl -s -o /dev/null -w "%{http_code}" "https://zoningresolution.planning.nyc.gov/jsonapi"          # 404
curl -s -o /dev/null -w "%{http_code}" "https://zoningresolution.planning.nyc.gov/node/18523?_format=json"  # 406
curl -s "https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=zoning%20resolution&limit=20"
# PDF HEADs (incl. newly pinned Appendix I)
curl -sI "https://zoningresolution.planning.nyc.gov/sites/default/files/article/Zoning%20Resolution%20Complete.pdf"
curl -sI "https://zoningresolution.planning.nyc.gov/sites/default/files/appendix/21238/APPENDIX%20I%20.pdf"
# Print route (small node only)
curl -sI "https://zoningresolution.planning.nyc.gov/print/pdf/node/18416"
# Amendment-history endpoint (the working form)
curl -s -H "X-Requested-With: XMLHttpRequest" "https://zoningresolution.planning.nyc.gov/ajax/get/amendment/section/22740?_wrapper_format=drupal_ajax"
# City of Yes official confirmations
curl -s -A "Mozilla/5.0" "https://council.nyc.gov/press/2024/12/05/2761/"
curl -s -A "Mozilla/5.0" "https://legistar.council.nyc.gov/LegislationDetail.aspx?ID=6888427&GUID=4B132BCA-7483-462C-8588-B6B921596C48"
# Search trap + pager depth
curl -s "https://zoningresolution.planning.nyc.gov/search?search_term=floor+area+ratio" | grep -c views-row   # 35
curl -s "https://zoningresolution.planning.nyc.gov/recently-adopted" | grep -o '?page=30.\{0,30\}'            # Go to last page
```

## 4. Open-questions ledger after G1 (OQ-1..OQ-12)

| OQ | Status after this review | Notes |
|---|---|---|
| OQ-1 | STILL OPEN | Appendix count reconciliation not investigated further; `/appendix-a` 404 re-confirmed |
| OQ-2 | **RESOLVED** | CoY = 12/5/2024, N 240290 ZRY — confirmed by the portal's own amendment popup + council.nyc.gov press + Legistar LU 0181-2024 (C2) |
| OQ-3 | **NARROWED** | Portal metadata labels per-amendment dates "Effective Date"; §11-47 Last Amended = popup Effective Date; adoption-vs-effective still not discriminated where they coincide (C1) |
| OQ-4 | STILL OPEN | Pre-2024-03-22 text channel unknown; nyc.gov 403 re-confirmed |
| OQ-5 | STILL OPEN | Chapters 1,2,3,5,6 re-observed live; full 14-article inventory at connector build |
| OQ-6 | STILL OPEN | Print route re-verified working for node 18416; stability/intent still unknown |
| OQ-7 | **NARROWED** | Both hosts self-canonicalize via `Link: rel="canonical"` headers to their own `/node/54`; no cross-host canonical exists (C9) |
| OQ-8 | STILL OPEN | Table markup uninspected — legitimately deferred |
| OQ-9 | **RESOLVED** | `/ajax/get/amendment/section/{id}?_wrapper_format=drupal_ajax` + XHR header → structured 6-column amendment history (C1) |
| OQ-10 | **PARTIALLY RESOLVED** | Depth = 31 pages (0–30) via last-page href (C5); entry mutability still open |
| OQ-11 | STILL OPEN | Authoritative-publication question — qualified-human/legal review; must not be guessed |
| OQ-12 | STILL OPEN | 102.6 MB vs 75.6 MB content identity — verify at archiver build |

## 5. Required corrections (proposed for orchestrator/producer application)

1. **C1 — research doc §1/§2.1/§3.3/§8 OQ-9; registry `fields_available.structure` + `open_questions`:** record the per-section amendment-history endpoint: markup href `/nojs/get/amendment/section/{sectionEntityId}` (404 to plain GET); working form `GET /ajax/get/amendment/section/{id}?_wrapper_format=drupal_ajax` with `X-Requested-With: XMLHttpRequest` → 200 JSON whose `insert` payload is a 6-column table (Effective Date | ULURP/CPC Report | Project Name | Action | Notes | Description), verified for §11-47 (id 22740: 12/5/2024 | N240290ZRY | City of Yes for Housing Opportunity | Added). Mark OQ-9 RESOLVED. Correct the over-broad "No content XHR endpoints exist in the page JS" to "the legal text is fully server-rendered; the only content XHR surface is the undocumented amendment-history popup route". Note section-entity IDs as a third ID namespace distinct from node IDs, and the same stability caveats as entity-print.
2. **C2 — research doc §3.4/§8 OQ-2, E18 row; registry `known_limitations`/`open_questions`/`fallback_source`:** mark OQ-2 RESOLVED and remove both [NEEDS G1 RE-VERIFICATION] markers: City of Yes for Housing Opportunity (N 240290 ZRY) adopted by City Council 2024-12-05 — confirmed by (a) the portal's own amendment popup, (b) `council.nyc.gov/press/2024/12/05/2761/`, (c) Legistar LU 0181-2024 (status Adopted, "Approved, by Council"). Add that council.nyc.gov and legistar.council.nyc.gov are automation-accessible (HTTP 200, no bot wall) — an official fallback channel for adoption records; the CPC report system `a030-cpc.nyc.gov/html/cpc/report.aspx?num={ULURP}` 302s to `www1.nyc.gov/assets/planning/download/pdf/about/cpc/{nnnnnn}.pdf` which is 403-bound (browser needed for the PDF itself).
3. **C3 — research doc §2.4/§5.5:** replace "no `/index.php/` prefix in the actual markup" with the precise finding: the raw markup DOES contain `/index.php/` links (theme site-logo/footer: `/index.php/`, `/index.php/disclaimer`, `/index.php/feedback`); `/index.php/{alias}` is a valid Drupal front-controller route (200 verified) but 404s for `/sites/default/files/` static assets — the summarizer's error was transferring a real HTML-route prefix onto PDF hrefs. Archive-PDF hrefs carry no prefix (re-confirmed byte-identical).
4. **C4 — research doc §2.3 (Appendix I row) and §9 E14; registry structure list:** Appendix I PDF now HEAD-verified: 200, `application/pdf`, **5,069,648 B**, Last-Modified Tue, 23 Jun 2026 00:53:12 GMT (trailing-space URL works as published; consistent with the 2026-06-23 batch). Remove "not HEAD-verified — size unknown".
5. **C5 — research doc §3.3/§8 OQ-10; registry structure list:** `/recently-adopted` raw HTML contains `<a href="?page=30" title="Go to last page">` — feed depth is **31 pages (0–30)** as of 2026-07-16, not "pages 0–8"; the 0–8 range was only the visible pager window. OQ-10's depth component is resolved; entry-mutability remains open.
6. **C6 — research doc §2.5 and fixture ZR-F8:** the wrong-parameter search page contains "Your search returned 0 results" but ALSO 25 `views-row` elements in non-results page blocks; the correct-parameter zero-hit page has 0. ZR-F8 must assert on the results-count string/results region, not a global `views-row` count.
7. **C7 — research doc §2.2 (E2 row):** live Socrata catalog `resultSetSize` = **25** (20 shown at limit=20), all geodata/derived — the "12 results" count is wrong or stale. The material claim (no ZR-text dataset) is re-confirmed; state the count as observed at review time or drop the number.
8. **C8 (minor, quote/parse fidelity) — research doc §4.3 and fixture ZR-F3:** (i) §12-01(c) source text uses straight double quotes (`The word "shall" is…`), not the single quotes shown inside the doc's "verbatim" quote; (ii) the §12-10 `FROM` attribution prefix has five observed variants (`FROM`, `FROM SECTION`, `FROM Section`, `FROM:`, double-space `FROM  `) with the section number wrapped `<a class="sec-link-inline"><span>…</span></a>`; (iii) each definition is its own Drupal node (`node--type-defined-term`, `about="/node/{nid}"`, `id="term-{name}"`) — add to ZR-F3 parsing assertions.
9. **C9 — research doc §8 OQ-7; registry `known_limitations`:** add the canonical-header evidence: each hostname serves a self-referencing `Link: <https://{host}/node/54>; rel="canonical"` — no cross-host canonical exists; hostname choice remains a connector-config decision with the alias recorded.

## 6. Defects

**None material.** No guessed schema, endpoint, unit, date, or value found in any of the three deliverables; every "verbatim" quote I re-extracted matched raw HTML (two fidelity nits, C3/C8). The two statements requiring correction ("no content XHR endpoints", "no /index.php/ in the markup") are over-broad phrasings of true underlying observations, both adjacent to items the producer honestly ledgered (OQ-9, §5.5). The missed amendment-history endpoint is an S1 completeness gap, remedied here with exact URLs and shapes — it strengthens, not contradicts, the producer's channel model.

## 7. Recommendation for G3

PASS this G1 with corrections C1–C9 applied. G3 should:
1. Re-run as its normal/boundary/missing/failure cases: the banner grep, the 11-02 `Last Amended` extraction, the `/jsonapi` 404 + `?_format=json` 406, one PDF HEAD, and the amendment-endpoint probe (exact commands in §3).
2. Confirm the corrected documents read coherently, especially the OQ-2/OQ-9 resolutions and the reframed XHR statement.
3. Treat OQ-1, OQ-4, OQ-8, OQ-11, OQ-12 as legitimately open; OQ-11 requires qualified-human/legal input and must not be closed by agents.
4. Verify no large/persistent local artifacts (producer HEAD-only; this reviewer fetched ~2.5 MB of HTML into the session sandbox, largest single page 1.3 MB §12-10; zero repo binaries, zero PDF downloads).

## 8. Evidence URL index (all retrieved 2026-07-16 by this reviewer)

| # | URL | What it verified |
|---|---|---|
| V1 | `https://zoningresolution.planning.nyc.gov/` (GET+HEAD) | 200/62,772 B; banner verbatim May 20, 2026; X-Generator Drupal 9 on 200; canonical Link node/54; "14 Articles and 11 Appendices…" verbatim |
| V2 | `https://zr.planning.nyc.gov/` | 200; same title; self-referencing canonical Link (C9) |
| V3 | `/jsonapi`, `/sitemap.xml`, `/node/18523?_format=json`, `/node/18416?_format=json`, `/article-i/chapter-1/11-99`, `/article-xv`, `/appendix-a` | 404/404/406/406/404/404/404 |
| V4 | `/article-i/chapter-1/11-02`, `/article-i/chapter-2/12-01`, `/article-i/chapter-1`, `/article-i`, `/article-i/chapter-2/12-10`, `/article-i/chapter-1/11-47`, `/node/79`, `/disclaimer`, `/appendix-i` | Last-Amended markup; §12-01 (a)(b)(c)(j) verbatim; chapter list 1,2,3,5,6; §11-47 title + 12/5/2024 stamp; 12-10 structure incl. FROM 66-11 raw; disclaimer verbatim; Appendix I stamp |
| V5 | Five PDF HEADs (Complete/Article I/Chapter 1/23Jun2026 snapshot/APPENDIX I .pdf) | all sizes and Last-Modified exact; Appendix I newly pinned 5,069,648 B (C4) |
| V6 | `/zr-downloads` | 10 hrefs byte-identical; sizes list; index.php theme links (C3) |
| V7 | `/entityprint/pdf/node/18416` → `/print/pdf/node/18416` | 302 → 200, 44,977 B, filename="1102.pdf" |
| V8 | `/ajax/get/amendment/section/22740?_wrapper_format=drupal_ajax` (+ /nojs/ 404 probes) | amendment-history JSON: 6-column table; CoY row 12/5/2024 N240290ZRY (C1) |
| V9 | `https://council.nyc.gov/press/2024/12/05/2761/` | Council adoption press release 2024-12-05 (C2) |
| V10 | `https://legistar.council.nyc.gov/LegislationDetail.aspx?ID=6888427&GUID=4B132BCA-…` | LU 0181-2024, "City of Yes for Housing Opportunity (N 240290 ZRY)", Adopted (C2) |
| V11 | `http://a030-cpc.nyc.gov/html/cpc/report.aspx?num=N%20240290%20ZRY` | 302 → www1.nyc.gov CPC PDF → 403 (recorded, not promoted) |
| V12 | `/search?search_term=…` ×2, `/search?fulltext=…`, `/recently-adopted`, `/recently-adopted/20-berry-st-n-240272-zrk`, `/robots.txt` | 35 rows / 0 rows / "0 results"+25 stray rows (C6); pager ?page=30 (C5); stub fields raw; stock Drupal robots |
| V13 | `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=zoning%20resolution&limit=20` | resultSetSize 25, all geodata; no ZR-text dataset (C7) |
| V14 | nyc.gov `zoning-text.page` + `planning/index.page` | HTTP 403 ×2 re-confirmed (S5) |

---

## Final summary for the orchestrator

**VERDICT: PASS** — with corrections C1–C9 (none invalidates the producer's findings; no guessed or materially false contract claim found).

Corrections, one line each:
- **C1:** Record the amendment-history AJAX endpoint (`/ajax/get/amendment/section/{id}?_wrapper_format=drupal_ajax` + XHR header → 6-col table incl. "Effective Date"); mark OQ-9 RESOLVED; fix the over-broad "no content XHR endpoints" sentence.
- **C2:** Mark OQ-2 RESOLVED and drop both [NEEDS G1 RE-VERIFICATION] markers: CoY-HO (N 240290 ZRY) adopted 2024-12-05, confirmed by portal popup + council.nyc.gov press + Legistar LU 0181-2024; note council/Legistar are automation-accessible official channels.
- **C3:** Fix §2.4/§5.5: `/index.php/` DOES appear in raw markup (theme links, 200 for HTML routes, 404 only for static files); no prefix on archive-PDF hrefs.
- **C4:** Appendix I PDF now HEAD-verified: 200, 5,069,648 B, Last-Modified 2026-06-23 00:53:12 GMT — remove "size unknown".
- **C5:** `/recently-adopted` depth is 31 pages (0–30, "Go to last page" href), not "0–8"; OQ-10 depth component resolved.
- **C6:** ZR-F8 must assert on the results-count string, not global `views-row` count (wrong-param page carries 25 stray views-rows).
- **C7:** Socrata catalog shows resultSetSize 25 (all geodata), not "12 results"; absence claim stands.
- **C8:** Quote/parse fidelity: §12-01(c) uses double quotes; FROM-prefix has 5 variants; definitions are per-definition Drupal nodes (`node--type-defined-term`) — add to ZR-F3.
- **C9:** OQ-7 evidence: both hostnames self-canonicalize via `Link: rel="canonical"` headers; no cross-host canonical.

OQs/markers resolved by this review: **OQ-2 (both [NEEDS G1 RE-VERIFICATION] markers), OQ-9, OQ-10 (depth component); OQ-3 and OQ-7 materially narrowed; the Appendix I unverified-href item closed.**

Could not verify (honestly recorded): nyc.gov pages remain 403 (zoning-text.page, planning index, and the CPC report PDF behind the a030-cpc redirect chain) — browser-capable session still required for OQ-4/OQ-11 inputs; the §12-10 print-PDF 504 was not re-triggered per instruction (corroborated instead by the 1.3 MB page size); OQ-1, OQ-8, OQ-11, OQ-12 remain legitimately open and must not be guessed. Per ADR-005 I wrote no repo files and ran no control CLI; the report content above is ready to be saved verbatim as `project-control/reports/M1-T004-G1-verification.md` (the only file I modified is my agent memory at `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\agent-memory\data-contract-verifier\reference_nyc-source-verification-techniques.md`).

Sources: council.nyc.gov press release 2024-12-05 (https://council.nyc.gov/press/2024/12/05/2761/), Legistar LU 0181-2024, NYC Zoning Resolution portal (https://zoningresolution.planning.nyc.gov/)
