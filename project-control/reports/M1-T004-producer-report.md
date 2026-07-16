# M1-T004 Producer Report — Official-source research: NYC Zoning Resolution text corpus

- **Task ID:** M1-T004
- **Producer agent:** official-source-researcher
- **Date:** 2026-07-16
- **Status requested:** `awaiting_gate` (G1 data-contract review + G3 walkthrough)
- **Report path:** `project-control/reports/M1-T004-producer-report.md`

## 1. Files changed (all new; no existing file modified)

1. `docs/research/zoning-resolution-2026-07-16.md` — full research report (exec summary, S1–S5, 14-fixture pack, 12-item OQ ledger, 18-entry source register E1–E18)
2. `docs/research/source-registry-drafts/zoning-resolution.json` — PRD §8.2 registry draft, all 18 fields (nulls where unknown), 12 open questions
3. `project-control/reports/M1-T004-producer-report.md` — this report

Contracts/schema changed: none. Production code touched: none. Local footprint: KB-scale docs + ~200 KB of temporary HTML captures in the session `/tmp` (auto-cleaned); no PDFs downloaded (HEAD only); low-storage policy respected.

## 2. Per-scenario evidence (exact commands/URLs, live 2026-07-16, ~21:14–21:25 UTC)

### S1 — Channel enumeration (normal) — DONE
- Portal live: `curl -s https://zoningresolution.planning.nyc.gov/` → 200, 62,772 B HTML saved and grepped raw. Drupal 9 proven by `X-Generator: Drupal 9` header (on the 404 response for the `/index.php/…` probe) + Pantheon/varnish headers.
- Alias host: `curl -sI https://zr.planning.nyc.gov/` → 200; title `Homepage | Zoning Resolution`.
- API surface probed and ABSENT: `/jsonapi` → 404 (WebFetch); `curl -w %{http_code} "/node/18523?_format=json"` → **406**; `/sitemap.xml` → 404.
- No Open Data ZR-text dataset: `api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=zoning%20resolution&limit=20` → 12 results, all geodata.
- PDF HEADs (no downloads): `Zoning Resolution Complete.pdf` → 200, **102,565,724 B**, Last-Modified Tue, 23 Jun 2026 00:58:19 GMT; `article/32/Article%20I.pdf` → 200, 3,170,980 B; `article/32/chapters/Chapter%201.pdf` → 200, 149,858 B; newest archive snapshot `2026-06/AllArticles_23Jun2026_compressed_0.pdf` → 200, **75,589,847 B**.
- Undocumented per-section print route: `curl -sI /entityprint/pdf/node/18416` → 302 → `/print/pdf/node/18416` → 200, 44,977 B, `filename="1102.pdf"`; same route for node 18523 (§12-10) → **504 Gateway Timeout**. Recorded as official-but-undocumented, stability unverified.

### S2 — Versioning/effective-date model (boundary) — DONE
- Currency banner captured verbatim from raw HTML: `All text changes approved by the city council as of <span class='date'>May 20, 2026</span>`.
- Per-section stamp raw markup: `Last Amended</span><div class="field-content"><time datetime="1961-12-15T12:00:00Z" class="datetime">12/15/1961</time>` (from `curl /article-i/chapter-1/11-02`).
- Historical versions: `/zr-downloads` raw HTML → exactly 10 dated complete-PDF snapshot hrefs, 2024-03-22 → 2026-06-23 (verbatim list in report §2.4).
- Amendment feed: `/recently-adopted` → 35 views-rows p.1, pager to `?page=8`; stub page `/recently-adopted/20-berry-st-n-240272-zrk` → date 3/26/2026, `Section 74-948 (Map 1)`, `N 240272 ZRK`, no amendment text.
- Disclaimer verbatim (raw curl `/disclaimer`): "CHANGES ARE MADE PERIODICALLY TO THE ZR AND THESE CHANGES MAY OR MAY NOT BE IMMEDIATELY REFLECTED…"; no official-version claim anywhere.
- City of Yes: `/search?search_term=city+of+yes` → 0 results (0 views-rows); in-text evidence §11-47 "…Filed Prior to December 5, 2024" + many 12/5/2024 Last-Amended stamps; the CoY↔12/5/2024 linkage rests on law-firm secondary sources only → **[NEEDS G1 RE-VERIFICATION]**, OQ-2.

### S3 — Structure inventory (missing/ambiguous) — DONE
- 14 articles + appendix menu extracted from raw HTML with titles; Appendix F = parent + 5 borough pages; `/appendix-a` → 404; "11 Appendices" count unreconciled → OQ-1 (not guessed).
- Full §12-01 rules of construction captured verbatim by raw curl + tag-strip, including the load-bearing (j) cross-reference-scope rule and (b) text-controls-over-tables rule.
- §12-10 structure (alphabetical, per-definition dates, applicability notes, `FROM 66-11` attributions) from live fetch; defined terms proven to be `<em>`-marked in raw markup.
- Chapter gap observed (Article I: chapters 1,2,3,5,6) → OQ-5, no inference recorded.

