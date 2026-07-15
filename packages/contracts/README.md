# @nyc-buildability/contracts

Versioned JSON Schema contracts shared by all modules (web, API, workers,
rules, reports). Individual modules may not invent competing schemas
(PRD section 32.3).

## Status: v1 (task M0-T009)

The v1 canonical contracts below were finalized in task M0-T009, fixing the
M0-T004 G3 defects D1 (provenance completeness), D2 (real-data enum/pattern
grounding), and D3 (meta-schema validation in CI).

| Schema | Purpose | PRD reference |
| --- | --- | --- |
| `schemas/v1/common.schema.json` | Shared grounded definitions: BBL, BIN, borough code/name, ZIP, timestamp shapes | 9, 32.3 |
| `schemas/v1/source_fact.schema.json` | Canonical provenance record; ALL PRD s9 mandatory fields are required (source id, original field name, original value, normalized value, retrieved timestamp, dataset/document version, effective date [nullable but present], BBL, confidence, user confirmed/overridden, conflict status) | 9, 19 |
| `schemas/v1/property_profile.schema.json` | One canonical property profile: identity/address, BBL/BIN, geometry, lot facts, existing-building facts, zoning, project intent, per-fact provenance (`provenance_ref` REQUIRED on every fact value), missing inputs, conflicts, user confirmations, profile version | 9, 19, 32.3 |
| `schemas/v1/coverage_status.schema.json` | Exactly the 6 PRD s12 coverage statuses; the 3 data-completeness values in `$defs/data_completeness` | 12 |
| `schemas/v1/analysis_state.schema.json` | Exactly the 14 PRD s32.1 workflow states, no extras | 32.1 |
| `schemas/v1/analysis_state_transition.schema.json` | Audit record for one state transition (actor, timestamps, correlation id); transition legality is enforced by the backend state machine | 25, 32.1 |

Deferred contracts (added additively in later milestones, per
`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md` "Canonical contracts"): rule
definition and rule evaluation trace (M4), scenario (M5), report evidence
item (M6). They are deliberately not stubbed here to avoid shipping
unreviewed shapes that downstream code might bind to.

## Data grounding (defect D2)

No enum value or pattern in these schemas is invented. Grounding, all traceable
to `docs/research/M0-T002-geoclient-address-resolution.md` (official sources
retrieved 2026-07-14):

- **BBL** — `^[1-5][0-9]{5}[0-9]{4}$`: 10 digits; borough prefix 1–5
  (Geoclient `/v2/search`: "A ten-digit number where the first digit is 1–5 is
  recognized as a BBL request"); 5-digit zero-padded block + 4-digit
  zero-padded lot (Geoclient `/v2/bbl` example: block `67` → `00067`, lot `1` →
  `0001`, `bbl` = `1000670001`). Source: Geoclient User Guide v2.0.4,
  https://mlipper.github.io/geoclient/. Rejects borough 0/6–9, wrong length,
  non-numeric. OPEN-WITH-FLAG: all-zero block/lot validity is not defined in
  official docs, so the pattern does not exclude it; existence checks are
  delegated to the Geoclient Function BL connector.
- **BIN** — `^[1-5][0-9]{6}$`: "A seven-digit number where the first digit is
  1–5 is recognized as a BIN request" (same guide); examples `1057127`,
  `1079043`, `1001026`.
- **Borough numbers** — 1–5 per Geoclient User Guide s2.2.1
  (Manhattan/MN/1 ... Staten Island/SI/5).
- **Borough names** — `Manhattan`, `Bronx`, `Brooklyn`, `Queens`,
  `Staten Island`: documented spellings (User Guide s2.2.1) and live GeoSearch
  v2 output (`"borough": "Manhattan"`). Raw connector spellings are preserved
  in provenance `original_value`; matching is case-insensitive (User Guide
  s2.2: parameter values are case-insensitive).
- **Dataset versions** — examples in descriptions use real release ids:
  Geosupport/PAD quarterly release `26B` (DCP GDE page), GeoSearch
  `addendum.pad.version` `26a` (live response).
- **Platform-defined enums** — `conflict_status`, conflict `resolution`,
  `user_confirmed_or_overridden`, transition `actor` are NOT government-source
  values; they are platform workflow enums grounded in PRD sections 2, 5, 8,
  9, and 32.1 and are labeled `PLATFORM-DEFINED` in their descriptions.
- **Zoning district codes** — deliberately NOT enumerated in v1: the zoning
  source family has not been researched yet (M0-T002 covered address/BBL/BIN
  only). Open-with-flag; enums land additively with the M2 zoning research.

## Fixtures

- `fixtures/valid/<schema>/*.json` — must validate against
  `schemas/v1/<schema>.schema.json`. Official values come verbatim from the
  research doc (120 Broadway: BBL `1000477501`, BIN `1001026`, PAD `26a`);
  synthetic values use clearly non-official ids (`test-fixture-synthetic`).
- `fixtures/invalid/<schema>/*.json` — must FAIL validation; each file's
  `_expected_failure` key states the intended defect. A passing "invalid"
  fixture fails the build.
- `fixtures/invalid_schemas/*.schema.json` — deliberately broken schemas that
  must fail meta-schema validation (typo keyword, bad `type` value, required
  name missing from `properties`).

`.github/scripts/validate_contracts.py` (CI `contracts` job) enforces all of
the above plus the property-profile invariant that every `provenance_ref`
resolves to a `provenance_id` (PRD s19). It runs a strict stdlib structural
meta-schema layer always, adds the `jsonschema` draft 2020-12 engine when
importable, and prints which engines ran; it never silently weakens.

## Versioning rules

- Schemas are versioned by directory (`v1`, `v2`, ...); `$id` contains the
  version directory.
- Within a version, changes must be **additive**: new optional fields and new
  schemas may be added; required fields are never removed or renamed; enum
  values are never removed; patterns may only be relaxed (accept more), never
  tightened.
- Breaking changes require a new version directory and a migration note.
- CI validates meta-schema conformance, fixtures, and expected failures on
  every push (see root README, CI job 3).
