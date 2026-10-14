# M5-T163 reviews (every return kept unchanged)

- G1 data-contract-verifier: PASS at 5a8228c1 (material b644f292; 2 advisories: the frontage-span assumption, routed to M5-T176; the glyph-authoritative 12-10 channel unavailable, disclosed); its agent review entry appended to NB-03 unchanged in bebcaeef; delta attestation: PASS carries to bebcaeef.

Every reviewer is an AI agent; none is a human or professional review.

## G1


G1 REVIEW — M5-T163 (NB-03 rev 2 + four ZR 12-10 street-definition captures). Reviewer: data-contract-verifier. Read-only, pinned head /root/project/w-wave20 @ 5a8228c14, material commit b644f2922.

VERDICT: PASS (G1). No REQUIRED findings; two ADVISORY notes.

MY OWN READING FIRST (worked from captured law text before NB-03's conclusions):
23-344(b) applies in R6-R12 (R6B qualifies): if a zoning lot's front lot line coincides with the street line of the "short dimension of a block", no rear yard within 100 ft of that street line. Deciding inputs: which street the front lot line is on; the block boundaries (12-10 "block" = bounded only by streets/public parks/RR ROW/airport/pierhead-shore/NYC corporate lines); and the dimension between the two bounding streets (<230 ft, a block-level City-Map measurement, measured once). For block 7334 (bounded by Northern Blvd, 215 Pl, 215 St, 45 Rd) the Northern Blvd frontage spans the 215 Pl↔215 St dimension; <230 ft ⇒ short dimension ⇒ (b) waives rear yard within 100 ft. 23-344(c)(3): in R6-R12, the beyond-100-ft portion of a side lot line (treated as rear lot line) needs no rear yard where it coincides with a SIDE lot line of an adjoining zoning lot — keys on the SUBJECT R6-R12 district + the ADJOINING lot's line type, NOT the neighbour's district. Stays unknown: lot depth (100/99.97/~101.06), the zoning-lot config, whether the tax-map ALLEY is a mapped street, whether a street setback line / district-boundary provision applies. NB-03 rev 2 matches this reading and is appropriately conditional.

WHAT I CHECKED (commands/outputs):
- `python3 tools/research_record_check.py --check` → exit 0 (NB-03 interpretation_awaiting_review, code_current True, review_state stale).
- `python services/api/scripts/sync_zr_snapshots.py --check` → exit 0 (189 files byte-identical).
- `pytest -q tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py` (lanes venv, PYTHONPATH=services/api) → 28 passed, exit 0 (S2, S3).
- 4 new captures: official_channel html, retrieved_at 2026-10-11T19:58:08Z, http_status 200, raw_html_sha256 8eb066d1… pinned; content_digest_sha256 == sha256(verbatim_excerpt) for all four (MATCH); request_url = …/article-i/chapter-2/12-10 with NO '#'; `cmp` canonical vs services/api/app/_zr_snapshots copies → byte-identical ×4; shape/keys identical to existing zr-12-10-* captures. Nodes/stamps: street 21676 (2/2/2011), street-setback-line 21679 (9/19/1985), street-wide 21683 (3/26/2026), street-narrow 21678 (12/15/1961). Print/PDF completeness channel 504 + per-node print 403 disclosed (DB-167); extraction_status extracted_draft, raw_html_verified false.
- wide/narrow per-definition text == full-page capture zr-12-10.snapshot.json word-for-word after normalizing quotes/#markers/whitespace (full == wide+narrow). NB-06 rev 2 search S3 ("street,wide/narrow not_found; live page truncated") is genuinely contradicted by the full-page capture already holding the text; producer FLAGGED it for routing to the NB-06 owner (M5-T170) and did NOT edit NB-06 (out of scope) — conflict preserved, correct.
- "street setback line" IS a real 12-10 defined term (node 21679; corroborated by the independently-captured street-line definition which references it verbatim, and by web sources; City Map Staten Island / Queens CD10). S4: all 8 gaps (a)-(h) carry a 2026-10-11 dated line + source(s) + next step; open ones say "stays open". S5: measurement_basis quantities use printed_tax_map/gis/derived/administrative_record — all within the nine bases {law,deed,survey,printed_tax_map,approved_plan,filing_attribute,administrative_record,gis,derived}; check enforces and passes. S6: worked_example expected values are law-text + arithmetic (200.01<230), prepared_by says "worked from the law text, not a program run" — no program output. S7: research_status unchanged (rev1 and rev2 both interpretation_awaiting_review); material commit b644f2922 touches only the record, 4 captures, 4 bundled copies, producer report — README.md and RESEARCH_REQUESTS.md correctly unchanged. All files within allowed_paths.
- gap (h): verified against the OFFICIAL DCP PLUTO Data Dictionary (May 2023, 23v1.1, s-media.nyc.gov/.../PLUTODD.pdf): LotFront = "The tax lot's frontage measured in feet." + NOTE "…if a lot fronts on more than one street, the PTS building address often determines which side…"; LotDepth = "The tax lot's depth measured in feet."; Data Source = Department of Finance – Property Tax System (PTS). Matches E14 verbatim; DOF/PTS ⇒ administrative_record basis correct, "not a survey" correct.
- D-094: R037 satisfied (no unconditional zero rear yard from GIS; depth left unresolved; (a) corner test explicitly treated as only ONE exception, not the only one). R079 satisfied (explicit (b) applicability check beside the 100-ft point test; exemption not presented as established). R036/R061 addressed at the research layer (diagram/engine update owed to M5-T167; legal facts captured as found, only genuine site facts unresolved). Authoritative per-requirement pass is the directive-compliance-verifier's.
- All 8 cited law-text sha256 (E1,E2,E8-E13) == capture file sha256 (LF-normalized). code_identity ee909d7e… == live rule file (LF) at head.
- No tax-lot≡zoning-lot equation (lot_scope zoning_lot_unconfirmed; condition states it); no index-as-instrument (settled_by names the 2017 survey + approved ZD1); conclusion stays interpretation_awaiting_review, labelled draft (ADR-007).

ADVISORY findings (do not block):
1. reading/measurement_basis equate "combined Northern Blvd frontage of lots 1 and 70" (203.13 gis / 200.01 tax map) with the block dimension between 215 Pl and 215 St (scope "whole block frontage between the two streets"). This assumes lots 1+70 span the Northern Blvd frontage corner-to-corner — well-supported (all other block-7334 lots are R4B on the side streets) but is an inference from parcel geometry, not a City-Map corner-to-corner measurement. Already listed under settled_by (City Map) and the reading is conditional; suggest noting the span assumption explicitly. Evidence: NB-03 measurement_basis.quantities[0-1], E7 excerpt ("combined … frontage of lots 1 and 70").
2. The exact verbatim of "street setback line" (E9) and the "street" (E8) list-marker glyphs could not be independently re-fetched (whole-page print/PDF 504; per-node print 403 without browser UA) — the documented DB-167 fallback. Existence/text corroborated as above; provenance fully disclosed; captures stay extracted_draft. Residual verification owed if the glyph-authoritative channel recovers.

WHAT I COULD NOT CHECK: the official ZR portal's glyph-authoritative print/PDF for §12-10 (504) and per-node print (403) — matching the producer's disclosed DB-167 behaviour; the DOB-approved ZD1 / survey (access_blocked, genuinely unresolved, correctly left open).

AGENT REVIEW ENTRY
{
  "reviewer": "data-contract-verifier",
  "date": "2026-10-11",
  "reviewed_revision": 2,
  "reviewed_code_identity": {
    "services/api/app/rules/rulesets/r6b_rear_yard_corner_waiver.rule.json": "ee909d7e0074490cbd59b2f965fbcda823182c9b57fa2fa94bf26b5d85260da4"
  },
  "verdict": "agrees",
  "findings": [
    "G1 PASS at 5a8228c14 (material b644f2922). Independently re-read ZR 23-344(b)/(c)(3) and 12-10 block/short-dimension/street/street-line from the captures; agrees with the conditional no-rear-yard reading, (b) deciding a lot within 100 ft and (c)(3) keying on the subject R6-R12 district plus the adjoining lot's line type, not the neighbour's district.",
    "Four new 12-10 captures verified: html channel, retrieved 2026-10-11, http 200, sha256 pinned, content_digest == sha256(verbatim), request_url has no '#', bundled copies byte-identical (cmp), shape matches existing zr-12-10-* captures; print/PDF 504 DB-167 fallback disclosed; extracted_draft.",
    "'street setback line' confirmed a real 12-10 defined term (node 21679); street,wide/street,narrow agree word-for-word with the full-page capture, so NB-06 rev 2 search S3 (not_captured) is contradicted and was correctly flagged to the NB-06 owner without editing NB-06.",
    "gap (h) verified against the official DCP PLUTO Data Dictionary (23v1.1): LotFront/LotDepth text verbatim, Data Source DOF-PTS, so the administrative_record basis and 'not a survey' are correct.",
    "All 8 gaps carry a dated line+source+next step; every quantity uses one of the nine bases; no program output among expected values; research_status unchanged so README/RESEARCH_REQUESTS correctly untouched; no tax-lot/zoning-lot equation, no index-as-instrument, no unconditional zero rear yard from GIS (D-094 R037).",
    "research_record_check.py --check and sync_zr_snapshots.py --check both exit 0; bundle and law-links tests 28 passed.",
    "Advisory: the block dimension is inferred from lots 1+70 combined frontage (assumes corner-to-corner span; confirm from the City Map); exact street/street-setback-line text could not be independently re-fetched (504/403) - captures stay raw_html_verified false."
  ],
  "report": null
}

END-OF-REPORT



DELTA ATTESTATION — M5-T163 G1 (data-contract-verifier, read-only). Verdict holds: G1 PASS at HEAD bebcaeef5 (commit immediately after 5a8228c14 on task/wave24-report-v3).

Confirmed:
1. `git diff 5a8228c14 HEAD -- docs/`: the ONLY change is my appended `review.agent_reviews` entry — byte-for-byte my JSON (reviewer "data-contract-verifier", date 2026-10-11, reviewed_revision 2, reviewed_code_identity {r6b_rear_yard_corner_waiver.rule.json: ee909d7e0074490cbd59b2f965fbcda823182c9b57fa2fa94bf26b5d85260da4}, verdict "agrees", 7 findings, report null), formatted at the file's indent=1. Key order and values match what I returned.
2. `git diff --name-only 5a8228c14 HEAD` lists only docs/research/evidence-records/NB-03-rear-yard-short-block.json; nothing else in NB-03 or any other M5-T163 file (the 4 captures, 4 bundled copies, producer report) changed. Advisory 1 (frontage-span assumption) correctly NOT applied here — routed to M5-T176, which revises NB-03 next.
3. `python3 tools/research_record_check.py --check` → exit 0; NB-03 status=interpretation_awaiting_review, code_current=True, review_state=current.
4. My G1 PASS carries unchanged to bebcaeef5: the appended entry IS the review, and no reviewed content moved.

END-OF-REPORT
