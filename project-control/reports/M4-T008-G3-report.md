# M4-T008 — G3 code review (D-004 Step 4 pilot; reviewer return, captured verbatim)

Orchestrator capture note: reviewer = code-reviewer, unnamed spawn, explicit Fable 5, frozen SHA
`2122cd27a49511df079e0bf30baf5093d384a012` (task/M4-T008-df6-exceptions). Return preserved
verbatim below (transport entity-decoding only; absolute worktree paths in the environment and
evidence-path lines normalized to repo-relative form per the no-machine-specific-data rule).

---

All evidence is in. Here is the gate report, returned verbatim for the orchestrator to save.

---

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M4-T008 — DF-6 rule-engine hardening: missing optional inputs in exception predicates route to indeterminate/PRR, never silently false
- Reviewer: code-reviewer (read-only, independent; not the producer)
- Producer: rules-engineer (spawned agent, harness worktree `agent-<id>`)
- Result: PASS
- Clean environment/worktree used: yes — reviewed in `.claude/worktrees/M4-T008-df6-exceptions` at frozen SHA `2122cd27a49511df079e0bf30baf5093d384a012` (`git rev-parse HEAD` confirmed; `git status --porcelain` clean; base `84c1bf29243bb862d344c909099c9bd9a3f6a766` is an ancestor; exactly one commit `2122cd2` between base and HEAD; diff touches exactly 4 files, all inside `allowed_paths`).

## Acceptance criteria reviewed

AS-1 through AS-6 from `project-control/tasks/M4-T008.json`, plus the nine review items in the gate dispatch. Findings per dispatch item:

**Item 1 — Correctness of the semantic rule: VERIFIED.**
- `_unsupplied_predicate_inputs` (evaluator.py:227-245) computes U purely by name via `_predicate_input_names` (walks `all`/`any`/`not` and every leaf `input`; evaluator.py:79-88), using `inputs.get(name) is None` — the identical test used by `_validate_inputs` (line 414) and the `optional_missing` computation (line 660). Absent key and present-`None` are both caught; falsy-but-supplied values (`False`, `0`, `""`) are correctly treated as supplied.
- U is computed at line 291 before `_eval_predicate` at line 292, and — decisively — from names, not outcomes, so a `not` wrapper cannot launder a missing input: the flip to True lands in the applies-branch (which adds the disclosure note), never in a silent skip.
- `condition is None` path (line 288-289): `holds=True, unsupplied=[]` — falls through to the unchanged applied path; the `if unsupplied:` note is skipped. Unchanged.
- U-empty: `holds` computed exactly as at base; `not holds and unsupplied` cannot trigger; skip (`continue`) and apply paths are line-for-line the base behavior with the `if unsupplied:` block a no-op. Byte-equivalent for both outcomes.
- The PRR fold (line 297) writes into the same `downgrade` value the base code used, returned as `exc_downgrade` and consumed by the existing `cov.most_severe(base_coverage, exc_downgrade, geom_downgrade)` at line 745 — no new composition path.

**Item 2 — Ruling on the disclosed deviation: deviation ACCEPTED — DF-6 closed as contracted.**
- The recorded defect (WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23 line 98, reproduced verbatim during review) is: "a missing optional input silently skips an exception that would DOWNGRADE coverage → fail-open miss of an escalation", remedy "route optional-input-missing inside an exception to indeterminate/PRR, never false". The silent skip is exactly the U-non-empty + holds-FALSE case, which the shipped code routes to PRR with a note naming the exception id and the sorted unsupplied inputs. Verified in code and by running tests, including the live defect site (`test_df6_as1_live_defect_site_r5_height_without_modifier_flags`: r5-height without the four modifier flags is now PRR with all four exceptions and all four inputs named).
- The U-non-empty + holds-TRUE case cannot be the recorded defect: I verified the full exception-effect vocabulary in `_apply_exceptions` (`professional_review_required` → PRR, `conditional_alternative` → conditional, anything else → note only) and `coverage.most_severe` (max-severity over `_SEVERITY`, coverage.py:51-69) — a fired exception can only hold or worsen coverage, never upgrade it. A fired escalation is by definition not a missed escalation; the shipped disclosure note ("was applied although its condition reads input(s) not supplied") removes the only residual defect (silence), and is tested (`test_df6_as1_not_wrapped_predicate_cannot_launder_an_unsupplied_input`).
- The blanket variant's cost is real, independently confirmed structurally: `r5_residential_far.rule.json` line 28 documents `site_class` as "When absent, the qualifying-site alternative is surfaced as conditional (not decided)"; its sole conditional exception (line 71) is the `not`-wrapped `site_class` predicate; `integration.py:69` sets `TARGET_FAMILY = "residential_far"` and lines 570-572 document that `site_class` is deliberately not derived; and `tests/api/test_rule_evaluation_api.py:262` (a forbidden path for this packet) asserts `coverage_status == conditional` for exactly that no-`site_class` live path — the blanket variant necessarily fails it. Blanket escalation would therefore override a documented rule-authoring decision (a legal-interpretation call reserved for qualified humans, principles 1/12) and change accepted API-visible behavior outside this packet's scope. The producer's refusal to make that call unilaterally, with measurement and disclosure, is the correct behavior.
- One honest caveat: the remedy text's literal "never false" could be stretched to cover the fired-`not` case (the inner predicate still evaluates the missing input to False before flipping). But the defect column defines the failure mode as the missed escalation, and no escalation can be missed in the fired direction; the fired direction is fail-closed-or-equal in every reachable case. The recorded defect is closed. If the owner wants the blanket semantic, that is a new task with a legal decision attached, not rework of this one.

