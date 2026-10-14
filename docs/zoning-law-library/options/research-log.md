# Research log — options second pass (M3-T007)

**Unreviewed draft (ADR-007).** Every search the pass rests on: the ten read-only research-helper
returns (saved outside git at `/root/project/lanes-runtime/owner-docs/session-2026-10-14a/research/`)
and the producer's own checks. Format: source | query or URL | result | missing item | next step.
Access blocks are recorded, never evaded. The snapshot folder decides capture state; the rulesets
folder decides handled state; official pages carry the "last amended" date read on the page.

## Producer's own checks (2026-10-14)

- `docs/research/zr-snapshots/v1/` (folder listing) | which `zr-*` snapshots exist | FOUND 189 files | — | the folder is authoritative on capture; HG's `NOT CAPTURED` for 23-20/33-12/33-121/35-30/35-31/35-32/35-33 was wrong (they are captured); no `zr-24-*`, no `zr-23-154`, no `zr-77-*`, no `zr-23-51` → those are NOT CAPTURED.
- snapshot `zr-32-131` / `zr-32-161` | titles | FOUND: 32-131 = Use Group III (community facilities); 32-161 = Use Group VI (shops) | — | confirms the option-5 use correction; `benchmark-r6b-sections.json` mislabel listed in the producer report.
- snapshot `zr-36-64` | body | FOUND: "whenever a #zoning lot# is divided by a boundary between districts having different requirements for #accessory# off-street loading berths … Article VII, Chapter 7, shall apply" | — | confirms 36-64 is a loading-berth pointer, not a general C-district rule.
- snapshot `zr-66-11` | title/date | FOUND: "Definitions", Article VI Ch 6, 8/14/2025 | — | confirms 66-11 is not the transit-zone definition (the 12-10 terms are).
- snapshot `zr-35-33` | scope sentence | FOUND: "In C1 and C2 Districts mapped within R6 Districts without a letter suffix, and in R7-1 Districts…" | — | confirms 35-33 excludes R6B.
- snapshot `zr-35-31` | combination rule | FOUND: "The total of all such #floor area ratios# shall not exceed the greatest #floor area ratio# permitted for any such #use# on the #zoning lot#…" | — | greatest-single-use cap confirmed.
- snapshot `zr-23-22` | R6B row | FOUND: R6B standard 2.00, qualifying 2.40, no footnote | — | confirms the option-2/3 FAR figures.
- snapshot `zr-23-432` | R6B row | FOUND: min base 30; standard 45/55; qualifying 45/65; no footnote | — | confirms the option-2/3 heights.
- snapshot `zr-33-121` | R6B row + columns | FOUND: lists C2-2; row "R5D R6B" A/B/C all 2.00; para (a) commercial ≤ Column A | — | confirms the overlay commercial/CF FAR.
- snapshot `zr-35-32` + `zr-12-10-qualifying-residential-site` | district scope | FOUND: rows and the term list R1-R5 only, no R6/R6B | — | confirms 35-32 does not reach R6B.
- official ZR portal | GET /article-ii/chapter-3/23-51 (WebFetch) | FOUND (HTTP 200), "Applicability", 12/5/2024, "the provisions of this Section shall not apply to #rooming units#" | — | confirms the option-9 density-exclusion correction.
- official ZR portal | GET /article-ii/chapter-7/27-111 (WebFetch) | FOUND (HTTP 200), "General definitions", 12/5/2024; defines UAP/MIH/regulatory-agreement; cites 23-154 (offsite option), 23-22, 23-432 | — | confirms the substantive UAP/affordable rules are in Article II Chapter 7, not 23-154.
- official ZR portal | GET /article-ii/chapter-4/24-11 (WebFetch) | FOUND (HTTP 200), "Maximum Floor Area Ratio and Percentage of Lot Coverage", 12/5/2024; R6B FAR 2.00, coverage 80 corner / 60 interior-or-through | — | confirms the option-6/7 CF FAR/coverage.
- official ZR portal | GET /article-ii/chapter-4/24-162 (WebFetch) | FOUND (HTTP 200), 12/5/2024; opening "…except R4-1, R4A, R4B, R5D, R6A, R6B and R6D Districts…" | — | confirms 24-162 excludes R6B.
- official ZR portal | GET /article-ii/chapter-3/23-154 (WebFetch, then documented browser-UA GET fallback) | **ACCESS BLOCKED, HTTP 403** on both | the verbatim text and current title of §23-154 | try the print/PDF node channel, else keep a durable access-blocked note; needed only for the UAP Offsite Option, not the benchmark lot.
- reference cases `docs/reference-cases/R6B/cases/step-p5-worked.json`, `step-p4-worked.json`, `suffix.json` | settled rows (two independent readers) | FOUND: transit-zone-value (Outer); mixed-use combination (greatest single-use FAR); shared-floor-area rule; parking per option; 34-111 exceptions do not reach R6B; qualifying-residential-site not R6B; dwelling-unit factors; suffix inheritance | — | cited in the option files for the points they settle.