### S4 — Cross-channel discrepancies (conflict) — DONE
- Banner date (May 20) vs PDF generation dates (Jun 23/24) distinguished; snapshot-coverage gap (nothing pre-2024-03-22); HTML vs PDF granularity; search-parameter trap (`fulltext=` silently ignored → false "0 results"; `search_term=floor+area+ratio` → 35 rows). Recommended PRD §8 order for M3: portal HTML (tier 4) primary → dated snapshots (tier 5) reproducibility archive → per-article/chapter PDFs cross-check → entity-print convenience only → nyc.gov browser-capture only. No tier 1–3 channel exists.

### S5 — Failure/bot-protection cases (failure) — DONE
- `www.nyc.gov/site/planning/zoning/zoning-text.page` → **403**; `www.nyc.gov/site/planning/index.page` → **403** (exact codes recorded).
- Clean 404s: `/article-i/chapter-1/11-99`, `/article-xv`, `/appendix-a`, `/index.php/sites/default/files/2026-06/AllArticles_23Jun2026_compressed_0.pdf`.
- 504 on `/print/pdf/node/18523` recorded as the portal-unavailable fixture shape (ZR-F13).
- **Summarizer-hallucination catch:** WebFetch reported `/index.php/`-prefixed archive hrefs; raw HTML has no such prefix and the prefixed URL 404s — documented in report §5.5 as a method-level warning for G1 and connector fixtures.

## 3. Test results / expected vs actual

Research task — no code tests. Every factual claim in the deliverables carries an E1–E18 evidence tag; expected-vs-actual deltas that arose (JS-app assumption false → server-rendered Drupal; `/index.php/` prefix false; `fulltext` param false) are all recorded in the report rather than silently corrected.

## 4. Assumptions and defaults

**Assumptions: none.** Everything stated as fact was live-verified; everything else is in the OQ ledger (12 items) or marked [NEEDS G1 RE-VERIFICATION] (2 markers: City of Yes adoption date, E18; and no others — E14 Appendix I PDF href was observed on the live page but its size was not HEAD-verified, stated as such).

## 5. Known limitations

1. City of Yes ↔ 12/5/2024 linkage rests on secondary sources (OQ-2) — G1 should re-verify via a browser-capable official channel.
2. "Last Amended" semantics (adoption vs effective) not officially defined (OQ-3) — material for effective-date rule logic; needs resolution before M4 rule publication.
3. Table markup not yet inspected (OQ-8) — required before M3 table ingestion; fixture ZR-F6 reserved.
4. Only Article I's chapter tree was enumerated; full 14-article chapter inventory deferred to connector build (OQ-5).
5. WebFetch summarization was used for some page descriptions (E1, E9 chapter-2/12-10, E11 stub, E14); all verbatim quotes and URL-level claims were confirmed by raw curl captures, but G1 may wish to spot-check the summarized structural descriptions.

## 6. Security/provenance impact

None on production (docs only). Provenance model strengthened: the report establishes the banner-date + per-section Last-Amended + snapshot-PDF triple as the ZR version-pinning contract for M3.

## 7. New risks / dependencies discovered

1. **No structured channel exists** for the ZR text — M3 must budget for HTML-crawl ingestion (tier 4), a heavier lift than the SODA/ArcGIS connectors of M1-T001/T003.
2. Pre-2024 historical text is currently unobtainable from verified official channels (OQ-4) — a dependency for any retroactive effective-date analysis.
3. The portal's legal-status disclaimer (no official-version claim) feeds directly into the platform's "verified" labeling policy — requires qualified-human input (OQ-11).

## 8. Recommended next tasks

1. M3 pre-task: browser-capable capture session for the 403-bound nyc.gov pages (resolves OQ-2, OQ-4, OQ-11 inputs; shared with M1-T001/T003 OQ-1).
2. M3 design task: `zr-portal-crawler` + `zr-snapshot-archiver` per report §7 with the 14-fixture pack (§6).
3. Full 14-article chapter/section inventory crawl (closes OQ-5, feeds `legal_sections` seeding).

## 9. Commands run (complete list)

All fetches live 2026-07-16. WebFetch: portal home ×2, `/jsonapi`, Socrata catalog, `/zr-downloads`, `/article-i`, `/article-i/chapter-1`, `/article-i/chapter-2`, `/article-i/chapter-2/12-10`, `/disclaimer`, `/recently-adopted/20-berry-st-n-240272-zrk`, `/search?fulltext=city+of+yes`, `/appendix-i`, `/article-i/chapter-2/12-01`. WebSearch: City of Yes adoption ×1. Bash/curl (all KB-scale or HEAD-only): HEADs on 6 PDFs + entityprint/print routes ×3; status probes on `/node/18523?_format=json`, `/sitemap.xml`, `/appendix-a`, `/article-i/chapter-1/11-99`, `/article-xv`, nyc.gov ×2, zr.planning.nyc.gov ×2; raw GET + grep on `/`, `/zr-downloads`, `/article-i/chapter-1/11-02`, `/article-i/chapter-2/12-01`, `/disclaimer`, `/search` (4 query variants), `/recently-adopted`, `/robots.txt`. No permission denials occurred this run. No git/gh/project_control commands run (ADR-005).