**Item 3 — Fail-closed direction / zero blast radius: VERIFIED.**
- By-name escalation is deliberately load-bearingness-blind (producer §10.2); e.g. `all[equals(missing_x), equals(supplied_y=False)]` escalates although `y` alone decided the skip, and `exists(missing_x)` escalates although "not present" was a supportable answer. Both are over-escalation — more severe than truth — i.e. fail-closed. No path in the diff became more permissive than base: the only behavior deltas are skip→PRR (more severe) and apply+extra-note (same coverage, more disclosure).
- Zero-blast-radius claim for `exists` confirmed: `grep '"op":\s*"exists"'` over `services/api` matches only the new test file; the single `exists` string in `app/rules/rulesets/` (r5b_height.rule.json:32) is prose in a description, not a predicate. Full exception inventory across all 8 rulesets (reproduced above): every skip-capable conditional exception carries effect `professional_review_required` itself, and the only `conditional_alternative`/`not`-wrapped exception (r5-far) can never take the skip path when its input is unsupplied.

**Item 4 — Amended `test_r5_height_setback.py`: VERIFIED, no assertion weakened.**
- The diff amends exactly 6 scenarios (`test_as1_r5_height_confident...`, `test_as1_r5_setback_confident...` [param], `test_as1_r5a...`, `test_as1_r5b...`, `test_as1_r5d...`, `test_as3_on_amendment_date_effective` [param]) by wrapping inputs in `_known_unmodified(...)`; every asserted value is character-identical to base (coverage `conditional`; outputs 35/45, param setback depths, 25/35, 35, 45; `in_effect is True`). No assertion was deleted, loosened, or converted to a weaker form.
- `_known_unmodified` intersects the explicit-false flags with the rule's own declared inputs, so it cannot inject undeclared inputs. The untouched tests in the file that still evaluate without modifier flags (e.g. lines 130-152, 186-197, 204-214, 295-299, 325-334) assert exception markers, never-verified, citations, determinism, and outputs — none asserts confident coverage, so they remain coherent under the new PRR outcome (and pass).

**Item 5 — New suite `test_rules_df6_exception_indeterminate.py` (37 tests): SOLID, minor gaps noted.**
- Behavior-level coverage confirmed present and meaningful: missing-input routing across leaf/`all`/`any`/`not(all)`/`exists`/`compare`/`in_set` (7-param test with a correct two-branch expectation for shapes that apply instead of skip), present-`None` boundary, partial supply (asserts only the unsupplied name appears in the note), the real r5-height defect site against the committed registry, all-inputs-present bit-equivalence in both directions, negative control (unread optional input keeps `missing_noncritical`), completeness-axis non-repurposing, required/applicability/not-applicable/invalid-input/invalid-date precedence, severity composition with geometry `data_conflict`, multi-exception note-per-exception, the schema-guard key-set test against both `additionalProperties:false` schemas, strict-JSON determinism, plain-string notes, never-upgrades. Synthetic rules go through `build_rule_definition` over the existing m4t003 snapshot store — no new fixture files, no registry pollution.
- Gaps (observations, not defects, all hypothetical today): (a) no test of a skip-direction indeterminate exception whose own effect is `conditional_alternative` or `documented_limitation` — the code hardcodes PRR there, which is packet-conform and fail-closed, but the over-escalation for a note-only limitation is untested and undocumented outside the docstring; zero live blast radius (see item 3 inventory). (b) `escalation_never_upgrades` is exercised on a draft rule only, not a published+G6 `verified_eligible` rule; guaranteed by `most_severe` ordering regardless.

