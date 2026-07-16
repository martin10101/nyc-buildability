# M1-T004 — Official-Source Research: NYC Zoning Resolution Text Corpus

- **Task:** M1-T004 — Official-source research: NYC Zoning Resolution text corpus (the law itself; geodata was M1-T003)
- **Producer agent:** official-source-researcher
- **Retrieval date for all sources:** 2026-07-16 (unless noted)
- **Evidence basis:** All claims below were verified by the producer via live fetches on 2026-07-16 (portal HTML read both via WebFetch summarization AND raw curl captures with grep extraction; HTTP HEAD requests for every PDF size claim; Socrata catalog search; probe requests for API surfaces). The evidence register in §9 lists every URL. Raw-HTML extraction was used to confirm every verbatim quote — one WebFetch summarizer error was caught and corrected this way (§5.5).
- **Discipline:** Claims that come only from a search-result listing — rather than a live fetch or a directly read official document — are marked **[NEEDS G1 RE-VERIFICATION]**. Legal text is quoted exactly or explicitly marked as summary. Unknowns are in the §8 OPEN QUESTIONS ledger. (Post-G1 note: both such markers were resolved by the G1 reviewer via official channels — see C2/C4 markers; none remain outstanding.)

---

## 1. Executive summary

| Aspect | Finding (all live-verified 2026-07-16) |
|---|---|
| **Primary official channel** | `https://zoningresolution.planning.nyc.gov/` — DCP's Zoning Resolution portal. **Drupal 9** (`X-Generator: Drupal 9` response header, E4), Pantheon-hosted, **server-rendered HTML** — NOT a client-side JS app (the task-packet risk assumption did not hold; the only JS is New Relic RUM + Google Analytics, E13). Full legal text is served as crawlable HTML at stable per-section URLs. |
| **Alias hostname** | `https://zr.planning.nyc.gov/` serves the same site (HTTP 200, same `Homepage \| Zoning Resolution` title, E16); the official disclaimer refers to the site as `HTTPS://ZR.PLANNING.NYC.GOV` (E12). Canonicality: OQ-7 — **[NARROWED AT G1 — C9]:** each hostname serves a self-referencing `Link: <https://{host}/node/54>; rel="canonical"` header; no cross-host canonical exists, so hostname choice is a connector-config decision with the alias recorded (G1 report §1.1). |
| **No structured API** | `/jsonapi` → 404; `/node/{nid}?_format=json` → 406; `sitemap.xml` → 404 (E5). **No NYC Open Data dataset of the ZR text exists** — Socrata catalog search returned only geodata products (E2). The portal HTML is the highest-tier machine channel available (PRD §8 tier 4). |
| **Currency model** | Homepage banner (verbatim, raw HTML, E3): `All text changes approved by the city council as of <span class='date'>May 20, 2026</span>`. Every section carries a machine-readable **Last Amended** stamp: `<time datetime="1961-12-15T12:00:00Z" class="datetime">12/15/1961</time>` (E9). |
| **Amendment feed** | `/recently-adopted` — paginated list (**[CORRECTED AT G1 — C5]:** 31 pages deep, 0–30) of adopted text amendments: project name + application number (e.g. `20 Berry St (N 240272 ZRK)`), date, affected section reference (`Section 74-948 (Map 1)`). Entries are stubs — no redlines/attached documents (E11). |
| **Historical versions** | `/zr-downloads` Archive page offers **10 dated complete-ZR PDF snapshots, 2024-03-22 through 2026-06-23** (24.32–84.74 MB each; June 2026 file HEAD-verified 75,589,847 B). Nothing older than March 2024 is on the portal (OQ-4). No per-section history view. (E7, E8) |
| **PDF channels** | Complete ZR: `/sites/default/files/article/Zoning Resolution Complete.pdf` = **102,565,724 B**, Last-Modified 2026-06-23 (E6). Per-article PDFs (`Article I.pdf` = 3,170,980 B) and per-chapter PDFs (`Chapter 1.pdf` = 149,858 B) exist at `/sites/default/files/article/...` paths (E6). Per-section on-the-fly PDF via Drupal entity_print: `/entityprint/pdf/node/{nid}` → 302 → `/print/pdf/node/{nid}` — 200 for a normal section (44,977 B for §11-02) but **504 Gateway Timeout** for the giant §12-10 definitions node (E10). Official-but-undocumented; stability unverified. |
| **Recommended M3 role** | Portal HTML = ingestion primary (per-section granularity + Last Amended stamps + `<em>` defined-term markup + hyperlinked cross-references). Dated complete-PDF snapshots = reproducibility archive (store in Supabase per release). Per-article/chapter PDFs = cross-check channel. See §5.6. |

**Legal-status warning (official disclaimer, verbatim, E12):** *"CHANGES ARE MADE PERIODICALLY TO THE ZR AND THESE CHANGES MAY OR MAY NOT BE IMMEDIATELY REFLECTED IN THE MATERIALS LOCATED AT OR INFORMATION PRESENT ON HTTPS://ZR.PLANNING.NYC.GOV."* The disclaimer nowhere states that the online version is the official legal text. The platform must present ZR-derived rules with this caveat and pin every extraction to a dated snapshot.

---

## 2. S1 — Distribution channels, identifiers, formats

### 2.1 Portal HTML (VERIFIED, live — primary channel)

