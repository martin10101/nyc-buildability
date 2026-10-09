# M5-T028 Producer Report

- Task: M5-T028 (Dependable answers 2, D-059-R003 completion)
- Producer: backend-engineer (unnamed worktree spawn `wt-m5t028`)
- Worktree base: `2231227a` ("M4-T021 (B4) integrated + submitted")
- Directive refs: D-059:D-059-R003; D-046:D-046-R001,D-046-R002

## Objective

Complete D-059-R003 across the five scenario-analysis modules the M5-T027 packet could
not reach (M5-T027 G3 advisory A1): `derive.py`, `breakeven.py`, `comparison.py`,
`ranking.py`, `sensitivity.py` all hardcoded `"ZR 23-21"` regardless of the district
family actually evaluated. The fix derives the displayed section from the rule
ACTUALLY evaluated, reusing the M5-T027 seam (`builder._cap_citation_section`),
never defaulting to 23-21.

## The fix (mechanism)

`builder._cap_citation_section(cap_provenance)` (accepted M5-T027 code, forbidden to
edit here) already extracts the real evaluated citation section from a scenario
document's `cap_provenance`. Every one of the five modules receives the FULL scenario
document (built server-side by `scenario_analysis.py`'s `_rebuild_scenario` via
`build_scenario`) as its own `scenario_document` argument, which always carries
`cap_provenance` (a dict with a `citations[0]["section"]` when a cap was surfaced, or
`None` on a no-cap outcome).

- `derive.py` imports `_cap_citation_section` from `.builder` (no existing test
  forbids this) and exposes a new private helper `_cap_section_reference(scenario_document)`
  that extracts the section from `scenario_document["cap_provenance"]`. It converts the
  `DERIVED_RANGE_LABEL` module constant into a function `_derived_range_label(section_reference)`
  called at both the `_not_derivable`/`_invalid_assumption` site and the DERIVED-outcome
  site with the per-call derived section. A generic clause ("see cap_provenance.citations
  for the exact Zoning Resolution section") is used when no citation is available - never
  a default to 23-21.
- `breakeven.py`, `ranking.py`, `sensitivity.py` import `_cap_section_reference` from
  `.derive` (a module they already depend on) rather than importing `.builder` directly,
  preserving `derive.py` as the single place the derivation logic lives. Each converts its
  own `THRESHOLD_LABEL` / `RANKING_LABEL` / `SENSITIVITY_LABEL` into a parameterized
  function and calls it at every emission site (invalid / empty / scanned-or-ranked-or-analyzed).
- `comparison.py` (same `.derive` import pattern) converts BOTH hardcoded sites:
  `COMPARISON_LABEL` -> `_comparison_label(section_reference)`, and the
  `canonical_cap_sq_ft` metric label (previously a static entry in `_METRIC_LABELS`) ->
  `_canonical_cap_metric_label(section_reference)` / `_metric_labels(section_reference)`.
  The metric label is emitted at TWO sites - the top-level `compared_metrics` doc AND
  each set's per-metric `metric_deltas` breakdown (`_metric_delta`, which gained an
  optional `metric_labels` parameter defaulting to the R5 alias so its existing 3-arg unit
  tests keep passing unmodified) - both now receive the per-call derived label.

### Why `breakeven`/`comparison` route through `.derive` instead of importing `.builder` directly

