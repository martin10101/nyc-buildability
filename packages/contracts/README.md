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
| `schemas/v1/source_fact.schema.json` | Canonical provenance record; ALL PRD s9 mandatory fields are required (source id, original field name, original value, normalized value, retrieved timestamp, dataset/document version, effective date [nullable but present], BBL, confidence, user confirmed/overridden, conflict status). Contract 1.2.0 adds four OPTIONAL identity/lineage keys (`fact_key`, `observation_id`, `value_digest`, `response_digest`) | 9, 19 |
| `schemas/v1/property_profile.schema.json` | One canonical property profile: identity/address, BBL/BIN, geometry, lot facts, existing-building facts, zoning, project intent, per-fact provenance (`provenance_ref` REQUIRED on every fact value), missing inputs, conflicts, user confirmations, profile version. Contracts 1.1.0 and 1.2.0 add the optional keys documented below | 9, 12, 19, 32.3 |
| `schemas/v1/coverage_status.schema.json` | Exactly the 6 PRD s12 coverage statuses; the 3 data-completeness values in `$defs/data_completeness` | 12 |
| `schemas/v1/analysis_state.schema.json` | Exactly the 14 PRD s32.1 workflow states, no extras | 32.1 |
| `schemas/v1/analysis_state_transition.schema.json` | Audit record for one state transition (actor, timestamps, correlation id); transition legality is enforced by the backend state machine | 25, 32.1 |

## Property profile contract 1.1.0 (task M1-T006, additive)