- **Platform:** Drupal 9 on Pantheon behind Fastly/Varnish. Evidence: `X-Generator: Drupal 9 (https://www.drupal.org)` header on the site's 404 page; `X-Pantheon-Styx-Hostname` headers on all responses; `Via: 1.1 varnish` (E4, E6). Custom Drupal theme `neoclassic`; custom modules visible in `drupalSettings.ajaxPageState.libraries`: `nyczr_search_global_search_form` (search), `nyczr_amendment_popup/popup`, `footnotes/footnotes` (E13). Homepage is `node/54`; content pages are Drupal nodes with clean aliases.
- **URL model (observed across live fetches E3, E8, E9):**
  - Article: `/article-i` … `/article-xiv` (14 articles, all present in nav, E3)
  - Chapter: `/article-i/chapter-1` — chapter page carries the **full text of all its sections** plus per-section anchors
  - Section: `/article-i/chapter-1/11-02` — dedicated per-section page (200 verified; node 18416)
  - Appendices: descriptive aliases, e.g. `/appendix-b-index-special-purpose-districts`, `/appendix-i`
  - Preamble: `/node/79` (unaliased, E14); Disclaimer: `/disclaimer` (node 8771, E12)
- **Failure behavior (S5):** nonexistent section `/article-i/chapter-1/11-99` → HTTP 404; nonexistent `/article-xv` → HTTP 404 (E15). Clean 404s, no soft-200s observed.
- **Rendering:** all legal text is in the server HTML (verified by raw curl + grep extraction of §12-01 full text, E13). **[CORRECTED AT G1 — C1]:** the original statement "No content XHR endpoints exist in the page JS" was over-broad. Corrected finding: the legal text is fully server-rendered; **the only content XHR surface is the undocumented amendment-history popup route** (`/ajax/get/amendment/section/{sectionEntityId}` — see §3.3; same stability caveats as entity-print). The only third-party scripts are New Relic RUM (`js-agent.newrelic.com`) and Google Analytics (E13). **The "JS-app / hidden JSON API" risk in the task packet did not materialize for the legal text itself.**

### 2.2 API-surface probes (VERIFIED absent)

| Probe | Result (2026-07-16) |
|---|---|
| `/jsonapi` (Drupal JSON:API index) | HTTP 404 (E5) |
| `/node/18523?_format=json` (Drupal REST export) | HTTP 406 (E5) |
| `/sitemap.xml` | HTTP 404 (E5) |
| Socrata catalog `q=zoning resolution` | **[CORRECTED AT G1 — C7]:** `resultSetSize` **25** observed at G1 review (the produced "12 results" figure was wrong/stale) — every result a geodata/derived product; **no ZR-text dataset** (E2; G1 report §1.4). The material absence claim stands |

There is **no official JSON/API channel for the ZR text**. Ingestion must be HTML + PDF.

### 2.3 PDF channels (VERIFIED via HEAD — no bulk downloads performed)

| File | URL | HEAD result (E6, E8, E10) |
|---|---|---|
| Complete ZR (current) | `/sites/default/files/article/Zoning%20Resolution%20Complete.pdf` | 200, `application/pdf`, **102,565,724 B (~97.8 MB)**, Last-Modified `Tue, 23 Jun 2026 00:58:19 GMT` |
| Complete ZR (dated snapshot, newest) | `/sites/default/files/2026-06/AllArticles_23Jun2026_compressed_0.pdf` | 200, **75,589,847 B (~72.1 MB)**, Last-Modified `Wed, 24 Jun 2026 21:15:07 GMT` |
| Article I | `/sites/default/files/article/32/Article%20I.pdf` | 200, **3,170,980 B**, Last-Modified 2026-06-23 |
| Article I Chapter 1 | `/sites/default/files/article/32/chapters/Chapter%201.pdf` | 200, **149,858 B**, Last-Modified 2026-06-23 |
| Appendix I | `/sites/default/files/appendix/21238/APPENDIX%20I%20.pdf` (note trailing space before `.pdf`) | **[CORRECTED AT G1 — C4]:** HEAD-verified at G1 (the trailing-space URL works exactly as published): 200, `application/pdf`, **5,069,648 B**, Last-Modified `Tue, 23 Jun 2026 00:53:12 GMT` (G1 report §1.5) |
| Per-section (entity_print) | `/entityprint/pdf/node/18416` → 302 → `/print/pdf/node/18416` | 200, `application/pdf`, **44,977 B**, `Content-Disposition: inline; filename="1102.pdf"` — generated on the fly |
| Per-section, giant node | `/print/pdf/node/18523` (§12-10 definitions) | **504 Gateway Timeout** — on-the-fly generation fails for very large sections |

All PDF Last-Modified dates cluster on 2026-06-23 — the per-article/chapter PDFs are regenerated as a batch (consistent with the 23Jun2026 snapshot name). The `entityprint` path is **official-but-undocumented (Drupal entity_print module); stability unverified; never to be treated as a guaranteed API** (OQ-6).

### 2.4 Archive of dated snapshots (VERIFIED, live — `/zr-downloads`)

Raw HTML of `/zr-downloads` (E8) contains exactly **10** complete-ZR PDF hrefs (**[CORRECTED AT G1 — C3]:** the archive-PDF hrefs carry no `/index.php/` prefix, but the raw page DOES contain `/index.php/` links elsewhere — see the corrected §5.5):

```
/sites/default/files/2026-06/AllArticles_23Jun2026_compressed_0.pdf
/sites/default/files/2025-12/AllArticles_31Dec2025_compressed.pdf
/sites/default/files/2025-09/All%20Articles%20ZR_23Sep2025_compressed.pdf
/sites/default/files/2025-07/All%20Articles%20ZR_1Jul2025_compressed.pdf
/sites/default/files/2025-03/All%20Articles%20ZR_25Mar2025_compressed.pdf
/sites/default/files/2025-03/All%20Articles%20ZR_21Mar2025_compressed.pdf
/sites/default/files/2024-10/All%20Articles%20ZR_2Oct2024-compressed.pdf
/sites/default/files/2024-07/All%20Articles%20ZR_17July2024_compressed.pdf
/sites/default/files/2024-06/All%20Articles%20ZR_12June2024-compressed2.pdf
/sites/default/files/2024-03/All%20Articles%20ZR_22March2024-compressed.pdf
```

