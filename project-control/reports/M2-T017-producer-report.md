# M2-T017 — Producer Report

**Task:** M2-T017 — Canonical `source_fact` and `analysis_state_transition` contract hardening (DF-4/DF-5, whole-system trust replan Area G).
**Role:** Producer (not controller). No merge/accept/replan; one PR against `main`; serializer NOT wired.
**Branch:** `task/M2-T017-contract-hardening` · **Base SHA:** `cc142081336f2dac0854a947694fec33559dcc8a` (post-D-002-consolidation main, M0-T024).
**Directive:** D-002 (regime v1.0; `D-002:ALL`).
**Dependencies:** M2-T003 (accepted; defined these contracts). No first-wave sibling dependency.

---

## 1. Outcome

Both canonical records are now CLOSED with `additionalProperties:false`, so a mandatory provenance/audit record can no longer silently accept an undocumented or mistyped key. A frozen, un-wired allowlist serializer enforces the same discipline at the (future) write boundary. All acceptance scenarios AS-1..AS-6 have executable evidence below; every changed path is inside `allowed_paths`; no forbidden path was touched.

## 2. Key finding + decision (READ THIS FIRST)

The task/replan risk note assumed `builder.py`'s provenance assembly was "already allowlist-based," i.e. that closing `source_fact` with a bare `additionalProperties:false` would break nothing. **That assumption is incomplete.** The accepted connectors deliberately emit lineage keys BEYOND the documented `source_fact` v1/M2-T004 property set, each with an in-code comment that explicitly relies on `source_fact` being an OPEN contract:

| Key | Emitted by (file:line) | Meaning (from code) |
|---|---|---|
| `dataset_id` | `pluto_soda.py:838`, `ztldb_soda.py:1425` | Socrata dataset 4x4 token (PLUTO `64uk-42ks`, ZTLDB `fdkv-4t4z`) |
| `request_url` | `pluto_soda.py:839`, `ztldb_soda.py:1426` | exact official request URL (secrets travel in headers, never here) |
| `input_vintages` | `pluto_soda.py:840` (PLUTO only) | map of PLUTO `VINTAGE_DATE_COLUMNS` present in the record → verbatim values |
| `source_rows_updated_at` | `ztldb_soda.py:1433` (ZTLDB only) | ZTLDB official `rowsUpdatedAt` RFC3339 timestamp (dataset-version freshness) |

The at-risk evidence: the committed valid fixture `packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json` (NOT in my allowed paths) embeds **84** provenance records each carrying `dataset_id`, `input_vintages`, `request_url`. A blanket `additionalProperties:false` would reject that fixture and, more importantly, real accepted-connector output.

**Decision — document-then-close (in scope, non-breaking):** rather than (a) blindly rejecting real production output, or (b) invoking the stop-condition (which applies only when closing *forces a change to a shared production entrypoint/builder* — it does not here), I documented the four connector-emitted lineage keys as OPTIONAL `source_fact` properties (the schema is mine to own), then closed with `additionalProperties:false`. This fully satisfies DF-4/DF-5 (no key is silently accepted; every accepted key is now explicitly documented; typos and diagnostic leaks are rejected) while touching zero forbidden files and breaking zero conformant records. The objective explicitly permits "`additionalProperties:false`, or a single versioned `extensions` object"; a nested `extensions` object was rejected because it would require changing the connectors (forbidden + breaking). Versioning: the file must stay at `v1/source_fact.schema.json` because the forbidden `property_profile.schema.json` `$ref`s it by filename; this is an in-place v1 hardening (additive in documented keys, restrictive only against genuinely-undocumented keys), recorded in the schema `description`. A v2 `$id`/file split is impossible without editing forbidden files and is therefore out of scope.

## 3. Deliverables (all within `allowed_paths`)

- `packages/contracts/schemas/v1/source_fact.schema.json` — 4 new optional documented properties + `additionalProperties:false` + hardening note (21 properties, 12 required, closed).
- `packages/contracts/schemas/v1/analysis_state_transition.schema.json` — `additionalProperties:false` + hardening note.
- `packages/contracts/generated/property_profile.ts` — regenerated (SourceFact gains 4 optional fields). **Sole owner this wave.**
- `services/api/app/_contract_schemas/v1/source_fact.schema.json` — byte-identical runtime bundle copy.
- `packages/contracts/fixtures/{invalid,valid}/{source_fact,analysis_state_transition}/**` — 6 negative + 3 positive fixtures (below).
- `services/api/app/contracts/{__init__.py,serializers.py}` — NEW frozen allowlist serializer (NOT wired).
- `services/api/tests/contracts/{test_closed_contracts.py,test_contract_serializers.py}` — negative + serializer tests.
- `project-control/reports/M2-T017-producer-report.md` — this report.

New fixtures:
- invalid/source_fact: `undocumented_field_rejected`, `typo_optional_field_rejected` (typo of optional `units`→`unit`), `diagnostic_leak_rejected`.
- invalid/analysis_state_transition: `undocumented_field_rejected`, `typo_optional_field_rejected` (`reason`→`resason`), `diagnostic_leak_rejected`.
- valid/source_fact: `pluto_full_lineage_fact` (all documented keys incl. the 4 lineage keys + internally-consistent canonical digests), `ztldb_lineage_fact` (proves `source_rows_updated_at` accepted).
- valid/analysis_state_transition: `initial_transition_null_from_state` (`from_state:null` initial transition).

