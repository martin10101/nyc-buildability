# Research requests — owner-assisted deep-research channel (D-050)

**What this is.** A running queue of research-shaped questions the build loop wants answered.
The owner runs them through external deep-research tooling (Astra) and brings back results —
making the campaign faster. Started 2026-09-13 (owner directive D-050).

**Read this from your phone (always current):**
https://github.com/martin10101/nyc-buildability/blob/candidate/D-024-mrl-option-b/docs/RESEARCH_REQUESTS.md
Every change to this file is committed AND pushed in the same step (D-050-R006), so that link
is never stale. From the phone you can also just ask the companion session to read out what's
open, or dictate results into the chat — it does the file work.

**The rules (D-050):**
- Results are **discovery aids, never sources of record.** Every load-bearing claim gets verified
  against the official text through the normal capture discipline (print/PDF-class completeness
  where applicable) before anything is encoded. Rule provenance always cites the captured official
  text — the research is credited only as a discovery note.
- **Non-blocking:** the loop never waits on this queue. An unanswered request just means the
  loop's own researcher does the work; an answered one saves that time.
- Questions about what a law **means** (interpretation) don't belong here — they go to
  `docs/ARCHITECT_REVIEW_QUESTIONS.md` (D-048) and come back as owner decisions or qualified
  rulings.
- Ask for **citations, section numbers, and exact quotes with URLs** in every answer — a claim
  without a pinpoint citation costs verification time instead of saving it.

**Entry format:** question · why it matters · what it unlocks · status (OPEN / ANSWERED
<date> / ROUTED-to-architect-doc).

**Lifecycle (D-050-R006):** results returned by the owner are stamped ANSWERED immediately
(date + named verification target) and pushed in the same step. Once a request is SATISFIED —
answer verified/consumed, everything checks out — its full entry is DELETED from the active
queue and collapsed to one line in the Closed register at the bottom (full text stays in git
history). The active queue never carries figured-out material.

---

## RQ-003 — The §12-10 "qualifying residential site" definition, verbatim — ANSWERED 2026-09-13

- **Question:** Quote the complete ZR §12-10 definition of "qualifying residential site"
  (City of Yes), enumerating every qualification route (transit proximity, community-facility
  floor space as of 2024-12-05, any others), each route's district inclusions/exclusions, and
  any cross-referenced sections. Full text, not a summary.
- **Why:** D-049-R004 encoded §23-424's 35/35 alternative as a fail-closed condition precisely
  because this definition wasn't captured; the FAR table also jumps R2/R2A to 1.00 on qualifying
  sites, so the definition moves floor-area numbers too.
- **Unlocks:** turning several "professional review required" flags into computed conditions.
- **Added 2026-09-13 (wave-3 finding):** while in §12-10, ALSO quote the current "street, wide"
  definition verbatim — the live text was AMENDED 3/26/2026 and is materially fuller than our
  accepted snapshot (an alternate-width clause + two named-street designations). The A2 build
  now requires a fresh §12-10 capture + architect ruling before the wide-street rules build.
- **ANSWERED 2026-09-13** (owner deep research, D-050;
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-003): complete
  route index (a)(1)–(c) + final affordability paragraph located, original §12-10 HTML in the
  owner's evidence archive; cross-refs §23-21 / §23-424 (35/35, 35/45, 45/55) / §27-111 /
  §66-11; **plus an express counterexample: §114-02 excludes certain >5-acre Special Bay Ridge
  lots from the definition** — a §12-10-only eligibility function is wrong. The research itself
  states print/PDF-class capture of the definition was NOT completed. Street-wide extension:
  amendment date 3/26/2026 corroborated (our own M4-T016 capture is already byte-verified).
  **Verification target:** the D-049-R004 conversion task must make its own recorded-official
  capture of §12-10 (qualifying residential site + street, wide) with print/PDF-class
  completeness, plus §23-21/§23-424/§27-111/§66-11 and the §114-02 exclusion; discovery aid is
  never cited as provenance.

## RQ-004 — Special-district priority inventory (A4 planning input) — ANSWERED 2026-09-13

- **Question:** List NYC's special purpose districts (Article/chapter numbers + names), and for
  each: the boroughs/neighborhoods covered and whether it modifies residential height/setback or
  FAR. Flag the ~10 with the largest residential development activity (e.g. Special Hillsides
  Preservation, Special Ocean Parkway, Special Midtown, Hudson Yards…).
- **Why:** A4 is sequenced last and is the elastic part of the timeline; a priority order over
  the special districts lets the owner pick the waves that matter for real deals instead of
  encoding alphabetically.
