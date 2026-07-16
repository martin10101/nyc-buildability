---
name: m1-t004-g3-carryforward
description: M1-T004 ZR text-corpus research G3 PASS (2026-07-16, zero defects); carry-forwards for M3 legal-corpus ingestion (zr-portal-crawler, snapshot archiver, amendment-endpoint enrichment-only owner directive)
metadata:
  type: project
---

M1-T004 (NYC Zoning Resolution text corpus research) G3 reviewed 2026-07-16: **PASS, zero defects** at commit ddebcca. All G1 corrections C1-C9 verified applied in both deliverables; stale-marker grep clean (only the line-7 discipline definition in the doc; zero in registry JSON — the M1-T001 D1-D3 defect class is absent). All five live re-runs reproduced exactly: banner "May 20, 2026"; 11-02 `<time datetime="1961-12-15T12:00:00Z">`; /jsonapi 404 + ?_format=json 406; Chapter 1.pdf HEAD 149,858 B; amendment AJAX endpoint 22740 → 200 JSON **4,230 B** (byte-identical to G1) with N240290ZRY/CoY-HO row. /article-xv 404 and nyc.gov 403 re-confirmed.

Carry-forwards to enforce when reviewing M3 legal-corpus ingestion tasks (zr-portal-crawler, zr-snapshot-archiver, legal_sections schema):
1. **OWNER DIRECTIVE (registry known_limitations):** the `/ajax/get/amendment/section/{id}` endpoint is monitored OPTIONAL ENRICHMENT with graceful fallback ONLY; amendment/legal-text truth chain = server-rendered section HTML (Last Amended stamps) + /recently-adopted + dated PDF snapshots. FAIL any task that makes the AJAX endpoint (or entity-print) a dependency.
2. Three identifier namespaces must not be conflated: section number, Drupal node ID, section-entity ID (22740-class).
3. §12-01(j) cross-ref scope: 4-digit ref = subtree, 5-digit = exact node; 101-00+ chapters shift the rule one digit. §12-01(b): text controls over tables/illustrations in extraction.
4. FROM-attribution parser must tolerate 5 variants (FROM/FROM SECTION/FROM Section/FROM:/double-space) with `<a class="sec-link-inline"><span>` wrap; each §12-10 definition is its own `node--type-defined-term` node.
5. Fixtures raw-capture only (summarizer transferred a real /index.php/ HTML-route prefix onto PDF hrefs — C3); search uses `search_term` with results-region assertion (ZR-F8/C6, 25 stray views-rows on wrong-param pages).
6. Open residuals gating M3 pieces: OQ-8 (table markup) before ZR-F6/table ingestion; OQ-5 (full 14-article chapter inventory) at crawler build; OQ-4 (pre-2024 text) for effective-date transitions; OQ-12 (102.6MB vs 75.6MB PDF identity) at archiver build; OQ-10 mutability at feed-walk. OQ-11 (which publication is legally authoritative) is QUALIFIED-HUMAN/LEGAL — fail any agent task that closes it.
7. Version pinning contract: banner date = legal currency; PDF Last-Modified = generation timestamp; per-section Last Amended semantics narrowed but adoption-vs-effective undiscriminated where dates coincide (OQ-3).
8. Rate discipline: shared Pantheon instance 504s on heavy pages; crawls low-rate/resumable; snapshot downloads (72-85 MB) on Render workers only, never owner PC.

Observation (not a defect): registry known_limitations OQ-3 line does not cross-reference the C1 narrowing (popup label "Effective Date"); the narrowing is recorded in the same file's open_questions, so no M1-T003-D1-style supersession exists.

**Why:** every corrected fact was verified present in BOTH the doc and the machine-consumable registry (the M1-T003 D1 lesson applied); live evidence reproduced byte-exact.
**How to apply:** first checks when reviewing anything consuming `docs/research/zoning-resolution-2026-07-16.md` / `source-registry-drafts/zoning-resolution.json`, or any M3 ingestion/crawler/archiver task packet. Related: [[m1-t003-g3-carryforward]], [[m1-t001-g3-carryforward]].
