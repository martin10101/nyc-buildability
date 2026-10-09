# Gate Report

> Saved VERBATIM by the orchestrator from the qa-engineer agent return (2026-09-14).
> The reviewer wrote its full report to its session scratchpad and asked the orchestrator
> to persist it; copied byte-for-byte from that file, no edits. Reviewer != producer.

- Gate ID: G4 (independent test-adequacy review)
- Task ID: M5-T028
- Reviewer: qa-engineer (independent, read-only)
- Producer: backend-engineer (unnamed worktree spawn `wt-m5t028`)
- Result: **PASS**
- Clean environment/worktree used: isolated agent worktree (`agent-abe84af2b76d024a9`) whose own HEAD
  (`d8b3899f`) is unrelated to this task. Content pinned via `git show 99f9b277:<path>` and a
  `git archive 99f9b277` extraction into a scratchpad directory (no shared-checkout `cd`, no writes to
  the real repository). All commands below ran against that extraction (or a scratch mutation/red-on-old
  copy of it), never against the tracked repo.

## Content-identity check

`git rev-parse HEAD` in my own worktree is `d8b3899f...` (an unrelated old merge commit — expected for
an isolated worktree). The pinned review target `99f9b277` is reachable from my worktree's shared object
store (`git cat-file -t 99f9b277` -> `commit`; `git log -1 99f9b277` shows the expected M5-T028
integration message). `git worktree list` shows the real `ctl24` checkout sits at `99f9b277` on branch
`candidate/D-024-mrl-option-b`.

HEAD has since drifted forward to `685d7ffb` via five more commits. Checked
`git diff --stat 99f9b277 685d7ffb`: every changed file is control-plane bookkeeping (`docs/
SESSION_HANDOFF.md`, two directive `verification.json` files, `M5-T027-G5.json` + report,
`state.json`, `M4-T021.json`, `M5-T027.json`, `M5-T028.json`) — **zero** touches to
`services/api/app/scenario/*` or `services/api/tests/scenario/*`. Content identity for everything I
reviewed and executed is therefore unaffected; I reviewed at `99f9b277` (== material commit `7e7cd85e`
cherry-picked, confirmed `git diff 7e7cd85e 23caea84 -- services/api/app/scenario services/api/tests/
scenario` is empty).

Note: `project-control/reports/M5-T028-G3-code-review.md` already exists at HEAD (a PASS from an
independent code-reviewer, zero blocking, recorded before my review). I read it for cross-reference
only; my own verdict below is independently derived, not adopted from it.

## Acceptance criteria reviewed

S1–S4 of `project-control/tasks/M5-T028.json`; the six judged test-adequacy items in the review
charge; D-059-R003 (functional correctness the tests must prove), D-046-R001/R002 (scope/dispatch —
noted but outside G4 test-adequacy scope, see below).

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-059-R003 (labels derived from actual evaluation, 5 sibling modules) | 99f9b277 (== 7e7cd85e) | PASS | All 10 live emission sites across the 5 modules call `_x_label(_cap_section_reference(scenario_document))` with the live per-request document (read every module in full); `_cap_section_reference` reuses `builder._cap_citation_section` (M5-T027 seam) unmodified; grep confirms no literal `"ZR 23-21"` survives in source outside the documented `_x_label("23-21")` legacy-alias parameterization; independently reproduced RED-on-old (see table below) and the full/contract suites (443/28). |
| D-046-R002 (disjointness) | 99f9b277 | PASS (code-level) | `M5-T028.allowed_paths` vs `M4-T021.allowed_paths`/`M5-T027.allowed_paths`: zero overlap (independently diffed the three task JSONs). `git diff --stat 2231227a 7e7cd85e` touches exactly the 11 files in `M5-T028.allowed_paths`; no `M4-T021`/`M5-T027` file touched. |
| D-046-R001 (concurrent-dispatch evidence) | n/a | **UNVERIFIABLE from this review** | This is a campaign-dispatch-record fact (progress logs across concurrently-running producers), not something a single task's file diff or test suite can prove. Belongs to the directive-compliance-verifier's evidence chain, not a G4 test-adequacy review. Not treated as a finding against this task. |

## Steps independently executed