## 4. Gate evidence (producer self-check; independent gates run by reviewers)

### G0 — scope / in-regime / plan
- In-regime task (`directive_refs: D-002:ALL`, `directive_regime_version 1.0`).
- `git status` changed-file set is a strict subset of `allowed_paths` (verified precisely; no `app/api/**`, `app/profile/builder.py`, `app/rules/**`, `packages/contracts/scripts/**`, other canonical schemas, `rule_evaluation.ts`/`scenario.ts`, `.github/**`, `.claude/**`, `tools/**`, `render.yaml`, `apps/web/**`, `CLAUDE.md`).

### G2 — producer self-check (tests) — all green
```
services/api tests/contracts/           65 passed
services/api tests/profile tests/connectors tests/api   498 passed
packages/contracts/scripts/tests/       24 passed
ruff check app/contracts + tests/contracts   All checks passed
```
The 498-count run is the critical regression surface: it builds real PLUTO/ZTLDB/wave profiles and validates them against the now-closed `source_fact` (via `property_profile`) — all pass, proving the close does not reject real production output.

### G3 — contract / data verification (executable)
- `python .github/scripts/validate_contracts.py` → **0 failures** (stdlib mini-validator + jsonschema cross-checked, no disagreements). Every valid fixture passes (incl. `builder_output_m1_t005.json`); every invalid fixture is rejected.
- Load-bearing proof (DF-4/DF-5): with `additionalProperties:false` an OPTIONAL-field typo (`unit`), an unknown key (`actor_ip`), and a diagnostic leak (`_debug_*`) are REJECTED; an otherwise-identical OPEN variant ACCEPTS them (`test_*_only_caught_by_close`). Documented lineage keys are ACCEPTED.

### G4 — CI-reproducible drift checks (exact CI commands)
```
python packages/contracts/scripts/generate_ts_types.py --check   → rc=0 (property_profile/client-block/rule_eval/scenario all up to date)
python services/api/scripts/sync_contract_schemas.py --check      → rc=0 (bundle byte-identical to canonical)
python .github/scripts/validate_contracts.py                      → rc=0
```
`property_profile.ts` committed blob is LF (repo stores LF; my diff is +6 lines only), so the CI byte-identity `--check` reproduces on the Linux runner.

### G5 — security / privacy
- **Diagnostic-leak safety:** the serializer rejects unknown keys and names offending KEYS only, never their VALUES (`test_unknown_field_error_never_echoes_the_value`, `test_multiple_unknown_keys_reported_sorted_names_only`) — a leaked stack trace / token can never travel out through the exception/log. `additionalProperties:false` blocks leaked diagnostic fields from being persisted into provenance/audit records.
- **No secrets in provenance:** `request_url` is documented as header-carried-secrets-only (mirrors `reproducibility.request_url`).
- **Serializer NOT wired (AS-4):** `test_serializer_not_imported_by_any_production_module` scans `services/api/app/**` (excluding `app/contracts/`) and asserts zero imports of the serializer.
- **No new dependencies**, stdlib-only serializer, no network, thin-client compliant.

## 5. Acceptance scenarios
- **AS-1** ✓ negative fixtures FAIL, positives PASS (validate_contracts 0 failures; contract tests).
- **AS-2** ✓ `sync_contract_schemas.py --check` + `generate_ts_types.py --check` byte-identical (rc=0); `property_profile.ts` regenerated (source_fact changed it) and committed.
- **AS-3** ✓ serializer rejects unknown keys, round-trips only documented fields, diagnostic-leak tests pass.
- **AS-4** ✓ serializer is a frozen interface; not imported by route/builder (regression test).
- **AS-5** ✓ no other canonical contract / generated artifact / schema modified (precise changed-file audit).
- **AS-6** ✓ G0/G2/G3/G4/G5 evidence in this report.

## 6. Contract / interface impact
- `source_fact` vNext: v1 in-place hardening — +4 documented optional lineage keys, closed with `additionalProperties:false`. `$id`/path unchanged (v1).
- `analysis_state_transition` vNext: v1 in-place hardening — closed with `additionalProperties:false`. No writer exists yet.
- `property_profile.ts` regenerated: **YES** (SourceFact +4 optional fields). No other generated artifact changed.
- `services/api/app/contracts/serializers.py`: NEW frozen interface (`SOURCE_FACT_SERIALIZER`, `ANALYSIS_STATE_TRANSITION_SERIALIZER`).

## 7. Risks / limitations
- The inner shape of `input_vintages` is intentionally left open (source-driven date-column names are never guessed into a closed set); only the TOP-LEVEL record is closed. This is the correct DF-4 boundary.
- The serializer performs KEY-level (allowlist) enforcement only; VALUE-level validation remains the JSON-schema validator's job (documented in the module).
- Local pytest is 8.4.2 (CI locks 9.0.3) and jsonschema 4.26 — CI uses the hash-pinned lock; results reproduce.

## 8. Next dependency unlocked
A later controller-contracted integration task wires `services/api/app/contracts/serializers.py` into `services/api/app/profile/builder.py` (schema-before-integration order; FIRST-WAVE-INTEGRATION-CONTRACT.md lane 3 downstream). No shared-entrypoint wiring happens in this producer task.

**Producer status after PR:** idle (awaiting independent gates G3/G4/G5 by reviewers + orchestrator acceptance).