Page-listed sizes: 72.09 / 74.29 / 76.03 / 77.34 / 77.88 / 77.74 / 82.26 / 82.91 / 84.74 / 24.32 MB. Cross-check: 72.09 MB × 1024² = 75,590,000 ≈ the HEAD-verified 75,589,847 B for the 23Jun2026 file — page sizes are trustworthy. File-name date = snapshot date; two snapshots exist for March 2025 (21st and 25th). Coverage starts 2024-03-22 — **no older text is retrievable from the portal** (OQ-4). Note the naming-convention drift over time (`All Articles ZR_…` → `AllArticles_…`) — parsers must not assume one pattern.

### 2.5 Portal search (VERIFIED, live — with a corrected parameter finding)

- Form: custom Drupal module — `<form class="nyczr-search-global-search-form" action="/search">`, text input **`name="search_term"`** (max length 128), checkbox `entire_phrase`, checkbox `type=appendix` (raw HTML, E13).
- **Hazard found live:** querying with a wrong parameter (`/search?fulltext=…`) returns HTTP 200 with `Your search returned <strong>0</strong> results.` — an ignored parameter is indistinguishable from a true zero-hit unless the connector uses `search_term`. Verified: `/search?search_term=floor+area+ratio` → 35 `views-row` results on page 1 (section-numbered hits: 13-455, 15-11, 15-111, 15-112, 23-20, 23-21, …) while `/search?fulltext=floor+area+ratio` → 0 (E13).
- `/search?search_term=city+of+yes` → **0 results** (correct parameter; 0 `views-row` elements) — the phrase "city of yes" does not occur in the ZR legal text (§3.4).

### 2.6 nyc.gov cross-channel (403-bound — recorded, not guessed)

- `https://www.nyc.gov/site/planning/zoning/zoning-text.page` → **HTTP 403**; `https://www.nyc.gov/site/planning/index.page` → **HTTP 403** (live, E17). Consistent with the M1-T001/T003 nyc.gov bot-protection pattern. Any DCP-page statements about the ZR (print edition, official-publication status) need a browser-capable capture (OQ-11; OQ-2 was resolved at G1 via the automation-accessible council channels — see §3.4, C2).

---

## 3. S2 — Versioning and effective-date model

### 3.1 Site-level currency statement (verbatim, raw HTML, E3)

```
All text changes approved by the city council as of <span class='date'>May 20, 2026</span>
```

(Lowercase "city council" is as-published.) The newest `/recently-adopted` entry is also dated 5/20/2026 (`147-14 Northern Boulevard (N 220416 ZRQ)`) — the banner date tracks the latest adopted amendment, not the page-generation date.

### 3.2 Per-section "Last Amended" stamps (verified in raw HTML, E9)

Every section page and every section block on chapter pages carries:

```html
Last Amended</span><div class="field-content"><time datetime="1961-12-15T12:00:00Z" class="datetime">12/15/1961</time>
```

Machine-readable ISO datetime. Observed values range from `12/15/1961` (original adoption era) to `3/26/2026` (§12-10, E9). Individual definitions inside §12-10 carry their own Last Amended dates (e.g. 10/7/2021, 2/2/2011, 12/5/2024, 6/6/2024 — E9 summarizer reading of the live page). **The portal does not state whether "Last Amended" means adoption date or effective date** — observed correspondence with `/recently-adopted` dates (e.g. `20 Berry St` dated 3/26/2026 amending §74-948; §12-10 Last Amended 3/26/2026) suggests adoption date, but this is producer inference, not an official statement → OQ-3. **[NARROWED AT G1 — C1]:** the amendment-history popup (§3.3) officially labels per-amendment dates "**Effective Date**", and §11-47's Last Amended (12/5/2024) equals its popup Effective Date — but adoption-vs-effective remains undiscriminated where the two coincide (G1 report §1.8); OQ-3 stays open as narrowed.

### 3.3 Amendment publication model (E11)

- `/recently-adopted` lists adopted text amendments, paginated. **[CORRECTED AT G1 — C5]:** the feed is **31 pages deep (0–30)** — the raw page-1 pager carries `<a href="?page=30" title="Go to last page">` (G1 report §1.9); the producer's "`?page=0`…`?page=8`" reflected only the numbered pager links, not the feed depth. 35 `views-row` elements on page 1 — rows appear twice per entry in the markup, so ~17 entries/page.
- Entry page examined live: `20 Berry St (N 240272 ZRK)` — fields: date `3/26/2026`, reference `Section 74-948 (Map 1)`, application number `N 240272 ZRK`. **No amendment text, no redline, no attached documents, no effective-date statement** — the amended text is only available already-incorporated in the affected sections (summary of E11 fetch).
- A `nyczr_amendment_popup` Drupal library exists (E13). **[RESOLVED AT G1 — C1]** (this was OQ-9; the original text mis-cited OQ-10): the popup is backed by a **per-section amendment-history AJAX endpoint**, live-verified by the G1 reviewer 2026-07-16 (G1 report §1.8):
  - Markup form on chapter/section pages: `href="/nojs/get/amendment/section/{sectionEntityId}"` (class `use-ajax action-icon revisions`; 51 such links on the chapter-1 page). Plain GET on the `/nojs/` form → 404.
  - Working form: `GET /ajax/get/amendment/section/{id}?_wrapper_format=drupal_ajax` with header `X-Requested-With: XMLHttpRequest` → **200, application/json** — a Drupal AJAX command array whose `insert` payload is the `amendment_history_popup` view: a 6-column table **Effective Date | ULURP/CPC Report | Project Name | Action | Notes | Description**.
  - Verified example — §11-47 (sectionEntityId **22740**): `12/5/2024 | N240290ZRY | City of Yes for Housing Opportunity | Added`.
  - **Section-entity IDs (e.g. 22740) are a third identifier namespace**, distinct from Drupal node IDs (§4.4) and from section numbers — connectors must track all three.
  - Status: official-but-undocumented, AJAX-wrapper-only — **same stability caveats as entity-print** (never a guaranteed API); far richer than the `/recently-adopted` stubs. The ULURP cell links into the CPC report chain, which ends 403-bound (§3.4).

