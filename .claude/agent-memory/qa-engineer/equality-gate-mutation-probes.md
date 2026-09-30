---
name: equality-gate-mutation-probes
description: How to judge test adequacy for the GeoSearch address->lot equality gate (DB-026) and any future gate that binds it - the mutation probes that must exist
metadata:
  type: project
---

The DB-026 equality gate (`apps/web/src/lib/address-search.ts` `resolveLotFromGeoSearch` +
`normalizeStreetForMatch`) promotes a GeoSearch feature to THE lot only when returned
housenumber == parsed input AND normalized street == parsed street, binding identity to
`addendum.pad.bbl`; `match_type`/`confidence` are recorded but never compared.

**Why:** GeoSearch returns a plausible WRONG lot for nonsense input at the SAME
`confidence:0.8 / match_type:"fallback"` as the true hit, so only field equality can refuse it.
The M5-T046 packet ADJUDICATION recorded that this gate library + the `geosearch.json` registry
match discipline BIND any FUTURE packet that introduces a live GeoSearch->lot promotion. So a
future QA review will re-encounter this gate.

**How to apply — the mutation probes that MUST exist for adequacy (all present at M5-T046
c9113e09):**
- A confidence/match_type-gating mutant must DIE: pin a feature scored `confidence:1 /
  match_type:"exact"` on a WRONG street and assert `no_match` (address-search.test.ts AS-4
  never-consult, ~:284). Plus the fallback/0.8 nonsense probes asserting `no_match` (~:275).
- A dropped-housenumber-gate mutant must die: out-of-range house "99999"->"207" asserts
  `no_match`.
- A dropped-street-gate mutant must die: nonexistent street "zzqqxx"->real lot asserts
  `no_match`.
- Identity-is-bbl (not bin/address-string): reverse frontage resolves through code to the SAME
  bbl with a DIFFERENT matchedName (~:256); GARAGE sibling same bbl / different bin.
- Ordinal-fold present: `normalizeStreetForMatch("37th street")==="37 STREET"` AND the "37th"
  body resolves to the same bbl (~:249) - kills a mutant that removes the fold.
- Fail-closed on unclear input: an abbreviated "37 st" (street-TYPE abbrev, never contracted to
  expand) resolves to `no_match` via the body's DEFAULT parse (~:298); a paired test supplying the
  unabbreviated reference parse resolves and records absent confidence/match_type as `null` (AS-5b,
  ~:318). The pair proves the no_match is fail-closed, not a structural parse failure (non-vacuous).
- Raw typed-input preservation (confirm arc): assert the entered-input `<strong>` textContent
  equals the typed string INCLUDING surrounding whitespace, and is DISTINCT from both the picked
  city-shaped suggestion label and the matched canonical address (address-confirm.test.tsx S9,
  ~:597; autocomplete.test.tsx onPick 2nd arg, ~:27).

**Known thin coverage (advisory, not blocking at M5-T046):** the GARAGE-through-code resolve path
is asserted at fixture level only; the entered-input ABSENT branch (`enteredInput ? : null` when
both typedInput blank and inputEcho empty) is untested; no dedicated /search-shaped abbreviation
body (behavior is endpoint-agnostic so it is covered in substance via the autocomplete default
parse). Re-flag these if a future promotion packet grows the gate.
