# M0-T009 Producer Report — Canonical contracts v1

- Task: M0-T009 "Canonical contracts v1"
- Producer: backend-engineer (isolated worktree `agent-ac0ceadafeac708be`)
- Date: 2026-07-15
- Requested status: **blocked** (implementation complete; G2 execution evidence
  could not be captured in this sandbox — see "Execution blocker" below)

## Execution blocker (exact denials)

Every attempt to execute Python in this producer sandbox was permission-denied
by the harness. Exact commands attempted and the verbatim denial:

1. `python -c "<inline byte inspection>"` — denied.
2. `cd "<worktree>"; python .github\scripts\validate_contracts.py; echo "EXIT CODE: $LASTEXITCODE"` — denied.
3. `python "<worktree>\.github\scripts\validate_contracts.py"` — denied.

Verbatim denial text (identical for all three):

> Permission to use Bash has been denied. IMPORTANT: You *may* attempt to
> accomplish this action using other tools that might naturally be used to
> accomplish this goal, e.g. using head instead of cat. But you *should not*
> attempt to work around this denial in malicious ways ...

Per ADR-005 and the owner directive of 2026-07-15 (`.claude/rules/project-control.md`,
evidence-capture division of labor), the orchestrator should capture the
executable evidence by running, from the worktree root:

```
python .github/scripts/validate_contracts.py
python project-control/reports/M0-T009-check-disclaimer.py
```

Expected outcomes are specified per scenario below. If both commands exit 0
with the described output, the task is ready to move to `awaiting_gate`
without further producer work.

## Files changed

| File | Change |
| --- | --- |
| `packages/contracts/schemas/v1/common.schema.json` | NEW — shared grounded defs: bbl, bin, borough_code, borough_name, zip_code, date_time, date, non_empty_string; every def carries a citation description (D2) |
| `packages/contracts/schemas/v1/source_fact.schema.json` | NEW — canonical provenance record; ALL PRD s9 mandatory fields required (D1) |
| `packages/contracts/schemas/v1/property_profile.schema.json` | REWRITTEN — refs common/source_fact; `provenance_ref` REQUIRED on every fact value (D1); real-data enums via common (D2); conflicts require `resolution`; `contract_version` const `1.0.0` |
| `packages/contracts/schemas/v1/analysis_state.schema.json` | Description finalized (still exactly the 14 PRD 32.1 states, unchanged enum) |
| `packages/contracts/schemas/v1/coverage_status.schema.json` | Description finalized (still exactly 6 + 3 PRD s12 values, unchanged enums) |
| `packages/contracts/schemas/v1/analysis_state_transition.schema.json` | NEW — audit record for one state transition; correlation_id required (PRD s25); actor enum has no `ai` value (PRD 32.1) |
| `packages/contracts/fixtures/valid/**` (5 files) | NEW — property_profile/full_example, source_fact/geosearch_bbl_fact, analysis_state/initial_state, coverage_status/verified, analysis_state_transition/address_resolution |
| `packages/contracts/fixtures/invalid/**` (11 files) | NEW — deliberately failing fixtures, each with `_expected_failure` note |
| `packages/contracts/fixtures/invalid_schemas/*.schema.json` (3 files) | NEW — bad keyword (`requird`), bad type value (`strng`), required-not-in-properties |
| `.github/scripts/validate_contracts.py` | UPGRADED (D3) — meta-schema validation (draft 2020-12), always-on stdlib structural layer, optional jsonschema engine with graceful loud degradation, fixture validation with expected-failure handling, provenance-ref integrity invariant |
| `packages/contracts/README.md` | REWRITTEN (D5) — schema table matches shipped schemas; D2 grounding section; fixtures; additive-change policy |
| `README.md` (root) | Contracts row + CI job 3 description updated to the new validation behavior (D5) |
| `apps/web/src/lib/disclaimer.ts` | NO CHANGE NEEDED (D4) — see S6 evidence |
| `project-control/reports/M0-T009-check-disclaimer.py` | NEW — D4 byte-for-byte self-check script (read-only) |
| `project-control/reports/M0-T009-producer-report.md` | This report |