1. `git rev-parse HEAD`, `git cat-file -t 99f9b277`, `git worktree list`, `git diff --stat 99f9b277 685d7ffb` — content-identity.
2. `git archive 99f9b277` extraction into a scratchpad; ran everything below against that extraction.
3. Read `project-control/tasks/M5-T028.json`, `M5-T028-producer-report.md`, `M5-T027-G3-code-review.md`
   (advisory A1 source finding), `builder.py:329-368` (`_cap_citation_section` seam), `constants.py`
   cross-reference, `scenario_analysis.py` (live-wiring proof — grepped every call site + confirmed
   `_rebuild_scenario`/`build_scenario` always yields `cap_provenance`).
4. Read all five production modules (`derive.py`, `breakeven.py`, `comparison.py`, `ranking.py`,
   `sensitivity.py`) in full; read all five test files' new `test_d059_r003_*` tests in full.
5. `grep "ZR 23-21"` / `"23-21"` across all five modules — confirmed no bare hardcode, only the
   documented `_x_label("23-21")` legacy-alias parameterization.
6. `python -c "..."` verified `r5_residential_far.rule.json` cites `"23-21"` and
   `r6_r12_residential_far.rule.json` cites `"23-22"` (walked the JSON structurally, not by eyeballing)
   — the hand-typed literals in the new tests match the real ruleset files exactly.
7. Independent byte-identity re-verification (own script, `byte_compare.py`) of all 5 label constants
   + the `canonical_cap_sq_ft` metric label, comparing `git show 2231227a:<file>`'s literal
   pre-fix constant text against `_x_label("23-21")` computed from the fixed code — all 6
   byte-identical.
8. RED-on-old: extracted `2231227a` (base commit, pre-fix) content for all five production files into a
   scratch copy carrying the FIXED test files; ran `pytest tests/scenario -q -k d059 -v` — reproduced
   **7 failed, 5 passed** independently, matching the producer's claim exactly, and captured the
   per-test identity (table below).
9. Mutation test of the grep/source-scan test: in a separate scratch copy, appended a literal
   `"always cites ZR 23-21 regardless of district"` string to `ranking.py`; re-ran
   `test_d059_r003_no_residual_hardcoded_zr_23_21_across_the_five_modules` alone — **it failed**,
   correctly naming `ranking.py` and quoting the injected text. Proves the test is non-vacuous.
10. `git diff 2231227a 7e7cd85e -- <each of the 5 test files>` filtered to removed lines (`grep "^-"`)
    — **zero deletions in any of the 5 test files** (pure appends); confirms no pre-existing assertion
    was touched.
11. `git diff --stat 2231227a 7e7cd85e` (full) — confirmed exactly 11 files changed (5 production + 5
    tests + 1 report), all inside `allowed_paths`; no `forbidden_paths` file touched.
12. Ran the full scenario suite, the contract suite, ruff, and `modularity_check.py --check` against
    the fixed tree, both from `services/api` and from repo root (documented command forms) — see
    "Expected versus actual".
13. Order-independence: ran the 5 R6-R12 new tests in explicit reverse-file order in one invocation —
    all 5 passed; re-ran the full 443-test suite a second time for determinism — 443 passed again.
14. `modularity_check.py --check` requires `git ls-files`; the scratch extraction has no `.git`. Built
    a throwaway, fully-isolated git repo *inside the scratchpad extraction only* (`git init` +
    `git add -A` there) purely so the tool's `git ls-files` call would resolve — this never touched the
    real `ctl24`/worktree repository state.

## Expected versus actual

| Check | Producer claim | Independently reproduced |
|---|---|---|
| `pytest services/api/tests/scenario -q` | 443 passed | **443 passed** (both from `services/api` and from repo root) |
| `pytest .../test_scenario_contract.py -q` | 28 passed | **28 passed** |
| `ruff check .` (from `services/api`) | All checks passed | **All checks passed** (ruff 0.13.0) |
| `modularity_check.py --check` | 0 failures, 17 warnings (baseline-identical) | **0 failures, 17 warnings**, `breakeven.py` present in the warning list exactly as disclosed |
| RED-on-old | 7 failed / 5 passed | **7 failed / 5 passed**, same 5 test names passing (see table below) |
| New-test count | 12 | **12** (`--collect-only -k d059` → 12 selected, 431 deselected) |
| Diff scope | 11 files, `allowed_paths` only | **11 files**, matches exactly; zero `forbidden_paths` touched |
| Byte-identity of 5 label constants + metric label | claimed via producer's own script | **Independently re-derived and confirmed** (6/6 byte-identical) via my own script |

No discrepancy found between the producer's narrated evidence and the reproduced repository/test state.

