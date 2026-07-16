---
name: socrata-pluto-gotchas
description: Live-verified Socrata/PLUTO API behaviors that are easy to get wrong (checkbox booleans, decimal BBLs everywhere, null omission under $select)
metadata:
  type: project
---

Live-verified 2026-07-16 against dataset 64uk-42ks during M1-T002 (fixtures under services/api/tests/fixtures/pluto/ are the durable evidence):

1. Socrata **checkbox** columns (splitzone, irrlotcode, zmcode, mih_opt1-4) arrive as JSON booleans, and SoQL predicates must be boolean: `$where=splitzone=true`. Using `splitzone='Y'` returns HTTP 400 `query.soql.type-mismatch` - a NON-drift 400, distinct from the drift signature `query.soql.no-such-column`.
2. Number-typed `bbl`/`appbbl` serialize with decimal tails (`"1000010100.00000000"`) in FULL records, not only `$select` projections - broader than the M1-T001 G1 C6 finding.
3. SODA omits null fields even under explicit `$select`: projecting the 8 vintage date columns for a record where they are null returns only `{"bbl": ...}`. Never infer schema or nullness from response keys; the 108-column inventory lives in the F08 fixture and as constants in app/connectors/pluto_soda.py.
4. Real PLUTO record BBL 1000010101 natively has numfloors omitted with numbldgs=10 (dictionary p.28 "not available" case) - useful as a genuine fixture, no synthesis needed.

**How to apply:** when writing any SoQL against NYC Open Data, check the column dataTypeName in the /api/views metadata first; reuse the M1-T002 fixture pack for downstream connector tests instead of re-hitting the API.
