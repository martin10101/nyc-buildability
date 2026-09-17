# M5-T034 producer report — B7 wide-street FAR wiring + B4 input-bounds closure

Written to the REVIEWER HONESTY BAR: observations are stated separately from
conclusions; no exhaustiveness or "most likely" ranking claims; every claim
carries an evidence reference (file:line, test name, or command output); what was
run locally is separated from what CI must prove; unverified items are marked
UNVERIFIED. Nothing here claims task completion or compliance — the gates decide.

## 0. Provenance of this unit's work (reconciliation)

This unit was launched labelled "fresh", but the worktree already carried an
uncommitted implementation from earlier loop runs of this task lineage (contract
note "runs-36/37 breaker mitigation"; packet progress_log "run 38"). Per the
CLAUDE.md start-of-session routine I reconciled repository reality against the
recorded state rather than assuming.

- Authored THIS unit: the ruff `UP037` fix in `integration.py` (§2) and ten new
  evaluator-seam tests in `tests/rules/test_rules_integration.py` (§4).
- Reviewed but not authored this unit (pre-existing uncommitted tree): the
  wiring module, the buffer-engine input bound, the `evaluate_property` fold, the
  route provider, and the wiring/engine test suites. Observations on them below
  are from source inspection, not authorship.

## 1. Commands run locally (this environment) vs. deferred to CI

