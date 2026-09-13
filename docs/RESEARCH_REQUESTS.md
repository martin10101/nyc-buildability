# Research requests — owner-assisted deep-research channel (D-050)

**What this is.** A running queue of research-shaped questions the build loop wants answered.
The owner runs them through external deep-research tooling (Astra) and brings back results —
making the campaign faster. Started 2026-09-13 (owner directive D-050).

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

---

## RQ-001 — Map the sky-exposure-plane and street-width height mechanics (A2 wave) — OPEN

- **Question:** For NYC ZR residential districts R6–R12 (City of Yes text), list every section
  that defines the height/setback mechanics that depend on geometry: sky exposure planes,
  street-width-dependent maximum base/building heights, setback depth rules, and permitted
  obstructions. For each: section number, exact title, which districts it names, whether "wide
  street"/"narrow street" changes the numbers, and the defined terms it leans on (base plane,
  street line, sky exposure plane, etc. — with the section where each term is defined,
  presumably §12-10).
- **Why:** the A2 geometry-mechanics wave builds these rules next; the street-width data
  connector is already live. A verified section map turns each rule task from "find the law"
  into "capture and encode the law."
- **Unlocks:** height/setback envelopes for the mid- and high-density residential districts —
  most of the city's multifamily lots.

## RQ-002 — Commercial district rule-structure survey (C-district lane) — OPEN

- **Question:** For NYC commercial districts C1 through C8: (1) where does the ZR set commercial
  FAR (section numbers + the table structure); (2) how do C1/C2 OVERLAYS on residential
  districts work — which section says the residential district's rules govern residential uses
  in an overlay, and where do overlay commercial FAR caps live; (3) where are the residential
  equivalents of commercial districts defined (e.g. "C4-6 has an R7 residential equivalent" —
  the section that establishes the mapping); (4) any §11-25-style general rules specific to
  commercial suffixes. Exact sections, titles, quotes, URLs.
- **Why:** the C-district research task is a named wave-3 lane; this is its skeleton.
- **Unlocks:** the commercial half of your "truly everything" order — including mixed lots where
  an overlay changes a residential answer.

## RQ-003 — The §12-10 "qualifying residential site" definition, verbatim — OPEN

- **Question:** Quote the complete ZR §12-10 definition of "qualifying residential site"
  (City of Yes), enumerating every qualification route (transit proximity, community-facility
  floor space as of 2024-12-05, any others), each route's district inclusions/exclusions, and
  any cross-referenced sections. Full text, not a summary.
- **Why:** D-049-R004 encoded §23-424's 35/35 alternative as a fail-closed condition precisely
  because this definition wasn't captured; the FAR table also jumps R2/R2A to 1.00 on qualifying
  sites, so the definition moves floor-area numbers too.
- **Unlocks:** turning several "professional review required" flags into computed conditions.

## RQ-004 — Special-district priority inventory (A4 planning input) — OPEN

- **Question:** List NYC's special purpose districts (Article/chapter numbers + names), and for
  each: the boroughs/neighborhoods covered and whether it modifies residential height/setback or
  FAR. Flag the ~10 with the largest residential development activity (e.g. Special Hillsides
  Preservation, Special Ocean Parkway, Special Midtown, Hudson Yards…).
- **Why:** A4 is sequenced last and is the elastic part of the timeline; a priority order over
  the special districts lets the owner pick the waves that matter for real deals instead of
  encoding alphabetically.
- **Unlocks:** an informed owner triage for the final campaign waves.

## RQ-005 — DCM Street Center Line: official width-definition + bulk-product facts (B2 hardening) — OPEN

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

---

*Loop: append new requests below with the same format. Owner: paste results to the companion
session or the build session; the receiving session marks the entry ANSWERED and names the
verification target.*