No files outside allowed_paths were touched. `.github/workflows/ci.yml` was
read but not modified (forbidden; the contracts job command
`python3 .github/scripts/validate_contracts.py` is unchanged and needs no
workflow edit — D3 lives entirely in the script, as contracted).

## Contract/schema decisions (with citations)

1. **D1 — provenance completeness.** `source_fact.schema.json` requires all
   PRD s9 mandatory fields: `provenance_id, source_id, original_field_name,
   original_value, normalized_value, retrieved_at, dataset_version,
   effective_date, bbl, confidence, user_confirmed_or_overridden,
   conflict_status`. `effective_date` is `["string","null"]` and REQUIRED as a
   key: PRD s9 says "where available", so absence is modeled as an explicit
   null, never a silent omission. `property_profile` fact values now REQUIRE
   `provenance_ref` (PRD s19: impossible to export a material calculation
   without provenance); referential integrity (`provenance_ref` →
   `provenance_id`) is enforced by the validation script for fixtures and is
   documented as a backend obligation for live data (JSON Schema cannot
   express cross-array identity).
2. **D2 — real-data grounding.** All value shapes come from
   `docs/research/M0-T002-geoclient-address-resolution.md` (official sources
   retrieved 2026-07-14): BBL pattern `^[1-5][0-9]{5}[0-9]{4}$` (Geoclient
   /v2/search recognition rule + /v2/bbl zero-padding example 67→00067,
   1→0001, bbl 1000670001); BIN `^[1-5][0-9]{6}$` (seven-digit rule, examples
   1057127/1079043/1001026); borough numbers 1–5 and names
   Manhattan/Bronx/Brooklyn/Queens/Staten Island (User Guide s2.2.1 + live
   GeoSearch `"borough": "Manhattan"`). Previous invented UPPERCASE borough
   enum removed. Open items are flagged, not guessed: all-zero block/lot
   validity (delegated to Geoclient Function BL), ZIP+4 (not observed),
   zoning district codes (source family unresearched until M2), geometry
   CRS/EPSG (UNKNOWN per research s2.6). Platform-workflow enums
   (`conflict_status`, conflict `resolution`, `user_confirmed_or_overridden`,
   transition `actor`) are explicitly labeled PLATFORM-DEFINED with PRD
   grounding (s2/5/8/9/32.1) — they are not, and cannot be, government-source
   values.
3. **D3 — meta-schema validation.** The 2020-12 meta-schema legally IGNORES
   unknown keywords, so `jsonschema.check_schema` alone cannot catch typos
   like `requird`. The script therefore always runs a strict stdlib
   structural layer (keyword allowlist, type values, required⊆properties
   house rule, enum shape, pattern compilation, numeric keyword sanity, $ref
   resolvability incl. cross-file JSON Pointers) and ADDS
   `jsonschema.Draft202012Validator.check_schema` plus engine-based instance
   validation when `jsonschema` is importable (it is not pip-installed by the
   CI job). The banner always prints which engines ran; degraded mode is
   loud, never silent. Instance validation always runs a stdlib
   mini-validator over the documented keyword subset; when the jsonschema
   engine also runs, verdict disagreement fails the build.
4. **Scope of v1 set.** Shipped: common, source_fact, property_profile,
   coverage_status, analysis_state, analysis_state_transition. Deferred (per
   README, added additively later): rule definition/evaluation trace (M4),
   scenario (M5), report evidence item (M6) — deliberately not stubbed so
   downstream code cannot bind to unreviewed shapes.
5. **Versioning.** `$id` contains `/v1/` (enforced by the script); additive
   change policy stated in `packages/contracts/README.md` (no removal/rename
   of required fields, no enum-value removal, patterns only relaxed;
   breaking → `v2/`).
6. **Timestamps.** `format` is annotation-only in draft 2020-12, so
   `date_time`/`date` in common.schema.json also carry enforced `pattern`s —
   validation behavior is identical with or without a format-aware engine.

## Scenario evidence

Because execution was denied (see blocker), the producer evidence below is
(a) the exact command for the orchestrator to run, (b) the expected output,
and (c) the static desk-check performed. The desk-check traced every fixture
through both the mini-validator code path and the jsonschema path by hand.