**Item 6 — Static typing/hygiene: no defect introduced; pre-existing typing debt confirmed.**
- Ran `python -m pyright app/rules/evaluator.py` (pyright 1.1.396): exactly 2 errors, both at line 745 (`exc_downgrade`/`geom_downgrade`: `str | None` vs `most_severe(*statuses: str)`). That call line and `coverage.py` are byte-unchanged from base (neither appears in the diff), so both errors are pre-existing base debt, not introduced by this task. Runtime is None-safe: `most_severe` explicitly skips `None` (coverage.py:65-66). The three new `most_severe` call sites (297/319/321) pass `downgrade or cov.COVERAGE_VERIFIED` — always `str` — and are pyright-clean. Nothing is masked.
- `_resolved` at evaluator.py:166-167 is an underscore-named tuple-unpacking placeholder in untouched base code (`for step, _resolved, result in computed`), not dead code.
- `python -m ruff check app/rules tests/rules`: "All checks passed!" (ruff 0.9.9); no unused imports; the diff adds no imports to evaluator.py.

**Item 7 — Contract integrity: VERIFIED.**
- Both `rule_evaluation.schema.json` copies resolve to the identical git blob `9e99b908a875cc190a410213ad2763edb286f022` at base AND at HEAD; sha256 `7454b3d5edb6a6438498ea1b022481d04b38ffbaaecd9a3aaccc9ae3974cb130` for both, matching the producer's report. Byte-unchanged, byte-identical.
- `git diff 84c1bf2..HEAD --name-only` = exactly 4 files (producer report, evaluator.py, two test files under `tests/rules/`); no forbidden path (`app/api/`, `app/contracts/`, `packages/contracts/`, `_contract_schemas/`, `tests/api/`, `.claude/`, `tools/`, `docs/` all untouched). Dependency files (pyproject/requirements/locks): zero diff.
- The schema-guard test compares the escalated exported trace's key set to the declared property set of both the engine trace schema and the canonical contract's `$defs.evaluation_trace` (each `additionalProperties:false`); full-document validation is exercised by the untouched, green `tests/api/test_rule_evaluation_api.py`.

**Item 8 — Independent test execution: EXACT MATCH.**
- `python -m pytest tests/rules -q` in the worktree's `services/api`: **328 passed in 3.77s** (expected 328).
- `python -m pytest tests -q`: **1066 passed in 13.51s** (expected 1066). Zero failures, zero skips, zero xfails. Arithmetic vs the producer's frozen-base baseline (291/1029 + 37 new) is consistent; the base-SHA baseline itself was not re-run (would require a checkout this read-only review cannot perform) and is not load-bearing for the verdict.

**Item 9 — Stale rule text: CONFIRMED not edited; follow-up, not rework.**
- `r5_height.rule.json` final limitations entry (verbatim, still present at HEAD): "…they are surfaced as professional_review_required only when a caller supplies the flag, and are otherwise a documented limitation." The "only when a caller supplies the flag" clause is now inaccurate (an unsupplied flag also surfaces PRR, as indeterminate). `git diff base..HEAD -- services/api/app/rules/rulesets/` is empty — the producer correctly did not touch a lifecycle-controlled legal artifact (principle 12; `.claude/rules/legal-rules.md`). Recommended follow-up task: correct the wording under legal-reviewer eyes; consider folding in the OBS-3 authoring guidance below.

## Directive/requirement verification

This packet carries `directive_refs: D-004 (ALL)`. Per the dispatch, the full requirement-by-requirement D-004 pass is performed by the independent `directive-compliance-verifier` and recorded in `verification.json`; this G3 report covers the two D-004 items named in AS-6 as far as a code review can:

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-004-R302 (worktree attestation before first write) | 2122cd2 | PASS as documented | Producer report §1 records the four-check attestation (frozen base `84c1bf2`, `agent-*` worktree, matching branch, clean tree) run before the first write; the attested base SHA equals the actual diff base and the harness-worktree naming is consistent. The runtime attestation itself is the producer's record; independent re-derivation belongs to the directive verifier. |
| D-004-R303 (evidence + requested status returned; no git/gh/CLI writes by producer) | 2122cd2 | PASS as documented | Work arrived as a single orchestrator-ported commit; producer report §1 states no git/gh/project_control invocations and requests `awaiting_gate` (§11) rather than claiming completion. Nothing in the diff or worktree contradicts it. |
| D-004 remaining requirement IDs | 2122cd2 | DEFERRED to directive-compliance-verifier | Outside this G3's dispatch scope by explicit orchestrator instruction; must be PASS in `verification.json` before acceptance. |

## Steps independently executed

