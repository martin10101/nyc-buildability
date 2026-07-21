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

Publishes `contract_version` `"1.2.0"` (the CLOSED enum became
`["1.0.0","1.1.0","1.2.0"]`; the rejected-exemplar fixture advanced to
`1.3.0` — and advanced again to `1.4.0` when M2-T006 published 1.3.0, see the
1.3.0 section below). **Every new key is OPTIONAL, so every valid 1.0.0/1.1.0
instance remains valid unchanged.** Owner code-audit P1 directive, 2026-07-17.

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
indistinguishable from "none" — this category also covers the 26v1-new
`affresfar`/`mnffar` FAR reference columns, which are informational values
with program-dependent conditional presence; G1 correction C2), geometry
columns (owned by the independent `geometry_validity` dimension), and
identity/administrative columns. Every
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

### `contract_version` semantics — RESOLVED by M2-T003 (supersedes the deferral)

M2-T004 published `1.2.0` in the schema enum (the shape) and deliberately left
the DECLARATION/VALIDATION decision to M2-T003. That decision is now made and
implemented:

**Decision (task M2-T003, owner code-audit P0 2026-07-17):**

1. **The builder DECLARES the version whose key set it fully covers** —
   `1.2.0` when this decision landed (M2-T003); advanced to `1.3.0` by M2-T006
   when the builder began emitting `reproducibility.staleness`
   (`PROFILE_CONTRACT_VERSION` in `services/api/app/profile/builder.py`). It
   never again declares a stale version.

2. **Declared version and emitted key set ARE validated against each other.**
   The declared version must be at least the minimum version that introduces
   any emitted optional key. Declaring `1.0.0`/`1.1.0` while emitting a later
   key (the exact stale-declaration bug deferred here) is rejected as a typed
   `internal_contract_error` — a built payload that misstates its own version
   never leaves the API. Introduction versions:
   `data_completeness`/`reproducibility` = 1.1.0; `status_dimensions` = 1.2.0;
   `reproducibility.staleness` = 1.3.0 (a DOTTED-PATH key — M2-T006 extended
   the check with dotted-path resolution for nested additive keys)
   (`app.profile.contract.VERSION_INTRODUCED`).

3. **Every 200 payload is validated against the SELECTED canonical schema
   before send.** The version is selected from the payload's declared version
   against the CLOSED published enum, which is read LIVE from this schema (no
   stale version is hard-coded in the backend). A schema-invalid payload
   becomes a typed `500 internal_contract_error`; an invalid 200 is impossible
   (`app.profile.contract.validate_profile`, wired in
   `services/api/app/api/v1/properties.py`).

4. **An unpublished declared version is a BOUNDED typed error.** A profile
   declaring a version outside the published enum (currently
   `["1.0.0","1.1.0","1.2.0","1.3.0","1.4.0"]`; e.g. `1.5.0`) yields a typed,
   correlation-id'd `500 unsupported_contract_version` with the declared
   version and the supported set — never a silent coercion and never a raw
   500 stack.

5. **Backward compatibility preserved.** Because every added key is optional, a
   valid `1.0.0` instance (no additive keys) and a valid `1.1.0` instance
   (`data_completeness` + `reproducibility`, no `status_dimensions`) both still
   pass backend validation and are served unchanged. Proven by
   `services/api/tests/api/test_property_contract.py` (S7) against the committed
   `full_example.json` (1.0.0) and `full_example_v1_1.json` (1.1.0) fixtures.
   The historical `builder_output_m1_t005.json` fixture intentionally remains a
   1.0.0-declaring snapshot of the M1-T005 builder — it is a SCHEMA fixture
   (validated against the version-agnostic schema in CI), not live builder
   output, and demonstrates that an optional-key-bearing 1.0.0 instance stays
   schema-valid; live builder output now declares 1.2.0.

**Deterministic TypeScript typegen (item E).** The canonical TS types are
generated from `property_profile.schema.json` (+ the three referenced files) by
a STDLIB-ONLY Python generator (`packages/contracts/scripts/generate_ts_types.py`;
no Node toolchain, no network — thin-client policy) into
`packages/contracts/generated/property_profile.ts` (committed). A CI job
(`contracts-typegen`) regenerates and fails on any byte-level divergence; the
generated types cover 100% of the schema keys and pin the closed
`contract_version` enum. This replaces any hand-written client representation
(removed when M2-T002 migrates the web client).

