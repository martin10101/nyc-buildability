# M4-T011 producer report — family-expansion consumer-test adaptation

Producer: qa-engineer/orchestrator. One bounded change; ENGINEERING_RELIABILITY_STANDARD §2
(owning boundary: the four api acceptance packs' trace/group selection), §3 (red/green below).

## What was changed (four modules, selection only — every expected VALUE untouched)

1. A module-local `_applicable_trace(rule_eval)` helper in `test_rule_evaluation_api.py`,
   `test_scenario_api.py`, `test_scenario_analysis_api.py`, and `test_evidence_api.py` (which
   also gains `_applicable_group(doc)` for `rule_citations`): selects the SINGLE evaluation
   whose `applicability_outcome is True`, asserting exactly one (zero or several fails loudly
   with the offending rule_ids — never a silent `[0]`).
2. The six CI-failing sites now select by applicability instead of position:
   - `test_rule_evaluation_api.py` `test_as3_confident_supported_family_is_200_draft` and
     `test_m2t020_s2_flag_on_live_substrate_reaches_evaluation_via_default_seam`:
     `len(evaluations) == 1` → `len(evaluations) == len(family_coverage["rule_ids"])` (the
     document's own family list — never a hardcoded 5 that rots on the next expansion; S4),
     `evaluations[0]` → `_applicable_trace(doc)`.
   - `test_evidence_api.py` AS-1/AS-2: `rule_citations[0]` → `_applicable_group(doc)`;
     `evaluations[0]` → `_applicable_trace(rule_eval)`. The AS-2 group↔trace zip comparison is
     untouched (order-preserving 5↔5 by construction of the evidence endpoint).
   - `test_scenario_api.py` / `test_scenario_analysis_api.py` AS-1: `evaluations[0]` →
     `_applicable_trace(rule_eval)` for the verbatim-cap read.
3. NOTHING else: no production code (forbidden by the packet — production selection was
   verified correct before contracting: `app/rules/integration.py` aggregates applicable
   traces; `app/scenario/builder.py::_find_residential_far_trace` selects the first applicable
   trace), no other test module, no value/coverage/citation/provenance expectation changed.

## Red/green record (§3.1)

RED (recorded BEFORE this packet existed, at 032dffe7): CI run 34664497740 api job —
**6 failed, 2956 passed** (the six sites above, KeyError 'max_residential_floor_area_sq_ft' /
`assert 5 == 1`), duplicated in exact-production-install; reproduced locally:
`python -m pytest tests/api -q` → **6 failed, 365 passed**.

GREEN (after the adaptation): `python -m pytest services/api/tests/api -q` → **371 passed**
(365 + the 6 repaired); `python -m pytest tests -q --ignore=tests/documents` → **1831 passed,
1 failed** where the single failure is `test_serializer_imported_exactly_at_the_profile_write_
boundary` AST-parsing a PEP 695 source on the LOCAL 3.11 sandbox (the recorded M2-T015
environment limitation — it passed on CI 3.12 at 032dffe7 and is untouched by this diff), and
`tests/documents` is excluded for the same 3.11 collection limitation (15 modules). CI on the
pushed head is the execution authority for the full 2962. `ruff check services/api/tests/api` →
All checks passed; `python tools/modularity_check.py --check` → exit 0.

## Non-failing observations deliberately NOT touched (scope discipline)

- `test_rule_evaluation_api.py:392-area` (`evaluations[0]["outputs"] == {}` in a missing-input
  case) and `test_evidence_api.py:1108` (`len(rule_citations) == len(evaluations)`) pass under
  the five-member family; the first is positionally fragile in principle but asserts a property
  that holds for EVERY family member on that path (no inputs → no outputs anywhere). Left
  untouched per the packet's six-failure scope; recorded here so the reviewer sees them judged,
  not missed.
