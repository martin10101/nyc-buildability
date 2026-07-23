# M4-T006 — future-hardening notes (non-blocking)

Raised by the independent G3/G4/G5 reviewers + producer disclosures at frozen `6509db3`. **None blocks
this gate.** All required gates (G0/G2/G3/G4/G5) PASS. Final acceptance/publication of the rule family
remains gated on **G6 qualified-human legal approval** (not weakened; independent of B-010). These are
recorded for the eventual G6/verification task and follow-up slices.

## Verification / provenance (for the G6 or a verification task)
- **FH-M4T006-V1 (raw-HTML byte verification):** all 5 ZR snapshots carry honest `raw_html_verified:false`,
  `extraction_status: extracted_draft`. The G6 / verification task must confirm each value against the
  live official ZR text at byte level before any Verified surface.
- **FH-M4T006-V2 (override-context verbatim capture):** §23-42, §23-426 (Historic District), §23-44
  (special districts), §23-425 (large sites) were captured only by description; they are implemented as
  `professional_review_required` exceptions with `citation_ref:null` (fail closed, no value emitted). A
  follow-up should capture their verbatim text + snapshots so those contexts can carry provenance.
- **FH-M4T006-V3 (snapshot digest scope — G5 LOW):** the snapshot `content_digest_sha256` covers only
  `verbatim_excerpt`, not the structured `table`/`notes` fields (`snapshots.py`, pre-existing M4-T001/T005
  infra outside this task's diff). A tamper limited to a `table` row would not be caught by the hash.
  Recommend the verification/publication task extend the digest to cover structured fields.

## Consumer-contract note (for the future M5 envelope-scenario task — G3 N1)
- **FH-M4T006-C1:** for *modifier* contexts (overlay/special-district/historic/large-site present), the
  numeric base value stays in `outputs` while `coverage_status` is downgraded to
  `professional_review_required` (the sanctioned "surface-but-flag" pattern from the accepted FAR rule).
  Downstream M5 consumers MUST gate on `coverage_status`, not on `outputs` emptiness.

## Test-coverage suggestions (G4)
- **FH-M4T006-Q1:** AS-3 on-amendment-date parametrization omits `r5a-height`; add it for symmetry
  (its 2024-12-05 effective point is currently covered only implicitly).
- **FH-M4T006-Q2 (from the proposal):** the follow-up yards / lot-coverage / parking rule slice, and the
  M5 task that consumes FAR + height/setback into a narrow bounded R5 massing.

## Scope / doc notes (G3)
- **FH-M4T006-K1:** `r5-setback` applies only to district `R5`; the §23-424 QRS envelope for R5A/R5B/R5D
  does not auto-emit a setback (documented limitation; acceptable for this draft slice).
- **FH-M4T006-K2 (doc nit):** the producer report cites stale intermediate commit hashes
  (`edddbbf` etc.); content verified equivalent at the actual frozen SHA `6509db3`.

**Legal correctness of the dimensional values (35/45 ft, 10/15 ft setback, §23-42x mapping) was NOT
assessed by G3/G4/G5 — it is explicitly a G6 qualified-human determination.** The family stays
`needs_review`/verified-ineligible, correctly deferring it.