## Helper HA — options 2 & 3 (affordable / senior)
- ZR portal | GET 23-22 / 23-432 / 12-10 (qualifying affordable, qualifying senior) / 27-111 / 27-131 / 27-14 / 27-151 | FOUND (200) | the Article II Chapter 7 chapter and Appendix F are NOT CAPTURED | capture 27-111, 27-131, 27-133 + Appendix F.
- ZR portal | GET 23-154 | ACCESS BLOCKED (HTTP 403) | §23-154 text/title | print/PDF node channel or durable block.
- Web (general) | "UAP section number" | third-party commentary only (not a source) | — | official text governs.

## Helper HB — option 5 (shops / mixed)
- ZR portal | GET 32-131 / 32-161 / 32-421 / 33-12 / 33-121 / 35-30 / 35-31 / 35-32 / 35-631 / 77-11 / 11-122 | FOUND (200) | 32-421 "select commercial overlays" sub-paragraph not extractable; R6B 33-121 row (later pinned by HX1); 33-26 date | print/PDF reads; see HX1.
- repo (NB-06) | 34-11 / 34-24 / 34-231 / 34-232 / 35-63 / 35-632 / 23-432 / 23-433 | FOUND | — | —.

## Helper HC — options 6 & 7 (community facility)
- ZR portal | GET 24-11 / 24-111 / 24-161 / 24-162 / 24-04 / 24-52 / 24-522 / 24-56 / 24-33 / 24-34 / 24-35 / 24-36 / 24-391 / 35-31 / 35-33 / 33-121 (full table) + Article II Ch 2 & Ch 4 indexes | FOUND (200; one browser-UA GET fallback for 24-52 body where WebFetch dropped it) | all `zr-24-*` NOT CAPTURED | capture the Chapter 4 sections options 6/7 rely on.
- No access-blocked events.

## Helper HD — option 8 (split lot)
- ZR portal | GET Article VII Ch 7 TOC / 77-01 / 77-11 / 77-22 / 77-27 / 77-28 / 36-64 / Article II Ch 3 TOC / 23-371 / Article II Ch 7 (renumbered) | FOUND (200) | 77-12/21/211/24/25/26 bodies (later read by HX1); overlay-edge-as-district-boundary unresolved | capture the 77-xx sections; see HX2.
- ZR portal | GET 12-10 (zoning-lot term) | NOT FOUND on the fetched slice (1.3 MB page) | the live zoning-lot term text | relied on the pinned capture `zr-12-10-zoning-lot` (disclosed).
- sample PDF | `pdftotext -layout` pp. 2, 5, 82-87 | FOUND | — | sample is Reading A.1; "Split Zone = No".

## Helper HE — option 9 (shared housing)
- ZR portal | GET 23-51 / 22-122 / 54-311; search "shared housing" (0 results), "rooming" (section list) | FOUND | 22-122/23-51/54-311 NOT CAPTURED; exact "this Section" referent | capture the nodes; see HX2.
- nysenate.gov | MDL §4; State S10497 / A11136 status | FOUND (official; in committee 2026) | — | pending 2027 legislation.
- codelibrary.amlegal.com | GET HMC §27-2004 | ACCESS BLOCKED (HTTP 403) | the HMC rooming-unit definition text | fetch via a browser-capable channel.
- legistar | NYC Intro 1475-2025 (guessed id) | NOT FOUND ("Invalid parameters!") | the bill's committee status | look up by File/Intro number.

