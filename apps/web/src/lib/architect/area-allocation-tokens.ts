/**
 * The web literals for the two-zone area illustration's fixed wording (M5-T187; D-094 R089/R090).
 *
 * The three strings below are byte-equal to the `wording` group of
 * docs/design/presentation-tokens.json (area_zone_apartment, area_zone_other,
 * area_illustration_caption) — the SAME strings the PDF kernel draws
 * (services/api/app/drawings/kit/presentation_tokens.py, WORDING[...]), so the
 * website and the PDF never drift apart (R096). The parity test
 * (answers/__tests__/area-allocation.test.tsx) reads that JSON from disk and
 * fails if a byte differs in either direction. The sentence-final full stops the
 * owner wrote are NOT part of the label or caption (design contract line 43), so
 * none of these carries one, and the caption uses the em dash (U+2014).
 *
 * Why a web literal rather than an import of the JSON: the token generator
 * (apps/web/scripts/presentation-tokens.mjs) renders the `wording` group to the
 * Python kit only, never to the web, so work-order G-15 is "the web carries a
 * literal whose test compares it with the JSON". The two methodology strings at
 * the bottom come from the presentation contract (not the JSON `wording` group),
 * so they are not parity-tested.
 */

/** The apartment zone's label — JSON wording.area_zone_apartment (no full stop). */
export const AREA_ZONE_APARTMENT = "Apartment area";

/** The other-building-area zone's label — JSON wording.area_zone_other (no full stop). */
export const AREA_ZONE_OTHER = "Other building area: core, circulation, walls and services";

/** The one caption beside the illustration — JSON wording.area_illustration_caption (em dash, no full stop). */
export const AREA_ILLUSTRATION_CAPTION = "Illustrative area allocation—not a floor plan";

/** The measure the share applies to, in plain words (presentation contract line 72; not a JSON token). */
export const AREA_MEASURE_WORDS = "Residential floor area";

/** The methodology item that stays explicitly not checked (presentation contract line 72; not a JSON token). */
export const PHYSICAL_PLATE_NOT_CHECKED =
  "Physical floor plate (gross-up, exclusions, wall thickness)";