## Per-module coverage table (judged item 1)

| Module | Low-density (23-21) test | R6-R12 (23-22) test | Generic/no-context fallback test | Both hardcode sites @ both call sites (comparison only) |
|---|---|---|---|---|
| `derive.py` | `test_d059_r003_derived_range_label_names_the_low_density_section` | `test_d059_r003_derived_range_label_names_the_r6_r12_section` | `test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance` — **present** | n/a |
| `breakeven.py` | `test_d059_r003_threshold_label_names_the_low_density_section` | `test_d059_r003_threshold_label_names_the_r6_r12_section` | **absent** (NB-1) | n/a |
| `comparison.py` | `test_d059_r003_comparison_label_names_the_low_density_section` (asserts `result["label"]` AND both `_cap_metric_label`/`_cap_delta_label` sites) | `test_d059_r003_comparison_label_names_the_r6_r12_section` (same, both sites) | **absent** (NB-1) | **Yes** — `compared_metrics` top-level doc site (`_cap_metric_label`) AND the per-set `metric_deltas` breakdown site (`_cap_delta_label`, row `"a"`) are both explicitly asserted in both tests, not just one |
| `ranking.py` | `test_d059_r003_ranking_label_names_the_low_density_section` | `test_d059_r003_ranking_label_names_the_r6_r12_section` | **absent** (NB-1) | n/a |
| `sensitivity.py` | `test_d059_r003_sensitivity_label_names_the_low_density_section` | `test_d059_r003_sensitivity_label_names_the_r6_r12_section` | **absent** (NB-1) | n/a |

Item 1 conclusion: low-density + R6-R12 coverage is complete and correct for all five modules (10/10
tests present and correct); comparison.py's two distinct hardcode sites are each verified at both
emission call sites. The generic/no-context-fallback path is asserted for `derive.py` only — see F1/NB-1
below for severity judgment.

## Per-test RED-on-old verdict table (judged item 2)

Reproduced independently by swapping the five production files back to `git show 2231227a:<file>`
content (base commit, pre-fix) while keeping the fixed test files, then running
`pytest tests/scenario -q -k d059 -v`.

| New test | RED-on-old result | Why |
|---|---|---|
| `test_scenario_derive.py::test_d059_r003_derived_range_label_names_the_low_density_section` | **PASSED on old code** (pins existing behavior, proves nothing about the fix) | Old code already hardcoded `(ZR 23-21)` unconditionally; the R5 assertion happens to match by coincidence of the pre-fix default |
| `test_scenario_derive.py::test_d059_r003_derived_range_label_names_the_r6_r12_section` | **FAILED on old code** (genuinely exercises the fix) | Old code still emitted `(ZR 23-21)` for an R6-R12 document; assertion requires `(ZR 23-22)` |
| `test_scenario_derive.py::test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance` | **FAILED on old code** | Old code always names `23-21`; never falls back to a generic clause |
| `test_scenario_derive.py::test_d059_r003_no_residual_hardcoded_zr_23_21_across_the_five_modules` | **FAILED on old code** | Old source text literally contains `"ZR 23-21"` in all five files |
| `test_scenario_breakeven.py::test_d059_r003_threshold_label_names_the_low_density_section` | **PASSED on old code** (pins existing behavior) | Same coincidence-match reason as derive's low-density test |
| `test_scenario_breakeven.py::test_d059_r003_threshold_label_names_the_r6_r12_section` | **FAILED on old code** | Genuinely exercises the fix |
| `test_scenario_comparison.py::test_d059_r003_comparison_label_names_the_low_density_section` | **PASSED on old code** (pins existing behavior) | Same reason |
| `test_scenario_comparison.py::test_d059_r003_comparison_label_names_the_r6_r12_section` | **FAILED on old code** | Genuinely exercises the fix (both label AND metric-label sites) |
| `test_scenario_ranking.py::test_d059_r003_ranking_label_names_the_low_density_section` | **PASSED on old code** (pins existing behavior) | Same reason |
| `test_scenario_ranking.py::test_d059_r003_ranking_label_names_the_r6_r12_section` | **FAILED on old code** | Genuinely exercises the fix |
| `test_scenario_sensitivity.py::test_d059_r003_sensitivity_label_names_the_low_density_section` | **PASSED on old code** (pins existing behavior) | Same reason |
| `test_scenario_sensitivity.py::test_d059_r003_sensitivity_label_names_the_r6_r12_section` | **FAILED on old code** | Genuinely exercises the fix |