1. `git -C <worktree> rev-parse HEAD` → `2122cd27a49511df079e0bf30baf5093d384a012`; `git status --porcelain` → clean; `git log --oneline 84c1bf2..HEAD` → single commit; `git merge-base --is-ancestor` → base is ancestor.
2. `git diff 84c1bf2..HEAD --name-only` and `--stat` → 4 files, +1202/−8.
3. Read full `evaluator.py` at HEAD plus the evaluator/test diffs hunk-by-hunk; read `coverage.py`, `test_rules_df6_exception_indeterminate.py` (all 37 tests), amended and unamended portions of `test_r5_height_setback.py`.
4. `sed -n '98p'` on the trust-replan report → verbatim DF-6 row.
5. Exception/effect/condition inventory script over all 8 `*.rule.json`; `grep` for `exists` as predicate op across `services/api`.
6. Verified `r5_residential_far.rule.json` site_class design text, `integration.py` TARGET_FAMILY + lines 570-572, and `test_rule_evaluation_api.py:246-262` (the blanket variant's structural casualty).
7. `git rev-parse HEAD:<schema>` / `BASE:<schema>` + `sha256sum` on both contract copies; dependency-file diff.
8. `python -m pytest tests/rules -q` (328 passed), `python -m pytest tests -q` (1066 passed), `python -m ruff check app/rules tests/rules` (clean), `python -m pyright app/rules/evaluator.py` (2 pre-existing errors at line 745 only).

## Expected versus actual

Every expected value matched: frozen SHA, single-commit topology, 4-file diff, byte-identical contract blobs, 328/1066 exact test counts, ruff clean, stale limitations sentence present and untouched, `exists` absent from all committed exception conditions.

## Evidence paths

- `services/api/app/rules/evaluator.py` (lines 227-245, 248-325, 745) — in worktree `.claude/worktrees/M4-T008-df6-exceptions`
- `services/api/app/rules/coverage.py` (lines 51-69)
- `services/api/tests/rules/test_rules_df6_exception_indeterminate.py`
- `services/api/tests/rules/test_r5_height_setback.py`
- `services/api/app/rules/rulesets/r5_height.rule.json` (limitations, final entry); `r5_residential_far.rule.json` (lines 28, 69-74); `services/api/app/rules/integration.py` (lines 69, 570-573)
- `services/api/tests/api/test_rule_evaluation_api.py` (line 262; untouched)
- `project-control/tasks/M4-T008.json`; `project-control/reports/M4-T008-producer-report.md`; `project-control/reports/WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23.md` (line 98)

## Human-style walkthrough findings

Not applicable (no UI). The trace-level user-visible artifact — the indeterminate note text — names the exception id, the exact unsupplied inputs, and states the fail-closed reasoning in plain language; the r5-height no-flags evaluation reads as an honest "cannot determine, professional review" rather than a false confident envelope.

## Regression/security/provenance findings

No regression (full suite green at exact expected counts; all-inputs-present behavior verified bit-equivalent by code reading and by AS-2 tests). No security surface touched. Provenance intact: rulesets, snapshots, citations, and both contract schema copies byte-unchanged; the fix uses only existing `coverage_status` and `notes` fields.

## Defects

No blocking defects. Observations for the record:
- OBS-1 (Low, follow-up): stale `r5_height.rule.json` limitations sentence (item 9) — needs a legal-reviewer-eyed wording correction task.
- OBS-2 (Low, follow-up): pre-existing pyright `reportArgumentType` x2 at `evaluator.py:745` — widen `coverage.most_severe` to `*statuses: str | None` (runtime already None-safe); pre-dates this task, masks nothing.
- OBS-3 (Low, informational): the skip-indeterminate path escalates to PRR regardless of the exception's own effect; packet-conform and fail-closed, with zero live blast radius today (every skip-capable committed exception is itself PRR-effect), but future rule authors adding a conditional `documented_limitation`/`conditional_alternative` exception should know an unsupplied input yields PRR, not the milder effect. Candidate content for the OBS-1 follow-up.
- OBS-4 (Low, informational): no explicit test for OBS-3's over-escalation case or for indeterminate-vs-verified_eligible composition; both are guaranteed by `most_severe` ordering and are hypothetical today.

## Required rework

None. OBS-1 through OBS-4 are follow-up/recorded items, not rework for M4-T008.

## Reviewer conclusion

The DF-6 fail-open (silent skip of a coverage-downgrading exception on an unsupplied optional input) is genuinely closed at the frozen SHA: detection is by-name and pre-outcome, the escalation rides the existing most_severe/PRR machinery, all-inputs-present behavior is bit-for-bit preserved, both contract copies are byte-identical to base, the test evidence is strong and behavior-level, and the producer's narrowing of the blanket semantic is a disclosed, measured, fail-closed-or-equal scope decision that correctly declines a legal-interpretation call — deviation ACCEPTED, DF-6 closed as contracted. Acceptance remains conditional on the independent D-004 directive verification pass (producer ≠ verifier) recorded by the orchestrator.

VERDICT: PASS — DF-6 is closed as recorded with the disclosed deviation accepted, all nine review items reproduced clean at SHA 2122cd2, and only non-blocking follow-up observations.