### 3.4 City of Yes-era amendments — how they appear

- Full-text search for "city of yes" (correct `search_term` parameter): **0 results** (E13). The program branding does not occur in the legal text; amendments are integrated inline without campaign names.
- Directly observed in section inventories: §11-47 is titled *"Applications for Certain Approvals Filed Prior to December 5, 2024"* (chapter-1 section list, E9), and many §12-10 definitions show Last Amended `12/5/2024` (E9).
- **[RESOLVED AT G1 — C2]** (former re-verification marker removed; OQ-2 RESOLVED): "**City of Yes for Housing Opportunity**" (application **N 240290 ZRY**) was adopted by the City Council on **2024-12-05**, confirmed at G1 via three official channels (G1 report §1.7):
  1. The portal's own amendment popup for §11-47 (§3.3): `12/5/2024 | N240290ZRY | City of Yes for Housing Opportunity | Added`.
  2. NYC Council press release `https://council.nyc.gov/press/2024/12/05/2761/` (2024-12-05): "New York City Council Passes Historic Citywide Zoning Reforms…" — naming CoY-HO as the "zoning text amendment, initiated by the Department of City Planning and modified by the Council".
  3. NYC Council Legistar **LU 0181-2024**: "City of Yes for Housing Opportunity (N 240290 ZRY)", status **Adopted**, "Approved, by Council", 12/5/2024.

  Channel discovery (C2): **council.nyc.gov and legistar.council.nyc.gov are automation-accessible official channels (no bot wall)** — an official fallback for adoption records. The CPC report chain `a030-cpc.nyc.gov/html/cpc/report.aspx?num={ULURP}` 302s to a `www1.nyc.gov` PDF that is **403-bound** (browser needed; URL pattern recorded, not promoted). The platform still must not label rules "City of Yes" from secondary sources — this adoption fact is now pinned to official records.

### 3.5 Snapshot/version model for reproducibility

- The current text is a moving target updated per adoption; the only official frozen versions are the **dated complete-PDF snapshots** (§2.4), at an irregular cadence (observed gaps: 3–6 months; 10 snapshots over 27 months).
- Complete/current PDFs and per-article PDFs were regenerated 2026-06-23 while the text banner says May 20, 2026 — **PDF file date = generation date; banner date = legal currency date**. Both must be recorded per ingest.
- **No historical per-section view** and no diff/changelog channel beyond `/recently-adopted` stubs. M3 must build its own section-version history from repeated crawls + snapshot PDFs.

---

## 4. S3 — Structure inventory (for the M3 ingestion hierarchy)

### 4.1 Top-level structure (official, verbatim, E3)

Homepage: *"14 Articles and 11 Appendices, plus 126 Zoning Maps, that establish the zoning districts for the City and the regulations governing land use and development. Articles I through VII contain the use, bulk, parking and other applicable regulations for each zoning district. The three major articles are Article II, with regulations for residence districts, Article III for commercial districts, and Article IV for manufacturing districts. Articles VIII through XIV set forth the purpose and regulations for each Special Purpose District."*

Article titles (portal contents menu, raw HTML, E12): I General Provisions; II Residence District Regulations; III Commercial District Regulations; IV Manufacturing District Regulations; V Non-Conforming Uses and Non-Complying Buildings; VI Special Regulations Applicable to Certain Areas; VII Administration; VIII–XIV Special Purpose Districts (each).

Appendix menu (raw HTML, E12): B — Index of Special Purpose Districts; C, Table 1 — City Environmental Quality Review (CEQR) Environmental Requirements: (E) Designations; C, Table 2 — … Environmental Restrictive Declarations; D — Zoning Map Amendment ("D") Restrictive Declarations; E — Design Requirements for Plazas, Residential Plazas and Urban Plazas Developed Prior to October 17, 2007; F — Mandatory Inclusionary Housing Areas and former Inclusionary Housing Designated Areas (**parent + five borough pages**: The Bronx, Brooklyn, Manhattan, Queens, Staten Island — the six `/appendix-f-…` URLs observed); G — Radioactive Materials; H — Arterial Highways; I (no subtitle in menu; content: transit-related community-district boundary maps, Last Amended 11/21/2024, E14); J — Designated Areas Within Manufacturing Districts; K — Areas With Nursing Home Restrictions. Plus a **Preamble** (`/node/79`).

**No Appendix A exists on the portal** (`/appendix-a` → 404, E14; not in any menu). Letters B–K = 10 appendices vs the stated "11" — the count reconciliation (C's two tables? F's parent?) is not officially stated → OQ-1.

### 4.2 Numbering convention (observed + official rule)

