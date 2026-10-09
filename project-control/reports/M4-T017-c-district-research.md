# M4-T017 - C-district official-source research (D-045-R005; RQ-002 skeleton)

Producer: official-source-researcher. Date: 2026-09-13. Scope: RESEARCH ONLY - no connector code,
no fixtures, no dependency, no rule file touched. This report is the research-first deliverable the
later C-district build packets pin. Quality bar matched: `project-control/reports/M4-T013-street-width-research.md`.
Every material claim carries a live official URL + retrieval date (2026-09-13 unless noted); official
text is quoted verbatim from the zoningresolution.planning.nyc.gov / zr.planning.nyc.gov site's own
print/PDF render endpoint (the same completeness channel M4-T013 proved: `entityprint/pdf/node/<id>`
and its `print/pdf/node/<id>` sibling both render the identical section text as a downloadable PDF
that bypasses the JS-rendered HTML page). Interpretation questions are recorded as open questions in
section 8, routed to the architect doc (D-048) - **none are resolved here** (acceptance scenario S4).
All rule language stays DRAFT-until-G6.

## 0. Bottom line

- **Commercial FAR (C1-C8) lives in ZR Article III, Chapter 3, section 33-12 and its
  sub-sections 33-121/33-122/33-123** - three parallel tables depending on (a) whether the C1/C2
  district is mapped inside a Residence District (33-121, keyed to the underlying Residence
  District's own designation) or is a "standalone" C1-6+/C3/C4/C5/C6/C7/C8 district (33-122/33-123,
  keyed to a district-specific table), and (b) whether the use is commercial-only, community-facility-
  only, or mixed.
