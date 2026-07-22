# M4-T004 — G3 (code review) verbatim return

_Verbatim independent code-reviewer return (transport decoding only). Orchestrator-recorded._

**Task:** M4-T004. **Frozen SHA:** `3e45524` (base `58432cf`). **Reviewer:** code-reviewer (read-only). **Verdict: PASS.**

## Commands (worktree @ 3e45524, from services/api)
`ruff check app tests` → All checks passed. `pytest tests/rules/ -q` → 152 passed. `pytest -q` → 742 passed. `git diff --name-only 58432cf 3e45524 -- services/api/app` → exactly evaluator.py, integration.py, registry.py.

## Scope — PASS
Source limited to the three allowed files. models.py/coverage.py/lifecycle.py/contracts/lock/manifest/scripts untouched. New tests/fixtures under tests/rules/fixtures/m4t004* + test_rules_fh_safeguards.py. Control-plane files are the task's own records.

## FH-1 — PASS
`datetime.date(year, month, day)` in try/except ValueError; regex groups → int safely; shape + isinstance(str) retained; leap logic delegated to stdlib (correct). Impossible days fail closed; genuine leap days valid; None/non-string unchanged. Verified by test_fh1_*.

## FH-3 — PASS
`evaluations` via `_as_list(...)`; `family_coverage` gated by isinstance(dict). Foreign non-list/non-dict treated as empty instead of raising TypeError. Verified-status guard still fires on top-level, a genuine trace inside a list (even with junk family_coverage), and a verified family_coverage. No behavior change for well-formed payloads. Verified by six test_fh3_*.

## FH-2 — PASS
Candidates = is_in_effect(as_of_date) AND applicability_satisfied(rule, inputs) using REAL RuleDefinition.is_in_effect (half-open [from,to)) and output_names() (models.py unchanged). Grouping by output name; contested = outputs emitted by ≥2 candidates; complementary (distinct outputs) → None; cross-family excluded (per-family _by_family lookup); disjoint applicability → ≤1 candidate → None. Determinism: contested sorted, competing rules keyed by rule_id then sorted, per-rule output_names sorted — load-order-independent (test proves byte-identical under reversed input; integration test proves reload-independence). applicability_satisfied uses a NARROW exception tuple (not bare except) → False. Typed object shape carries competing_rules with rule_id/version/effective_from/effective_to/output_names; no outputs/determination produced; strict-JSON holds (only str/bool/None/list-of-str). Integration _conflict_result builds a valid PropertyRuleEvaluation with PRR, evaluations=[], no determination, provenance/district preserved, typed rule_conflict, coverage_source fail_safe; rule_conflict added additively to as_dict/export; assert_not_verified/export/never-Verified hold. as_of_date threading additive (default None preserves behavior); conflict check placed after inputs/input_provenance built and before the eval loop. Real single-rule R5 unaffected (no conflict, unchanged 1.5 FAR/15000, rule_conflict=None).

## Test quality — PASS
Adversarial, deterministic, offline. Positive conflict + every negative control + half-open boundary + load-order independence + strict-JSON + provenance + never-Verified. Non-tautological: parametrized FAR expectations (1.0/2.0) map to distinct fixture params, so assertions fail if as_of_date threading or the half-open boundary broke; removing an FH-3 guard fails test_fh3_*; removing the sort fails the load-order test. Fixtures clearly SYNTHETIC.

## Observations (INFO, non-blocking)
INFO-1: detect_rule_conflicts does not re-validate as_of_date through _valid_iso_date; relies on is_in_effect lexical comparison. Harmless today (single real rule; a hypothetical multi-rule family with an impossible date at most surfaces a PRR conflict — still fail-closed, no value); the eval loop separately fails closed on invalid dates. Worth noting for the future public-endpoint task; not a defect at this slice.

## Legal/provenance safety
No legal value produced from competing rules; a conflict is always professional_review_required, never Verified. Provenance preserved. No rule promotion/ranking/merging/superseding — detection only. Consistent with permanent principles 1, 2, 6, 12.

## VERDICT: PASS
