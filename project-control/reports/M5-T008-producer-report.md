# M5-T008 PRODUCER OUTPUT RECORD — deterministic single-assumption sensitivity/what-if analysis

> **Authorship note:** the worker (scenario-optimization-engineer, run persistent-local-24) built the
> code + tests to UNIT_COMPLETE (audit seq 320) and stopped cleanly at `--max-tasks 1` **without over-revision
> (no codex-review cycle this run)** and did not author a separate producer report. This record is written by
> the **orchestrator** to document the delivered output and the reproduced evidence for the gate wave. It is a
> record of producer output, not a review; the independent G1/G3/G4/G5 + DCV wave (reviewers ≠ producer) verify.

## What was delivered (allowed_paths only)

| File | Change |
|---|---|
| `services/api/app/scenario/sensitivity.py` | **new, 705 lines** — the feature |
| `services/api/app/scenario/__init__.py` | edited — **additive** facade export (`SENSITIVITY_LABEL`, `SENSITIVITY_RESPONSE_METRIC`, `SensitivityKind`, `SensitivityVariable`, `analyze_scenario_sensitivity`); no existing export changed |
| `services/api/tests/scenario/test_scenario_sensitivity.py` | **new, 507 lines** — 25 test functions → **49 parametrized items** |
| `project-control/reports/M5-T008-producer-report.md` | this record |

**No forbidden path touched** — `builder.py`/`models.py`/`constants.py`/`contract.py`/**`derive.py`**/**`ranking.py`**/`packages/contracts/**` all unmodified and consumed READ-ONLY (`git diff --name-only` = the 4 files above only).

## What it is

Public function `analyze_scenario_sensitivity(...)` (`sensitivity.py:585`) plus its typed vocabulary
(`SensitivityVariable` @:84, `SensitivityKind` @:100, `SENSITIVITY_LABEL`, `SENSITIVITY_RESPONSE_METRIC`),
exported from `app.scenario`. It varies ONE explicitly-named assumption (`SensitivityVariable`, e.g.
utilization_factor / efficiency_ratio) across an EXPLICIT caller-provided list of values, runs each through the
accepted `derive_practical_usable_range` (M5-T005/T006) READ-ONLY, and returns an ordered response of illustrative
usable-area points with a transparent per-point breakdown. Contract-free (a new object; never the canonical
scenario contract; never stored/presented as Verified).

## Hard boundaries (mapped to tests)

The 7 acceptance scenarios map to real tests in `test_scenario_sensitivity.py`:
- **AS-1** deterministic stable order — `test_as1_points_ordered_by_tried_value_ascending`, `test_as1_byte_identical_across_input_reorderings_and_duplicates`, `test_as1_identical_input_is_byte_identical`.
- **AS-2** named variable + transparent components — `test_as2_names_variable_and_metric_and_transparent_components`, `test_as2_no_point_emitted_without_naming_the_variable`.
- **AS-3** explicit-values-only / never fabricates — `test_as3_one_point_per_supplied_value_never_fabricates`, `test_as3_empty_values_returns_single_baseline_point_not_a_fabrication`, `test_as3_not_derivable_value_is_kept_in_value_order_not_relocated`.
- **AS-4** fail-closed + strict-JSON-safe — `test_as4_*` (unknown/malformed variable, no-cap empty, malformed container, degenerate doc, malformed value, unserializable object, huge-int overflow, object dict-key).
- **AS-5** never up-labels / never Verified — `test_as5_response_is_never_verified_and_honestly_labelled`, `test_as5_incoming_verified_coverage_is_capped_to_conditional`, `test_as5_literal_verified_variable_is_invalid_and_never_emitted`.
- **AS-6** read-only, no recompute — `test_as6_inputs_are_byte_unchanged_and_not_aliased`, `test_as6_point_uses_only_surfaced_numbers_no_recompute`.
- **AS-7** strict-JSON-safe + consumes derive + full regression — `test_as7_response_output_is_strict_json_safe`, `test_as7_consumes_derive_breakdown_for_every_derivable_point`, `test_as7_efficiency_ratio_variable_also_works`.

## Evidence (orchestrator-reproduced)

- **Command (documented):** `python -m pytest services/api/tests/scenario` → **222 passed** (173 pre-existing + **49 new sensitivity items**), 0 regression. Reproduced by the orchestrator in `wt-m5t008` at the producer output.
- **Imports** (`sensitivity.py:57-66`): `__future__`, `copy`, `json`, `math`, `enum.Enum`, `typing.Any`, `.constants.NOT_VERIFIED_DISCLAIMER`, `.derive` — no network/storage/env/file/subprocess. Negative grep `supabase|geoclient|requests|httpx|socket|urllib|os.environ|getenv|subprocess|open(` → no matches. Offline, no credentials.
- **No producer commit** — the orchestrator commits the working tree at the gate (ADR-005).

The orchestrator did NOT self-accept; evidence is submitted for the independent G0/G1/G3/G4/G5 gate wave + D-038 DCV.