**Client-regression fixtures (item F).** `fixtures/client_regression/` holds
adversarial API-response fixtures the frontend must defend against but that the
real app never emits — currently `http500_state_no_match.json` (the incoherent
HTTP 500 + `state=no_match` pair). This directory is outside `valid/`/`invalid/`
so `validate_contracts.py` does not treat it as a contract fixture; M2-T002
wires it as a client regression input.

## Property profile contract 1.3.0 (task M2-T006, additive — typed staleness and description refreshes)

Publishes `contract_version` `"1.3.0"` (the CLOSED enum is now
`["1.0.0","1.1.0","1.2.0","1.3.0"]`; the rejected-exemplar fixture
`fixtures/invalid/property_profile/contract_version_unknown.json` advanced to
`1.4.0` in the same change — an "invalid" fixture that starts validating
fails the contracts CI job). **Every new key is OPTIONAL, so every valid
1.0.0/1.1.0/1.2.0 instance remains valid unchanged.** Sources: M1-T009 G1
findings D1/D2 and M2-T002 G3 finding N3 (both LOW, corrective, contracted to
ride this revision).

### Typed serve-freshness (`reproducibility.staleness`) — G1 D2

The machine-readable successor to the `served_from_last_known_good:`
connector-note convention (the human-readable note in
`reproducibility.connector_notes` is RETAINED alongside it). Shape:
`served_from_cache` + `stale` (REQUIRED booleans), `upstream_error_type`,
`original_retrieved_at`, `age_seconds` (optional, conditionally required):

- fresh build → `{served_from_cache: false, stale: false}` and nothing else
  (no invented age/error values);
- within-TTL cache hit → `served_from_cache: true, stale: false` +
  `original_retrieved_at` + `age_seconds` (the explicit cache-serve marker D2
  asked for);
- last-known-good serve after an upstream failure → `served_from_cache:
  true, stale: true` + `upstream_error_type` + `original_retrieved_at` +
  `age_seconds`.

Conditionals (`served_from_cache: true` ⇒ timestamp+age required;
`stale: true` ⇒ error type required and `served_from_cache: true`) are
encoded with `allOf`/`anyOf`/`const` — the keyword subset
`validate_contracts.py` supports (`if`/`then` is NOT in its allowlist) — and
enforced by JSON-Schema validation (backend boundary + fixture CI). The
GENERATED TypeScript types carry the two required booleans and three optional
fields WITHOUT the cross-field conditionals (the typegen generator does not
emit conditional types); TS consumers rely on runtime validation for those.
ABSENCE semantics: an absent `staleness` object means a pre-1.3.0 producer —
consumers must not infer freshness from absence and fall back to the
connector-note convention plus the truthful `retrieved_at`. A 1.3.0 builder
emits the object on EVERY serve. Emission: the resilience fetcher
(`services/api/app/resilience/fetcher.py`) stamps cache-hit and LKG serves
from its own serve record (injected monotonic-clock ages; nothing invented);
`reproducibility.retrieved_at` is never rewritten to serve time.

### `correlation_id` description refresh — G1 D1

The 1.1.0-era sentence "equals the X-Correlation-ID response header" was
written when every 200 was a fresh stateless build and became falsifiable
once M1-T009 cache/LKG serves existed. The refreshed description states the
truth the G1 review adjudicated (J1): the field joins the profile to the
retrieval that PRODUCED it — equal to the serving request's header only on
fresh builds; on cache/LKG serves it stays the ORIGINAL fetch's id while the
`X-Correlation-ID` header identifies the serving HTTP exchange. Description
change only; no payload semantics changed.

### Open-schema key documentation — G3 N3

Description-level (annotation-only, NO structural tightening — the generated
TS types are unchanged for these shapes and the client's runtime-narrowing
helpers remain the accepted pattern): `zoning.mapped_features` items document
the builder-emitted keys (`feature`, `value`, `provenance_ref`,
`coverage_status`, optional `units`); conflict `values[]` items document the
open `derivation` string; conflict items document the open nullable `reason`.

### Version-publication coordination (systemic note)

