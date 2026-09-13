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

## RQ-003 — The §12-10 "qualifying residential site" definition, verbatim — OPEN

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

---

## Closed register (one line per satisfied request; full text in git history)

- **RQ-001** — satisfied by the loop's own accepted research (M4-T016, A2 geometry-mechanics
  section map, 201st accepted) — closed 2026-09-13 — answer lives in the M4-T016 report.
- **RQ-002** — satisfied by the loop's own accepted research (M4-T017, C-district survey,
  202nd accepted; corrected the C4-6 example: residential equivalent is R10, not R7) — closed
  2026-09-13 — answer lives in the M4-T017 report.