Totals: **7 failed / 5 passed** — matches the producer's claim exactly, verdict-by-verdict (I did not
just check the aggregate count; I checked which 5 specific tests passed and confirmed they are exactly
the five "names_the_low_density_section" tests, i.e. the ones whose expected value happens to equal the
pre-fix hardcoded default — an honest coincidence, correctly disclosed by the producer, not evidence of
a weak test since the paired R6-R12 test for the same module/site DOES fail on old code).

## Mutation result (judged item 4)

Target: `test_d059_r003_no_residual_hardcoded_zr_23_21_across_the_five_modules`
(`test_scenario_derive.py`).

Mutation: appended `_REGRESSION_HARDCODE = "always cites ZR 23-21 regardless of district"` to a scratch
copy of `ranking.py` (fixed tree, otherwise untouched).

Result: `pytest tests/scenario/test_scenario_derive.py -q -k no_residual_hardcoded -v` **FAILED**,
correctly identifying `ranking.py` and quoting the injected literal in the assertion message. The test
is proven non-vacuous — it would catch a reintroduced hardcode anywhere in any of the five files'
source text, including inside what looks like an unrelated declaration.

## Non-tautology check (judged item 3)

Grepped `services/api/tests/scenario/` for calls to `_cap_section_reference(`, `_derived_range_label(`,
`_threshold_label(`, `_comparison_label(`, `_canonical_cap_metric_label(`, `_metric_labels(`,
`_ranking_label(`, `_sensitivity_label(` — **zero matches**. No test builds its expected string by
calling the derivation helper under test; every new assertion is a hand-typed literal
(`"(ZR 23-21)"`, `"(ZR 23-22)"`, `"under ZR 23-21"`, etc.) checked with `in`/`not in` against the
emitted `result["label"]` / metric label. Cross-verified the literals themselves against the real
ruleset files (item above) rather than trusting the docstrings' claim.

## No-weakened-assertions check (judged item 5)

`git diff 2231227a 7e7cd85e -- <file>` filtered to `^-` (excluding the `---` diff header) for each of
the five test files returns **empty** in all five cases — every pre-existing test line is byte-unchanged;
the entire diff in each test file is a pure append of new tests/helpers at the end.

`comparison.py::_metric_delta` gained an optional 4th parameter (`metric_labels: dict[str, str] | None
= None`). Read both pre-existing callers directly:
- `test_as4_percent_delta_against_zero_baseline_is_not_computable` — calls
  `_metric_delta("usable_range_point", 0.0, 5.0)` (3 positional args, unchanged).
- `test_as4_absent_or_nonfinite_baseline_metric_is_not_computable` — calls
  `_metric_delta("usable_range_point", baseline_value, 5.0)` (3 positional args, unchanged).

Neither test asserts on `entry["metric_label"]`, so the new default (`_METRIC_LABELS`, the R5-alias
dict) is immaterial to what either test checks — both continue to assert exactly what they did before
the change. Confirmed by direct read, not by trusting the producer's claim.

## Isolation / hygiene / count audit (judged item 6)

- Offline: every new test is a pure in-process call (`build_scenario` + `derive_practical_usable_range`
  / `find_scenario_threshold` / `compare_scenario_assumption_sets` / `rank_scenario_assumption_sets` /
  `analyze_scenario_sensitivity`), no I/O; consistent with the modules' own documented offline
  guarantee.
- Order independence: ran the five R6-R12 tests in explicit non-file-order in a single invocation — all
  passed; ran the full 443-test suite twice — 443 passed both times, byte-identical result.
- No shared mutable state: `S.profile()` returns a fresh `copy.deepcopy`; `S.canonical_rule_evaluation()`
  re-parses JSON from disk on every call (confirmed by reading `_support.py`); each new test's
  `_r6_r12_rule_evaluation()` helper operates on its own freshly-loaded copy. No cross-test aliasing risk.
- Count audit: `pytest --collect-only -k d059` → **12 selected, 431 deselected** (exact). Full suite:
  **443 passed** = 431 pre-existing + 12 new, reconciled exactly.

## Evidence paths