`property_profile.schema.json` accepts `profile_version.contract_version`
`"1.0.0"` **or** `"1.1.0"` (a CLOSED enum — unpublished versions are
rejected). Version 1.1.0 documents the keys the accepted M1-T005 API already
emits (G3 adjudication #1, defects D2/D4) and adds district provenance
linkage. **Every key below is OPTIONAL, so every valid 1.0.0 instance remains
valid unchanged**; the required key set, existing types, and existing
patterns are untouched.

- **`fact_value.coverage_status`** (per fact) — `$ref` to
  `coverage_status.schema.json`: exactly the 6 PRD s12 coverage statuses,
  never duplicated inline. Derived only from review status and
  conflict/drift state — never from connector confidence, and never
  `verified` before a published-rule/reviewer pipeline exists.
- **`data_completeness`** (top level) — `$ref` to
  `coverage_status.schema.json#/$defs/data_completeness`: exactly the 3 PRD
  s12 values, derived deterministically from `missing_inputs` criticality.
- **`reproducibility`** (top level) — retrieval metadata that makes the
  profile build reproducible (PRD s9 snapshot retention; PRD s20 item 17
  reproducibility identifier). When present, ALL 10 subfields are required
  because the M1-T005 builder emits each unconditionally: `correlation_id`,
  `source_id`, `dataset_id`, `dataset_version` (nullable — key present,
  explicitly `null` when the source exposes no version), `request_url`,
  `retrieved_at`, `record_count`, `drift_signals`, `connector_notes`,
  `coverage_policy` (the verbatim deterministic policy that produced every
  coverage label in the profile).
- **`zoning.district_provenance` / `zoning.commercial_overlay_provenance` /
  `zoning.special_district_provenance`** (G3 D4) — optional maps from a
  value in the sibling plain-string array (`districts` /
  `commercial_overlays` / `special_districts`) to a NON-EMPTY LIST of
  `provenance_ref` ids. The plain-string arrays are unchanged and remain the
  canonical value lists; the maps only annotate them. A list (not a single
  ref) lets one district value be corroborated by multiple provenance
  records (e.g. PLUTO `zonedist*` today plus the M2 DCP GIS zoning-features
  cross-check later) without another contract bump. Two validator-enforced
  integrity rules: every map key must be a member of the sibling array, and
  every listed ref must resolve to a `provenance_id` in the profile's
  `provenance` array. Partial linkage is legal; an absent map means
  provenance is joinable only via `provenance[].original_field_name` (the
  documented 1.0.0 situation).

`validate_contracts.py` enforces referential integrity at EVERY
`provenance_ref` site: fact values, `zoning.mapped_features` entries, and
the three provenance maps. Its pytest suite lives in
`.github/scripts/tests/` (run `python -m pytest .github/scripts/tests` from
the repo root); it also exercises the legacy jsonschema `RefResolver` path
that is live on the CI runner (jsonschema 4.10.3), including the fail-closed
remote-`$ref` guard.

Consumers that build their own `$ref` registry for
`property_profile.schema.json` must load **all four** referenced documents:
`property_profile`, `source_fact`, `common`, and (since 1.1.0)
`coverage_status`. Loading every schema in `schemas/v1/` — as
`validate_contracts.py` does — is the forward-compatible pattern.

## Property profile contract 1.2.0 (task M2-T004, additive — data semantics and snapshot lineage)

Publishes `contract_version` `"1.2.0"` (the CLOSED enum is now
`["1.0.0","1.1.0","1.2.0"]`; the rejected-exemplar fixture advanced to
`1.3.0`). **Every new key is OPTIONAL, so every valid 1.0.0/1.1.0 instance
remains valid unchanged.** Owner code-audit P1 directive, 2026-07-17.

### Independent status dimensions (`status_dimensions`, top level)

Five INDEPENDENT dimensions, never collapsed into one label (PRD s12; GDS
s3.3). All six subfields are REQUIRED when the object is present (omitting a
dimension would silently collapse the set); a dimension the platform cannot
yet compute is DECLARED `not_computed` — never inferred, never invented:

- **`source_record_completeness`** — `complete | partial | not_computed`.
  Judged ONLY against the documented feasibility-relevant column basis (next
  section), never against all 108 PLUTO columns.
- **`analysis_readiness`** — `ready | blocked_missing_critical |
  blocked_data_conflict | not_computed`. A DATA statement (critical inputs
  present, usable, unconflicted), explicitly NOT the PRD s32.1 workflow
  state; it never implies user confirmation occurred.
- **`rule_coverage`** — `not_computed` (single-value enum BY DESIGN until the
  M4 rule engine makes applicability computable; extended additively then).
- **`geometry_validity`** — `missing | not_computed`. `missing` = the source
  supplied no usable geometry (a positive statement); `not_computed` =
  geometry present but the M2 tax-lot geometry validation pipeline does not
  exist yet. `valid`/`invalid`/`repaired` land additively with it.
- **`financial_readiness`** — `not_computed` until a financial engine exists
  (GDS Phase C).
- **`policy`** — verbatim derivation policy (self-description pattern of
  `reproducibility.coverage_policy`).

The legacy top-level `data_completeness` (3 PRD s12 values) is UNCHANGED in
key, enum, and placement for v1.1 consumers; only its derivation basis is
fixed (below).

### Feasibility-relevant completeness basis (the 108-column defect fix)

`data_completeness` and `source_record_completeness` are derived ONLY from
the 19-column basis `FEASIBILITY_COLUMNS` in
`services/api/app/profile/builder.py` — critical: `lotarea`, `zonedist1`;
noncritical: `lotfront`, `lotdepth`, `lottype`, `irrlotcode`, `splitzone`,
`landuse`, `bldgclass`, `bldgarea`, `numbldgs`, `numfloors`, `unitsres`,
`unitstotal`, `yearbuilt`, `builtfar`, `residfar`, `commfar`, `facilfar`.
Grounding: every column exists in the official 108-column SODA inventory
(fixture F08, `/api/views/64uk-42ks.json`, retrieved 2026-07-16) and its
meaning/units/null semantics are cited per column against the official
"PLUTO DATA DICTIONARY — May 2026 (26v1)" in the builder's basis comment and
`docs/research/pluto-mappluto-2026-07-16.md` s4.1/s4.3 (e.g. LotArea p.21,
LotFront/LotDepth p.29, NumFloors p.28, YearBuilt p.34-35, BldgArea p.22,
ResidFAR/CommFAR/FacilFAR p.36-37). Documented exclusions: conditional-
presence zoning/regulatory columns (SODA null-omission makes absence
indistinguishable from "none"), geometry columns (owned by the independent
`geometry_validity` dimension), and identity/administrative columns. Every
`missing_inputs[]` entry now carries OPTIONAL `feasibility_relevant`
(basis membership) — ALL absent columns stay listed (unknown is stated,
never hidden); only flagged entries drive the labels.

### Fact identity and snapshot lineage (`source_fact` additive keys)

Three identities with distinct lifetimes, all coexisting on each record:

| Key | Lifetime | Purpose |
| --- | --- | --- |
| `fact_key` | STABLE across re-observations AND dataset versions | track the logical fact (`fact:<source_id>:<dataset_id>:<bbl>:<field>`) |
| `provenance_id` | stable within one dataset version (unchanged from M1-T002) | referential target of every `provenance_ref` |
| `observation_id` | IMMUTABLE, unique per retrieval event, never reused | pin one observation (`obs:<event-id>:<bbl>:<field>`; event id minted fresh per fetch) |

Lineage chain, gap-free on every fact: `observation_id` + `retrieved_at`
(observation) → `dataset_version`/`dataset_id`/`source_id` (source version)
→ `request_url` (request) → `response_digest` (exact content).

### Canonical digests

`value_digest` (per fact, over verbatim `original_value`) and
`response_digest` (per retrieval, over the ENTIRE parsed response body; also
in `reproducibility` with the verbatim spec in
`reproducibility.digest_canonicalization`). Canonicalization
(`canonical-json-1`, `common.schema.json#/$defs/digest_sha256`): SHA-256
over the UTF-8 encoding of the parsed value serialized with keys sorted
lexicographically by Unicode code point, `,`/`:` separators, no
insignificant whitespace, non-ASCII preserved (no escaping), no Unicode
normalization, Python `json.dumps` number defaults. Parsed-value digesting
makes byte-different but semantically identical responses digest EQUAL while
any value change flips the digest.

### `contract_version` semantics — recorded as an INPUT to M2-T003

This task publishes `1.2.0` in the schema enum (the shape). What it
deliberately does NOT decide (owner sequencing 2026-07-17: M2-T003 builds
validation/typegen against this settled shape): which version a producer
DECLARES, and whether declared version and emitted key set are validated
against each other. The accepted builder still declares `"1.0.0"` while
emitting the additive keys — legal at every published version because all
additive keys are optional (the same precedent as M1-T005/M1-T006). M2-T003
owns the declaration/validation decision.

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
the above plus the property-profile invariant that every `provenance_ref` —
in fact values, `zoning.mapped_features`, and the contract-1.1.0 zoning
provenance maps — resolves to a `provenance_id`, and that provenance-map
keys are members of their sibling value array (PRD s19). It runs a strict stdlib structural
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
