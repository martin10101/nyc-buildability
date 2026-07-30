# M4-T008 Producer Report — DF-6 fail-open closure in `_apply_exceptions`

Producer: rules-engineer (spawned agent, isolated harness worktree)
Date: 2026-07-30
Task: M4-T008 (D-004 Step 4 pilot, re-dispatch)
Requested status: **awaiting_gate** (with one disclosed scope deviation and one required follow-up — see sections 8 and 9)

## 1. Attestation

Adapted attestation per D-004-R302 via the R061 harness-isolation pattern. Commands run from the
starting cwd, verbatim: `pwd; git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD`
plus `git status --porcelain`. Windows user prefix redacted; paths written from `.claude/...` onward.

| Check | Value (verbatim, prefix-redacted) | Verdict |
|---|---|---|
| 1. `git rev-parse HEAD` | `84c1bf29243bb862d344c909099c9bd9a3f6a766` | PASS — exactly the frozen base |
| 2a. `pwd` | `.claude/worktrees/agent-a44a98e3f5810e4d8` | PASS |
| 2b. `git rev-parse --show-toplevel` | `.claude/worktrees/agent-a44a98e3f5810e4d8` | PASS — same directory as `pwd`; is an `agent-*` isolated worktree, not the primary checkout root, not an `M*-*` task worktree |
| 3. `git branch --show-current` | `worktree-agent-a44a98e3f5810e4d8` | PASS — harness branch matches own worktree directory name |
| 4. `git status --porcelain` | (empty output) | PASS — clean tree |

All four checks passed, so work proceeded. This file was the first write.
No `git add/commit/push`, no `gh`, no `tools/project_control.py` was run (D-004-R303). The working
tree is left UNCOMMITTED for orchestrator port.

## 2. The defect, verified against the code (not assumed)