- **Unlocks:** an informed owner triage for the final campaign waves.
- **ANSWERED 2026-09-13** (owner deep research, D-050;
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-004): 59 current
  chapter families inventoried (Articles VIII–XIV) with geography + H/F effect flags + section
  targets; measured activity ranking (DCP Housing Database 25Q4 × NYSP boundaries — Gowanus /
  MX / Lower Manhattan / LIC / Downtown Brooklyn top five) with its limitations stated;
  suggested implementation order incl. a separate small-house track (South Richmond, Ocean
  Parkway, Hillsides, Natural Area). **Two index inconsistencies flagged:** §11-122 still lists
  Garment Center at Art. XII Ch. 1 (now Midtown South Mixed Use) and omits Ch. 145
  (Eastchester–East Tremont). **Verification target:** A4 contracting verifies the inventory
  against official chapter text (never the DCP guide's numbers — e.g. §92-23 says 215 ft, not
  the guide's 210), resolves both index inconsistencies from the official text, and treats the
  activity ranking as a planning aid only.

## RQ-005 — DCM Street Center Line: official width-definition + bulk-product facts (B2 hardening) — ANSWERED IN PART 2026-09-13; residual (1) OPEN

- **Question:** (1) Find the official DCP/City Map documentation that defines exactly WHAT the
  DCM Street Center Line `Streetwidth` value records geometrically (mapped right-of-way /
  property-line-to-property-line vs roadbed) — the dataset metadata has NO field-level
  definition; cite the document, section, exact quote, URL. (2) The exact download URL + file
  name of the DCM street-centerline BYTES shapefile (nyc.gov returns 403 to non-browser
  clients; needs a browser). (3) The verbatim LION data-dictionary text defining `StreetWidth`
  ("narrowest width of the paved area…" is search-derived, not yet byte-read — it lives deep in
  lion_metadata.pdf). Exact quotes + URLs for all three.
- **Why:** these are the accepted M4-T013/M4-T015 open questions OQ-1, OQ-5, and E2/OQ-7 — the
  three pure fact-finding gaps left in the street-width connector's provenance. (OQ-3, the
  ambiguity-class policy, is interpretation and stays with the architect doc / G6.)
- **Unlocks:** closes the connector's remaining research caveats before the A2 wave consumes it;
  the width-definition citation also strengthens the wide-street rule's G6 package.
- **ANSWERED IN PART 2026-09-13** (owner deep research, D-050;
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-005):
  **(2) CLOSED** — exact bulk product byte-verified: `dcm_20251031shp.zip` (October 2025
  release; internal `DCM_StreetCenterLine.shp/.dbf/.shp.xml`; 19,554,628 bytes; ZIP sha256
  `ad21afd2c7c6…`; download URL in the archived report). **(3) CLOSED** — LION 26C metadata
  PDF page 24 byte-read: `StreetWidth_Min` (alias `StreetWidth`), Double, verbatim "Formerly
  known as StreetWidth, this represents the narrowest width, in feet, of the paved area of the
  street." (PDF sha256 `b98255a2…`) — confirms M4-T013's paved-vs-mapped finding; Geoclient
  width stays KILLED for legal use. **(1) REMAINS OPEN (honest gap, confirmed real):** the
  research checked BOTH the metadata PDF (page 4) AND the shapefile's embedded XML — the
  `Streetwidt` field has NO field-level definition anywhere recovered ("width 50" is string
  capacity, not feet); dataset-level "official street names and widths from the Official City
  Map" supports mapped-width intent but the exact geometric convention
  (property-line-to-property-line; variable-width handling; nonnumeric encodings) is
  undocumented. **Residual authoritative target:** DCP Technical Review / the relevant Borough
  Topographical Office field convention, or the applicable City Map alteration for ambiguous
  segments. **Verification target:** the B2-hardening/G6-package task makes its own recorded
  captures of the DCM metadata PDF + LION 26C PDF (shas above make that cheap) and keeps the
  connector fail-closed-to-narrow until (1) resolves; the ambiguity POLICY itself stays OQ-3 /
  architect-doc (interpretation, untouched here).

---

*Loop: append new requests below with the same format. Owner: paste results to the companion
session or the build session; the receiving session marks the entry ANSWERED and names the
verification target.*

---

## Closed register (one line per satisfied request; full text in git history)

- **RQ-001** — satisfied by the loop's own accepted research (M4-T016, A2 geometry-mechanics
  section map, 201st accepted) — closed 2026-09-13 — answer lives in the M4-T016 report.
  Owner research (same day) additionally returned a broader discovery map (23-431/434/435/436,
  23-44x, 23-732–739, 35-81, waterfront/flood/transit/split-lot dispatch boundary) — see
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-001 (aid only).
- **RQ-002** — satisfied by the loop's own accepted research (M4-T017, C-district survey,
  202nd accepted; corrected the C4-6 example: residential equivalent is R10, not R7) — closed
  2026-09-13 — answer lives in the M4-T017 report. Owner research (same day) corroborated
  C4-6→R10 and additionally returned the §33-122 standalone values our report deferred
  (C4-6=3.4, C4-7=10.0, C6-11=12.0, C6-12=15.0 — non-monotonic!), §35-31/35-32 mixed-building
  caps, and §32-121/122 C7/C8/C3A use gates — see the same archived report §RQ-002 (aid only;
  family-2 build still captures its own values).