`services/api/app/scenario/{derive,breakeven,comparison,ranking,sensitivity}.py`;
`services/api/tests/scenario/test_scenario_{derive,breakeven,comparison,ranking,sensitivity}.py`;
`services/api/app/scenario/builder.py:329-368` (`_cap_citation_section` seam, read-only,
forbidden-path); `services/api/app/api/v1/scenario_analysis.py` (live-wiring proof, read-only,
forbidden-path); `services/api/app/rules/rulesets/{r5_residential_far,r6_r12_residential_far}
.rule.json`; `project-control/tasks/M5-T028.json`; `project-control/reports/M5-T028-producer-report.md`;
`project-control/reports/M5-T027-G3-code-review.md` (advisory A1 source); `project-control/directives/
{D-059-mvp-review-dependable-answers,D-046-parallel-family-production}/requirements.json`.

## Human-style walkthrough findings

N/A — backend, non-UI task (no `apps/web/**` change; not in scope).

## Regression/security/provenance findings

None found beyond NB-1 below. Provenance prose is byte-identical apart from the section-reference
clause across all five modules — independently re-derived and confirmed via my own byte-comparison
script (not the producer's), covering all five label constants plus the `canonical_cap_sq_ft` metric
label (the second comparison.py hardcode site).

## Defects

None blocking.

**F1 / NB-1 (non-blocking, recommend a fast follow-up).** The task's own S2 acceptance text states
"each surface's section reference follows the evaluated rule **or is generic**" for the four sibling
surfaces (breakeven/comparison/ranking/sensitivity), but only `derive.py` carries a test asserting the
generic-fallback branch's actual TEXT when `cap_provenance` is absent
(`test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance`). The other four modules' own
`_threshold_label`/`_comparison_label`/`_ranking_label`/`_sensitivity_label` functions each independently
implement the identical ternary fallback pattern (verified correct by direct source read — none of the
four hardcodes a section number in the fallback branch), and the runtime path IS already exercised
without crashing by pre-existing EMPTY/INVALID-outcome tests (e.g.
`test_as4_no_cap_document_is_typed_empty_with_reason` in breakeven, parametrized over
`unsupported_rule_evaluation`/`conflict_rule_evaluation`/`missing_lot_area_rule_evaluation`, all of
which carry no `cap_provenance`) — but none of those pre-existing tests assert on the label TEXT, so a
subtly-wrong (not hardcoded-23-21, just incorrect) fallback string in any of the four sibling modules
would not be caught by this test suite. Mitigation already in place: the grep-based
`test_d059_r003_no_residual_hardcoded_zr_23_21_across_the_five_modules` test (proven non-vacuous by
mutation above) DOES catch the specific regression D-059-R003 exists to prevent (a reintroduced literal
`"ZR 23-21"`) anywhere in any of the five files' source text, including inside a broken fallback branch —
so the residual risk is narrowly "wrong-but-not-23-21" fallback text in 4/5 modules, not a silent
reintroduction of the original defect. Not blocking this gate; recommend a small follow-up task adding
one `_x_label(None)`-style assertion (or an integration-level no-cap-provenance test) per sibling module.

## Required rework

None required for M5-T028 acceptance. NB-1 is an advisory for an immediate, small follow-up (consistent
with how the M5-T027 G3 review handled its own A1 advisory in this same defect lineage).

## Reviewer conclusion

Independently reproduced every claim in the producer report against the pinned content identity
(`99f9b277` / material commit `7e7cd85e`), not by trusting the producer's narrative: the full scenario
suite (443), the contract suite (28), ruff, and the modularity check all match exactly; the RED-on-old
claim was re-derived from scratch (own swap of pre-fix production files against the fixed test files)
and verified test-by-test, not just by aggregate count; the grep-based regression test was proven
non-vacuous by actual mutation, not by inspection alone; every pre-existing assertion in all five test
files is confirmed byte-unchanged (zero deletions in the diff); the six hand-typed label/metric-label
literal constants were independently re-derived and confirmed byte-identical to the pre-fix originals
(a second, independent script from the producer's own); the two hand-typed section literals ("23-21"/
"23-22") were checked against the real ruleset JSON files structurally, not by eyeballing; no test
builds its expectation by calling the code under test. Coverage is complete and correct for the core
D-059-R003 requirement across all five modules (both district families, and both of comparison.py's two
hardcode sites at both of their emission call sites). One non-blocking coverage gap found and disclosed
(NB-1): the generic/no-context fallback TEXT is asserted for `derive.py` only, not for the four sibling
modules, though the underlying mechanism is proven correct by direct source read and the regression this
task targets is independently guarded by the (mutation-proven) grep test.

**Verdict: PASS.** NB-1 is flagged as a non-blocking advisory for an immediate follow-up task.
