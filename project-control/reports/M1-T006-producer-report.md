# M1-T006 Producer Report — Property-profile contract v1.1 (additive)

- **Task:** M1-T006 — contract 1.1.0: document coverage_status / data_completeness / reproducibility + district provenance linkage (M1-T005 G3 adjudication #1, defects D2/D4)
- **Producer:** backend-engineer
- **Status requested:** `awaiting_gate` (with ONE mandatory integration pairing noted in §6 — a one-line fix in a path forbidden to this producer)
- **Worktree:** `.claude/worktrees/M1-T006`, branch `task/M1-T006-contract-v1-1`, based on main @ `c6ad0e6`
- **Environment:** local Python 3.11.9, jsonschema 4.26.0, pytest 8.x, ruff 0.9.9; full local exec available; total new disk use ≈ 90 KB of text fixtures/tests (no installs, no datasets)
- **Note on the task packet:** `project-control/tasks/M1-T006.json` does not exist inside the worktree (branch was cut from `c6ad0e6` before the orchestrator committed the packet). I read it from the main checkout `project-control/tasks/M1-T006.json` (read-only) and treated it as binding.

## 1. Files changed

Modified:
- `packages/contracts/schemas/v1/property_profile.schema.json` — contract 1.1.0 (all changes additive; required key set of 1.0.0 unchanged; nothing removed or retyped)
- `.github/scripts/validate_contracts.py` — `profile_provenance_invariant` extended to ALL provenance_ref sites (fact values, `zoning.mapped_features`, the three new zoning provenance maps + map-key membership rule); module docstring layer-6 updated; exit-code semantics untouched (main still returns 0/1)
- `packages/contracts/README.md` — contract 1.1.0 key documentation, additive-versioning statement, consumer registry guidance (load all four referenced schemas)

Added — valid fixtures:
- `packages/contracts/fixtures/valid/property_profile/full_example_v1_1.json` — handcrafted 1.1.0 example exercising ALL additive keys: per-fact `coverage_status`, `data_completeness`, `reproducibility` (with the nullable `dataset_version` branch: key present, explicitly `null`), all three provenance maps, one district (`C4-1`) corroborated by TWO provenance records (list semantics), mapped_feature with provenance_ref
- `packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json` — **S6 ground truth, 69.7 KB**: byte-exact output of the accepted M1-T005 builder (deterministic run of `fetch_by_bbl` + `build_property_profile` over the committed F05 split-zone connector fixture, fixed clock `2026-07-16T12:00:00Z`, fixed correlation_id `m1t006-s6-ground-truth`); `contract_version` `"1.0.0"` + the three additive keys exactly as emitted; 84 provenance records, districts `["R3-2","C4-1"]`, special `["GI"]`, 8 mapped_features. Because it sits in `fixtures/valid/`, S6 re-executes on every future validator/CI run.
- (regression fixture) `fixtures/valid/property_profile/full_example.json` — **untouched, byte-identical** (`git diff --quiet` exits 0); this is the pure-1.0.0 no-additive-keys fixture required by the packet.

Added — invalid fixtures (each carries the repo's `_expected_failure` convention):
- `bad_coverage_status_enum.json` — fact `coverage_status: "approved"` (rejected by the $ref'd 6-value enum)
- `bad_data_completeness_enum.json` — `data_completeness: "partial"` (rejected by the $ref'd 3-value enum)
- `reproducibility_missing_correlation_id.json` — reproducibility present, `correlation_id` absent (rejected by `required`)
- `district_provenance_dangling_ref.json` — SCHEMA-CLEAN; fails ONLY via the validator's referential-integrity invariant (packet S5)
- `district_provenance_orphan_value.json` — SCHEMA-CLEAN; fails ONLY via the map-key membership invariant (companion to S5)
- `contract_version_unknown.json` — `"1.2.0"` rejected by the closed enum (packet risk 3)

Added — tests:
- `.github/scripts/tests/__init__.py`, `.github/scripts/tests/test_validate_contracts.py` — 24 tests (invariant units incl. crash-safety on broken shapes; per-fixture intended-reason assertions; S6/S2 fixture assertions; full-run subprocess exit-0; legacy RefResolver path incl. fail-closed guard)

Report: `project-control/reports/M1-T006-producer-report.md` (this file).

## 2. Design decisions

### 2.1 District provenance linkage (G3 D4)

Chosen shape — three OPTIONAL sibling maps under `zoning`, one per plain-string array:

```json
"zoning": {
  "districts": ["R6", "C4-1"],
  "district_provenance": {
    "R6": ["prov-zonedist1-0001"],
    "C4-1": ["prov-zonedist2-0001", "prov-zonedist2-gis-0001"]
  }
}
```

`district_provenance` / `commercial_overlay_provenance` / `special_district_provenance` all `$ref` one shared `$defs/district_provenance_map`, whose values are `$defs/provenance_ref_list` (array, `minItems: 1`, items = `common.schema.json#/$defs/non_empty_string`).

Justification:
- **Additive by construction.** The plain-string arrays are untouched and remain the canonical value lists; the maps only annotate. Every 1.0.0 instance (no maps) and the accepted M1-T005 API output (no linkage) validate unchanged — proven by S2/S6 below.
- **List of refs, not a single ref.** (a) Duplicate source columns can never silently drop a record; (b) one district value can be corroborated by multiple provenance records — concretely, PLUTO `zonedist*` today plus the M2 DCP GIS zoning-features cross-check later — with no further contract bump. Exercised by `full_example_v1_1.json` (`C4-1` → 2 refs).
- **Map keyed by value, not by column.** The consumer (Priority 4 property screen) holds a district string from the array and needs its evidence; a value-keyed map is a direct O(1) machine-resolvable join, with no knowledge of PLUTO column names required. Column names remain visible inside the resolved provenance records (`original_field_name`).
- **Two validator-enforced integrity rules** (schema cannot express either): every listed ref resolves to a `provenance_id`; every map key is a member of the sibling array (an orphan key would be a fabricated district — exactly what PRD §9/§19 forbid). Both rules have dedicated invalid fixtures and unit tests, and the backend must mirror them for live data (documented in the schema description).
- **Partial linkage is legal** — an absent/partial map degrades to the documented 1.0.0 situation (join via `provenance[].original_field_name`), so future sources that cannot link a value fail visible, not fail closed.

### 2.2 jsonschema 4.10.3 legacy path (packet risk 1)

`validate_contracts.py::make_validator` takes the legacy `RefResolver` branch when `referencing` is not importable — the LIVE branch on the CI runner (jsonschema 4.10.3), fail-closed since M0-T005-R1. I introduced **no new `$ref` pattern**; the three patterns v1.1 uses all pre-exist in the contract set and have passed on the real 4.10.3 runner since M0-T009:
1. whole-document cross-file ref — `coverage_status.schema.json` (pre-existing precedent: `source_fact.schema.json` from `provenance.items`)
2. cross-file ref into `$defs` — `coverage_status.schema.json#/$defs/data_completeness` (precedent: `common.schema.json#/$defs/date_time` etc.)
3. internal ref — `#/$defs/district_provenance_map`, `#/$defs/provenance_ref_list` (precedent: `#/$defs/fact_value`)

Additionally the new test suite **forces the legacy branch locally** (monkeypatching `sys.modules["referencing"] = None` makes the `from referencing import ...` raise ImportError, driving `make_validator` onto the exact RefResolver code path) and proves: all three property_profile valid fixtures resolve with zero errors, enum rejection still fires, and an unknown remote `$ref` still fails closed with `remote $ref fetch blocked`. See S7 evidence.

### 2.3 reproducibility required-subfield set

`services/api/app/profile/builder.py:382-393` emits all ten keys unconditionally, so all ten are `required` when the object is present: `correlation_id`, `source_id`, `dataset_id`, `dataset_version`, `request_url`, `retrieved_at`, `record_count`, `drift_signals`, `connector_notes`, `coverage_policy`. `dataset_version` is typed `["string","null"]` with `minLength: 1` because the connector's `PlutoFetchResult.dataset_version` is `str | None` (`pluto_soda.py:340`) — required key, explicitly `null` when the source exposes no version, mirroring the accepted `source_fact.effective_date` visible-absence pattern. `record_count` is `integer, minimum 0`; `drift_signals`/`connector_notes` are arrays of non-empty strings; everything else is `non_empty_string` (+ `date_time` pattern for `retrieved_at`). Each subfield's description carries its PRD §9 / §20-item-17 / §25 grounding. The object stays open (no `additionalProperties: false`) consistent with the rest of the contract, so the M2 multi-source evolution (per-source array ALONGSIDE) stays additive.

### 2.4 Other decisions

- `contract_version`: `const "1.0.0"` → **closed** enum `["1.0.0", "1.1.0"]`; description states new versions are admitted only by an accepted contract task. Negative fixture `contract_version_unknown.json` proves `1.2.0` is rejected.
- `coverage_status` and `data_completeness` are pure `$ref`s — the 6/3 PRD §12 enums live only in `coverage_status.schema.json`, never duplicated.
- The validator invariant now also checks `zoning.mapped_features[*].provenance_ref` — the builder already asserts this site (`_assert_provenance_integrity`, builder.py:293-295) but the fixture validator did not; the packet's "ALL provenance_ref sites" requirement closes that gap.
- Invariant crash-safety: non-string refs / non-list map values / non-string array members degrade to schema-layer errors instead of raising (unit-tested), so a malformed fixture can never crash the CI gate.
- `$id` stays in the `/v1/` directory: the directory is the MAJOR version; 1.1.0 is a minor, in-place, additive revision (README "Versioning rules" unchanged and now cross-referenced).

## 3. Acceptance scenarios S1–S8 — commands and actual outputs

All commands run from the worktree root (`.claude/worktrees/M1-T006`) unless stated.

### S1 (primary) + S2 (backward-compat) + S3 (enum boundary) + S4 (missing/null) + S5 (referential integrity) + S8 (schema meta) — full validator run

Command: `python .github/scripts/validate_contracts.py` → **EXIT=0**

Output (complete; property_profile lines are the S-evidence):

```text
meta-schema engines : stdlib-structural + jsonschema 4.26.0
instance engines    : stdlib mini-validator + jsonschema 4.26.0 (cross-checked)
OK   packages\contracts\schemas\v1\analysis_state.schema.json (Analysis Run State)
OK   packages\contracts\schemas\v1\analysis_state_transition.schema.json (Analysis State Transition)
OK   packages\contracts\schemas\v1\common.schema.json (Common Contract Definitions)
OK   packages\contracts\schemas\v1\coverage_status.schema.json (Coverage Status)
OK   packages\contracts\schemas\v1\property_profile.schema.json (Canonical Property Profile)   <-- S8
OK   packages\contracts\schemas\v1\source_fact.schema.json (Source Fact (Provenance Record))
OK   packages\contracts\fixtures\valid\analysis_state\initial_state.json (valid fixture passes analysis_state)
OK   packages\contracts\fixtures\valid\analysis_state_transition\address_resolution.json (valid fixture passes analysis_state_transition)
OK   packages\contracts\fixtures\valid\coverage_status\verified.json (valid fixture passes coverage_status)
OK   packages\contracts\fixtures\valid\property_profile\builder_output_m1_t005.json (valid fixture passes property_profile)   <-- S6
OK   packages\contracts\fixtures\valid\property_profile\full_example.json (valid fixture passes property_profile)             <-- S2
OK   packages\contracts\fixtures\valid\property_profile\full_example_v1_1.json (valid fixture passes property_profile)        <-- S1
OK   packages\contracts\fixtures\valid\source_fact\geosearch_bbl_fact.json (valid fixture passes source_fact)
OK   packages\contracts\fixtures\invalid\analysis_state\unknown_state.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\analysis_state_transition\missing_correlation_id.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\coverage_status\unknown_status.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\property_profile\bad_coverage_status_enum.json (invalid fixture correctly rejected: $.lot_facts.lot_area_sf.coverage_status: value 'approved' is not one of the allowed enum values ['verified', 'conditional', 'professional_review_required', 'data_conflict', 'unsupported', 'not_applicable'])   <-- S3
OK   packages\contracts\fixtures\invalid\property_profile\bad_data_completeness_enum.json (invalid fixture correctly rejected: $.data_completeness: value 'partial' is not one of the allowed enum values ['complete', 'missing_noncritical', 'missing_critical'])   <-- S3
OK   packages\contracts\fixtures\invalid\property_profile\bbl_borough_6.json (invalid fixture correctly rejected: ... pattern ...)   <-- S2/S7 pre-existing set intact
OK   packages\contracts\fixtures\invalid\property_profile\bbl_non_numeric.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\property_profile\bbl_wrong_length.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\property_profile\contract_version_unknown.json (invalid fixture correctly rejected: $.profile_version.contract_version: value '1.2.0' is not one of the allowed enum values ['1.0.0', '1.1.0'])   <-- risk 3
OK   packages\contracts\fixtures\invalid\property_profile\dangling_provenance_ref.json (invalid fixture correctly rejected: $.lot_facts.lot_area_sf: provenance_ref 'prov-does-not-exist' does not resolve to any provenance_id in the profile's provenance array (PRD s19))
OK   packages\contracts\fixtures\invalid\property_profile\district_provenance_dangling_ref.json (invalid fixture correctly rejected: $.zoning.district_provenance['R6']: provenance_ref 'prov-does-not-exist' does not resolve to any provenance_id in the profile's provenance array (PRD s19))   <-- S5
OK   packages\contracts\fixtures\invalid\property_profile\district_provenance_orphan_value.json (invalid fixture correctly rejected: $.zoning.district_provenance: key 'C1-9' is not a member of the sibling zoning.districts array (contract 1.1.0: the map only annotates values that are actually listed))   <-- S5 companion
OK   packages\contracts\fixtures\invalid\property_profile\fact_missing_provenance_ref.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\property_profile\provenance_missing_conflict_status.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\property_profile\reproducibility_missing_correlation_id.json (invalid fixture correctly rejected: $.reproducibility: missing required property 'correlation_id')   <-- S4
OK   packages\contracts\fixtures\invalid\source_fact\missing_dataset_version.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid\source_fact\missing_effective_date_key.json (invalid fixture correctly rejected: ...)
OK   packages\contracts\fixtures\invalid_schemas\bad_keyword.schema.json (broken schema correctly rejected: ...)
OK   packages\contracts\fixtures\invalid_schemas\bad_type_value.schema.json (broken schema correctly rejected: ...)
OK   packages\contracts\fixtures\invalid_schemas\required_not_in_properties.schema.json (broken schema correctly rejected: ...)
Checked 6 schema file(s); 0 failure(s).
```

(`...` elisions are the pre-existing rejection messages, unchanged from the M0-T009 baseline; the full un-elided run is reproducible with the single command above and was byte-inspected by the producer. Every line above marked with an S-number is quoted verbatim.)

S4's second half (fact_value WITHOUT coverage_status still valid = 1.0 compat) is proven by `full_example.json` passing (its `lot_area_sf` has no coverage_status) and by S2's byte-identity check below.

S2 byte-identity of the pre-existing v1.0.0 fixture:

```text
$ git diff --quiet -- packages/contracts/fixtures/valid/property_profile/full_example.json && echo "byte-identical (no diff)"
byte-identical (no diff)
```

### S6 — ground-truth conformance (accepted M1-T005 builder output vs v1.1 schema)

Fixture generation (deterministic; run from `services/api`, read-only against `services/**`):

```text
$ python -c "<fetch_by_bbl over committed connector fixture tests/fixtures/pluto/F05_split_zone_lot.json,
   fixed clock 2026-07-16T12:00:00Z, correlation_id m1t006-s6-ground-truth; build_property_profile;
   json.dump -> packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json>"
written ...\packages\contracts\fixtures\valid\property_profile\builder_output_m1_t005.json 69655 bytes
districts: ["R3-2", "C4-1"]
overlays: []
special: ["GI"]
mapped_features n: 8
mf[0]: {"feature": "splitzone", "value": true, "provenance_ref": "pluto-64uk-42ks-26v1-1000010010-splitzone", "coverage_status": "conditional"}
data_completeness: missing_noncritical
reproducibility: { "correlation_id": "m1t006-s6-ground-truth", "source_id": "nyc-dcp-pluto-soda", "dataset_id": "64uk-42ks",
  "dataset_version": "26v1", "request_url": "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1000010010",
  "retrieved_at": "2026-07-16T12:00:00Z", "record_count": 1, "drift_signals": [], "connector_notes": [], "coverage_policy": "coverage_status is derived only from review status and conflict/drift state: ... (PRD section 12)." }
provenance n: 84
```

Verification: the `OK ... builder_output_m1_t005.json (valid fixture passes property_profile)` line in the S1 run (both engines, cross-checked, zero errors, referential integrity across all 84 records incl. 8 mapped_features), plus the dedicated test `test_s6_builder_output_validates_without_modification` which additionally asserts `contract_version == "1.0.0"` and the presence of the three additive keys. The fixture was NOT modified after generation.

### S7 — regression + jsonschema 4.10.3 legacy-path consideration

(a) Full contract suite — see S1 run: every pre-existing schema, valid fixture, invalid fixture, and invalid_schema behaves exactly as at base `c6ad0e6`; exit 0.

(b) New validator pytest suite: `python -m pytest .github/scripts/tests -v` → **24 passed** (`24 passed, 5 warnings in 0.65s`; the 5 warnings are the pre-existing `jsonschema.__version__` DeprecationWarning in validate_contracts.py:147, out of scope). Includes the forced legacy-RefResolver tests:

```text
TestLegacyRefResolverPath::test_v1_1_refs_resolve_on_the_legacy_path[full_example.json] PASSED
TestLegacyRefResolverPath::test_v1_1_refs_resolve_on_the_legacy_path[full_example_v1_1.json] PASSED
TestLegacyRefResolverPath::test_v1_1_refs_resolve_on_the_legacy_path[builder_output_m1_t005.json] PASSED
TestLegacyRefResolverPath::test_enum_rejection_works_on_the_legacy_path PASSED
TestLegacyRefResolverPath::test_remote_ref_fails_closed_on_the_legacy_path PASSED
```

(c) services/api suite (read-only regression probe, run from `services/api`): `python -m pytest -q` →

```text
FAILED tests/api/test_properties_v1.py::test_s1_200_profile_validates_against_property_profile_v1
1 failed, 141 passed in 2.03s
```

The single failure is the integration coupling analyzed in §6 (the test's own 3-schema registry, not a defect in the contract). 141/142 pass, including every builder/coverage/reproducibility assertion.

(d) ruff (packet: line-length 100): `ruff check --config services/api/pyproject.toml .github/scripts/tests/` → **All checks passed** (exit 0). `ruff check --config services/api/pyproject.toml .github/scripts/validate_contracts.py` reports 28 findings (25×E501, 3×UP038) — **all pre-existing**: the identical command against the base file (`git show c6ad0e6:.github/scripts/validate_contracts.py`) reports the same 28, and a rule+message set diff is empty:

```text
$ diff /tmp/base_findings.txt /tmp/cur_findings.txt && echo "IDENTICAL: ..."
IDENTICAL: all 28 findings pre-exist at base c6ad0e6; M1-T006 introduced zero new ruff findings
```

(The file has never been in CI's ruff scope — CI runs ruff only inside `services/api`. Reflowing 28 pre-existing lines would bloat this contract diff with unrelated hunks; left for a hygiene task.)

### S8 — schema meta-sanity

Covered by the `OK ... property_profile.schema.json (Canonical Property Profile)` line: stdlib structural layer (keyword allowlist, required-in-sibling-properties house rule, $ref resolvability across the set) + `Draft202012Validator.check_schema`, both clean. The three `invalid_schemas` expected-failure cases still reject.

## 4. Assumptions and defaults

1. **Reproducibility required set = all ten builder keys** (builder emits each unconditionally). If a future source cannot supply one, that is a contract discussion, not a silent omission.
2. **Partial district linkage is legal** (map may cover a subset of the array). Rationale in §2.1; the alternative (mandatory completeness when the key is present) can be tightened later ONLY via a major version, so the permissive reading is the additive-safe default.
3. **Map keys must be members of the sibling array** — I treated an orphan key as a fabricated-district integrity violation, enforced by the validator (and unit-tested), though the packet only mandated ref-resolution. Documented in the schema description; backend must mirror it.
4. `contract_version` stays in the `/v1/` directory ($id unchanged): directory = major line, enum = published minors.
5. The S6 fixture uses connector fixture F05 (split-zone, districts + special district populated) rather than F01, to make the linkage-relevant zoning arrays non-trivial; both are committed M1-T002 fixtures of the accepted connector.

## 5. Known limitations

1. **69.7 KB valid fixture** (`builder_output_m1_t005.json`): deliberate — it is the executable S6 ground truth and re-runs on every CI validator pass. Well within "small text fixtures" policy, but it is the largest fixture in the package.
2. The new pytest suite is **not wired into CI** — the `contracts` CI job installs nothing (stdlib-only by design) and `.github/workflows/**` is forbidden to this task. The suite runs locally/one-command (`python -m pytest .github/scripts/tests`); recommend the orchestrator decide wiring (see §8).
3. The legacy-path tests force the RefResolver **branch** on local jsonschema 4.26; that is the same code path but not literally 4.10.3. Mitigation: zero new $ref patterns (§2.2) + the real 4.10.3 runner exercises the schemas on every CI push of this branch.
4. Schema cannot express the two linkage integrity rules; they live in the validator (fixtures) and must be mirrored by the backend when the builder starts emitting linkage (follow-up, §8).

## 6. MUST-FIX integration pairing (out of my allowed paths)

`services/api/tests/api/test_properties_v1.py::profile_validator` (lines 156-161) builds its own $ref registry from a hardcoded 3-document list (`property_profile`, `source_fact`, `common`) and now fails with an unresolved-reference error, because contract 1.1.0 legitimately `$ref`s `coverage_status.schema.json`. This is the fail-closed behavior working as designed in a consumer that under-mirrors `validate_contracts.py` (which loads ALL schemas — its docstring even says "mirrors validate_contracts.py").

- **Failure:** `test_s1_200_profile_validates_against_property_profile_v1` — `referencing.exceptions._WrappedReferencingError` (unresolved `coverage_status.schema.json`); 141/142 other tests pass.
- **Exact fix (one line, forbidden path `services/**` — orchestrator/rework must apply when integrating):** in the `docs = [...]` tuple of `profile_validator`, add `"coverage_status.schema.json",` after `"common.schema.json",`.
- **Fix verified by producer (read-only):** reproducing the exact `profile_validator` construction with the 4-document registry validates the S6 builder profile with zero errors:
  `errors with 4-doc registry: []`
- Without this pairing, the `api` CI job fails on merge; the `contracts` CI job passes either way. README now documents the load-all-schemas registry rule for consumers.

## 7. Security / provenance impact

- Strengthens provenance: referential integrity now enforced at every provenance_ref site in fixtures (previously fact sections only), plus the anti-fabrication map-key membership rule. No provenance requirement was weakened; every new key is optional and additive.
- The fail-closed remote-$ref guard (M0-T005-R1) is regression-tested for the first time (forced legacy branch + `remote $ref fetch blocked` assertion).
- No secrets, no network calls (S6 generation ran entirely against a committed fixture via injected transport), no new dependencies, ~90 KB local disk, nothing written outside the worktree. `request_url` documentation states tokens never appear in it (they travel in headers — accepted M1-T005 behavior).
- Invariant crash-safety prevents a hostile/malformed fixture from crashing the CI gate; error strings pass through the existing `sanitize_for_log` on emit.

## 8. Recommended next steps

1. **Pair the one-line `profile_validator` registry fix (§6) with this merge** — same commit or an immediate fixup; G4 CI cannot pass without it.
2. G3 reviewer: reproduce the four commands (validator run; `.github/scripts` pytest; services/api pytest with/without the one-line fix; ruff base-vs-current diff).
3. Follow-up task (M2, builder side): emit `district_provenance`/`commercial_overlay_provenance`/`special_district_provenance` from the PLUTO `zonedist*/overlay*/spdist*` facts and extend `_assert_provenance_integrity` with the map rules — the contract and validator are ready for it.
4. Orchestrator decision: wire `python -m pytest .github/scripts/tests` into CI (either the `api` job with a path tweak or a new stdlib+pytest step); currently local-only.
5. Hygiene (optional, low priority): fix the 28 pre-existing ruff findings in `validate_contracts.py` in a dedicated no-behavior-change task.