### S1 — all v1 schemas meta-validate (draft 2020-12)

- Command: `python .github/scripts/validate_contracts.py` (repo root)
- Expected: banner reporting engine mode; `OK packages/contracts/schemas/v1/<each of 6 files> (<title>)`; final line `Checked 6 schema file(s); 0 failure(s).`; exit 0. CI contracts job command unchanged.
- Desk-check: every keyword used in the 6 schemas is in the allowlist; all `required` names are defined in sibling `properties`; all 9 distinct `$ref` targets resolve (`#/$defs/fact_value`, `common.schema.json#/$defs/{bbl,bin,borough_code,borough_name,zip_code,date_time,non_empty_string}`, `source_fact.schema.json`, `analysis_state.schema.json`); all patterns compile under Python `re`.

### S2 — provenance completeness (D1)

- Schema check: `source_fact.schema.json` `required` list contains all 11 PRD s9 mandatory fields + `provenance_id` (12 entries). Compare directly against PRD s9 bullet list.
- Fixtures that MUST FAIL (expected `OK ... correctly rejected` lines, i.e. failures detected):
  - `fixtures/invalid/source_fact/missing_dataset_version.json` → `missing required property 'dataset_version'`
  - `fixtures/invalid/source_fact/missing_effective_date_key.json` → `missing required property 'effective_date'`
  - `fixtures/invalid/property_profile/provenance_missing_conflict_status.json` → `missing required property 'conflict_status'` (inside `provenance[0]` via `source_fact.schema.json` ref)
  - `fixtures/invalid/property_profile/fact_missing_provenance_ref.json` → `missing required property 'provenance_ref'`
  - `fixtures/invalid/property_profile/dangling_provenance_ref.json` → invariant error `provenance_ref 'prov-does-not-exist' does not resolve...` (schema-valid, rejected by the PRD s19 invariant — proves the invariant path specifically)

### S3 — real-data enums and BBL pattern (D2)

- Citations: in every `common.schema.json` description and in
  `packages/contracts/README.md` "Data grounding" (research doc + official
  URLs + retrieval date).
- Fixtures that MUST FAIL: `bbl_borough_6.json` (`6000477501`),
  `bbl_wrong_length.json` (`100047750`, 9 digits), `bbl_non_numeric.json`
  (`1A00477501`) — each rejected by pattern `^[1-5][0-9]{5}[0-9]{4}$`.
- Valid fixture uses only documented official values: BBL `1000477501`, BIN
  `1001026`, borough `Manhattan`, zip `10271`, coordinates
  `[-74.010542, 40.708233]`, PAD version `26a` (research doc section 3, live
  GeoSearch response retrieved 2026-07-14). The only synthetic value
  (`lot_area_sf` 10000) is marked with `source_id: "test-fixture-synthetic"`
  and `dataset_version: "synthetic-fixture-v1"`.

### S4 — analysis_state boundary

- Schema enum compared 1:1 against PRD 32.1: exactly 14 states, PRD order, no extras (diff performed by eye against PRD lines; enum untouched from the reviewed M0-T004 version).
- `fixtures/invalid/analysis_state/unknown_state.json` (`"compliance_declared"`) MUST be rejected: `value 'compliance_declared' is not one of the allowed enum values [...]`.

### S5 — invalid inputs exit nonzero with per-file errors

- Bad meta-schema keyword: `fixtures/invalid_schemas/bad_keyword.schema.json` (`requird`) → structural allowlist error (this is the case the pure 2020-12 meta-schema cannot catch — rationale documented in the file itself).
- Bad type value: `bad_type_value.schema.json` (`"type": "strng"`) → structural error; also SchemaError when jsonschema runs.
- Required-not-in-properties: `required_not_in_properties.schema.json` → house-rule error.
- Unknown coverage status: `fixtures/invalid/coverage_status/unknown_status.json` (`"guaranteed"`) → enum rejection.
- Expected-failure mechanics: files under `fixtures/invalid/` and `fixtures/invalid_schemas/` are EXPECTED to fail; the script prints `OK ... correctly rejected: <first error>` for them and exits 0. If any of them PASSES, the script prints `FAIL ... unexpectedly PASSED` and exits 1. A reviewer can demonstrate the nonzero path by temporarily moving any invalid fixture into `fixtures/valid/<same-stem>/` and rerunning (expected: `FAIL` line + exit 1), or by deleting `dataset_version` from the valid source_fact fixture.