- Section numbers are `CC-NN[N[N]]` where the two-digit prefix = article ordinal + chapter ordinal: Article I Chapter 1 → `11-…`; Article I Chapter 2 → `12-…`; Article VII Chapter 4 → `74-…` (observed: §74-948 in E11). Special-purpose-district chapters use **three-digit prefixes starting at 101-00** (official basis: §12-01(j) quotes "Sections starting with 101-00", E13).
- Hierarchy within a chapter (observed in the E9 chapter-1 inventory): 4-digit ALL-CAPS heads (e.g. `11-00 TITLE`, `11-10 ESTABLISHMENT AND SCOPE …`) → 4-digit title-case sections (`11-01 Long Title`) → 5-digit subsections (`11-111 Applicability of this Resolution`, `11-271 …`). Chapter gaps exist: Article I lists chapters 1, 2, 3, 5, 6 — **no chapter 4** (E8); whether reserved or repealed is not stated → OQ-5.
- **Official cross-reference scope rule — §12-01(j), verbatim (raw HTML, E13):** *"References within a Section or cross-references to a Section numbered with four digits shall include all following Sections with numbers whose first four digits are identical with such Section number but references or cross-references to a Section numbered with five digits shall refer only to such specific five-digit Section. For Sections starting with 101-00, references within a Section or cross-references to a Section numbered with five digits shall include all following Sections with numbers whose first five digits are identical with such Section number but references or cross-references to a Section numbered with six digits shall refer only to such specific six-digit Section."* This rule is load-bearing for M3 cross-reference resolution: a 4-digit reference is a subtree reference, not a single node.

### 4.3 Text conventions (official + observed markup)

- **Rules of construction — §12-01, full text captured verbatim** (raw HTML, E13; Last Amended 2/2/2011). Key items: (a) *"The particular shall control the general."* (b) *"In case of any difference of meaning or implication between the text of this Resolution and any caption, illustration, summary table or illustrative table, the text shall control."* (c) *"The word "shall" is always mandatory and not discretionary. The word "may" is permissive."* — **[CORRECTED AT G1 — C8]:** the source uses straight **double** quotes around "shall"/"may" (verified via `od -c` at G1, report §1.3); the original rendering with single quotes was a transcription infidelity in a quote labeled verbatim. (h) 'and' = all apply; 'or' = singly or in any combination; 'either…or' = singly but not in combination. (b) is critical: **table/illustration extractions can never override running-text extractions** in the rule pipeline.
- **Defined terms are rendered as `<em>` elements** in section HTML (verified: `<em>residential building</em>`, `<em>building</em>`, `<em>use</em>` in §12-01 markup, E13) — a machine-detectable signal linking running text to §12-10 definitions.
- **§12-10 DEFINITIONS** (node 18523; section Last Amended 3/26/2026, E9): alphabetical entries; each definition carries its own Last Amended date; district-scoped definitions carry applicability notes (e.g. *"Applicable to Article VI - Chapter 6"*); definitions originating in other sections are marked `FROM <section>` with a hyperlink (observed: *"FROM 66-11: For the purposes of this Chapter, an 'above-grade mass transit station' shall refer to a mass transit station with a platform that is located entirely above five feet from curb level."* — E9 summarizer reading of the live page; the `FROM 66-11` attribution was raw-HTML-confirmed at G1). **[CORRECTED AT G1 — C8]** (parse-fidelity additions, raw-verified, G1 report §1.10): the FROM-attribution prefix has **5 observed variants** — `FROM` (×95), `FROM SECTION` (×5), `FROM Section` (×1), `FROM:` (×4), and double-space `FROM  ` (×6) — with the section number wrapped `<a class="sec-link-inline" …><span>66-11</span></a>`; and **each definition is its own Drupal node** (`node--type-defined-term`, `about="/node/{nid}"`, `id="term-{name}"`, e.g. `/node/21970`, `id="term-above-grade mass transit station"`). Both facts are folded into fixture ZR-F3 (§6).
- **Cross-reference hyperlink format:** `href='/article-i/chapter-1#11-23'` (anchor on the chapter page) observed in §12-10 markup (E9). Chapter pages use `#CC-NN` anchors; dedicated per-section pages also exist — both URL forms must be normalized to one section identity at ingestion.
- Footnotes module is installed (`footnotes/footnotes`, E13) — footnote markup should be expected in some sections (not directly observed this task).

### 4.4 Known node-ID anchors (for fixture pinning)

| Content | Node | URL |
|---|---|---|
| Homepage | 54 | `/` |
| Preamble | 79 | `/node/79` |
| §11-02 Short Title | 18416 | `/article-i/chapter-1/11-02` |
| §12-10 DEFINITIONS | 18523 | `/article-i/chapter-2/12-10` |
| Disclaimer | 8771 | `/disclaimer` |
| Article I files directory | 32 | `/sites/default/files/article/32/…` |
| Appendix I files directory | 21238 | `/sites/default/files/appendix/21238/…` |

**[CORRECTED AT G1 — C1]:** node IDs are not the only content-entity identifier — **section-entity IDs** (e.g. **22740** for §11-47, used by the amendment-history AJAX endpoint, §3.3) form a **third identifier namespace** distinct from both Drupal node IDs and section numbers. Fixture pinning and connector keys must not conflate the three (G1 report §1.8).

---

## 5. S4 — Cross-channel discrepancies and recommended PRD §8 priority order

### 5.1 Banner date vs PDF dates

Text-currency banner: May 20, 2026. Complete/current PDF Last-Modified: 2026-06-23; newest archive snapshot: `AllArticles_23Jun2026…`. Interpretation (producer, from timestamps): the June files are a batch regeneration **containing** text current through the May 20 adoptions. Connectors must treat the banner date as the legal-currency version label and the PDF Last-Modified as a generation timestamp only.

### 5.2 HTML vs PDF granularity

HTML: per-section pages with Last Amended stamps, `<em>` term markup, hyperlinked cross-references. PDFs: no per-section retrievability (except unstable entity-print), no hyperlink semantics, but they are the only **frozen dated snapshots**. The two channels are complementary, not redundant.

### 5.3 Snapshot coverage gap

Portal archive starts 2024-03-22. Reports generated later must reproduce against stored snapshots — for any rule extracted before the next DCP snapshot lands, **our own Supabase-stored crawl snapshot is the only frozen record**. Pre-2024 text (needed for effective-date transitions, e.g. pre-City of Yes states) has **no verified official channel** yet (OQ-4).