Run verbatim through the approval broker (the packet's documented commands):

| Command | Result (observed) |
|---|---|
| `python -m ruff check services/api` | `All checks passed!` (exit 0) after the §2 fix |
| `python tools/modularity_check.py --check` | `selected 439 files; failures 0; warnings 19` (exit 0) |
| `python tools/validate_directive_compliance.py --check` | exit 0, no output |
| `python -m pytest services/api/tests/rules -q` | exit 2 — collection error, `ModuleNotFoundError: No module named 'app'` |
| `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q` | not separately re-run; same environment limitation applies |
| `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` | not separately re-run; same environment limitation applies |

Observation: the three pytest commands cannot execute in this thin-client
environment. `services/api/pyproject.toml:85` sets `testpaths = ["tests"]`
(relative to `services/api`) and the `app` package is not pip-installed here;
local Python is 3.11 while `requires-python = ">=3.12"` (pyproject.toml:10). The
packet anticipates this: "CI api job on the pushed head is the executable
authority; the orchestrator captures CI evidence at the seam."

Conclusion (bounded): ruff, modularity, and directive-compliance are GREEN
locally. All pytest evidence — including the ten tests added this unit — is
UNVERIFIED locally and must be proven by the api CI job on the pushed head.

## 2. Fix authored this unit — ruff UP037

Observation: `python -m ruff check services/api` initially failed with one error:
`UP037` at `services/api/app/rules/integration.py:572` — a quoted type annotation
`"WideStreetDetermination | None"`. The module has `from __future__ import
annotations` (integration.py:42), so annotations are lazy strings and the explicit
quotes are redundant; `WideStreetDetermination` is imported under `TYPE_CHECKING`
(integration.py:56) so the unquoted name is available to type checkers and never
evaluated at runtime.

Change: removed the quotes (integration.py:572). Conclusion: ruff then reported
`All checks passed!`. This was a real CI-blocking lint error (the api CI job runs
ruff first).

## 3. Implementation observations (source inspection)

### 3.1 Own-module wiring (AS-1) — `app/rules/wide_street_wiring.py`
Observation: the wiring is a standalone module consuming
`dcm_street_width_policy` and `wide_street_buffer_engine` through their public
interfaces (imports at wide_street_wiring.py:73-88). It does not modify or add
wiring into the buffer engine. `determine_wide_street_far` (wiring:288) keys
routing off `PolicyDecision.decision_state`, never `routed_to` (wiring:331-356;
`ROUTED_TO_NOT_USED_NOTICE` wiring:137). Modularity check reports `failures 0`.

### 3.2 Typed fail-closed input bound (AS-2) — `app/connectors/wide_street_buffer_engine.py`
Observation: a new `InputBoundsError` (`error_type="input_bounds_exceeded"`,
engine:339) plus three bounds — `MAX_WIDE_SEGMENTS=512`,
`MAX_VERTICES_PER_PATH=5000`, `EXTENT_ABS_MAX_FT=5_000_000.0` (engine:246-248).
Checks are wired into `compute_wide_street_buffer_intersection`: lot extent
(engine:754), segment count (engine:816), per-path vertex count BEFORE linework
construction (engine:828), and linework extent BEFORE the buffer op (engine:830).
Non-finite handling: `abs(±inf) <= bound` is False and any NaN comparison is
False, so `_extent_within_bound` rejects them (engine docstring at ~647). No file
split; no wiring added into the engine (satisfies the M4-T021 G3 precedent).
UNVERIFIED: the deterministic bound tests in
`tests/connectors/test_wide_street_buffer_engine.py` (119 added lines) — CI must
prove.

### 3.3 Evaluator-seam fold (AS-3) — `app/rules/integration.py`
Observation: `select_conditional_far_row` (integration.py:471) folds a
determination into the governing row, reading the two FAR candidates from the
rule's OWN byte-checked parameters (never inventing a value). `evaluate_property`
gained an optional `wide_street_determination` param (integration.py:572) and an
additive fold block (integration.py:755-790): it acts only when exactly one
applicable trace carries both `standard_far_by_district` and
`wide_street_far_by_district` for the district; a professional-review
determination escalates coverage via `cov.most_severe(...)` and grants no bonus.
With no determination supplied the result is byte-identical to before.

Observation on rule-JSON: `r6_r7_r8_wide_street_conditional_far.rule.json` is NOT
modified. The determination is consumed at the evaluator seam, reading the rule's
existing `standard_far_by_district` / `wide_street_far_by_district` params
(rule.json:36-37) as the single source of FAR values. This differs from the
packet output line "rule.json updated to consume the real determination"; the
determination reaches evaluation server-side (task output #4) through
`evaluate_property`, and the DSL has no wide-street-determination input primitive.
Flagged for reviewer judgement — not asserted as satisfying that output line.

Applicability check (evidence): the flat `r6-r12-residential-far` rule covers
suffixed/higher districts (R6A,R6B,R7A,R8A,R9–R12; rule file values line 42) and
the conditional rule covers exactly bare R6/R7-1/R7-2/R8 — disjoint, so a bare-R6
lot yields one applicable trace (the conditional rule).

### 3.4 Route provider (task output #4) — `app/api/v1/rule_evaluation.py`
Observation: a server-side `get_wide_street_determination_provider`
(rule_evaluation.py:141) whose default returns `None` (rule_evaluation.py:135),
injected into `get_rule_evaluation` and passed to `evaluate_property`
(rule_evaluation.py:308-312). Never browser-supplied. The default-None path is
byte-identical to prior behaviour and is exercised by the existing endpoint tests.

## 4. Tests added this unit — `tests/rules/test_rules_integration.py`
Ten tests (evaluator-seam fold), covering: WITHIN→wide row + higher FAR for R6
(3.00) and R8 (7.20); NOT_WITHIN→standard conservative row for R6 (2.20);
professional-review→coverage escalation + no bonus; determination ignored for a
non-conditional district (R5) with export byte-identical to the no-determination
path; wide fields default None when no determination is supplied; and three direct
`select_conditional_far_row` unit tests (within/not-within/professional-review).
A `WideStreetDetermination` is built directly as a fixture so no shapely geometry
is needed at this layer (the engine-driven construction is covered in
`test_wide_street_wiring.py`). Ruff passes on the additions. Test PASS/FAIL is
UNVERIFIED locally — CI must prove.

## 5. Acceptance-scenario mapping (evidence + verification status)

- AS-1 own module: source-confirmed (§3.1); modularity `failures 0`. Behavioural
  tests UNVERIFIED (CI).
- AS-2 typed input bound: source-confirmed (§3.2). Tests UNVERIFIED (CI).
- AS-3 rule behaviour server-side: source-confirmed (§3.3) + ten tests added
  (§4). UNVERIFIED (CI).
- AS-4 exceptions_checked / named-street override honesty: source-confirmed
  (`_elevated_exceptions_checked` wiring:226; named-pending fail-safe
  wiring:378-395). Tests present in `test_wide_street_wiring.py`
  (`test_named_street_override_candidate_never_claims_exceptions_checked`).
  UNVERIFIED (CI).
- AS-5 T019 leftovers + conflicting-records + fallback direction: tests present in
  `test_wide_street_wiring.py` (`test_t019_le_74_...`, `test_t019_lt_80_...`,
  `test_t019_gt_60_...`, `test_conflicting_or_unrecognized_records_...`,
  `test_fallback_direction_lower_far_is_conservative_...`). UNVERIFIED (CI). I did
  not re-derive the D-052 oracle values this unit.
- AS-6 provenance quintuple + DRAFT, no verified/published language:
  source-confirmed (`_provenance` wiring:210; `DRAFT_LABEL_NOTICE` wiring:130;
  rule.json `status: needs_review` line 7). Tests
  `test_provenance_quintuple_present_...`, `test_draft_marker_present_...`.
  UNVERIFIED (CI).
- AS-7 ruff + suites + CI green: ruff PASS locally; suites UNVERIFIED (CI).
- AS-8 report to honesty bar: this document.

## 6. Observations for reviewers / recommended follow-ups (honest gaps)

1. Route override path UNVERIFIED and untested this unit: the provider default
   (None) is covered by existing endpoint tests, but a test exercising the
   provider RETURNING a determination through the full `/rule-evaluation`
   endpoint is not added (it needs an R6/R7-1/R7-2/R8 PLUTO+substrate fixture
   through the whole endpoint; I could not verify it locally). Recommended
   follow-up or reviewer direction.
2. rule.json not modified (§3.3) — reviewer judgement on the packet output line.
3. Out of scope per packet (not resolved here, by design): the 2-row named-street
   override / alternate-width table and the EC-4 tangency legal tolerance.
   Segments that may touch the named-street override never claim
   `exceptions_checked=True` (fail-safe).

## 7. Directive notes
- D-045-R009: rule stays `needs_review` (rule.json:7); DRAFT markers on every
  determination; no published/verified language authored.
- D-045-R002/R008: A2 geometry-mechanics wiring; first production consumer of the
  accepted wide-street stack.
- D-066-R001: I did not regenerate the code graph (thin client); I verified the
  disjoint-applicability conclusion directly in the ruleset source (§3.3) rather
  than relying on the graph.

## 8. Status
Not complete and not self-certified. Producer evidence only; ruff/modularity/
directive-validator GREEN locally; all pytest evidence deferred to the api CI job
on the pushed head and to the independent gates.
