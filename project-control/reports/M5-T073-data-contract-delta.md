# M5-T073 — Data-contract delta verification at the second re-freeze (data-contract-verifier)

> Transmission history: ONE message, complete (END-OF-REPORT present). Saved verbatim by
> the orchestrator. This delta extends M5-T073-data-contract.md (PASS with required F1) to
> the re-frozen head 218d7fca after the [ORCH-CORRECTED per data-contract F1/F2/F5]
> cluster (e89456f0).

Verified at HEAD `218d7fca39ad3babb25b7dfdff18a0a6f7f645b4` (`git rev-parse HEAD` matches).

**F1 — VERIFIED.** `PROVENANCE.md` now opens, before the "Byte source" section, with an `[ORCH-CORRECTED per M5-T073 data-contract review F1, 2026-09-24]` block that scopes the two pre-harvest sections to P01–P04 only and states the P05–P08 account: direct raw-body storage in this directory, capture through the two accepted connectors' own query builders over the official NYC DCP MapPLUTO ArcGIS endpoint per the `HARVEST_SPEC.md` recipe (keyless GET, `Accept: application/json`, verbatim bytes, sha256 over the exact UTF-8 body bytes), the `raw_esri_body` / `raw_geojson_body` kinds, and the 26v2/26v1 versus 26v2/26v2 per-side split. I re-checked the two claims it newly asserts as counts: 5 boroughs (Manhattan ×3, Queens, Bronx, Brooklyn, Staten Island ×2) and 7 distinct `geometry_class` values across 8 pairs — both correct. The false byte-source sentence is now scoped rather than left standing, and the original text is preserved.

**F2 — VERIFIED.** `HARVEST_SPEC.md` leads with an EXECUTED marker naming commit `06e3e72d` (confirmed as the harvest commit), the P05–P08 registrations, and the fact that the `_auth_response_body` branch the spec requested already exists in the harness. Non-blocking cosmetic nit: all six marker lines begin with `#`, so they render as six consecutive H1 headings.

**F5 — VERIFIED.** The LotArea-not-`Shape__Area` clarification is carried in the PROVENANCE.md correction block.

**Material identity carry — VERIFIED.** `git diff 06db8ab9 218d7fca` over `services/api/tests/connectors/fixtures/bridge_ring_pairs/` touches only the two `.md` files, 25 insertions and zero deletions. Every fixture body and `pairs_manifest.json` is byte-identical to what I verified at the prior head, so all 16 digest, endpoint, and `dataset_version` verifications carry forward unchanged. The harness still passes at this head: 14 passed.

**Report preservation — VERIFIED.** `project-control/reports/M5-T073-data-contract.md` carries my report with F1–F6, all six duty assessments, the verdict line, and the END-OF-REPORT marker intact.

DATA-CONTRACT DELTA VERDICT: PASS

END-OF-REPORT
