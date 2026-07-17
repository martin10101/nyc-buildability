---
name: property-profile-frontend-rules
description: Non-obvious rules for consuming the property-profile API from the web frontend (documented-keys-only trap, D5 fallback, CORS gap, lockfile workflow)
metadata:
  type: project
---

Frontend rules for the property-profile API v1.1 learned in M2-T001.

**Why:** these cost real analysis time and are easy to get wrong; several are
review-blocking (documented-keys-only is a task rule enforced by G3).

**How to apply:**
- The M1-T005 builder emits provenance-record keys NOT documented in
  source_fact.schema.json (`dataset_id`, `request_url`, `input_vintages`).
  The frontend may consume only documented keys — take dataset id /
  request-URL host from the documented top-level `reproducibility` object.
- The live builder emits contract 1.0.0 (`PROFILE_CONTRACT_VERSION` in
  builder.py): NO zoning district-provenance maps on live data. The D5
  fallback join (provenance[].original_field_name in zonedist1..4 /
  overlay1..2 / spdist1..3) is the production path; the map path is testable
  only with derived 1.1.0 fixtures.
- The API has NO CORS configuration (checked 2026-07-16). Browser pages on a
  different origin cannot read responses; e2e harnesses must add
  CORSMiddleware from outside services/**, and a production proxy/CORS
  decision is an open follow-up ([[property-screen-followups]]).
- Server BBL validation has codes the "10-digit borough 1-5" client mirror
  deliberately does not cover (invalid_block/invalid_lot for all-zero
  block/lot) — that gap is the legitimate way to exercise the server 422
  path from the UI without bypass flags.
- apps/web lockfile cannot be generated on the owner PC; the sanctioned
  mechanism is dispatching .github/workflows/generate-lockfile.yml on the
  branch (bot commits package-lock.json).
- The e2e seam for the real FastAPI app is the `get_pluto_fetcher`
  dependency override + scripted transports replaying committed fixtures in
  services/api/tests/fixtures/pluto/ (same pattern as the accepted M1-T005
  tests); control BBLs must keep block/lot non-zero to survive validation.