### 5.4 Search-parameter trap

`/search` silently ignores unknown query parameters and reports zero results (§2.5). Any search-based tooling must use `search_term` and must treat "0 results" as unverifiable without a positive control query.

### 5.5 Research-method discrepancy (recorded honestly)

The WebFetch summarizer reported `/zr-downloads` archive hrefs with an `/index.php/` prefix; the archive-PDF hrefs in the raw HTML carry **no** such prefix, and the `/index.php/…` variant of the newest snapshot URL returned **404** via curl while the clean URL returned 200 (E7, E8). **[CORRECTED AT G1 — C3]:** the original diagnosis ("no such prefix in the actual markup; summarizer hallucination") was itself imprecise. The raw page **does** contain `/index.php/`-prefixed links — in the theme's site-logo and footer (`/index.php/`, `/index.php/disclaimer`, `/index.php/feedback`). `/index.php/{alias}` is a **valid Drupal front-controller route for HTML pages** (`/index.php/disclaimer` → 200, G1-verified) but 404s for `/sites/default/files/` static assets. The summarizer therefore transferred a real HTML-route prefix from the page chrome onto the PDF hrefs rather than inventing it outright (G1 report §1.5) — which cleanly explains both the summarizer's error and the producer's E7 404. Consequence for M3 unchanged: **URL-level claims must always be confirmed against raw HTML**, and connector fixtures must store raw bytes, not summarizer output.

### 5.6 Recommended priority order for M3 ingestion (PRD §8 tiers, argued from evidence)

1. **Portal HTML** (`zoningresolution.planning.nyc.gov`, tier 4 — official HTML ingestion) — **ingestion primary.** No tier 1–3 channel exists (no API, no SODA dataset, no structured download of the text). Per-section crawl driven by the article→chapter→section link tree (no sitemap available); store raw HTML per section in Supabase Storage with retrieval timestamp + banner date + per-section Last Amended.
2. **Dated complete-PDF snapshots** (`/zr-downloads`, tier 5) — reproducibility archive; download each new snapshot once on a Render worker (72–85 MB, well within worker bounds; never on the owner PC) into `source-pdfs`.
3. **Per-article / per-chapter PDFs** (tier 5) — spot cross-check channel for G1-style verification of HTML extraction (chapter PDFs are KB–MB scale).
4. **entity-print per-section PDFs** — evidence convenience only; undocumented, 504s on large nodes; never a dependency.
5. **nyc.gov DCP pages** — blocked (403) for automation; browser-capture only for print-edition statements (OQ-11). **[RESOLVED AT G1 — C2]:** for amendment-adoption records specifically, `council.nyc.gov` and `legistar.council.nyc.gov` are automation-accessible official channels (no bot wall) — use them as the official fallback before resorting to browser capture (OQ-2 resolved this way).

---

## 6. Proposed contract-test fixture pack (KB-scale; captured at connector build)

All fixtures: raw unmodified responses + request URL + retrieval timestamp. No bulk PDF downloads in fixtures — HEAD metadata only for the large files.

| # | Fixture | Request | Asserts |
|---|---|---|---|
| ZR-F1 | Section fetch (normal) | `GET /article-i/chapter-1/11-02` | 200; title `11-02`; `Last Amended` `<time datetime=…>` parse; body text extraction stable |
| ZR-F2 | Chapter TOC + full text | `GET /article-i/chapter-1` | section inventory (11-00 … 11-70) with per-section hrefs and `#CC-NN` anchors; heading-case hierarchy (CAPS heads vs title-case sections vs 5-digit subsections) |
| ZR-F3 | Definitions structure | `GET /article-i/chapter-2/12-10` (bounded extraction) | alphabetical entries; per-definition Last Amended; applicability note parse; `FROM <sec>` cross-ref parse. **[CORRECTED AT G1 — C8]:** FROM-prefix parser must tolerate the 5 observed variants (`FROM`/`FROM SECTION`/`FROM Section`/`FROM:`/double-space `FROM  `) with the section number wrapped `<a class="sec-link-inline"><span>`; assert per-definition node identity (`node--type-defined-term`, `about="/node/{nid}"`, `id="term-{name}"`) |
| ZR-F4 | Defined-term markup | §12-01 body | `<em>` term spans map to §12-10 entries; verbatim text equality against stored fixture |
| ZR-F5 | Cross-reference semantics | §12-01(j) + observed `href='/article-i/chapter-1#11-23'` | 4-digit ref expands to subtree; 5-digit ref is exact; 101-00+ rule; anchor-URL vs page-URL normalization |
| ZR-F6 | Table handling | a section containing a summary table (select at build; none captured this task — OQ-8) | table extraction + §12-01(b) text-controls-over-tables flag |
| ZR-F7 | Missing section (failure) | `GET /article-i/chapter-1/11-99` | HTTP 404 (verified live 2026-07-16) |
| ZR-F8 | Search positive + parameter guard | `/search?search_term=floor+area+ratio` vs `/search?fulltext=…` | **[CORRECTED AT G1 — C6]:** assert on the **results-count string / results region** (`Your search returned <strong>N</strong> results` and the results block), NOT a global `views-row` count — the wrong-param page carries **25 stray `views-row` elements in non-results blocks** (G1 report §1.9). Correct param → count ≥1 in results region; wrong param → reported count 0 (trap detection with positive control) |
| ZR-F9 | Currency banner | `GET /` | `All text changes approved by the city council as of <span class='date'>…</span>` parse; date advances monotonically; alert on parse failure (schema drift) |
| ZR-F10 | Amendment feed | `GET /recently-adopted` (+ one stub page) | entry fields (name, application number, date, section ref); pagination; new-entry detection triggers re-crawl of referenced sections |
| ZR-F11 | Archive manifest diff | `GET /zr-downloads` | snapshot href list vs stored manifest; new-snapshot detection; filename-pattern tolerance (two naming styles observed) |
| ZR-F12 | Snapshot HEAD | `HEAD` newest archive PDF | 200, `application/pdf`, Content-Length recorded as version metadata (no download in CI) |
| ZR-F13 | Portal-unavailable (failure) | recorded 504 shape from `/print/pdf/node/18523` | 5xx handling: retry with backoff, no partial-content persistence, job resumability |
| ZR-F14 | Amendment-diff (M3) | same section, two stored crawl snapshots | text diff produces a section-version record keyed by Last Amended change |