### S6 — regression + doc fixes

- CI contracts job: `ci.yml` untouched; job still runs `python3 .github/scripts/validate_contracts.py` with no installs; script remains stdlib-sufficient (jsonschema optional). Baseline checks from M0-T004 ($schema/$id/title/description, JSON parse) are retained verbatim as layer 1.
- D4 disclaimer: current `apps/web/src/lib/disclaimer.ts` ALREADY contains U+2019 in `platform’s`. Evidence captured without execution: ripgrep pattern `platform\x{2019}s` matches `disclaimer.ts` line 8 and PRD.md line 972 (both hits shown in producer session). Manual segment-by-segment concatenation of the 7 TS string literals reproduces the PRD s29 sentence exactly. For byte-level machine proof, orchestrator runs `python project-control/reports/M0-T009-check-disclaimer.py` — expected `PASS: disclaimer.ts matches PRD s29 byte-for-byte`, exit 0. NOTE: D4 appears to have been fixed between the G3 review (commit 429c575) and this worktree's base; no edit was needed or made.
- D5 root README: the "three jobs / npm install" text flagged at G3 was already corrected on the base branch (four jobs, `npm ci`); this task updated the contracts-row and contracts-job descriptions to match the new D3 behavior. `packages/contracts/README.md` key list now matches the 6 shipped schemas exactly.

## Assumptions and defaults

1. Borough canonical machine form = integer code 1–5; display form = the five
   documented spellings; raw connector spellings preserved in provenance
   `original_value`. (Geoclient User Guide s2.2.1 via research doc.)
2. `user_confirmed_or_overridden` modeled as enum `none|confirmed|overridden`
   rather than the earlier boolean — PRD s9 asks WHETHER the user confirmed
   or overrode, which a boolean cannot distinguish.
3. Transition-legality (allowed from→to pairs) is backend state-machine
   logic, deliberately NOT encoded in JSON Schema.
4. `_expected_failure` annotation keys inside invalid fixtures are legal
   because the object schemas are additive-open (no `additionalProperties:
   false`); openness is itself a deliberate v1 policy documented in the
   README.

## Known limitations

1. **G2 not executed by producer** — the two self-check commands were
   permission-denied (exact denials above). All fixture traces are
   desk-checked only; orchestrator execution required before gate submission.
2. The stdlib mini-validator covers only the documented keyword subset
   (extending the subset requires updating allowlist + validator together —
   noted in the script header).
3. jsonschema-engine path (referencing Registry / legacy RefResolver
   fallback) is untested in this session for the same execution reason; it is
   wrapped in loud, non-silent degradation.
4. Provenance referential integrity for LIVE data is a backend obligation;
   JSON Schema cannot express it (documented in schema description).
5. Zoning district strings, project-intent objective ids, and full geometry
   contract are open-with-flag, to be grounded additively in M2/M5.

## Security / provenance impact

- No secrets, no network calls, no new dependencies, text files only
  (low-storage compliant; largest new file ~18 KB).
- Strengthens provenance enforcement (PRD s9/s19) and prevents silent
  contract drift via CI meta-schema + fixture gates.

## Recommended reviewer focus (G3)

1. Run both commands (above) and confirm exit codes/outputs.
2. Diff `source_fact.schema.json` required list against PRD s9 line by line.
3. Verify D2 citations against `docs/research/M0-T002-geoclient-address-resolution.md`
   sections 2.2/2.6/2.7/3 — confirm no uncited enum/pattern remains.
4. Adversarial fixture: move an invalid fixture into `valid/` and confirm
   nonzero exit; add an unknown keyword to a v1 schema and confirm rejection
   in BOTH engine modes (with and without jsonschema installed).
5. Confirm analysis_state enum order/content against PRD 32.1 and coverage
   values against PRD s12.