`_apply_exceptions` evaluated exception conditions with the two-valued `_eval_predicate`. The
predicate ops in `operations.py` are deliberately TOTAL — `equals` / `in_set` / `compare` return
`False` for a value they never saw rather than raising (docstring: "a missing/bad value is a
completeness concern, not a truthiness error"). Consequence: an unsupplied OPTIONAL input made a
coverage-downgrading exception answer "does not apply", and the result kept full `conditional`
coverage. Measured on the frozen base, with the primitive unchanged:

```
_eval_predicate({'op':'equals','input':'overlay_present','value':True}, {'zoning_district':'R5'})[0]
  -> False        # a False the engine had no evidence for
```

Live defect site (real committed rules, not synthetic): `r5_height.rule.json` declares four OPTIONAL
modifier flags — `overlay_present`, `special_district_present`, `historic_district`, `large_site` —
each gating a `professional_review_required` exception. Evaluated as `{"zoning_district": "R5"}`,
the pre-fix engine reported a confident 35 ft / 45 ft envelope at `conditional` while all four
escalations had been silently skipped. `r5_setback`, `r5a_height`, `r5b_height`, `r5d_height`,
`r5_qrs_height` share the pattern.

### Claims from the design guidance that I verified — two did not hold

* **"the missing-name set is broader than `optional_missing`: an exception predicate may reference
  names not declared in `rule.inputs` at all"** — FALSE for any rule that reaches the evaluator.
  `dsl.py` `_check_predicate_refs` (invoked at lines 105–110 for every exception condition) raises
  `DSLError` when a predicate input is not a declared input, and `build_rule_definition` is the only
  constructor path. The name set is therefore always a subset of declared inputs. The implementation
  is nonetheless written against the predicate tree (not against `rule.inputs`), so it stays correct
  for a directly-constructed `RuleDefinition`.
* **"required inputs are excluded by load-time validation (dsl.py lines 101–109)"** — FALSE as
  stated; those lines only check *declaredness*, not requiredness. The real reason required inputs
  cannot reach the exception stage is `evaluate` step 1 (`evaluator.py:663`, `if missing_required or
  invalid_inputs:`), which returns before step 5. Verified by test
  `test_df6_as4_missing_required_input_path_unchanged`.
* **"do NOT add new keys to `exceptions_applied` if `rule_evaluation.schema.json` would reject
  them"** — the schema actually declares `exceptions_applied` as a bare `{"type": "array"}` in BOTH
  schemas, so extra keys would *not* be rejected. I still took the notes-only route, on the stronger
  ground that an untyped array is exactly where an undocumented key would go unnoticed. Guarded by
  `test_df6_as5_exceptions_applied_entries_keep_exactly_three_keys`.

## 3. The implemented semantic rule, stated precisely

In `_apply_exceptions`, for each exception, let `U` = the set of input names the exception's
condition READS that were not supplied, where "not supplied" is the engine-wide test used by
`_validate_inputs` and by the `optional_missing` computation: **the key is absent from `inputs`, OR
present with the value `None`**. `U` is computed BY NAME from the predicate tree via
`_predicate_input_names` (walking `all` / `any` / `not` and every leaf), never inferred from an
evaluation outcome. Let `holds` be the two-valued outcome of `_eval_predicate(condition, inputs)`.

| Case | Behaviour |
|---|---|
| `condition is None` | Applies. Unchanged. |
| `U` empty | Evaluated exactly as before, **both** outcomes (supplied-True applies; supplied-False skips silently). All-inputs-present behaviour is bit-for-bit preserved. |
| `U` non-empty **and** `holds` is false | **INDETERMINATE.** Coverage downgrade `professional_review_required` folded into the returned downgrade (so step 5's existing `cov.most_severe(base_coverage, exc_downgrade, geom_downgrade)` carries it), plus a `notes` entry naming the exception id and the sorted `U`. The exception is **NOT** added to `exceptions_applied`. Never a silent skip. |
| `U` non-empty **and** `holds` is true | The exception is applied as before, **plus** a `notes` entry making the unsupported basis explicit. Applying is the conservative direction — `cov.most_severe` can only move coverage away from `verified` — so this is not a fail-open miss; the note removes the silence. |

Unsupplied optional inputs that NO exception condition reads are untouched: they remain an
`optional_missing` note with `missing_noncritical` completeness.

`data_completeness` is deliberately NOT repurposed: the escalation rides the coverage axis (PRR),
while `data_completeness` continues to describe input supply only, keeping `missing_critical`
reserved for a missing REQUIRED input. Guarded by `test_df6_as3_completeness_axis_is_not_repurposed`.

### Why by-name detection, and why the `not` case is handled the way it is

By-name detection is required because a predicate outcome carries no information about whether an
input was read: the ops are total. Detecting after the fact would also be defeated by a `not`
wrapper, which converts the unsupported `False` into an equally unsupported `True`.

The design guidance implied the `not` case should also route to PRR. I verified what that costs and
chose not to, deliberately and with disclosure — see section 8. In short: an exception that *fires*
has already escalated (effects are only `professional_review_required`, `conditional_alternative`, or
a documented note; `cov.most_severe` never upgrades), so firing is not the DF-6 fail-open. The
remaining defect in that case is silence about the unsupported basis, which the second note fixes.

## 4. Changed files

| File | Change | Rationale |
|---|---|---|
| `services/api/app/rules/evaluator.py` | New `_unsupplied_predicate_inputs` (line 227); `_apply_exceptions` (line 248) becomes three-valued. +82/−0 net per `git diff --stat` (docstrings dominate). | The whole fix. `_eval_predicate`, `_predicate_input_names`, `evaluate`'s step 5 wiring, the `RuleResult`/`EvaluationTrace` shapes, and every other engine path are untouched — `_apply_exceptions` keeps its exact 3-tuple signature and its only caller (`evaluator.py:743`) is unchanged. |
| `services/api/tests/rules/test_r5_height_setback.py` | Added `_NO_MODIFIERS` + `_known_unmodified()` helper; 6 AS-1/AS-3 scenarios now supply the modifier flags explicitly. +65/−8. | These scenarios assert a CONFIDENT envelope. Pre-fix they obtained it from the fail-open — they asserted a confident legal result from inputs the engine had never seen. They now state their assumption ("an R5 lot affirmatively known to carry no overlay / special district / historic district / large-site designation"), which is the all-inputs-present case AS-2 preserves. The scenarios' meaning and their asserted values (35/45, 10/15, 25/35) are unchanged. |
| `services/api/tests/rules/test_rules_df6_exception_indeterminate.py` | NEW, 37 tests. | The DF-6 regression pack (section 6). |
| `project-control/reports/M4-T008-producer-report.md` | NEW. | This report. |

Nothing else is modified. `git status --porcelain` at the end of work:

```
 M services/api/app/rules/evaluator.py
 M services/api/tests/rules/test_r5_height_setback.py
?? project-control/reports/M4-T008-producer-report.md
?? services/api/tests/rules/test_rules_df6_exception_indeterminate.py
```

## 5. HARD CONSTRAINT — no contract change (verified, not asserted)

`git status --porcelain -- packages/contracts services/api/app/_contract_schemas services/api/app/rules/schemas`
returns **empty**. sha256 of the schema files at end of work:

```
7454b3d5edb6a6438498ea1b022481d04b38ffbaaecd9a3aaccc9ae3974cb130  24446  packages/contracts/schemas/v1/rule_evaluation.schema.json
7454b3d5edb6a6438498ea1b022481d04b38ffbaaecd9a3aaccc9ae3974cb130  24446  services/api/app/_contract_schemas/v1/rule_evaluation.schema.json
dc7910e2e4f3bdfb374f734444ff82d039b9cde0601dd23065b50b6111dd74b6   6246  services/api/app/rules/schemas/v1/evaluation_trace.schema.json
57d315add9e57d08129f3e37ed89582dfd26e38c94f86c0efdf7a3358af2c716  11805  services/api/app/rules/schemas/v1/rule_definition.schema.json
```

Both `rule_evaluation.schema.json` copies are byte-identical to each other and byte-unchanged from
the frozen base. Only the pre-existing `coverage_status` and `notes` fields carry the new outcome.
`test_df6_as5_escalated_trace_introduces_no_new_contract_key` asserts the exported escalated trace's
key set equals the declared property set of BOTH the engine trace schema and the canonical
`rule_evaluation` contract's `$defs.evaluation_trace` (each `additionalProperties: false`). Responses
still validate: `tests/api/test_rule_evaluation_api.py` (which validates whole documents against the
canonical contract with a resolving registry) is green and untouched.

**No contract change was needed, so `needs_split` on that ground does not arise.**

## 6. Acceptance-scenario coverage

New file `services/api/tests/rules/test_rules_df6_exception_indeterminate.py` (37 tests). Categories
required by the acceptance standard — positive, negative, boundary, missing-input, exception,
effective-date — are all present.

| Packet AS | Category | Tests | Result |
|---|---|---|---|
| **AS-1** exception reading a MISSING input routes to PRR with a note naming the input + exception; never a silent skip | missing-input (+ boundary) | `test_df6_as1_unsupplied_input_in_exception_condition_routes_to_prr`; `..._present_none_is_treated_as_unsupplied`; `..._not_wrapped_predicate_cannot_launder_an_unsupplied_input`; `..._every_combinator_and_op_reaches_the_unsupplied_name` (7 params: leaf, `all`, `any`, `not(all)`, `exists`, `compare`, `in_set`); `..._partially_supplied_condition_still_escalates`; `..._live_defect_site_r5_height_without_modifier_flags` | PASS (12) |
| **AS-2** all-inputs-present behaviour unchanged (R5 height/setback + full exception suite) | positive | `test_df6_as2_supplied_input_evaluates_exactly_as_before` (True/False params); `..._r5_height_all_modifier_flags_known_stays_conditional`; `..._r5_height_known_overlay_still_downgrades`; `..._r5_far_all_inputs_present_unchanged`; `..._condition_null_exception_is_unaffected`; `..._rule_with_no_exceptions_is_unaffected` — plus the whole pre-existing suite (see section 7) | PASS (7) |
| **AS-3** missing optional input NOT referenced by an exception keeps `COMPLETENESS_MISSING_NONCRITICAL` | negative control | `test_df6_as3_unsupplied_input_not_read_by_any_exception_is_untouched`; `..._completeness_axis_is_not_repurposed` | PASS (2) |
| **AS-4** required/applicability three-valued indeterminate path unchanged | exception / prior-path | `test_df6_as4_missing_required_input_path_unchanged`; `..._applicability_indeterminate_path_unchanged`; `..._not_applicable_never_reaches_exceptions`; `..._invalid_supplied_input_still_fails_closed_first`; `..._geometric_uncertainty_still_composes`; `..._multiple_exceptions_each_reported` — plus the untouched `test_rh_s13_indeterminate_determination_when_proposal_omitted` | PASS (6) |
| **AS-5** contract schemas byte-unchanged (both copies); responses still validate | contract | Section 5 hashes; `test_df6_as5_escalated_trace_introduces_no_new_contract_key` (2 params); `..._exceptions_applied_entries_keep_exactly_three_keys`; `..._indeterminate_trace_validates_against_engine_schema`; `..._indeterminate_trace_is_strict_json_and_deterministic`; `..._notes_are_plain_strings`; `..._escalation_never_upgrades_coverage` | PASS (8) |
| **AS-6** worktree attestation before first write; evidence + status returned; no git/gh/CLI writes | process | Section 1 of this report; no such command was run | PASS |
| **AS-6 (effective-date category)** | effective-date | `test_df6_as6_not_yet_effective_wins_over_indeterminate_exception`; `..._on_and_after_effective_date_the_escalation_applies` (2 dates incl. the inclusive first day); `..._invalid_as_of_date_still_fails_closed_first` | PASS (3) |

Synthetic rules are built in-code with `build_rule_definition` over the existing
`tests/rules/fixtures/m4t003/snapshots` store, so the pack adds **no** new fixture files and injects
**no** new rule id into any registry (which would have perturbed family-coverage assertions
elsewhere).

## 7. Self-check output (verbatim tails)

Baseline on the frozen base, before any edit:

```
$ python -m pytest tests/rules -q
291 passed in 5.45s

$ python -m pytest tests -q
1029 passed in 12.61s
```

After the change (run from `.claude/worktrees/agent-a44a98e3f5810e4d8/services/api`):

```
### SELF-CHECK 1: python -m pytest tests/rules -q
........................................................................ [ 87%]
........................................                                 [100%]
328 passed in 3.70s

### SELF-CHECK 2: python -m pytest tests -q (whole services/api)
........................................................................ [ 94%]
..........................................................               [100%]
1066 passed in 10.97s

### SELF-CHECK 3: ruff
All checks passed!

### SELF-CHECK 4: new pack only
.....................................                                    [100%]
37 passed in 0.32s
```

Counts: `tests/rules` 291 -> 328 (+37, all new DF-6 tests; 0 failures, 0 skips). Whole
`services/api` suite 1029 -> 1066 (+37; 0 failures). `python -m ruff check app/rules tests/rules`
clean. Nothing is red, xfail, or skipped.

Behavioural evidence, captured from the worktree:

```
--- AFTER FIX: r5-height, modifier flags NOT supplied ---
  coverage_status = professional_review_required
  exceptions_applied ids = ['no_minimum_base_height']
  NOTE: exception commercial_overlay_modification indeterminate: its condition reads input(s) not supplied: ['overlay_present'...
  NOTE: exception special_district_modification indeterminate: its condition reads input(s) not supplied: ['special_district_p...
  NOTE: exception historic_district_base_height_match indeterminate: its condition reads input(s) not supplied: ['historic_dis...
  NOTE: exception large_site_modification indeterminate: its condition reads input(s) not supplied: ['large_site']; whether th...

--- AFTER FIX: r5-height, all four modifier flags KNOWN false (all-inputs-present) ---
  coverage_status = conditional
  outputs = {'max_base_height': 35.0, 'max_building_height': 45.0}
  indeterminate notes = []
```

## 8. DISCLOSED SCOPE DEVIATION — the `not`-wrapped case is NOT routed to PRR

**What I did differently from the design guidance, and why the gate must judge it.**

The guidance said the by-name pre-check should also stop a `not`-wrapped predicate from flipping to
True. I implemented the by-name detection but escalate to PRR only when the exception would have been
**skipped**; when it **fires**, I apply it and emit an explicit unsupported-basis note instead.

I first implemented the blanket variant (escalate whenever `U` is non-empty, regardless of outcome)
and measured it. Evidence:

* Blanket variant: **20 failures / 1009 passed**, including
  `tests/api/test_rule_evaluation_api.py::test_as3_confident_supported_family_is_200_draft` — a file
  inside this packet's `forbidden_paths`, which I may not repair.
* Skip-only variant (shipped): breakage confined to
  `services/api/tests/rules/test_r5_height_setback.py` (allowed path), then resolved by stating the
  scenarios' modifier assumptions explicitly. Full suite green.

The blast radius is not incidental. `integration.py` sets `TARGET_FAMILY = "residential_far"`, so the
live API path evaluates only `r5-residential-far`, whose sole conditional exception is
`{"not": {"op":"equals","input":"site_class","value":"standard_zoning_lot"}}`. The blanket variant
turns **every confident R5 property** on that endpoint from `conditional` to
`professional_review_required`. And that `not` construction is a deliberate, documented design, not
an accident:

* `r5_residential_far.rule.json`, `site_class` input description: *"When absent, the qualifying-site
  alternative is surfaced as conditional (not decided)."*
* Same file, exception description: *"when the site class is unknown or qualifying, the result is
  conditional and the higher FAR may apply."*
* `integration.py:570-572`: *"site_class is deliberately NOT derived: whether a lot is a 'qualifying
  residential site' is a separate legal determination the rule defers. Leaving it absent makes the
  rule surface the higher-FAR alternative as conditional."*

Substantive reasoning for the narrowing, independent of the test cost: DF-6 is recorded as a
**fail-OPEN** — *"a missing optional input silently skips an exception that would DOWNGRADE
coverage -> fail-open miss of an escalation"*, remedy *"never false"*. An exception that fires cannot
be a missed escalation: exception effects are `professional_review_required`,
`conditional_alternative`, or a documented note, and `cov.most_severe` only moves coverage away from
`verified`. So firing is strictly the conservative direction. Its real defect is *silence* about the
unsupported basis, which the second note now removes. The shipped behaviour is fail-closed-or-equal
to the frozen base in every reachable case; it is never more permissive.

**What the gate should decide.** If the reviewer holds that DF-6 requires the blanket semantic, this
task must be **split**: the remaining half changes accepted API-contract-visible behaviour
(`conditional` -> `professional_review_required` for every confident R5 property), requires edits in
`services/api/tests/api/**` and probably `services/api/app/rules/integration.py` — both in this
packet's `forbidden_paths` — and overrides a documented rule-authoring decision, which is a legal
interpretation reserved for a qualified human (principles 1 and 12). I did not make that call
unilaterally.

## 9. REQUIRED FOLLOW-UP — a rule file's `limitations` text is now stale

`services/api/app/rules/rulesets/r5_height.rule.json:71` states:

> "Historic-district (23-426) and large-site (23-425) overrides have no canonical property_profile
> field; they are surfaced as professional_review_required **only when a caller supplies the flag,
> and are otherwise a documented limitation**."

After this fix, an unsupplied flag also surfaces as `professional_review_required` (indeterminate), so
the bolded clause no longer describes engine behaviour. I did **not** edit it: rule DSL documents are
legal artifacts under lifecycle control (principle 12; `.claude/rules/legal-rules.md`), and silently
rewriting one to match code I just changed is exactly the move a producer must not make. Recommend a
follow-up task to correct the wording with legal-reviewer eyes. No other ruleset carries comparable
text (`grep` over `app/rules/rulesets/` returns this one line only).

## 10. Assumptions, limitations, and residual risk

1. "Not supplied" is defined as `inputs.get(name) is None`, matching `_validate_inputs` and
   `optional_missing`. A rule that wants to treat `None` as a meaningful value cannot; no rule does,
   and no predicate op could distinguish them anyway (both reach `inputs.get()` -> `None`).
2. Escalation is **by name, not by load-bearingness**. `all[equals(missing_x), equals(present_y=fail)]`
   escalates even though `y` alone already decides it. Deliberate: computing load-bearingness means
   trusting the two-valued outcomes this fix exists to distrust. Over-escalation is fail-closed.
3. `exists` is NOT carved out — `{"op":"exists","input":"x"}` inside an exception with `x`
   unsupplied escalates like any other op (`test_df6_as1_every_combinator_and_op_reaches_the_unsupplied_name`,
   `exists` param). Zero blast radius today: no rule or fixture uses `exists` in an exception
   condition (verified). A future rule wanting "applies when X was not supplied" would need a
   different construction; flagged rather than pre-solved.
4. Outputs are still emitted alongside a PRR coverage label. That is the pre-existing exception
   behaviour (a known overlay already produced PRR + outputs); this fix did not change it.
5. Everything ran locally in the harness worktree on the owner's machine; CI has not run this branch.
   No dependency was added, installed, or upgraded.
6. I am the producer. Nothing here is a gate result, and G6/human approval remains mandatory before
   any rule publication.

## 11. Requested status

**awaiting_gate** — DF-6's recorded fail-open is closed with 37 new deterministic tests, the whole
`services/api` suite is green (1066 passed, 0 failed), and both `rule_evaluation` contract copies are
byte-unchanged; the one deviation from the design guidance (section 8) and the one stale rule-file
sentence (section 9) are disclosed for the reviewer to rule on rather than resolved unilaterally.