## Helper HF — option 10 (parking / transit)
- repo snapshots | 25-02/20/211/212/22/221/222/23/231/232/80/811; 36-21/231/232/25/62/70/711; 66-11; appendix-i; 12-10 transit-zone terms | FOUND | "Transit Zone, Inner" and 25-30+ CF parking and 25-241 NOT CAPTURED | capture them.
- ZR portal | GET 25-211 / 25-221 / 25-222 (live re-confirm) | FOUND (200), 12/5/2024, R6 row 25% / 0% / 15 | — | —.
- NYC Open Data `6ztr-wgff` | point-in-polygon on the lot point | FOUND: `transtzone` = "Outer Transit Zone", exactly one polygon | — | agrees with the recorded reference value.
- s-media.nyc.gov | appendix I transit-zones metadata PDF | ACCESS BLOCKED (binary/unreadable to the fetch tool) | field-level provenance | optional offline parse.

## Helper HG — option 11 (combinations)
- ZR portal | GET 35-31 / 35-32 / 35-33 / 23-20 / 33-121 / 24-11 | FOUND (200), 12/5/2024 | reported 23-20/33-12/33-121/35-30/35-31/35-32/35-33 as NOT CAPTURED **(wrong — the folder shows them captured; corrected by the producer and HX1)** | list the folder for capture state, never an index.
- repo | scenario add-on engine (catalogue.py, recalculation.py, options.py) | FOUND | — | option 11 currently reduces to the single best qualifying-housing program.

## Helper HS — the owner's sample (options 2-7, 9-11)
- sample PDF | `pdftotext -layout` pp. 2, 16-87 (per-scenario first pages + full-range section-token scan) | FOUND | the sample cites almost no ZR sections (only 12-10, 23-232, and 23-22/23-432/23-52 on specific sheets) | a "comparable" report should add the per-stat ZR links the sample lacks.

## Helper HX1 — verbatim follow-ups (options 5, 6-7, 8, 11)
- pinned snapshots | 33-121 (row R5D/R6B A/B/C = 2.00; columns pinned); 35-32 + qualifying-residential-site (R1-R5 only); 35-30/31/33; 33-12; 23-20 | FOUND | — | capture states settled by listing the folder.
- ZR portal | GET 24-11 / 24-111 / 32-421 / 33-26 / 33-27 / 33-28 / 33-30 / 33-301 / 77-12 / 77-21 / 77-211 / 77-24 / 77-25 / 77-26 / 23-372 / 23-35 / 23-351 / 23-352 / 23-353 | FOUND (200), one page each | 24-111 "select commercial overlays" membership of C2-2; the single mixed-building rear-yard governing rule | print/PDF read of the 12-10 "select commercial overlays" term; verbatim-read 33-26 + the residential-equivalency rear-yard provision.
- No access-blocked events.

## Helper HX2 — three open legal questions (options 5, 8, 9, 10)
- ZR portal | GET 77-01 / 76-11 / 76-131 / 76-141 / 11-122 / 11-151 / 22-00 / 22-121 / 22-122 / 23-51 / 32-00 / 32-121 | FOUND (200) | overlay-edge-as-Chapter-7-boundary not settled by the text (both readings); 76-00/76-01 scaled-measurement bodies (TOC only) | DCP determination/FAQ on an overlay-only split; open 76-00/76-01.
- DCP (official) | "C1 & C2 Commercial Overlay Districts" sheet; Commercial Zoning Data Tables | FOUND (one page each) | the actual mapped overlay line at lot 70 | read the DCP Zoning Map sheet / ZoLa / the NYCO GIS geometry.
- No access-blocked events; the browser-UA fallback was not needed for HX2.