The web client pins a CLOSED runtime `SUPPORTED_CONTRACT_VERSIONS` set
(`apps/web/src/lib/contract.ts`) and fail-closes on versions outside it, so
**publishing a contract version is always a coordinated schema + backend +
client-vocabulary change in ONE atomic change set** (this revision shipped
under M2-T006 amendment A1 for exactly that reason). A future contracts-
tooling task may generate the client's runtime version array from the schema
enum to remove the hand-edit.

Deferred contracts (added additively in later milestones, per
`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md` "Canonical contracts"): rule
definition and rule evaluation trace (M4), scenario (M5), report evidence
item (M6). They are deliberately not stubbed here to avoid shipping
unreviewed shapes that downstream code might bind to.

## Property profile contract 1.4.0 (task M2-T012, additive — wave-connector + spatial-intersection integration)

Publishes `contract_version` `"1.4.0"` (the CLOSED enum is now
`["1.0.0","1.1.0","1.2.0","1.3.0","1.4.0"]`; the rejected-exemplar fixture
`fixtures/invalid/property_profile/contract_version_unknown.json` advanced to
`1.5.0` in the same change — that string is a NEVER-PUBLISHED rejection
exemplar, unrelated to the owner STOP condition on real 1.5.0 publication).
One coordinated update (owner directive 2026-07-20: no successive contract
versions) carries the accepted connector-wave and spatial-intersection facts
into the canonical profile. **Every new key is OPTIONAL, so every valid
1.0.0/1.1.0/1.2.0/1.3.0 instance remains valid unchanged**; the builder now
declares `1.4.0` and a PLUTO-only build (no wave data) emits no 1.4.0 key and
stays declared-vs-emitted consistent.

### Three additive top-level keys (each with full provenance)

- **`zoning_features`** — per-layer RETRIEVAL facts for the six DCP GIS
  zoning-features layers (M2-T007): `layers[]` each carrying `layer`,
  `provenance_ref` (resolves to a provenance record), `coverage_status`
  (`conditional`, or `unsupported` on a drift signal), and open pass-through
  keys (`record_count`, `normalized_digest`, `source_data_last_edited`, `crs`,
  `drift_signals`). CITYWIDE reference data, **not** lot-level determinations
  (the official use limitation is explicit).
- **`lot_geometry`** — per-BBL MapPLUTO tax-lot geometry facts (M2-T009):
  `outcome`, `provenance_ref`, plus open `review_required`, `geometry_status`,
  `area_sq_ft`, digests, `crs`, library versions. The validity taxonomy is
  preserved; never a legal boundary certification.
- **`spatial_intersection`** — the M2-T013 lot/zoning facts-with-uncertainty
  substrate: exact geometric results, boundary distances, split-share **ranges**
  (`share_min/point/max`), positional-uncertainty classes (`pair_class`,
  `lot_overall_class`), professional-review flags, `coverage_note`, and
  `provenance_refs`. **Uncertainty is NEVER collapsed** into a definitive
  single-district assignment, nothing is `Verified`, and the engine-internal
  `coverage_audits` diagnostic is deliberately EXCLUDED (owner amendment
  invariant 6).

### Fourth (geometric) evidence stream — through the EXISTING conflict shape

The M2-T008 lot-level zoning cross-check (`app.profile.zoning_crosscheck`)
gains a fourth evidence stream: `geometric_zoning_observations()` emits a
geometric `zonedist1` observation ONLY when the lot is
`single_district_confident` (the geometry firmly places the whole lot in one
base district); fed to `crosscheck_lot_zoning` via `external_observations`, a
geometric value disagreeing with the ZTLDB/PLUTO `zonedist1` becomes a typed
`conflict` (`resolution='unresolved'`) in the existing `conflicts` array and —
being on the critical column — gates `analysis_readiness`. No new conflict
shape; uncertain lots emit no collapsing value (uncertainty preserved).

### Referential integrity

Every `provenance_ref` / `provenance_refs` in the three new keys resolves to a
provenance record in the profile's `provenance` array. The backend is the
integrity authority for live data
(`app.profile.builder._assert_provenance_integrity`, extended to the three new
sites). **Follow-up (out of this task's file scope):**
`.github/scripts/validate_contracts.py`'s `profile_provenance_invariant` still
checks only the pre-1.4.0 fixture sites; extending it to the three new sites is
a recommended companion change in a `.github/`-scoped task.

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