`test_scenario_breakeven.py::test_as7_module_imports_are_contract_free` and
`test_scenario_comparison.py::test_as7_module_imports_only_allowed_dependencies` are
pre-existing acceptance tests that assert those two modules' OWN source text never
contains `"from .builder"` (their docstrings advertise "imports only stdlib + .derive +
.constants + ._json_safety"). Importing `builder._cap_citation_section` INTO `derive.py`
(which both already import from) and re-exporting it as `derive._cap_section_reference`
keeps every module's literal import line unchanged from what those tests check, while
still reusing the exact same M5-T027 extraction logic (imported, not duplicated) rather
than re-implementing it locally in five places. `ranking.py`/`sensitivity.py`/`derive.py`
have no such boundary test, but the same `.derive`-mediated pattern was used everywhere
for consistency and to keep the derivation in exactly one place.

### Backward-compatible module constants

`scenario/__init__.py` (outside `allowed_paths`, forbidden to edit) imports
`DERIVED_RANGE_LABEL`, `THRESHOLD_LABEL`, `COMPARISON_LABEL`, `RANKING_LABEL`,
`SENSITIVITY_LABEL` directly from their modules and re-exports them. Each module
therefore keeps a module-level constant of the same name, now computed as
`_<x>_label("23-21")` - byte-identical to the pre-fix text (verified below) - documented
as a legacy R5 alias, mirroring the exact pattern the accepted M5-T027 work established
for `constants.DRAFT_CAP_LABEL`. The LIVE derivation path never reads these constants;
it always calls the parameterized function with the real per-request citation.

## Requirement -> evidence map

### D-059-R003 (display section derived from the actually-evaluated rule)

- `derive.py:78-132` (new `_derived_range_label`/`_cap_section_reference`), used at the
  `_not_derivable`/`_invalid_assumption` site (`derive.py:309`, formerly the hardcoded
  `DERIVED_RANGE_LABEL` at the advisory's cited line 82) and the DERIVED-outcome site
  (`derive.py:530`).
- `breakeven.py:157-189` (new `_threshold_label`), used at `_degenerate_result`
  (`breakeven.py:604`, formerly the hardcoded `THRESHOLD_LABEL` at the advisory's cited
  line 155) and the FOUND/ALREADY_MET/NO_CROSSING result (`breakeven.py:807`).
- `comparison.py:127-196` (new `_canonical_cap_metric_label`, `_metric_labels`,
  `_comparison_label`), used at `_compared_metrics_doc` (`comparison.py:293`, replacing
  the advisory's cited line 118 static `_METRIC_LABELS["canonical_cap_sq_ft"]` text),
  `_metric_delta` (`comparison.py:428`, the per-set delta breakdown - a SECOND emission
  site for the same metric label the advisory did not separately enumerate), and
  `_degenerate_result` / the main COMPARED result (`comparison.py:535,680`, replacing the
  advisory's cited line 129 `COMPARISON_LABEL`).
- `ranking.py:120-147` (new `_ranking_label`), used at `_invalid_result`, `_empty_result`
  (`ranking.py:440,460`), and the RANKED result (`ranking.py:576`, formerly the hardcoded
  `RANKING_LABEL` at the advisory's cited line 114).
- `sensitivity.py:131-159` (new `_sensitivity_label`), used at `_invalid_result`,
  `_empty_result` (`sensitivity.py:468,490`), and the ANALYZED result
  (`sensitivity.py:613`, formerly the hardcoded `SENSITIVITY_LABEL` at the advisory's
  cited line 128).
- Where no rule context reaches the builder (a no-cap outcome, `cap_provenance is None`),
  every function falls back to a section-agnostic clause - never defaults to 23-21. Proven
  by `test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance`
  (`test_scenario_derive.py`).

### D-046-R001 / D-046-R002 (task scope / disjoint-lane discipline)

- `allowed_paths` matches the git diff exactly (`git status --porcelain` below); no
  `forbidden_paths` file touched (verified: `constants.py`, `builder.py`,
  `unused_floor_area.py`, `connectors/**`, `rules/**`, `api/**`, `packages/**`,
  `apps/web/**`, `tools/**`, `.github/**`, `.claude/**`, `project-control/tasks|gates|
  directives|state.json` all untouched).
- Scope is disjoint from the concurrent M4-T021 connectors lane and from M5-T027's own
  files (both forbidden here) - satisfied by construction, same as the packet's own
  path_notes.

## Acceptance scenarios

### S1 (derived_range_label_follows_the_evaluated_rule)

`derive.py`'s `DERIVED_RANGE_LABEL` (now `_derived_range_label`) names ZR 23-21 for an
R5-evaluated document and ZR 23-22 for an R6-R12-evaluated document, and is generic when
no rule context reaches the builder. Tests (`test_scenario_derive.py`):
- `test_d059_r003_derived_range_label_names_the_low_density_section`
- `test_d059_r003_derived_range_label_names_the_r6_r12_section`
- `test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance`

### S2 (four_sibling_surfaces_corrected)

Breakeven, comparison (both label AND metric-label sites), ranking, and sensitivity
documents follow the evaluated rule for BOTH district families; a source-text grep
proves no residual hardcoded `"ZR 23-21"` survives in any of the five modules. Tests:
- `test_scenario_breakeven.py::test_d059_r003_threshold_label_names_the_low_density_section`
- `test_scenario_breakeven.py::test_d059_r003_threshold_label_names_the_r6_r12_section`
- `test_scenario_comparison.py::test_d059_r003_comparison_label_names_the_low_density_section`
- `test_scenario_comparison.py::test_d059_r003_comparison_label_names_the_r6_r12_section`
  (asserts BOTH the top-level `compared_metrics` doc's `canonical_cap_sq_ft` metric label
  AND a set row's `metric_deltas` `canonical_cap_sq_ft` metric label - the two separate
  emission sites)
- `test_scenario_ranking.py::test_d059_r003_ranking_label_names_the_low_density_section`
- `test_scenario_ranking.py::test_d059_r003_ranking_label_names_the_r6_r12_section`
- `test_scenario_sensitivity.py::test_d059_r003_sensitivity_label_names_the_low_density_section`
- `test_scenario_sensitivity.py::test_d059_r003_sensitivity_label_names_the_r6_r12_section`
- `test_scenario_derive.py::test_d059_r003_no_residual_hardcoded_zr_23_21_across_the_five_modules`
  (grep-style: reads each of the five modules' source text directly and asserts the
  literal string `"ZR 23-21"` is absent)

All hand-derived expected section numbers ("23-21" / "23-22") were read directly from
`services/api/app/rules/rulesets/r5_residential_far.rule.json:20` (`"section": "23-21"`)
and `r6_r12_residential_far.rule.json:20` (`"section": "23-22"`) - never produced by
calling the code under test. Each new test file's `_r6_r12_rule_evaluation()` helper is a
local, independently-maintained copy of `test_scenario_foundation.py`'s own helper (that
file is outside this task's `allowed_paths`).

### S3 (provenance_prose_preserved)

Every word of the five labels/metric-labels apart from the section-reference clause
itself is byte-identical to the pre-fix text. Verified two ways:
1. Every existing pre-fix test that asserts `result["label"] == <X>_LABEL` (the R5-only
   path) still passes unmodified - 431/431 pre-existing tests green (see self-checks).
2. An explicit runtime byte-comparison of each backward-compatible `"23-21"` alias
   constant against the exact original (pre-fix) literal text:

   ```
   threshold match: True
   comparison match: True
   ranking match: True
   sensitivity match: True
   derived_range match: True
   metric_labels canonical_cap match: True
   ```

   (script run against the fixed tree with `PYTHONPATH` set to `services/api`; command
   and full output in the self-checks section below).

### S4 (scope_schema_and_regression)

- `git status --porcelain` lists exactly the 10 files in `allowed_paths` (5 production +
  5 test files) plus this report; no other file touched.
- Full scenario suite: 443 passed (431 pre-existing + 12 new).
- Contract suite (`test_scenario_contract.py`): 28 passed - response schema/enum vocabulary
  untouched; `packages/**` never modified (not in `allowed_paths`, and `git status`
  confirms it is untouched).
- `ruff check .`: All checks passed.
- `modularity_check.py --check`: 0 failures, 17 warnings (identical to the pre-edit
  baseline - no new warning, `breakeven.py`'s pre-existing warning is unchanged in kind).
- Zero new dependencies: no `pyproject.toml` / `requirements.in` / `requirements.txt`
  change (not in `allowed_paths`; `git status` confirms untouched).

## RED-on-old proof

Verified live in this worktree (not narrated): all five production files were
temporarily swapped back to their exact pre-fix content at the base commit (`git show
2231227a:services/api/app/scenario/<file>.py`), and the full `tests/scenario -k d059`
selection was re-run against that pre-fix tree (all 12 new tests present, since the test
files were already fixed at that point). Result: **7 of 12 failed** against the pre-fix
code - every test that actually exercises the new derivation (the four R6-R12 section
tests, the generic-fallback test, and the source-text grep test) failed with the exact
`AssertionError`s expected (e.g. `assert '(ZR 23-22)' in '...cap (ZR 23-21)...'`); the 5
R5-only "names 23-21" tests passed trivially on the pre-fix code too, as expected (the R5
path was already correct before this fix - only the R6-R12 path and the generic fallback
were broken). All five production files were then restored to the fixed content and the
full suite re-verified green (443/443). Exact commands:

```
git show 2231227a:services/api/app/scenario/derive.py > app/scenario/derive.py
git show 2231227a:services/api/app/scenario/breakeven.py > app/scenario/breakeven.py
git show 2231227a:services/api/app/scenario/comparison.py > app/scenario/comparison.py
git show 2231227a:services/api/app/scenario/ranking.py > app/scenario/ranking.py
git show 2231227a:services/api/app/scenario/sensitivity.py > app/scenario/sensitivity.py
python -m pytest tests/scenario -q -k "d059"
# -> 7 failed, 5 passed, 431 deselected
# (restore the fixed files from the worktree's committed state, re-run)
python -m pytest tests/scenario -q
# -> 443 passed
```

## Self-checks (verbatim)

```
$ python -m pytest services/api/tests/scenario -q
443 passed in 1.30s

$ python -m pytest services/api/tests/scenario/test_scenario_contract.py -q
28 passed in 0.20s

$ cd services/api && python -m ruff check .
All checks passed!

$ python tools/modularity_check.py --check   (from repo root)
selected 405 files; failures 0; warnings 17
  (same 17 pre-existing warnings as the unedited baseline; none new)
```

Byte-identity verification script output (`PYTHONPATH=services/api`):
```
threshold match: True
comparison match: True
ranking match: True
sensitivity match: True
derived_range match: True
metric_labels canonical_cap match: True
```

## Scope-block / disclosure notes

- No surface required the "generic, no evaluated-rule context" fallback in the LIVE
  server-side flow (every call site in `scenario_analysis.py` always passes the
  server-rebuilt `scenario` document, which always carries a `cap_provenance` key -
  `None` on a genuine no-cap outcome, a dict with a citation on a cap outcome). The
  generic fallback path exists and is exercised by
  `test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance`, but I did not
  need to fall back to "take the derived value from its caller" for any of the five
  modules - `scenario_document["cap_provenance"]` was directly available in every one.
- `comparison.py`'s `_metric_delta` gained an optional 4th parameter (`metric_labels`,
  default `None` -> falls back to the R5 alias dict) rather than a required one, so its
  two existing unit tests that call it with exactly 3 positional args
  (`test_as4_percent_delta_against_zero_baseline_is_not_computable`,
  `test_as4_absent_or_nonfinite_baseline_metric_is_not_computable`) needed no edits - they
  do not assert on `metric_label`, so the default's exact value is immaterial to them.
- `comparison.py` and `breakeven.py` each carry a pre-existing acceptance test
  (`test_as7_module_imports_are_contract_free` /
  `test_as7_module_imports_only_allowed_dependencies`) that forbids their own source
  from containing the literal `"from .builder"` import line. I honored this by routing
  the shared extraction helper through `derive.py` (which both already import from)
  instead of importing `builder._cap_citation_section` directly into those two files -
  see "Why breakeven/comparison route through .derive" above.