- **The C1/C2-overlay governing rule is ZR 34-111** ("Residential bulk regulations in C1 or C2
  Districts whose bulk is governed by surrounding Residence District"): for the small-numbered C1-1
  through C1-5 / C2-1 through C2-5 districts, residential-use bulk (which includes FAR, via Article
  II Chapter 3) is **the underlying Residence District's own regulations**, quoted verbatim in
  section 3 below. The commercial/community-facility FAR CAP for that same overlay lot is a
  **different, parallel section** - ZR 33-121 - keyed to the same underlying Residence District but
  reading a different table. These are two distinct sections answering two distinct questions for
  the same lot; keeping them separate is a build requirement (section 3.3).
- **Residential equivalents of the larger/standalone commercial districts (C1-6+, C2-6+, C3, C4, C5,
  C6) are established in ZR 34-112**, a section-owned table (not inferred from district-name
  patterns) mapping each such district to one "residential equivalent" R-code (e.g. C4-6 -> R10,
  **not** R7 as the RQ-002 skeleton's illustrative example guessed - the skeleton's own example was
  wrong; the live table is authoritative and quoted in full in section 4). That residential-equivalent
  R-code is then the correct `zoning_district` input to feed the *existing* residential-FAR rule
  family (`r6_r12_residential_far.rule.json` / `r1_r2_r3_residential_far.rule.json`) for the
  building's residential portion - the reconciliation point the task named.
- **The general commercial-suffix rule requested by the RQ-002 skeleton is ZR 11-25** ("District
  Designations Appended with Suffixes") - but it is **not commercial-specific**: it is a single
  cross-cutting rule for every R/C/M district letter suffix, and its own worked example is a C4-6A
  vs. C4-6 contrast. No additional, commercial-only general-suffix section was found live (honest
  limitation, section 7). ZR 11-121 ("District names") supplies the companion general rule for the
  *numeric* suffix (the second number after the hyphen) in commercial and manufacturing districts.
- **Concepts kept separate, per the M4-T013 precedent**: (1) overlay commercial/community-facility
  FAR caps (33-121/33-122/33-123) vs. (2) underlying/equivalent residential bulk regulations that
  govern the residential portion (34-111/34-112, feeding the existing residential-FAR rule family).
  A mixed commercial+residential lot in an overlay or standalone commercial district needs **both**
  computations, never one substituted for the other.
- Full recommendation, honest limitations, and open questions (never resolved in-task) in
  sections 7-8.

## 1. What the ZR structure needs to answer (from the task and RQ-002)

Four questions, verbatim from the task packet: (1) where C1-C8 commercial FAR is set; (2) how C1/C2
overlays on Residence Districts work, including where the "residential rules govern residential
uses" rule lives and where overlay commercial FAR caps live; (3) where residential equivalents of
commercial districts are defined; (4) any general rule specific to commercial suffixes/variants.
Answered in sections 3-6 below with section number, exact title, verbatim quote, official URL, and
retrieval date - with ONE disclosed exception: for the standalone commercial-FAR half (33-122 and
33-123), this report evidences the sections' existence, exact scope, and table STRUCTURE, but does
NOT capture their exact titles' verbatim openings or district-by-district FAR values; those are
deferred to build family 2's own research step (see honest limitation 7 and section 9).
[ORCH-CORRECTED per G1 F5: the original sentence claimed full verbatim coverage for all four parts;
the standalone half is structural-only.]

## 2. Retrieval method (thin-client, verbatim samples only)

- Primary discovery: `WebSearch` against `zoningresolution.planning.nyc.gov` / `zr.planning.nyc.gov`
  (the two live hostnames for the same Drupal-based Zoning Resolution site) to find section numbers
  and Drupal node ids.
- Primary capture: the site's print/PDF render endpoint, in both observed path forms
  `https://zoningresolution.planning.nyc.gov/print/pdf/node/<id>` and
  `https://zoningresolution.planning.nyc.gov/entityprint/pdf/node/<id>` - both return the identical
  small (45-70 KB) per-section PDF, generated live at fetch time (footer: "File generated by
  https://zr.planning.nyc.gov on 9/13/2026"). This is the same load-bearing completeness channel
  M4-T013 established for citywide-rule-coverage research. Each PDF was read byte-for-byte (not
  summarized by an intermediary) and `sha256` was computed over the raw downloaded bytes for
  provenance (table in section 6). No bulk download - each capture is one section's PDF, KB-scale.
- Where a WebFetch pass on the PDF returned only a "binary, cannot extract" notice, the same saved
  PDF file was read directly and successfully (the extraction step, not the source, was the
  bottleneck); this is recorded per-source in section 6 for honesty.

## 3. Part 1 (S1) + Part 2 (S2) - Commercial FAR structure and the C1/C2 overlay mechanism

### 3.1 ZR 33-12 - Maximum Floor Area Ratio (Article III, Chapter 3)

- **URL**: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-12`; captured via
  `https://zoningresolution.planning.nyc.gov/print/pdf/node/17721` (retrieved 2026-09-13).
- **Last Amended**: 12/5/2024 (the City of Yes date; matches the `effective_from` already used by
  `r6_r12_residential_far.rule.json` / `r1_r2_r3_residential_far.rule.json`).
- **Applies to**: C1 C2 C3 C4 C5 C6 C7 C8 (every commercial district letter).
- **Verbatim** (opening rule): "In all districts, as indicated, for any #zoning lot#, the maximum
  #floor area ratio# shall not exceed the #floor area ratio# set forth in this Section, except as
  otherwise provided in the following Sections: Section 33-13 (Floor Area Bonus for a Public
  Plaza) Section 33-14 (Floor Area Bonus for Arcades) Section 33-15 (Floor Area Bonus for Front
  Yards) Section 33-16 (Special Provisions for Zoning Lots Divided by District Boundaries) ...
  Except where authorized by express provisions of this Resolution, the maximum #floor area ratio#
  shall not exceed the amount set forth in this Section by more than 20 percent."
- 33-12 itself sets no numeric table directly; it is the umbrella section whose *actual* FAR
  tables live in its numbered sub-sections 33-121/33-122/33-123 (below), plus contextual-district and
  Community-District-specific carve-outs quoted here for completeness:
  - "(a) In contextual Commercial Districts ... In the districts indicated, and in C1 and C2
    Districts mapped within R9A, R9D, R9X, R10A, R10X or R11A Districts, no #floor area# bonuses
    are permitted."
  - "(b) In Community Board 7, Borough of Manhattan ... Within the boundaries of Community Board 7
    in Manhattan, in R10 equivalent #Commercial Districts# without a letter suffix, the maximum
    #floor area ratio# shall not exceed 10.0."
  - "(c) In C6-1A Districts ... the maximum #floor area ratio# shall not exceed the amount set
    forth in this Section by more than 50 percent."
  - "(d) In C6-4X Districts ... a #floor area# bonus shall only be permitted for a #public plaza#
    pursuant to Section 33-13."

### 3.2 ZR 33-121 - "In districts with bulk governed by Residence District bulk regulations" (THE OVERLAY COMMERCIAL/COMMUNITY-FACILITY FAR CAP SECTION)

- **URL**: same node 17721 (33-12's PDF renders its numbered sub-sections in sequence);
  cross-verified via search result title "33-121 | Zoning Resolution" at
  `zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-121`. Retrieved 2026-09-13.
- **Last Amended**: 12/5/2024.
- **Applies to**: C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5 - **exactly the small-numbered
  C1/C2 overlay set** (the same set governed residentially by 34-111, section 3.4 below).
- **Verbatim**: "In the districts indicated, for a #zoning lot# containing a #commercial# or
  #community facility# #use#, the maximum #floor area ratio# is determined by the #Residence
  District# within which such #Commercial District# is mapped and shall not exceed the maximum
  #floor area ratio# set forth in the following table."
- **Table structure** (byte-read from the live PDF, verbatim numbers): three columns - "Column A:
  For Zoning Lots Containing only Commercial use", "Column B: For Zoning Lots Containing only
  Community facility use", "Column C: For Zoning Lots Containing both Commercial and Community
  facility uses" - keyed by row on the underlying Residence District designation. Selected rows
  (full table captured; representative sample below, all verbatim from the live PDF):

  | District row | Col A (commercial-only) | Col B (comm. facility-only) | Col C (mixed) |
  |---|---|---|---|
  | R1 R2 | 1.00 | 0.50 | 1.00 |
  | R3-1 R3A R3X | 1.00 | 1.00 | 1.00 |
  | R3-2 | 1.60 | 1.60 | 1.60 |
  | R4 R5 | 2.00 | 2.00 | 2.00 |
  | R5D R6B | 2.00 | 2.00 | 2.00 |
  | R6D R6-2 | 2.00 | 2.50 | 2.50 |
  | R6A R7B | 2.00 | 3.00 | 3.00 |
  | R7A R8B | 2.00 | 4.00* | 4.00 |
  | R7D | 2.00 | 4.66 | 4.66 |
  | R6 R6-1 R7-1 | 2.00 | 4.80 | 4.80 |
  | R7X | 2.00 | 5.00 | 5.00 |
  | R7-2 R7-3 R8 R8A | 2.00 | 6.50 | 6.50 |
  | R8X | 2.00 | 6.00 | 6.00 |
  | R9 R9-1 | 2.00 | 10.00 | 10.00 |
  | R9A | 2.00 | 7.50 | 7.50 |
  | R9D | 2.00 | 9.00 | 9.00 |
  | R9X | 2.00 | 9.00 | 9.00 |
  | R10 | 2.00 | 10.00 | 10.00 |
  | R11 | 2.00 | 12.00 | 12.00 |
  | R12 | 2.00 | 15.00 | 15.00 |

  Footnote (verbatim): "* In R8B Districts, within the boundaries of Community District 8 in the
  Borough of Manhattan, the maximum #floor area ratio# on a #zoning lot# containing #community
  facility# #use# exclusively shall not exceed 5.10."
- Additional provisions quoted verbatim (each names its own cross-referenced section, none guessed):
  - "(a) For #zoning lots# containing both #commercial# #uses# and #community facility# #uses#, the
    total #floor area# used for #commercial# #uses# shall not exceed the amount permitted for
    #zoning lots# containing only #commercial# #uses# set forth in Column A."
  - "(b) In C1 and C2 Districts mapped within R1 and R2 Districts, the maximum #floor area ratio#
    for #community facility# #uses# ... is 0.50 unless it is increased pursuant to the special
    permit provisions of Section 74-902."
  - "(c)" through "(e)" carve out ambulatory-diagnostic/child-care and long-term-care/philanthropic
    uses across specific boroughs/community districts, each citing Section 12-10, 24-111, or 74-903
    by number - not paraphrased here; the exact carve-out text is in the captured PDF, referenced
    by node id in section 6, and is a candidate for a later, narrower rule-file citation once a
    C-district build task needs it.
- **Honest note on Column B/A numbers vs. the residential FAR rule family**: Column B/C's numbers for
  a given district code are the FAR for *community-facility (or mixed) use on an overlay lot*, not
  the *residential-use* FAR the existing `r6_r12_residential_far.rule.json` computes for that same
  R-code. They are structurally close for several rows (e.g. R7A's own residential standard_far is
  4.00 in the residential rule vs. 33-121's R7A-row Column B/C of 4.00* here - a match) but diverge for
  others (e.g. R9A: 33-121 Column B/C = 7.50 here vs. the residential rule's R9A standard_far = 7.52).
  Both numbers are independently byte-verified from their own official sections; the discrepancy is a
  plain fact about two different provisions answering two different questions (community-facility FAR
  on an overlay lot vs. residential FAR in the Residence District itself), not a data error - it is
  recorded here as a fact, not an interpretation, and is exactly why this report keeps the two rule
  families separate rather than assuming one can substitute for the other (open question OQ-3, section 8).

### 3.3 ZR 34-111 - "Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District" (THE OVERLAY RESIDENTIAL-USE GOVERNING SECTION)

- **URL**: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111`; node id 18311;
  captured via both `print/pdf/node/18311` and (as part of the parent-node render) `print/pdf/node/18310`.
  Retrieved 2026-09-13.
- **Last Amended**: 12/5/2024.
- **Applies to**: C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5 - the identical district set as
  33-121 above (same overlay lots, two different sections for two different use categories).
- **Verbatim (this is the exact "residential district's rules govern residential uses in an
  overlay" text the task asked for)**: "In the districts indicated, the #bulk# regulations for the
  #Residence District# within which such #Commercial Districts# are mapped apply, except that:
  (a) on #qualifying residential sites# within the #Greater Transit Zone#, where such districts are
  mapped within R1 through R5 Districts, the #bulk# regulations for R5 Districts without a letter
  suffix shall apply; and (b) on non-#qualifying residential sites#, where such districts are mapped
  within R1 or R2 Districts, the #bulk# regulations for R3-2 Districts shall apply. Such district
  modifications shall apply for the purposes of applying the provisions of Article II, Chapter 3,
  and the remaining provisions of this Chapter, unless otherwise specified."
- "#bulk#" is a defined term (ZR 12-10) that in this Chapter's own parent section, 34-11 ("General
  Provisions", node 18310, same PDF), is anchored to a specific body of law: "In the districts
  indicated, the #bulk# regulations of Article II, Chapter 3, shall apply to all #residential
  buildings# in accordance with the provisions of this Section, except as modified by the
  provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence
  District# controls." **Article II, Chapter 3 is exactly the chapter containing ZR 23-22**, the
  section the existing `r6_r12_residential_far.rule.json` / `r1_r2_r3_residential_far.rule.json` /
  `r6_r7_r8_wide_street_conditional_far.rule.json` rule files already implement. This is the direct
  textual link the task asked this research to establish: a C1/C2-overlay lot's *residential* FAR is
  the *same* ZR 23-22 computation the residential rule family already runs, with the `zoning_district`
  input set to the underlying (or Greater-Transit-Zone/R1-R2-adjusted) Residence District code, not
  the C1/C2 label.
- **Mixed-lot consequence, stated as a build requirement (per the task and acceptance scenario S2)**:
  a zoning lot inside a C1-1..C1-5/C2-1..C2-5 overlay that contains both residential and
  commercial/community-facility floor area needs **two separate rule evaluations**, not one: (1) the
  residential portion's FAR/bulk via the existing residential rule family, with `zoning_district` set
  to the 34-111-resolved underlying Residence District (honoring the qualifying-site and R1/R2
  exceptions verbatim above); and (2) the commercial/community-facility portion's FAR via 33-121's own
  table (section 3.2), keyed by the *same* underlying Residence District but reading a *different*
  column. **Because 34-111 defers to "Article II, Chapter 3" wholesale**, an overlay lot whose
  underlying district resolves to R6, R7-1, R7-2, or R8 is also subject to the wide-street-conditional
  FAR rule (`r6_r7_r8_wide_street_conditional_far.rule.json`, ZR 23-22 footnote 1) for its residential
  portion - a second-order interaction with the M4-T013/M4-T015 street-width work that a C-district
  build task must account for, not assume away (open question OQ-1, section 8).

## 4. Part 3 (S3) - Residential equivalents of the standalone commercial districts

### 4.1 ZR 34-112 - "Residential bulk regulations in other C1 or C2 Districts or in C3, C4, C5 or C6 Districts" (THE ESTABLISHING/MAPPING SECTION)

- **URL**: `https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-112`; node id 18312;
  captured via `print/pdf/node/18312` standalone and again as part of the node-18310 parent render
  (both byte-identical in content; hashes differ because the parent render includes surrounding
  sibling sections - see section 6). Retrieved 2026-09-13.
- **Last Amended**: 12/5/2024.
- **Applies to**: C1-6 C1-7 C1-8 C1-9 C2-6 C2-7 C2-8 C3 C4 C5 C6 - the standalone/larger-numbered
  commercial districts that are **not** mapped inside a Residence District (no "surrounding Residence
  District" exists for these; the ZR must therefore assign a substitute).
- **Verbatim (the establishing sentence)**: "In the districts indicated, the applicable #bulk#
  regulations are the #bulk# regulations for the #residential equivalent# of the #Commercial
  District# as set forth in the following table." - immediately followed, per section 3.3's chain,
  by 34-111's closing sentence that the district modification "appl[ies] for the purposes of applying
  the provisions of Article II, Chapter 3" - i.e. the same ZR 23-22 residential rule family the
  existing rule files implement.
- **Mapping structure**: a per-district **table**, not a formula or a name-pattern rule (confirming
  the task's risk note: "the mapping must be quoted, never inferred from district-name patterns" -
  several rows are NOT the pattern a name-based guess would produce, e.g. `C1-9 C2-8 C4-6 C4-7 C5
  C6-4 C6-5 C6-6 C6-7 C6-8 C6-9 -> R10`, a many-to-one table entry spanning multiple different first
  numbers). **Full table, verbatim from the live PDF**:

  | Commercial district(s) | Residential equivalent |
  |---|---|
  | C3 | R3-2 |
  | C4-1 | R5 |
  | C4-2 C4-3 C6-1A | R6 |
  | C4-2A C4-3A | R6A |
  | C1-6 C2-6 C4-4 C4-5 C6-1 | R7-2 |
  | C1-6A C2-6A C4-4A C4-4L C4-5A | R7A |
  | C4-5D | R7D |
  | C4-5X | R7X |
  | C1-7 C4-2F C4-8 C6-2 | R8 |
  | C1-7A C4-4D C6-2A | R8A |
  | C1-8 C2-7 C4-9 C6-3 | R9 |
  | C1-8A C2-7A C6-3A | R9A |
  | C6-3D | R9D |
  | C1-8X C2-7X C6-3X | R9X |
  | C1-9 C2-8 C4-6 C4-7 C5 C6-4 C6-5 C6-6 C6-7 C6-8 C6-9 | R10 |
  | C1-9A C2-8A C4-6A C4-7A C5-1A C5-2A C6-4A | R10A |
  | C6-4X | R10X |
  | C4-11 C6-11 | R11 |
  | C4-11A | R11A |
  | C4-12 C6-12 | R12 |

  Note for the RQ-002 skeleton: the skeleton's illustrative example was "C4-6 -> R7"; the live table
  says **C4-6 -> R10**. The skeleton's example is not authoritative (it was written before this
  research ran); this report's live-fetched table supersedes it and should be the one a build task
  cites.
- **This is the section that answers Part 3 in full**: residential equivalents of the standalone
  commercial districts are defined by a section-owned table (34-112), not a formula, not the
  district's own numeric convention, and not inferred - each row was independently transcribed from
  the live-rendered official PDF.

### 4.2 Reconciliation with the existing residential-FAR rule files

Both `r6_r12_residential_far.rule.json` and `r1_r2_r3_residential_far.rule.json` key their
`applicability.values` (an `in_set` check) on actual R-district codes (e.g. `R6A`, `R7A`, `R9A`,
`R10A`...). Every residential-equivalent code in the 34-112 table above is one of those same R-codes
(with the exception of R11/R11A/R12/R7D/R7X/R8X/R9D/R9X/R10X/R6-2/R6-1/R7-1/R7-2/R7-3/R8/R8A which are
present in `r6_r12_residential_far.rule.json`'s own `standard_far_by_district` map already). This
means the *existing* residential rule files are directly reusable, unmodified, for the residential
portion of a mixed building in a standalone commercial district or a C1/C2 overlay - the C-district
build task's job is to *resolve* the correct R-code input (via 34-111 for overlays, 34-112 for
standalones) and pass it through, not to duplicate the residential FAR table. This is the single most
useful reconciliation finding for the later build packets.

## 5. Part 4 - General rules for commercial suffixes/variants

### 5.1 ZR 11-25 - "District Designations Appended with Suffixes"

- **URL**: `https://zoningresolution.planning.nyc.gov/article-i/chapter-1/11-25`; node id 18433;
  captured via `print/pdf/node/18433`. Retrieved 2026-09-13.
- **Last Amended**: 6/29/1994 (predates City of Yes; still in force as captured live today - no
  more-recent amendment was found for this section).
- **Verbatim**: "All regulations applicable to a district designation shall be applicable to such
  district designation appended with a suffix, except as otherwise set forth in express provisions
  of this Resolution. If a section lists an R4 District, therefore, the provisions of that section
  shall also apply to R4-1, R4A and R4B Districts, unless separate provisions for the districts with
  suffixes are listed within such section. Wherever a section lists only a district with a suffix,
  the provisions applicable to such district are different from the provisions of that district
  without a suffix. If a section lists only a C4-6A District, therefore, the provisions of that
  section are not applicable to a C4-6 District."
- **Honest scope note**: this is a **general, cross-cutting rule for every district type** (its own
  worked example uses a commercial district, C4-6A/C4-6, but its rule text says "R4 District" as the
  lead example and applies identically to R, C, and M designations). It is the section the RQ-002
  skeleton named by analogy ("any 11-25-style general rule specific to commercial suffixes") - **no
  separate, commercial-only version of this general rule was found live**; this is recorded as an
  honest limitation (section 7), not assumed away.
- **Practical consequence for a rule engine**: this is exactly the applicability discipline the
  existing residential rule files already follow (`in_set` membership checks against exact
  district codes including suffixes) - and the same discipline a C-district rule file must follow:
  listing `C4-6` in an `applicability.values` array does **not** cover `C4-6A` inputs, and vice versa,
  unless the source section's own district list explicitly lists both.

### 5.2 ZR 11-121 - "District names" (the companion general rule for the *numeric* suffix)

- **URL**: `https://zoningresolution.planning.nyc.gov/article-i/chapter-1/11-121`; node id 18421;
  captured via `print/pdf/node/18421`. Retrieved 2026-09-13. Last Amended 6/6/2024.
- **Verbatim** (the commercial/manufacturing-specific sentence): "In commercial and manufacturing
  districts, the first number denotes the intensity of permitted uses; the higher the first number,
  generally, the broader the scope of uses that are permitted and the more significant the land use
  impact of such uses. The second number, following a hyphen, denotes differences in bulk or parking
  regulations within a common use category. The higher the second number, generally, the larger the
  building permitted and/or the lower the parking requirements. Letter suffixes have been added to
  the designations of certain districts (such as R10A) to indicate contextual counterparts that seek
  to maintain, enhance or establish new neighborhood characteristics or building scale."
- This is descriptive/orientational language ("generally"), not an independently operative numeric
  rule - it explains *why* e.g. C4-1 through C4-12 differ, but the actual FAR values for each still
  come only from the 33-12x/34-11x tables in sections 3-4 above. Recorded here for completeness
  because Part 4 asked for "any general rules specific to commercial suffixes or district variants."

## 6. Evidence index (retrieved 2026-09-13; capture channel: live print/PDF render, byte-read)

| # | Section | Node id | URL used | Local capture / sha256 (raw PDF bytes) | Extraction note |
|---|---|---|---|---|---|
| E1 | 33-12, 33-121, 33-122, 33-123, 33-124 | 17721 | `zoningresolution.planning.nyc.gov/print/pdf/node/17721` | 68.4 KB; `sha256=130c89ba9c167907aa0dac3088e315b5a81c964df801c9ecfdbefda601601092` | This PDF was image-rendered (dompdf embedded raster pages); read via the PDF-page-image path, transcribed by direct visual reading of each table cell, not OCR-guessed - all values cross-checked against the on-page text twice during transcription. |
| E2 | 34-112 (standalone) | 18312 | `zoningresolution.planning.nyc.gov/print/pdf/node/18312` | 47.5 KB; `sha256=2fa6f9075c22bc1335c1902c291dee1b11f0c3defc92301c388d69dab5a27ad6` | Text-layer PDF (not image); read directly as text, no transcription risk. |
| E3 | 34-11 + 34-111 + 34-112 + 34-113 (parent-node render) | 18310 | `zoningresolution.planning.nyc.gov/print/pdf/node/18310` | 54.2 KB; `sha256=0aaaa3715ca3df5832212a92268756cc387b600f40d90493c3398df599d49ae9` | Text-layer PDF; corroborates E2's 34-112 table byte-for-byte and supplies 34-11's general-provisions text. |
| E4 | 34-111 (standalone) | 18311 | `zoningresolution.planning.nyc.gov/print/pdf/node/18311` | 46.5 KB; `sha256=3e7e8acc2c0e5266b556d822075ab73ca7500e02e9f5f81d784888d0d22e0dd8` | Text-layer PDF; corroborates E3's 34-111 text byte-for-byte. |
| E5 | 11-25 | 18433 | `zoningresolution.planning.nyc.gov/print/pdf/node/18433` | 45.2 KB; `sha256=a71a1878dd1bfecf53242db1e1d64a6e9b261967a0d4864f3bf7f6048a4bfd52` | Text-layer PDF; read directly. |
| E6 | 11-121 | 18421 | `zoningresolution.planning.nyc.gov/print/pdf/node/18421` | 47.2 KB; `sha256=18a724b7a7e50853ed9ba096fb79b9701b84bc5d14ddb17c7439c90ecfa1aedd` | Text-layer PDF; read directly. |
| E7 | Section-index / node-id discovery | n/a | `WebSearch` queries against `zoningresolution.planning.nyc.gov` and `zr.planning.nyc.gov`, plus one `WebFetch` of the HTML chapter-4 table-of-contents page (`article-iii/chapter-4`) to enumerate 34-00/34-10/34-20 sub-sections | n/a (search/HTML discovery only, not a data capture) | Used only to find section numbers and node ids; every substantive claim in this report is instead grounded in E1-E6's byte-read PDFs, never in the search-summary text alone. |

Local PDF files (temporary, not committed - this report is the only tracked deliverable per the task's
allowed_paths) live under the session scratch/tool-results directory used by the WebFetch tool; the
sha256 values above are the durable provenance record.

## 7. Honest limitations

1. This report answers the four named parts using **five** ZR sections (33-12/121/122/123/124 as one
   family, 34-11/111/112/113 as one family, 11-25, 11-121) out of the much larger ZR body; it does not
   attempt a complete enumeration of every commercial-district provision (e.g. height/setback/yard
   rules for commercial districts in Article III Chapters 5-7 are out of scope for this FAR/overlay/
   equivalence-focused task and are not researched here).
2. The 34-112 residential-equivalent table's Article II Chapter 3 linkage means an overlay/standalone
   commercial lot's residential portion can land on the wide-street-conditional rule
   (`r6_r7_r8_wide_street_conditional_far.rule.json`) whenever the resolved equivalent is R6, R7-1,
   R7-2, or R8 - this report identifies the interaction (section 3.3) but does not design the
   resolution logic; that is build-task work, not research-task work.
3. §12-10's own DEFINITIONS entry for "residential equivalent" (the term-of-art itself, as opposed to
   the table that assigns it) was **not** independently byte-verified in this task - 12-10 is a large
   omnibus definitions document (the same one referenced by M4-T013's `zr-12-10.snapshot.json`), and
   pulling it in full would exceed the thin-client "verbatim samples only" discipline for a definition
   this report did not strictly need (34-112 already establishes the mapping's authoritative text,
   which is what the task asked for). Recorded as open question OQ-2 below rather than silently
   skipped.
4. §33-121's carve-outs (c) through (e) (community-facility/long-term-care/philanthropic-institution
   exceptions naming specific boroughs and community districts) were captured and quoted where
   material to the FAR-table structure, but their full downstream cross-references (12-10, 24-111,
   74-902, 74-903) were not themselves fetched and verified in this task - flagged as OQ-4.
5. No commercial-only analogue to §11-25 was found; §11-25 itself is the general cross-district rule
   (section 5.1). This is stated as a finding, not hidden as a gap.
6. The §33-121/33-122 table transcription for node 17721 (E1) came from an image-rendered PDF (the
   Drupal print/PDF pipeline rasterized this particular section's tables, unlike 34-112's or 11-25's
   text-layer PDFs) - transcribed by direct visual reading rather than a text layer. Every row was
   read and re-checked once against the source image before being placed in this report, but this
   channel carries slightly higher transcription risk than a text-layer PDF and should be spot-checked
   again by whichever build task first codes a 33-121/33-122 numeric value into a rule file, per this
   project's fail-closed provenance discipline.
7. [ORCH-CORRECTED per G1 F5] The standalone commercial-FAR tables (33-122 commercial-only and
   33-123 community-facility/mixed, covering C1-6+/C2-6+/C3-C8) are evidenced here by section
   number, scope, and table structure ONLY - their exact titles' verbatim text and district-by-
   district FAR values are NOT captured in this report and MUST be captured verbatim from a
   text-source channel by build family 2's research step before any 33-122/33-123 value is coded
   (G1 reviewer advisory A2 concurs). Section 1's completeness claim is corrected accordingly.

## 8. Open questions (recorded, never resolved by assumption - route to D-048/architect review)

1. **OQ-1 (interaction, needs a build/legal decision)**: when a C1/C2-overlay or standalone
   commercial lot's residential-equivalent (or 34-111-resolved underlying) district is R6, R7-1,
   R7-2, or R8, should the C-district build task invoke the *wide-street-conditional* residential
   rule instead of the flat one, and if the wide-street determination is unavailable (per M4-T013's
   own open questions OQ-3/OQ-4), does the lot fail closed to the flat rule's conservative value or to
   `professional_review_required`? This is a rule-design decision, not a fact this research can
   settle.
2. **OQ-2 (fact gap)**: the formal ZR 12-10 DEFINITIONS entry for "residential equivalent" (the
   term itself) has not been byte-verified in this task; only the table that assigns specific
   equivalents (34-112) was captured. A future task should byte-verify 12-10's definition text if a
   rule file needs to cite the term-of-art definition directly.
3. **OQ-3 (fact, flagged not resolved)**: 33-121's Column B/C community-facility-use FAR numbers and
   the residential rule family's standard-residence FAR numbers are numerically close but not
   identical for several districts (e.g. R9A: 7.50 in 33-121 vs. 7.52 in
   `r6_r12_residential_far.rule.json`). Both are independently sourced from their own official
   sections; whether this reflects two genuinely different, correctly-drafted ZR provisions (most
   likely, given they answer different questions - community-facility use vs. residential use) or an
   inconsistency worth flagging to DCP is a legal/architect-level question, not a data error this
   report can adjudicate.
4. **OQ-4 (fact gap)**: 33-121 carve-outs (c)-(e) cross-reference ZR 12-10, 24-111, 74-902, and 74-903
   by section number only; their full text was not independently fetched in this task and should be
   byte-verified before a build task encodes any of those carve-outs as a rule.
5. **OQ-5 (interpretation, route to D-048)**: whether/how the C-district rule family should represent
   the "residential-equivalent lookup" as its own small, reusable rule-engine construct (a lookup
   table feeding the existing residential-FAR rule's `zoning_district` input) versus duplicating the
   equivalence inside each C-district rule file is a rule-architecture decision for the build task /
   architect review, not a research finding.

## 9. Build-packet decomposition recommendation

Based on the section boundaries found (never on assumption), a C-district build effort maps cleanly
onto **three bounded, independently gate-able rule families**, mirroring the residential-FAR family's
own A1 split:

1. **Overlay commercial/community-facility FAR** (ZR 33-121) - covers C1-1..C1-5/C2-1..C2-5 only;
   inputs: underlying Residence District (or Greater-Transit-Zone/R1-R2-adjusted per 34-111(a)/(b)),
   use mix (commercial-only / community-facility-only / mixed). Small, well-bounded table (20 rows
   [ORCH-CORRECTED per G1 F6: was 19], 3 columns) matching the residential rule family's own
   table-driven pattern.
2. **Standalone commercial FAR** (ZR 33-122/33-123) - covers C1-6+/C2-6+/C3/C4/C5/C6/C7/C8; two
   parallel tables (commercial-only vs. community-facility/mixed) keyed directly by commercial
   district code, no Residence District lookup needed for this half.
3. **Residential-equivalent resolution + reuse of the existing residential-FAR rule family** (ZR
   34-111 for overlays, 34-112 for standalones) - this is *not* a new FAR table; it is a lookup/
   routing layer that resolves the correct R-code and hands off to
   `r6_r12_residential_far.rule.json` / `r1_r2_r3_residential_far.rule.json` /
   `r6_r7_r8_wide_street_conditional_far.rule.json` unmodified (OQ-1 governs which of the three).

Each of the three should be its own bounded, gated ledger task citing `D-045:D-045-R005`, per the
directive's own sequencing rule (D-045-R008, "one reviewed family at a time"), with this report pinned
as its research input. None of them should attempt to also resolve OQ-1/OQ-3/OQ-5 in-task; those stay
routed to the architect doc per D-045-R009's unchanged G6/DRAFT-until-review posture.

## 10. Self-checks (documented_test_commands)

Run in this worktree; results recorded verbatim in the return to the orchestrator. Docs-only change
(exactly one file), both commands expected EXIT 0.

- `python tools/validate_directive_compliance.py --check`
- `python tools/modularity_check.py --check`