---

## 7. Connector implementation plan (plan only — no code in this task)

1. **`zr-portal-crawler` (Render worker, monthly + amendment-triggered):** crawl article → chapter → section tree; store raw HTML per section in Supabase Storage (`source-snapshots`); persist section records (number, title, hierarchy path, Last Amended, body, `<em>` term spans, cross-ref hrefs, banner date, retrieval timestamp) → `legal_sections` / `legal_section_versions`. Re-crawl triggers: banner-date change (ZR-F9) or new `/recently-adopted` entry (ZR-F10).
2. **`zr-snapshot-archiver`:** on new `/zr-downloads` entry, download the dated complete PDF on a worker → `source-pdfs` bucket; record size/Last-Modified/banner date.
3. **Cross-check job (G1-style):** per release, sample N sections and compare HTML text against the corresponding chapter PDF text (tier-5 cross-check per PRD §8).
4. **Rate discipline:** the site is bot-friendly today (no 403s, no robots.txt content restrictions beyond Drupal defaults — E5), but crawls must stay low-rate and off-peak; the platform is a shared Pantheon instance that already 504s on heavy pages.

---

## 8. OPEN QUESTIONS ledger

| # | Question | Status / what is needed |
|---|---|---|
| OQ-1 | "11 Appendices" count vs observed letters B–K (10) — is Appendix A reserved/repealed? Does the count include C's two tables or F's parent? | OPEN — `/appendix-a` 404 (live); no official statement found on the portal; nyc.gov 403 |
| OQ-2 | Official confirmation that the 12/5/2024 Last-Amended wave = "City of Yes for Housing Opportunity" adoption | **RESOLVED AT G1 (C2)** — CoY-HO (N 240290 ZRY) adopted by City Council 2024-12-05; confirmed via the portal's own amendment popup + council.nyc.gov press release 2024-12-05 + Legistar LU 0181-2024 (G1 report §1.7); marker removed from §3.4/E18 |
| OQ-3 | Does "Last Amended" mean City Council adoption date or legal effective date? | **NARROWED AT G1 (C1)** — the amendment popup officially labels per-amendment dates "Effective Date"; §11-47 Last Amended = popup Effective Date; adoption-vs-effective remains undiscriminated where the two coincide (G1 report §1.8); still open for the non-coinciding case |
| OQ-4 | Where is pre-2024-03-22 historical ZR text officially retrievable? | OPEN — portal archive starts 2024-03-22; BYTES/nyc.gov pages 403; needed for effective-date-transition rules |
| OQ-5 | Article I has no Chapter 4 (chapters 1,2,3,5,6) — reserved or repealed? Full chapter inventory per article not yet enumerated | OPEN — enumerate all 14 article pages at connector build; do not infer chapter continuity |
| OQ-6 | entity-print (`/print/pdf/node/{nid}`) stability and DCP's intent for it; 504 threshold | OPEN — undocumented Drupal module route; works for §11-02 (44,977 B), 504s for §12-10; treat as convenience only |
| OQ-7 | Canonical hostname: `zoningresolution.planning.nyc.gov` (PRD §30) vs `zr.planning.nyc.gov` (disclaimer's self-reference) | **NARROWED AT G1 (C9)** — each hostname serves a self-referencing `Link: <https://{host}/node/54>; rel="canonical"` header; no cross-host canonical (G1 report §1.1). Hostname choice is a connector-config decision with the alias recorded |
| OQ-8 | Table markup conventions in section HTML (colspan structures, illustrative vs summary tables) | OPEN — no table-bearing section captured this task; required for ZR-F6 before M3 table ingestion |
| OQ-9 | `nyczr_amendment_popup` module behavior — does it expose per-section amendment metadata beyond the Last Amended stamp? | **RESOLVED AT G1 (C1)** — yes: `GET /ajax/get/amendment/section/{sectionEntityId}?_wrapper_format=drupal_ajax` + `X-Requested-With: XMLHttpRequest` → 200 JSON, 6-column amendment-history table (Effective Date \| ULURP/CPC Report \| Project Name \| Action \| Notes \| Description); undocumented, entity-print-grade stability caveats; see §3.3 (G1 report §1.8) |
| OQ-10 | `/recently-adopted` feed total depth and whether entries are ever revised/removed | **PARTIALLY RESOLVED AT G1 (C5)** — depth = **31 pages (0–30)** via the raw `?page=30` "Go to last page" pager href; entry mutability (revision/removal) STILL OPEN — full walk at connector build |
| OQ-11 | Official print-edition status and any statement identifying the legally authoritative ZR publication | OPEN — the portal disclaimer conspicuously does NOT claim the site is the official version; the authoritative-publication statement likely lives on 403-bound nyc.gov or in the City Charter/adopted resolution — needs qualified-human/legal review before any "verified" labeling policy is finalized |
| OQ-12 | Full-ZR complete PDF (102.6 MB, `Zoning Resolution Complete.pdf`) vs newest archive snapshot (75.6 MB, compressed) — content identity unverified | OPEN — presumed same text, different compression; verify at snapshot-archiver build if the complete file is used at all |

---

## 9. Source register (all fetched live by the producer on 2026-07-16)

| Ev | URL | Access method | Used for |
|---|---|---|---|
| E1 | `https://zoningresolution.planning.nyc.gov/` | WebFetch (summarized) | initial channel survey; nav overview; "server-rendered" observation |
| E2 | `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=zoning%20resolution&limit=20` | live fetch | absence of any ZR-text Open Data dataset (all results geodata; **[CORRECTED AT G1 — C7]:** count observed at review = `resultSetSize` 25, not 12) |
| E3 | `https://zoningresolution.planning.nyc.gov/` | raw curl → `grep` (62,772 B HTML saved) | verbatim currency banner incl. `<span class='date'>`; 14 article + 16 appendix-page hrefs; "14 Articles and 11 Appendices…" statement; homepage = node/54; recently-adopted hrefs |
| E4 | 404-page response headers (via E7's `/index.php/…` probe) | curl -I | `X-Generator: Drupal 9`; Pantheon/varnish headers |
| E5 | `/jsonapi`; `/node/18523?_format=json`; `/node/18416?_format=json` implied class; `/sitemap.xml`; `/robots.txt` | WebFetch + curl status probes | API-surface absence: 404 / 406 / 404; standard Drupal robots.txt |
| E6 | `/sites/default/files/article/Zoning%20Resolution%20Complete.pdf`; `/sites/default/files/article/32/Article%20I.pdf`; `/sites/default/files/article/32/chapters/Chapter%201.pdf` | curl -I (HEAD only) | sizes 102,565,724 / 3,170,980 / 149,858 B; all Last-Modified 2026-06-23 |
| E7 | `/index.php/sites/default/files/2026-06/AllArticles_23Jun2026_compressed_0.pdf` | curl -I | **404** — summarizer-reported `/index.php/` prefix disproved (§5.5) |
| E8 | `/zr-downloads` (raw curl saved) + `/sites/default/files/2026-06/AllArticles_23Jun2026_compressed_0.pdf` (curl -I) + `/article-i` (WebFetch) | raw curl + HEAD + WebFetch | 10 archive hrefs verbatim; sizes list; snapshot 200 = 75,589,847 B Last-Modified 2026-06-24; Article I chapter list (1,2,3,5,6) + article PDF href |
| E9 | `/article-i/chapter-1` (WebFetch); `/article-i/chapter-2` (WebFetch); `/article-i/chapter-2/12-10` (WebFetch); `/article-i/chapter-1/11-02` (raw curl) | WebFetch + raw curl | full chapter-1 section inventory with hrefs; §12-10 structure (alphabetical, applicability notes, FROM refs, per-definition dates); raw `Last Amended … <time datetime="1961-12-15T12:00:00Z">` markup; node 18416; §12-10 Last Amended 3/26/2026, node 18523 |
| E10 | `/entityprint/pdf/node/18523` (curl -I, 302); `/print/pdf/node/18523` (curl -I, **504**); `/print/pdf/node/18416` (curl -I, 200, 44,977 B, `filename="1102.pdf"`) | curl -I | per-section print-PDF channel + its failure mode |
| E11 | `/recently-adopted/20-berry-st-n-240272-zrk` (WebFetch); `/recently-adopted` (raw curl) | WebFetch + raw curl | amendment-stub fields (date 3/26/2026, `Section 74-948 (Map 1)`, `N 240272 ZRK`); 35 views-rows; pager `?page=6..8` |
| E12 | `/disclaimer` (raw curl, stripped text) | raw curl | full disclaimer verbatim (WITHOUT WARRANTIES…; CHANGES ARE MADE PERIODICALLY…; DCP IS NOT RESPONSIBLE…; site self-named `HTTPS://ZR.PLANNING.NYC.GOV`); contents-menu article/appendix titles incl. Appendix F borough pages; node 8771 |
| E13 | `/article-i/chapter-2/12-01` (raw curl, full body extracted); `/search?fulltext=…` ×2; `/search?search_term=floor+area+ratio`; `/search?search_term=city+of+yes` (all raw curl) | raw curl | §12-01 items (a)–(j) verbatim incl. (j) cross-ref rule; `<em>` defined-term markup; search form `search_term` param + `nyczr_search_global_search_form`; 35 hits vs 0-hit trap; "city of yes" 0 hits; drupalSettings libraries (`nyczr_amendment_popup`, `footnotes`); New Relic/GA only JS |
| E14 | `/appendix-i` (WebFetch); `/appendix-a` (curl status) | WebFetch + curl | Appendix I title/content/Last Amended 11/21/2024 + PDF href with trailing-space filename (**[CORRECTED AT G1 — C4]:** PDF now HEAD-verified, §2.3); `/appendix-a` **404**; Preamble `/node/79` (raw E3/E12 grep) |
| E15 | `/article-i/chapter-1/11-99`; `/article-xv` | curl status probes | clean 404 failure behavior (S5) |
| E16 | `https://zr.planning.nyc.gov/` | curl -I + curl title grep | 200; `<title>Homepage \| Zoning Resolution` — alias hostname live |
| E17 | `https://www.nyc.gov/site/planning/zoning/zoning-text.page`; `https://www.nyc.gov/site/planning/index.page` | curl status probes | **HTTP 403** ×2 — nyc.gov bot protection recorded (S5) |
| E18 | WebSearch result listing (law-firm alerts: gtlaw, hklaw, nixonpeabody, akerman, herrick, et al.) | search-evidenced only | City of Yes adoption date 2024-12-05 — secondary sources only at production time; no content claim was promoted to fact. **[RESOLVED AT G1 — C2]:** superseded by three official channels (§3.4; G1 report §1.7); marker removed |
